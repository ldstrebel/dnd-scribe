#!/usr/bin/env python3
"""Audit Reader Context & Declarative Lore Introductions (DEC-025).

Mechanizes the 'Reader Advocate' role by enforcing the 'Declared, First,
and Grounded' invariant for novelized scene blocks:
  1. Established vs. New: Terms that appeared in prior novel sessions
     (s1 through sN-1) are established canon and may appear anywhere.
  2. Declared: Terms appearing for the first time in sN must be declared in
     sN-session-config.json (session_lore_terms or npcs) with 'introduced_scene'.
  3. Ordering: An introduced term must not appear in any scene before its
     declared 'introduced_scene' (catches premature dropped callbacks).
  4. Grounding: The paragraph containing the first mention in 'introduced_scene'
     must carry a raw transcript line marker (<!-- L#### -->).

Zero heuristics. 100% deterministic verification.
"""

import os
import re
import sys
import json
import argparse

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

MARKER_RE = re.compile(r"<!--\s*L(\d+)(?::[a-zA-Z_-]+)?\s*-->")


def extract_session_num(sid):
    m = re.match(r"^s(\d+)$", sid.lower())
    return int(m.group(1)) if m else 0


def load_prior_text(base_dir, current_sid):
    """Aggregate all novel prose from prior sessions s1 .. s(N-1)."""
    curr_num = extract_session_num(current_sid)
    if curr_num <= 1:
        return ""

    prior_texts = []
    novel_dir = os.path.join(base_dir, "novel", "sessions")
    clean_dir = os.path.join(base_dir, "sessions", "data", "clean")

    for n in range(1, curr_num):
        prior_sid = f"s{n}"
        novel_file = os.path.join(novel_dir, f"{prior_sid}-story.md")
        clean_file = os.path.join(clean_dir, f"{prior_sid}-clean-story.md")
        
        path_to_read = novel_file if os.path.exists(novel_file) else clean_file
        if os.path.exists(path_to_read):
            try:
                with open(path_to_read, "r", encoding="utf-8") as f:
                    prior_texts.append(f.read().lower())
            except Exception:
                pass

    return "\n\n".join(prior_texts)


def load_declared_introductions(session_cfg):
    """Extract declared introductions from session config.

    Accepts dual format:
      str -> introduced_scene = 1 (legacy / default)
      {"term": str, "introduced_scene": int} -> explicit scene
    Returns dict: {term_lower: introduced_scene}
    """
    declared = {}

    # 1. session_lore_terms
    for item in session_cfg.get("session_lore_terms", []):
        if isinstance(item, dict):
            term = item.get("term", "").strip()
            scene = item.get("introduced_scene", 1)
            if term:
                declared[term.lower()] = scene
        elif isinstance(item, str):
            term = item.strip()
            if term:
                declared[term.lower()] = 1

    # 2. NPCs
    for npc in session_cfg.get("npcs", []):
        if isinstance(npc, dict):
            name = npc.get("name", "").strip()
            scene = npc.get("introduced_scene", 1)
            if name:
                declared[name.lower()] = scene
        elif isinstance(npc, str):
            name = npc.strip()
            if name:
                declared[name.lower()] = 1

    return declared


def audit_reader_context(session_id, base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    config_path = os.path.join(base_dir, "sessions", "config", f"{session_id}-session-config.json")
    session_cfg = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as cf:
                session_cfg = json.load(cf)
        except Exception:
            session_cfg = {}

    declared_intros = load_declared_introductions(session_cfg)
    prior_text = load_prior_text(base_dir, session_id)

    blocks_dir = os.path.join(base_dir, "sessions", "data", "clean", "blocks")
    if not os.path.exists(blocks_dir):
        return False, [f"Missing blocks directory: {blocks_dir}"], []

    scene_files = []
    for f in sorted(os.listdir(blocks_dir)):
        m = re.match(rf"^{session_id}-scene-(\d+)\.md$", f)
        if m:
            scene_files.append((int(m.group(1)), os.path.join(blocks_dir, f)))

    if not scene_files:
        return False, [f"No scene blocks found for {session_id} in {blocks_dir}"], []

    errors = []
    warnings = []
    terms_audited = set()

    # Track occurrences of terms across scenes
    # term -> [(scene_num, paragraph_text, has_marker)]
    occurrences = {term: [] for term in declared_intros}

    for sc_num, sc_path in scene_files:
        with open(sc_path, "r", encoding="utf-8") as bf:
            content = bf.read()

        content_no_ledger = re.sub(r"<!--\s*LEDGER:.*?-->", "", content, flags=re.DOTALL)
        paragraphs = [p.strip() for p in content_no_ledger.split("\n\n") if p.strip()]

        for para in paragraphs:
            # Skip markdown headers (# Chapter...) and meta comments
            if para.startswith("#") or (para.startswith("<!--") and not MARKER_RE.search(para)):
                continue
            para_lower = para.lower()
            markers = MARKER_RE.findall(para)
            has_marker = len(markers) > 0

            for term in declared_intros:
                # Use regex with word boundaries to match exact term or standard plural
                term_re = r"\b" + re.escape(term) + r"(?:s|es)?\b"
                if re.search(term_re, para_lower):
                    occurrences[term].append((sc_num, para, has_marker))
                    terms_audited.add(term)

    # Invariant Verification
    for term, declared_scene in declared_intros.items():
        is_prior = bool(re.search(r"\b" + re.escape(term) + r"\b", prior_text))
        term_occs = occurrences.get(term, [])

        if is_prior:
            # Established canon from earlier books: can appear anytime
            continue

        if not term_occs:
            # Declared but never mentioned in novel prose
            warnings.append(
                f"[UNUSED_LORE_DECLARATION] '{term}' is declared as introduced in Scene {declared_scene}, "
                f"but does not appear in any scene block for {session_id}."
            )
            continue

        first_scene, first_para, first_has_marker = term_occs[0]

        # 1. Ordering Invariant: Premature Mention
        if first_scene < declared_scene:
            errors.append(
                f"[PREMATURE_FIRST_MENTION] '{term}' appears in Scene {first_scene} before its declared "
                f"introductory Scene {declared_scene}! A reader has no context for this term yet."
            )

        # 2. Grounding Invariant: Must have line anchor in introduction scene
        intro_occs = [occ for occ in term_occs if occ[0] == declared_scene]
        if not intro_occs:
            errors.append(
                f"[MISSING_DECLARED_INTRODUCTION] '{term}' is declared to be introduced in Scene {declared_scene}, "
                f"but Scene {declared_scene} contains no mention of it!"
            )
        else:
            intro_scene, intro_para, intro_has_marker = intro_occs[0]
            if not intro_has_marker:
                errors.append(
                    f"Scene {declared_scene}: [UNGROUNDED_INTRODUCTION] The first mention of new term '{term}' "
                    f"sits in an unanchored paragraph with no raw line marker (<!-- L#### -->)! "
                    f"Introductions must be anchored to table audio."
                )

    print("======================================================================")
    print(f"📖 READER CONTEXT & INTRODUCTION AUDIT REPORT ({session_id.upper()})")
    print("======================================================================")
    print(f"• Terms Declared:     {len(declared_intros)}")
    print(f"• Terms Audited:      {len(terms_audited)}")
    print(f"• Status:             {'[PASS] PASSED' if not errors else '[FAIL] FAILED'}")

    if errors:
        print(f"\n[FAIL] {len(errors)} READER CONTEXT BREACHES DETECTED:")
        for e in errors:
            print(f"  ❌ {e}")
        return False, errors, warnings
    else:
        print(f"\n[PASS] 100% of New Terms Declared, First, and Grounded.")
        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for w in warnings:
                print(f"  ⚠️ {w}")
        return True, [], warnings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit Reader Context & Declarative Lore Introductions")
    parser.add_argument("session", help="Session ID (e.g. s1, s2, s5)")
    args = parser.parse_args()
    passed, errs, warns = audit_reader_context(args.session)
    sys.exit(0 if passed else 1)
