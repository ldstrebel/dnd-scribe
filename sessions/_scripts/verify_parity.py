import sys
import os
import re
import json
import hashlib

def get_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def clean_lines(filepath):
    lines = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = re.match(r"^L\d{4}:\s*(.*)$", line)
            if match:
                lines.append(match.group(1))
            else:
                lines.append(line)
    return lines

def parse_ledger_list(list_str):
    list_str = list_str.strip()
    if list_str == "[]" or not list_str:
        return []
    matches = re.findall(r"L?(\d+)", list_str)
    return [int(m) for m in matches]

def calculate_dialogue_words(lines, start_line, end_line):
    word_count = 0
    for idx in range(start_line - 1, min(end_line, len(lines))):
        line = lines[idx]
        match = re.match(r"^\*\*([^*]+):\*\*\s*(.*)$", line)
        if match:
            dialogue_text = match.group(2)
            word_count += len(dialogue_text.split())
    return word_count

# High-salience hallucinated vehicles and modern anachronisms to audit
SUSPECT_VEHICLES_AND_TECH = [
    "truck", "ford", "chevy", "toyota", "helicopter", "subway", 
    "motorcycle", "tanker", "tank combat", "smartphone", "laptop", "wifi"
]

def verify_semantic_grounding(s_content, raw_lines, m_start, m_end, scene_id, all_session_raw_text):
    """
    Forensic semantic audit:
    1. Checks that specific vehicles/technologies introduced in prose exist in the raw transcript.
    2. Checks that major NPCs present in raw transcript dialogue are represented in the prose.
    """
    errors = []
    warnings = []

    raw_window_lines = raw_lines[m_start - 1: min(m_end, len(raw_lines))]
    raw_scene_text = " ".join(raw_window_lines).lower()
    prose_text = re.sub(r"<!--.*?-->", "", s_content).lower()

    # 1. Unanchored concrete vehicle/tech check
    for entity in SUSPECT_VEHICLES_AND_TECH:
        # Ignore clothing terms like "tank top"
        if entity == "tank" and "tank top" in prose_text:
            continue
        if re.search(rf"\b{entity}s?\b", prose_text):
            # Check if it appeared anywhere in the raw transcript for this session
            if not re.search(rf"\b{entity}s?\b", all_session_raw_text):
                errors.append(
                    f"HALLUCINATED ENTITY in Scene {scene_id}: Concrete vehicle/tech '{entity}' "
                    f"appears in prose but is NEVER mentioned in the raw transcript for this entire session!"
                )

    # 2. Major NPC presence check
    raw_speakers = set()
    for r_line in raw_window_lines:
        sm = re.match(r"^\*\*([^*]+):\*\*", r_line)
        if sm:
            speaker_full = sm.group(1).lower()
            names = re.findall(r"\b[a-zA-Z]{3,}\b", speaker_full)
            for n in names:
                if n not in ["luke", "foreman", "gm", "william", "webb", "sophie", "noone", "dan", "strebs", "john", "hagey", "luke_s"]:
                    raw_speakers.add(n)

    for spk in raw_speakers:
        if raw_scene_text.count(spk) >= 3:
            if not re.search(rf"\b{spk}\b", prose_text):
                warnings.append(
                    f"POTENTIAL CHARACTER OMISSION in Scene {scene_id}: NPC '{spk.capitalize()}' is mentioned {raw_scene_text.count(spk)} times "
                    f"in raw lines {m_start}-{m_end} but is absent from the novelized scene prose."
                )

    return errors, warnings

def verify_parity(session_id, manifest_path=None, story_path=None,
                  blocks_dir=None, indexed_path=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = manifest_path or os.path.join(base_dir, "data", "index", f"{session_id}-manifest.json")
    indexed_path = indexed_path or os.path.join(base_dir, "data", "index", f"{session_id}-raw-indexed.md")
    story_path = story_path or os.path.join(base_dir, "data", "clean", f"{session_id}-clean-story.md")

    errors = []
    warnings = []

    if not os.path.exists(manifest_path):
        errors.append(f"Manifest not found at {manifest_path}")
        return False, errors, warnings
    if not os.path.exists(indexed_path):
        errors.append(f"Indexed file not found at {indexed_path}")
        return False, errors, warnings
    if not os.path.exists(story_path):
        errors.append(f"Story file not found at {story_path}")
        return False, errors, warnings

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    actual_hash = get_sha256(indexed_path)
    expected_hash = manifest.get("raw_file_hash")
    if actual_hash != expected_hash:
        errors.append(f"HASH LOCK MISMATCH: indexed file hash is '{actual_hash}', manifest expected '{expected_hash}'")

    raw_lines = clean_lines(indexed_path)
    all_session_raw_text = " ".join(raw_lines).lower()
    total_raw_lines = manifest.get("total_raw_lines")

    with open(story_path, "r", encoding="utf-8") as f:
        story_content = f.read()

    sections = re.findall(
        r"<!--\s*RAW_RANGE:\s*\[(\d+),\s*(\d+)\]\s*\|\s*SCENE_ID:\s*(\d+)\s*(?:\|\s*(OOC))?\s*-->\s*(.*?)(?=<!--\s*RAW_RANGE:|$)", 
        story_content, 
        re.DOTALL
    )

    covered_lines = set()
    story_scenes = {}

    for start_str, end_str, scene_id_str, ooc_flag, block_content in sections:
        start, end = int(start_str), int(end_str)
        scene_id = int(scene_id_str)
        is_ooc = bool(ooc_flag)

        block_lines = set(range(start, end + 1))
        overlap = block_lines.intersection(covered_lines)
        if overlap:
            errors.append(f"OVERLAP IN STORY: Scene {scene_id} range [{start}, {end}] overlaps with other scenes on lines: {sorted(list(overlap))[:10]}...")
        covered_lines.update(block_lines)

        story_scenes[scene_id] = {
            "range": (start, end),
            "content": block_content.strip(),
            "is_ooc": is_ooc
        }

    missing_lines = set(range(1, total_raw_lines + 1)) - covered_lines
    if missing_lines:
        errors.append(f"LINE LEAK DETECTED IN STORY: {len(missing_lines)} lines are not covered. Missing lines: {sorted(list(missing_lines))[:20]}...")

    manifest_scenes = {b["scene_id"]: b for b in manifest.get("scene_blocks", [])}

    for scene_id, m_block in manifest_scenes.items():
        m_start, m_end = m_block["line_range"]
        m_ooc = m_block.get("ooc", False)

        if scene_id not in story_scenes:
            errors.append(f"MISSING SCENE IN STORY: Scene {scene_id} ('{m_block['title']}') is present in manifest but missing from story.")
            continue

        s_block = story_scenes[scene_id]
        s_start, s_end = s_block["range"]
        s_ooc = s_block["is_ooc"]

        if s_start != m_start or s_end != m_end:
            errors.append(f"RANGE MISMATCH: Scene {scene_id} in story covers [{s_start}, {s_end}], but manifest expects [{m_start}, {m_end}]")

        if s_ooc != m_ooc:
            errors.append(f"OOC FLAGS MISMATCH: Scene {scene_id} OOC is {s_ooc} in story, but manifest expects {m_ooc}")

        if not m_ooc:
            ledger_match = re.search(
                r"<!--\s*LEDGER:\s*rendered=\[(.*?)\]\s*skipped=\[(.*?)\]\s*-->", 
                s_block["content"]
            )
            if not ledger_match:
                errors.append(f"MISSING LEDGER FOOTER: Scene {scene_id} does not contain a ledger footer block.")
                continue

            rendered_lines = parse_ledger_list(ledger_match.group(1))
            skipped_lines = parse_ledger_list(ledger_match.group(2))

            expected_ledger = [turn["line"] for turn in m_block.get("dialogue_ledger", [])]

            double_counted = set(rendered_lines) & set(skipped_lines)
            if double_counted:
                errors.append(f"LEDGER PARTITION VIOLATION in Scene {scene_id}: lines listed as both rendered and skipped: {sorted(double_counted)}")

            story_ledger = set(rendered_lines) | set(skipped_lines)
            for expected_line in expected_ledger:
                if expected_line not in story_ledger:
                    errors.append(f"DIALOGUE TURN DROP in Scene {scene_id}: Line L{expected_line:04d} from manifest is not accounted for in story ledger.")
            phantom = story_ledger - set(expected_ledger)
            if phantom:
                errors.append(f"PHANTOM LEDGER ENTRIES in Scene {scene_id}: footer lists lines not in manifest dialogue ledger: {sorted(phantom)}")

            covered = set(skipped_lines)
            for turn in m_block.get("dialogue_ledger", []):
                span = turn.get("covers")
                if span:
                    covered.update(range(span[0], span[1] + 1))
                else:
                    covered.add(turn["line"])
            uncovered = [n for n in range(m_start, m_end + 1) if n not in covered]
            if uncovered:
                errors.append(f"UNACCOUNTED RAW LINES in Scene {scene_id}: lines not inside any rendered beat span or skipped list: {uncovered}")

            skipped_raw_str = ledger_match.group(2)
            skipped_items = re.findall(r"(\d+)(?:\(([^)]+)\))?", skipped_raw_str)
            for num_str, reason in skipped_items:
                if not reason or reason not in ["ooc", "duplicate"]:
                    errors.append(f"ILLEGAL SKIP REASON in Scene {scene_id}: Line L{int(num_str):04d} has unapproved skip reason: '{reason}'")

            content_no_ledger = re.sub(
                r"<!--\s*LEDGER:.*?-->", "", s_block["content"], flags=re.DOTALL
            )
            marker_re = re.compile(r"<!--\s*L(\d+)\s*-->")

            inline_markers = []
            for para in content_no_ledger.split("\n\n"):
                para = para.strip()
                if not para:
                    continue
                para_markers = [int(x) for x in marker_re.findall(para)]
                if not para_markers:
                    continue
                tail = para
                trailing = 0
                while True:
                    m = re.search(r"<!--\s*L\d+\s*-->\s*$", tail)
                    if not m:
                        break
                    trailing += 1
                    tail = tail[: m.start()].rstrip()
                if trailing != len(para_markers):
                    errors.append(f"MID-PARAGRAPH MARKER in Scene {scene_id}: markers must be a trailing cluster at paragraph end (found {len(para_markers)} markers, only {trailing} trailing): '{para[:60]}...'")
                if len(para_markers) > 3:
                    warnings.append(f"MARKER PILE-UP in Scene {scene_id}: one paragraph carries {len(para_markers)} turn markers — verify these turns are genuinely fused: '{para[:60]}...'")
                inline_markers.extend(para_markers)

            expected_rendered = rendered_lines
            if expected_rendered and not inline_markers:
                errors.append(
                    f"MISSING INLINE MARKERS in Scene {scene_id}: manifest expects "
                    f"{len(expected_rendered)} rendered dialogue turns but the prose "
                    f"contains no <!-- Lxxxx --> markers."
                )
            else:
                for i in range(len(inline_markers) - 1):
                    if inline_markers[i] >= inline_markers[i + 1]:
                        errors.append(
                            f"DIALOGUE ORDER VIOLATION in Scene {scene_id}: "
                            f"L{inline_markers[i]:04d} appears in prose before "
                            f"L{inline_markers[i + 1]:04d} (raw order is reversed or duplicated)."
                        )

                missing = set(expected_rendered) - set(inline_markers)
                extra = set(inline_markers) - set(expected_rendered)
                if missing:
                    errors.append(
                        f"INLINE MARKER GAP in Scene {scene_id}: rendered turns missing "
                        f"markers in prose: {sorted(missing)}"
                    )
                if extra:
                    errors.append(
                        f"INLINE MARKER EXCESS in Scene {scene_id}: prose markers not in "
                        f"manifest rendered set: {sorted(extra)}"
                    )

            # 6b. Semantic Grounding & Hallucinated Entity Check
            sem_errors, sem_warnings = verify_semantic_grounding(
                s_block["content"], raw_lines, m_start, m_end, scene_id, all_session_raw_text
            )
            errors.extend(sem_errors)
            warnings.extend(sem_warnings)

            # 6c. Compression ratio guardrail
            prose_words = len(s_block["content"].split())
            dialogue_words = calculate_dialogue_words(raw_lines, m_start, m_end)

            if dialogue_words > 0:
                ratio = prose_words / dialogue_words
                if ratio < 0.35:
                    warnings.append(f"COMPRESSION WARNING: Scene {scene_id} prose word count is {prose_words} vs {dialogue_words} raw dialogue words (ratio {ratio:.2f} < 0.35)")

    # 7. Whitelist header validation
    forbidden_headers = re.findall(r"^(###\s+.*)$", story_content, re.MULTILINE)
    if forbidden_headers:
        errors.append(f"HEADER FORMAT VIOLATION: Whitelist breach. Forbidden headers found: {forbidden_headers}")

    # Output report
    if errors:
        print(f"[FAIL] PARITY AUDIT FAILED for {session_id.upper()}:")
        for err in errors:
            print(f"  - {err}")
        if warnings:
            print("Warnings:")
            for warn in warnings:
                print(f"  - {warn}")
        return False, errors, warnings
    else:
        print(f"[PASS] PARITY AUDIT PASSED for {session_id.upper()}: 100% transcript coverage and semantic grounding confirmed.")
        if warnings:
            print("Warnings during pass:")
            for warn in warnings:
                print(f"  - {warn}")
        return True, errors, warnings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_parity.py <session_id> (e.g. s1)")
        sys.exit(1)
    passed, _, _ = verify_parity(sys.argv[1])
    sys.exit(0 if passed else 1)
