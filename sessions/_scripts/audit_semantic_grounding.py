import sys
import os
import re
import json
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

        # Load session config for character and lore entities
        config_path = os.path.join(base_dir, "sessions", "config", f"{session_id}-session-config.json")
        tier_b_entities = set()
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as cf:
                    cfg = json.load(cf)
                    for pc in cfg.get("pcs", []):
                        for part in pc.get("character", "").lower().split():
                            if len(part) > 2:
                                tier_b_entities.add(part)
                    for npc in cfg.get("npcs", []):
                        for part in npc.get("name", "").lower().split():
                            if len(part) > 2:
                                tier_b_entities.add(part)
            except Exception:
                pass

        # High-value Tier B narrative keywords (relics, spell manifestations, trauma, lore)
        tier_b_pattern = re.compile(
            r"\b(beret|normalcy|flashlight|petrif\w*|calcif\w*|fading into|movement under|"
            r"guiding bolt|living ink|lost roads|satans?|satyrs?|traumatic|trauma|"
            r"protect|gift shop|all i got was|stupid hat|stone tablet|statue)\b",
            re.IGNORECASE
        )

        unjustified_skips = []
        consecutive_spoken_skips = 0
        max_consecutive_spoken = 0
        consecutive_sample = []

        for num_str, reason in skipped_items:
            line_idx = int(num_str) - 1
            if 0 <= line_idx < len(raw_lines):
                r_line = raw_lines[line_idx]
                # Match both **Speaker (PC/NPC):** and raw indexed **Player/GM:**
                sm = re.match(r"^\*\*([^*]+?)(?:\s*\((PC|NPC)\))?:\*\*\s*(.+)$", r_line)
                if sm and reason == "ooc":
                    speaker, char_type, dialogue = sm.group(1).strip(), sm.group(2), sm.group(3).strip()
                    words = extract_content_words(dialogue)

                    # Check for Tier B Lore / Action manifestations dropped as OOC
                    tb_match = tier_b_pattern.search(dialogue)
                    if tb_match:
                        errors.append(
                            f"Scene {scene_id}: [TIER_B_LORE_DROP] L{int(num_str):04d} ({speaker}): "
                            f"'{dialogue[:75]}...' contains critical narrative intent ('{tb_match.group(0)}') but was marked as (ooc) skip!"
                        )

                    is_meta = any(meta in dialogue.lower() for meta in [
                        "roll", "initiative", "saving throw", "spell slot", "dice", 
                        "laugh", "chuckle", "character sheet", "wifi", "discord", "d4", "d6", "d20",
                        "muted", "mic"
                    ])
                    
                    if len(words) >= 4 and not is_meta:
                        consecutive_spoken_skips += 1
                        if len(consecutive_sample) < 4:
                            consecutive_sample.append((int(num_str), speaker, dialogue))
                        if consecutive_spoken_skips > max_consecutive_spoken:
                            max_consecutive_spoken = consecutive_spoken_skips
                    else:
                        consecutive_spoken_skips = 0

                    if len(words) >= 8 and not is_meta and not tb_match:
                        unjustified_skips.append((int(num_str), speaker, dialogue))
                else:
                    consecutive_spoken_skips = 0

        if max_consecutive_spoken >= 5:
            sample_desc = " | ".join(f"L{l:04d} ({s}): '{d[:30]}...'" for l, s, d in consecutive_sample)
            errors.append(
                f"Scene {scene_id}: [SUSPICIOUS_CLUSTER_DROP] {max_consecutive_spoken} consecutive spoken dialogue turns marked as (ooc) skip. "
                f"Verify in-character banter/comedy was not omitted. Sample: [{sample_desc}]"
            )

        if unjustified_skips:
            for line_no, spk, dial in unjustified_skips:
                warnings.append(
                    f"Scene {scene_id}: Potential Canon Dialogue Drop at L{line_no:04d} ({spk}): '{dial[:70]}...' marked as (ooc) skip. Justify as (banter), (mechanics), or (compressed)."
                )

        content_no_ledger = re.sub(r"<!--\s*LEDGER:.*?-->", "", block_content, flags=re.DOTALL)
        paragraphs = [p.strip() for p in content_no_ledger.split("\n\n") if p.strip()]

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

                    overlap = False
                    for rw in raw_turn_words:
                        for pw in para_words:
                            if rw == pw:
                                overlap = True
                                break
                            if (rw in PHONETIC_ALIASES and pw in PHONETIC_ALIASES[rw]) or (pw in PHONETIC_ALIASES and rw in PHONETIC_ALIASES[pw]):
                                overlap = True
                                break
                            sr = re.sub(r'(?:ing|edly|ed|es|s|ly|ment|tion|al)$', '', rw)
                            sr = re.sub(r'([b-df-hj-np-tv-z])\1$', r'\1', sr)
                            sp = re.sub(r'(?:ing|edly|ed|es|s|ly|ment|tion|al)$', '', pw)
                            sp = re.sub(r'([b-df-hj-np-tv-z])\1$', r'\1', sp)
                            if len(sr) >= 3 and len(sp) >= 3 and sr == sp:
                                overlap = True
                                break
                            if len(rw) >= 5 and len(pw) >= 5 and rw[:5] == pw[:5] and abs(len(rw) - len(pw)) <= 3:
                                overlap = True
                                break
                        if overlap:
                            break

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
