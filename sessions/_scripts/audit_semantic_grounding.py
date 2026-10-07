import sys
import os
import re
import json
import math
import argparse
import datetime
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "at", "by", "for", 
    "with", "about", "against", "between", "into", "through", "during", "before", "after", 
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", 
    "again", "further", "then", "once", "here", "there", "all", "any", "both", "each", 
    "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", 
    "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", 
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", 
    "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", 
    "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "would",
    "like", "yeah", "okay", "yes", "oh", "um", "uh", "well", "know", "say", "said", "think",
    "going", "want", "see", "look", "get", "got", "come", "came", "make", "made", "table", "note",
    "also", "really", "right", "sure", "thing", "things", "good", "mean", "much", "even"
}

HIGH_RISK_FOREIGN_PROPS = {
    "sensor", "sensors", "laser", "lasers", "elevator", "keycard", "helicopter", 
    "lockpick", "lockpicks", "suv", "sedan", "ford", "chevy", "toyota"
}

PHONETIC_ALIASES = {
    "nancy": {"nincy", "nanci"},
    "nincy": {"nancy", "nanci"},
    "crit": {"critical"},
    "critical": {"crit"}
}

import unicodedata

def clean_lines(filepath):
    lines = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = unicodedata.normalize("NFKD", line.strip())
            match = re.match(r"^L\d{4}:\s*(.*)$", line)
            if match:
                lines.append(match.group(1))
            else:
                lines.append(line)
    return lines

def extract_content_words(text):
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return [w for w in words if w not in STOPWORDS]

def parse_ledger_list(list_str):
    if not list_str or list_str.strip() == "[]":
        return []
    matches = re.findall(r"L?(\d+)", list_str)
    return [int(m) for m in matches]


def words_overlap(raw_words, prose_words):
    """Fuzzy content-word overlap: exact, phonetic alias, crude stem, or 5-char prefix."""
    for rw in raw_words:
        for pw in prose_words:
            if rw == pw:
                return True
            if (rw in PHONETIC_ALIASES and pw in PHONETIC_ALIASES[rw]) or (pw in PHONETIC_ALIASES and rw in PHONETIC_ALIASES[pw]):
                return True
            sr = re.sub(r'(?:ing|edly|ed|es|s|ly|ment|tion|al)$', '', rw)
            sr = re.sub(r'([b-df-hj-np-tv-z])\1$', r'\1', sr)
            sp = re.sub(r'(?:ing|edly|ed|es|s|ly|ment|tion|al)$', '', pw)
            sp = re.sub(r'([b-df-hj-np-tv-z])\1$', r'\1', sp)
            if len(sr) >= 3 and len(sp) >= 3 and sr == sp:
                return True
            if len(rw) >= 5 and len(pw) >= 5 and rw[:5] == pw[:5] and abs(len(rw) - len(pw)) <= 3:
                return True
    return False


# ---------------------------------------------------------------------------
# Skip-Ledger Governance (DEC-002 tiers, DEC-011/016 inclusive fiction, DEC-024)
# ---------------------------------------------------------------------------
# (ooc) is Tier C only: short technical/meta fragments. A spoken turn carrying
# SUBSTANTIVE_SKIP_MIN_WORDS+ content words cannot hide behind a naked (ooc);
# it must be rendered, typed (banter|mechanics|compressed), or exempted with a
# recorded reason in sN-session-config.json legitimate_ooc_lore_skips.

SUBSTANTIVE_SKIP_MIN_WORDS = 8
COMPRESSED_MIN_SHARED_WORDS = 2
COMPRESSED_MIN_SHARED_RATIO = 0.25

META_TABLE_MARKERS = [
    "roll", "initiative", "saving throw", "spell slot", "dice",
    "laugh", "chuckle", "character sheet", "wifi", "discord", "d4", "d6", "d20",
    "muted", "mic"
]

def load_skip_exemptions(cfg):
    """legitimate_ooc_lore_skips accepts legacy ints or {line, reason} records. Returns {line: reason}."""
    exemptions = {}
    for entry in cfg.get("legitimate_ooc_lore_skips", []):
        if isinstance(entry, dict):
            line = entry.get("line")
            if isinstance(line, int):
                exemptions[line] = entry.get("reason") or "(no reason recorded)"
        elif isinstance(entry, int):
            exemptions[entry] = "(legacy exemption, no reason recorded)"
    return exemptions


def _lexicon_term_to_regex(term):
    term = term.strip().lower()
    if not term:
        return None
    if term.endswith("*"):
        return r"\b" + re.escape(term[:-1]) + r"\w*"
    body = re.escape(term).replace(r"\ ", r"\s+")
    tail = r"\b" if re.match(r"\w", term[-1]) else ""
    return r"\b" + body + tail


def load_lore_lexicon(session_id, base_dir, session_cfg=None):
    """Union of campaign-config lore_lexicon, session_lore_terms, and NPC names. Returns a compiled regex or None.

    Lore vocabulary lives in config, never in Python, so a new session extends the
    gate by adding terms rather than editing the auditor."""
    terms = []
    campaign_path = os.path.join(base_dir, "sessions", "config", "campaign-config.json")
    if os.path.exists(campaign_path):
        with open(campaign_path, "r", encoding="utf-8") as f:
            terms.extend(json.load(f).get("lore_lexicon", []))

    if session_cfg is None:
        session_cfg = {}
        cfg_path = os.path.join(base_dir, "sessions", "config", f"{session_id}-session-config.json")
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    session_cfg = json.load(f)
            except Exception:
                session_cfg = {}
    for item in session_cfg.get("session_lore_terms", []):
        t = item.get("term", "") if isinstance(item, dict) else str(item)
        t = t.strip()
        if t:
            terms.append(t)
    # NPC names count as lore only as whole phrases; generic descriptor parts
    # ("Spectral Child", "The Three Fates") would otherwise fire on table talk.
    for npc in session_cfg.get("npcs", []) or []:
        name = npc.get("name", "") if isinstance(npc, dict) else str(npc)
        name = name.strip()
        if name:
            terms.append(name)

    patterns = [p for p in (_lexicon_term_to_regex(t) for t in terms) if p]
    if not patterns:
        return None
    return re.compile("|".join(patterns), re.IGNORECASE)


def audit_skip_ledger(scene_id, skipped_items, raw_lines, rendered_prose_words,
                      lore_re, exemptions):
    """Governs the skipped=[...] ledger of one scene. Returns (errors, warnings)."""
    errors, warnings = [], []
    consecutive_spoken_skips = 0
    max_consecutive_spoken = 0
    consecutive_sample = []

    for num_str, reason in skipped_items:
        num = int(num_str)
        line_idx = num - 1
        if not (0 <= line_idx < len(raw_lines)):
            continue
        r_line = raw_lines[line_idx]
        sm = re.match(r"^\*\*([^*]+?)(?:\s*\((PC|NPC)\))?:\*\*\s*(.+)$", r_line)
        if not sm:
            consecutive_spoken_skips = 0
            continue
        speaker, dialogue = sm.group(1).strip(), sm.group(3).strip()
        words = extract_content_words(dialogue)
        is_meta = any(meta in dialogue.lower() for meta in META_TABLE_MARKERS)
        exempt_reason = exemptions.get(num)

        if reason == "compressed":
            unique = set(words)
            shared = [w for w in unique if words_overlap([w], rendered_prose_words)]
            needed = min(len(unique), max(COMPRESSED_MIN_SHARED_WORDS,
                                          math.ceil(len(unique) * COMPRESSED_MIN_SHARED_RATIO)))
            if len(shared) < needed and not exempt_reason:
                errors.append(
                    f"Scene {scene_id}: [HOLLOW_COMPRESSED_SKIP] L{num:04d} ({speaker}): '{dialogue[:70]}...' "
                    f"tagged (compressed) but shares {len(shared)} content word(s) with the rendered prose (need {needed}). "
                    f"Novelize its substance, retag honestly, or exempt with a reason."
                )
            consecutive_spoken_skips = 0
            continue

        if reason not in {"ooc", "banter", "mechanics"}:
            consecutive_spoken_skips = 0
            continue

        tb_match = lore_re.search(dialogue) if lore_re else None
        if tb_match and not exempt_reason:
            errors.append(
                f"Scene {scene_id}: [TIER_B_LORE_DROP] L{num:04d} ({speaker}): "
                f"'{dialogue[:75]}...' contains lore term '{tb_match.group(0)}' but was skipped as ({reason}). "
                f"Render it, tag (compressed) with real prose coverage, or exempt with a reason in legitimate_ooc_lore_skips."
            )

        if reason == "ooc":
            # Track consecutive non-meta spoken turns marked as naked ooc
            if len(words) >= 4 and not is_meta and not exempt_reason:
                consecutive_spoken_skips += 1
                if len(consecutive_sample) < 4:
                    consecutive_sample.append((num, speaker, dialogue))
                max_consecutive_spoken = max(max_consecutive_spoken, consecutive_spoken_skips)
            else:
                consecutive_spoken_skips = 0

            if len(words) >= SUBSTANTIVE_SKIP_MIN_WORDS and not is_meta and not tb_match and not exempt_reason:
                errors.append(
                    f"Scene {scene_id}: [UNJUSTIFIED_OOC_DROP] L{num:04d} ({speaker}): '{dialogue[:70]}...' "
                    f"({len(words)} content words) hides behind a naked (ooc). Render it, type it as "
                    f"(banter)/(mechanics)/(compressed), or exempt it with a reason in legitimate_ooc_lore_skips."
                )
        elif reason in {"banter", "mechanics"}:
            consecutive_spoken_skips = 0
            # Spoken in-character dialogue or roleplay quotes cannot be dropped under banter or mechanics
            has_quoted_speech = bool(re.search(r'["“][^"”]+["”]', dialogue))
            if has_quoted_speech and len(words) >= 2 and not is_meta and not exempt_reason:
                errors.append(
                    f"Scene {scene_id}: [UNJUSTIFIED_DIALOGUE_DROP] L{num:04d} ({speaker}): '{dialogue[:70]}...' "
                    f"contains quoted in-character speech but was skipped as ({reason}). "
                    f"Render it, novelize as action, or exempt with a reason in legitimate_ooc_lore_skips."
                )

    if max_consecutive_spoken >= 5:
        sample_desc = " | ".join(f"L{l:04d} ({s}): '{d[:30]}...'" for l, s, d in consecutive_sample)
        errors.append(
            f"Scene {scene_id}: [SUSPICIOUS_CLUSTER_DROP] {max_consecutive_spoken} consecutive spoken dialogue turns marked as skip ({sample_desc}). "
            f"Verify in-character banter/comedy was not omitted."
        )
    return errors, warnings

# ---------------------------------------------------------------------------
# Transcript Boundary Check (FP-17 enforcement)
# ---------------------------------------------------------------------------
# A scene block must terminate at the final tabletop turn declared in the index.
# Track A hard-cuts at the session cutoff; Track B may carry staging past it
# only when the intent contract itemizes a liberty with "boundary": "post_cutoff".

BOUNDARY_TAIL_WORD_ALLOWANCE = 40

ANY_MARKER_RE = re.compile(r"<!--\s*L(\d+)(?:-L(\d+))?(?::[a-zA-Z_-]+)?\s*-->")
RAW_RANGE_RE = re.compile(r"<!--\s*RAW_RANGE:\s*\[(\d+),\s*(\d+)\]\s*\|\s*SCENE_ID:\s*(\d+)")


def load_session_cutoff(session_id, base_dir):
    """Return (cutoff_line, source). Declared cutoff beats derived cutoff."""
    for rel, key in (
        (os.path.join("sessions", "config", f"{session_id}-session-config.json"), "session_cutoff"),
        (os.path.join("sessions", "data", "index", f"{session_id}-source-decisions.json"), "session_cutoff"),
    ):
        path = os.path.join(base_dir, rel)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cutoff = data.get(key)
        if isinstance(cutoff, dict) and isinstance(cutoff.get("line"), int) and cutoff["line"] > 0:
            return cutoff["line"], os.path.basename(path)
    return None, None


def load_pc_names(session_id, base_dir):
    """Character tokens (>2 chars, excluding honorifics) for every PC in the session config."""
    path = os.path.join(base_dir, "sessions", "config", f"{session_id}-session-config.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    names = set()
    players = cfg.get("players", {})
    values = players.values() if isinstance(players, dict) else players
    for full in values:
        for part in str(full).replace(".", " ").split():
            if len(part) > 2 and part.lower() not in {"prof", "dr", "the"}:
                names.add(part)
    return sorted(names)


def load_post_cutoff_liberties(session_id, base_dir):
    path = os.path.join(base_dir, "sessions", "config", f"{session_id}-intent-contract.json")
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        intent = json.load(f)
    return {
        lib.get("scene", "").lower()
        for lib in intent.get("authorial_liberties", [])
        if lib.get("boundary") == "post_cutoff"
    }


def check_boundary_prose(block_text, pc_names, cutoff_line=None, tail_allowance=BOUNDARY_TAIL_WORD_ALLOWANCE):
    """Inspect one scene block for narrative that continues past its last transcript anchor.

    Returns a dict with:
      max_anchor       highest anchored raw line in the block (None if unanchored)
      beyond_cutoff    anchors that exceed the declared cutoff
      tail_words       words of prose after the final anchored paragraph
      tail_pc_actions  PC names that appear in that trailing prose
      flagged          True when the tail stages a PC or exceeds the word allowance
    """
    body = re.sub(r"<!--\s*LEDGER:.*?-->", "", block_text, flags=re.DOTALL)
    body = re.sub(r"<!--\s*RAW_RANGE:.*?-->", "", body, flags=re.DOTALL)

    anchors = []
    for m in ANY_MARKER_RE.finditer(body):
        anchors.append(int(m.group(1)))
        if m.group(2):
            anchors.append(int(m.group(2)))
    max_anchor = max(anchors) if anchors else None
    beyond_cutoff = sorted({a for a in anchors if cutoff_line is not None and a > cutoff_line})

    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    last_anchor_idx = -1
    for idx, para in enumerate(paragraphs):
        if ANY_MARKER_RE.search(para):
            last_anchor_idx = idx

    tail_paragraphs = []
    for para in paragraphs[last_anchor_idx + 1:]:
        clean = re.sub(r"<!--.*?-->", "", para).strip()
        if not clean or re.fullmatch(r"[\*\s\-_#]+", clean):
            continue
        tail_paragraphs.append(clean)
    tail_text = " ".join(tail_paragraphs)
    tail_words = len(tail_text.split())
    tail_pc_actions = sorted({n for n in pc_names if re.search(rf"\b{re.escape(n)}\b", tail_text)})

    return {
        "max_anchor": max_anchor,
        "beyond_cutoff": beyond_cutoff,
        "tail_words": tail_words,
        "tail_pc_actions": tail_pc_actions,
        "tail_preview": tail_text[:90],
        "flagged": bool(tail_pc_actions) or tail_words > tail_allowance,
    }


def audit_transcript_boundary(session_id, base_dir, blocks_dir=None, alt_blocks_dir=None):
    """Apply check_boundary_prose to the final Track A scene and its Track B counterpart.

    Returns (errors, warnings, info_lines).
    """
    blocks_dir = blocks_dir or os.path.join(base_dir, "sessions", "data", "clean", "blocks")
    alt_blocks_dir = alt_blocks_dir or os.path.join(base_dir, "sessions", "data", "clean", "blocks_authorial")
    errors, warnings, info = [], [], []

    prefix = f"{session_id}-scene-"
    if not os.path.isdir(blocks_dir):
        return errors, warnings, info
    track_a = []
    for fn in sorted(os.listdir(blocks_dir)):
        if not (fn.startswith(prefix) and fn.endswith(".md")) or "-alt" in fn:
            continue
        with open(os.path.join(blocks_dir, fn), "r", encoding="utf-8") as f:
            text = f.read()
        hdr = RAW_RANGE_RE.search(text)
        if hdr:
            track_a.append((int(hdr.group(2)), int(hdr.group(3)), fn, text))
    if not track_a:
        return errors, warnings, info

    pc_names = load_pc_names(session_id, base_dir)
    declared_cutoff, cutoff_source = load_session_cutoff(session_id, base_dir)
    all_anchor_max = max(
        (r["max_anchor"] for r in (check_boundary_prose(t, pc_names) for _, _, _, t in track_a) if r["max_anchor"]),
        default=None,
    )
    cutoff = declared_cutoff or all_anchor_max
    cutoff_label = f"L{cutoff:04d} ({cutoff_source})" if declared_cutoff else f"L{cutoff:04d} (derived from max anchor)"
    info.append(f"Session cutoff: {cutoff_label}")

    range_end, scene_id, fn, text = max(track_a, key=lambda t: t[0])
    report = check_boundary_prose(text, pc_names, cutoff)
    if report["beyond_cutoff"]:
        errors.append(
            f"Scene {scene_id}: [ANCHOR_BEYOND_CUTOFF] {fn} anchors {report['beyond_cutoff']} exceed session cutoff L{cutoff:04d}."
        )
    if report["flagged"]:
        who = ", ".join(report["tail_pc_actions"]) or "narration"
        errors.append(
            f"Scene {scene_id}: [POST_CUTOFF_STAGING] Track A {fn} continues {report['tail_words']} words past its final anchor "
            f"L{report['max_anchor']:04d} staging {who}: '{report['tail_preview']}...'. "
            f"Track A must cut at the transcript boundary (FP-17); move dramatized staging to Track B with an itemized "
            f"'boundary': 'post_cutoff' liberty."
        )
    else:
        info.append(f"Track A {fn}: cuts at L{report['max_anchor']:04d} (+{report['tail_words']} closing words) [PASS]")

    alt_fn = fn.replace(".md", "-alt.md")
    alt_path = os.path.join(alt_blocks_dir, alt_fn)
    if os.path.exists(alt_path):
        with open(alt_path, "r", encoding="utf-8") as f:
            alt_text = f.read()
        alt_report = check_boundary_prose(alt_text, pc_names, cutoff)
        scene_key = f"scene-{scene_id:02d}"
        licensed = scene_key in load_post_cutoff_liberties(session_id, base_dir)
        if alt_report["flagged"] and not licensed:
            who = ", ".join(alt_report["tail_pc_actions"]) or "narration"
            errors.append(
                f"Scene {scene_id}: [UNLICENSED_POST_CUTOFF_STAGING] Track B {alt_fn} stages {who} for "
                f"{alt_report['tail_words']} words past L{alt_report['max_anchor']:04d} with no "
                f"'boundary': 'post_cutoff' liberty for {scene_key} in {session_id}-intent-contract.json."
            )
        elif alt_report["flagged"]:
            info.append(
                f"Track B {alt_fn}: {alt_report['tail_words']} words of post-cutoff staging licensed by itemized liberty ({scene_key})."
            )
        else:
            info.append(f"Track B {alt_fn}: cuts at L{alt_report['max_anchor']:04d} [PASS]")

    return errors, warnings, info


def audit_session_grounding(session_id, base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    indexed_path = os.path.join(base_dir, "sessions", "data", "index", f"{session_id}-raw-indexed.md")
    manifest_path = os.path.join(base_dir, "sessions", "data", "index", f"{session_id}-manifest.json")
    story_path = os.path.join(base_dir, "sessions", "data", "clean", f"{session_id}-clean-story.md")
    history_path = os.path.join(base_dir, "sessions", "data", "index", "audit_history.json")

    if not os.path.exists(indexed_path) or not os.path.exists(manifest_path) or not os.path.exists(story_path):
        print(f"[ERROR] Required files missing for session {session_id}")
        return False, []

    raw_lines = clean_lines(indexed_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(story_path, "r", encoding="utf-8") as f:
        story_content = f.read()

    errors = []
    warnings = []
    grounding_scores = []

    sections = re.findall(
        r"<!--\s*RAW_RANGE:\s*\[(\d+),\s*(\d+)\]\s*\|\s*SCENE_ID:\s*(\d+)\s*(?:\|\s*(OOC))?\s*-->\s*(.*?)(?=<!--\s*RAW_RANGE:|$)", 
        story_content, 
        re.DOTALL
    )

    marker_re = re.compile(r"<!--\s*L(\d+)\s*-->")

    session_cfg = {}
    config_path = os.path.join(base_dir, "sessions", "config", f"{session_id}-session-config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as cf:
                session_cfg = json.load(cf)
        except Exception:
            session_cfg = {}
    lore_re = load_lore_lexicon(session_id, base_dir, session_cfg)
    skip_exemptions = load_skip_exemptions(session_cfg)

    print(f"\n================================================================================")
    print(f"🛡️  FORENSIC GROUNDING AUDITOR: SESSION {session_id.upper()}")
    print(f"================================================================================")

    for start_str, end_str, scene_id_str, ooc_flag, block_content in sections:
        start_line, end_line = int(start_str), int(end_str)
        scene_id = int(scene_id_str)
        if ooc_flag:
            continue

        raw_window_lines = raw_lines[start_line - 1: min(end_line, len(raw_lines))]
        raw_scene_text = " ".join(raw_window_lines)
        raw_scene_words = set(extract_content_words(raw_scene_text))

        ledger_match = re.search(r"<!--\s*LEDGER:\s*rendered=\[(.*?)\]\s*skipped=\[(.*?)\]\s*-->", block_content)
        if not ledger_match:
            errors.append(f"Scene {scene_id}: Missing LEDGER footer.")
            continue

        rendered_lines = parse_ledger_list(ledger_match.group(1))
        skipped_raw_str = ledger_match.group(2)
        skipped_items = re.findall(r"(\d+)(?:\(([^)]+)\))?", skipped_raw_str)

        content_no_ledger = re.sub(r"<!--\s*LEDGER:.*?-->", "", block_content, flags=re.DOTALL)
        paragraphs = [p.strip() for p in content_no_ledger.split("\n\n") if p.strip()]
        rendered_prose_words = set(extract_content_words(re.sub(r"<!--.*?-->", "", content_no_ledger)))

        s_errors, s_warnings = audit_skip_ledger(
            scene_id, skipped_items, raw_lines, rendered_prose_words, lore_re, skip_exemptions
        )
        errors.extend(s_errors)
        warnings.extend(s_warnings)

        scene_turns_evaluated = 0
        scene_grounded_turns = 0

        for para in paragraphs:
            markers = [int(m) for m in marker_re.findall(para)]
            if not markers:
                continue

            para_text_clean = re.sub(r"<!--.*?-->", "", para).strip()
            para_words = set(extract_content_words(para_text_clean))

            # Foreign prop check
            for prop in HIGH_RISK_FOREIGN_PROPS:
                if prop in para_words and prop not in raw_scene_words:
                    errors.append(
                        f"Scene {scene_id}: UNANCHORED FOREIGN PROP '{prop}' detected in prose with 0 occurrences in raw transcript."
                    )

            for m in markers:
                raw_idx = m - 1
                if 0 <= raw_idx < len(raw_lines):
                    r_line = raw_lines[raw_idx]
                    
                    # Tactical table note represents action
                    if r_line.startswith("*Table Note:"):
                        scene_turns_evaluated += 1
                        scene_grounded_turns += 1
                        continue

                    # Spoken dialogue turns
                    has_dialogue = re.match(r"^\*\*([^*]+):\*\*\s*(.*)$", r_line)
                    if not has_dialogue:
                        scene_turns_evaluated += 1
                        scene_grounded_turns += 1
                        continue

                    scene_turns_evaluated += 1
                    w_start = max(0, min(raw_idx, min(markers) - 1) - 4)
                    w_end = min(len(raw_lines), max(raw_idx + 1, max(markers)) + 5)
                    raw_turn_text = " ".join(raw_lines[w_start:w_end])
                    raw_turn_words = set(extract_content_words(raw_turn_text))

                    overlap = words_overlap(raw_turn_words, para_words)

                    if overlap:
                        scene_grounded_turns += 1
                    else:
                        warnings.append(
                            f"Scene {scene_id}: UNGROUNDED TURN at L{m:04d}.\n"
                            f"  Raw Line: '{raw_lines[raw_idx][:80]}...'\n"
                            f"  Prose: '{para_text_clean[:80]}...'\n"
                            f"  Diagnosis: 0 semantic token overlap between prose and raw transcript window."
                        )

        scene_prose_words = set(extract_content_words(content_no_ledger))
        common_scene_keywords = raw_scene_words.intersection(scene_prose_words)
        
        grounding_ratio = (scene_grounded_turns / scene_turns_evaluated) if scene_turns_evaluated > 0 else 1.0
        grounding_scores.append((scene_id, grounding_ratio, len(common_scene_keywords)))
        if grounding_ratio < 0.70:
            errors.append(
                f"Scene {scene_id}: CRITICAL LOW GROUNDING RATIO ({grounding_ratio*100:.1f}% < 70%). "
                f"Too many ungrounded turns in novelized scene."
            )

    print("\n--- SCENE FIDELITY & GROUNDING MATRIX ---")
    print(f"{'Scene ID':<10} | {'Turn Grounding %':<18} | {'Shared Topic Keywords':<22} | {'Status'}")
    print("-" * 65)
    for sc_id, g_ratio, kw_count in grounding_scores:
        status = "PASS" if g_ratio >= 0.85 else "WARN" if g_ratio >= 0.70 else "FAIL"
        print(f"Scene {sc_id:<4} | {g_ratio*100:>15.1f}% | {kw_count:>21} | {status}")

    print("\n--- TRANSCRIPT BOUNDARY (FP-17) ---")
    b_errors, b_warnings, b_info = audit_transcript_boundary(session_id, base_dir)
    for line in b_info:
        print(f"  {line}")
    errors.extend(b_errors)
    warnings.extend(b_warnings)

    print("\n--- FORENSIC VERDICT ---")
    
    # Record history
    history_record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": session_id,
        "status": "PASS" if not errors else "FAIL",
        "errors_count": len(errors),
        "warnings_count": len(warnings),
        "scene_scores": [{"scene_id": s, "ratio": round(r, 3), "keywords": k} for s, r, k in grounding_scores],
        "top_errors": errors[:5],
        "top_warnings": warnings[:5]
    }
    
    history_data = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        except Exception:
            history_data = []
    history_data.append(history_record)
    # keep last 50 runs
    history_data = history_data[-50:]
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, indent=2)

    if errors:
        print(f"[FAIL] {len(errors)} CRITICAL GROUNDING BREACHES DETECTED:")
        for e in errors:
            print(f"  ❌ {e}")
        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for w in warnings:
                print(f"  ⚠️ {w}")
        return False, errors
    else:
        print(f"[PASS] 100% TRANSCRIPT-TO-PROSE GROUNDING VERIFIED.")
        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for w in warnings:
                print(f"  ⚠️ {w}")
        return True, warnings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forensic Transcript Grounding & Semantic Entailment Auditor")
    parser.add_argument("session", help="Session ID (e.g. s1, s2, s3)")
    args = parser.parse_args()
    passed, _ = audit_session_grounding(args.session)
    sys.exit(0 if passed else 1)
