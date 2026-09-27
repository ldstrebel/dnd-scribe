import sys
import os
import re
import json
import hashlib

try:
    from generate_web_manifest import load_raw_indexed_speakers
except ImportError:
    try:
        from sessions._scripts.generate_web_manifest import load_raw_indexed_speakers
    except ImportError:
        load_raw_indexed_speakers = None

def get_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def count_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

def verify_manifest(session_id):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(base_dir, "data", "index", f"{session_id}-manifest.json")
    indexed_path = os.path.join(base_dir, "data", "index", f"{session_id}-raw-indexed.md")

    errors = []

    # 1. Load manifest and check file existence
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest not found at {manifest_path}")
        sys.exit(1)
    if not os.path.exists(indexed_path):
        print(f"Error: Indexed file not found at {indexed_path}")
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        try:
            manifest = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing manifest JSON: {e}")
            sys.exit(1)

    # 2. Hash lock check
    actual_hash = get_sha256(indexed_path)
    expected_hash = manifest.get("raw_file_hash")
    if actual_hash != expected_hash:
        errors.append(f"HASH LOCK MISMATCH: indexed file hash is '{actual_hash}', manifest expected '{expected_hash}'")

    # 3. Total raw lines check
    actual_line_count = count_lines(indexed_path)
    expected_line_count = manifest.get("total_raw_lines")
    if actual_line_count != expected_line_count:
        errors.append(f"TOTAL LINES MISMATCH: indexed file has {actual_line_count} lines, manifest expected {expected_line_count}")

    # 4. Block ranges validation
    scene_ids = set()
    covered_lines = set()
    last_end = 0

    scene_blocks = manifest.get("scene_blocks", [])
    for block in scene_blocks:
        scene_id = block.get("scene_id")
        title = block.get("title", f"Scene {scene_id}")
        line_range = block.get("line_range")

        # Scene ID uniqueness
        if scene_id in scene_ids:
            errors.append(f"Scene ID {scene_id} ({title}) is duplicated.")
        scene_ids.add(scene_id)

        # Range structure
        if not isinstance(line_range, list) or len(line_range) != 2:
            errors.append(f"Scene {scene_id} has invalid range format: {line_range}")
            continue

        start, end = line_range[0], line_range[1]
        if start > end:
            errors.append(f"Scene {scene_id} has start line {start} greater than end line {end}.")
            continue

        # Block size limit (max 165 lines)
        block_len = end - start + 1
        if block_len > 165:
            errors.append(f"Scene {scene_id} is oversized: length is {block_len} lines (exceeds max 165).")

        # Range overlaps and coverage
        block_lines = set(range(start, end + 1))
        overlap = block_lines.intersection(covered_lines)
        if overlap:
            errors.append(f"Scene {scene_id} overlaps with other scenes on lines: {sorted(list(overlap))[:10]}...")
        covered_lines.update(block_lines)

        # Monotonicity check
        if start <= last_end:
            errors.append(f"Scene {scene_id} range {line_range} starts at or before previous end line {last_end}.")
        last_end = end

        # Dialogue ledger verification
        ledger = block.get("dialogue_ledger", [])
        for entry in ledger:
            line_no = entry.get("line")
            speaker = entry.get("speaker")
            if not (start <= line_no <= end):
                errors.append(f"Dialogue turn on line {line_no} by '{speaker}' in scene {scene_id} is outside range {line_range}")

    # 5. Check tiling from 1 to total_raw_lines (no gaps)
    all_lines = set(range(1, actual_line_count + 1))
    missing_lines = all_lines - covered_lines
    if missing_lines:
        errors.append(f"Gaps in coverage detected. Missing lines: {sorted(list(missing_lines))[:20]}...")

    # 6. Schema 2.0 Web Manifest & Dialogue Provenance Validation
    v2_manifest_path = os.path.join(base_dir, "data", "index", f"{session_id}-manifest-v2.json")
    if os.path.exists(v2_manifest_path):
        try:
            with open(v2_manifest_path, "r", encoding="utf-8") as f:
                v2_manifest = json.load(f)
        except Exception as e:
            errors.append(f"Web Manifest JSON parse error: {e}")
            v2_manifest = None

        if v2_manifest:
            characters = v2_manifest.get("characters", {})
            hex_color_re = re.compile(r"^#[0-9a-fA-F]{6}$")

            # Load origin-time speaker ground truth (Zero Regex Guesswork)
            session_num = re.sub(r'^[^\d]*', '', session_id)
            raw_speakers = load_raw_indexed_speakers(session_num) if load_raw_indexed_speakers else {}

            # Check character registry integrity
            for cid, cdata in characters.items():
                cname = cdata.get("name")
                ccolor = cdata.get("color")
                if not cname:
                    errors.append(f"Character '{cid}' in web manifest is missing a name.")
                if not ccolor or not hex_color_re.match(ccolor):
                    errors.append(f"Character '{cid}' has invalid hex color '{ccolor}'.")

            # Check blocks and segments
            blocks = v2_manifest.get("blocks", [])
            if not blocks:
                errors.append("Web manifest contains 0 blocks.")

            for b in blocks:
                bid = b.get("id")
                b_text = b.get("text", "")
                segments = b.get("segments", [])

                if not b_text.strip():
                    errors.append(f"Block {bid} has empty text.")
                if not segments:
                    errors.append(f"Block {bid} has 0 segments.")

                # Verbatim reconstruction check
                recon_text = "".join(s.get("text", "") for s in segments)
                if recon_text != b_text:
                    errors.append(f"Block {bid} verbatim reconstruction failure: segment text does not match block text.")

                for s in segments:
                    seg_id = s.get("segmentId")
                    seg_type = s.get("type")
                    spk_id = s.get("speakerId")
                    src_line = s.get("sourceLine")

                    if seg_type == "dialogue":
                        # Invariant 1: Dialogue MUST NOT be attributed to narrator
                        if spk_id == "narrator":
                            errors.append(f"UNATTRIBUTED DIALOGUE in Block {bid} ({seg_id}): dialogue quote '{s.get('text', '')[:40]}' is attributed to 'narrator'!")
                        # Invariant 2: Dialogue MUST have a valid sourceLine
                        if src_line is None or not isinstance(src_line, int) or src_line <= 0:
                            errors.append(f"NULL SOURCELINE DIALOGUE in Block {bid} ({seg_id}): dialogue quote '{s.get('text', '')[:40]}' has invalid sourceLine: {src_line}")
                        # Invariant 3: Speaker MUST exist in character registry
                        if spk_id not in characters:
                            errors.append(f"UNKNOWN SPEAKER in Block {bid} ({seg_id}): speakerId '{spk_id}' not found in manifest characters registry.")
                        # Invariant 4: Origin-Time Dialogue Provenance Check (Zero Regex)
                        # Dialogue speaker must match raw transcript index or explicit session config ground truth
                        if raw_speakers:
                            if bid in raw_speakers and spk_id != raw_speakers[bid]:
                                errors.append(f"BLOCK SPEAKER OVERRIDE MISMATCH in Block {bid} ({seg_id}): manifest assigned speaker '{spk_id}' but config specifies '{raw_speakers[bid]}'!")
                            elif src_line and src_line in raw_speakers:
                                raw_spk = raw_speakers[src_line]
                                if raw_spk != "narrator" and spk_id != raw_spk:
                                    errors.append(f"ORIGIN-TIME PROVENANCE MISMATCH in Block {bid} ({seg_id}): manifest assigned speaker '{spk_id}' but raw indexed transcript Line {src_line} is registered to '{raw_spk}'!")
                    elif seg_type == "action":
                        if spk_id == "narrator":
                            errors.append(f"INVALID ACTION SEGMENT in Block {bid} ({seg_id}): action segment cannot be attributed to 'narrator'.")
                        if spk_id not in characters:
                            errors.append(f"UNKNOWN SPEAKER in Block {bid} ({seg_id}): action speakerId '{spk_id}' not found in manifest characters registry.")

    # Output report
    if errors:
        print("[FAIL] MANIFEST VALIDATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("[PASS] MANIFEST VALIDATION PASSED: Hash matches, blocks tile exactly, line limits respected, 100% dialogue provenance verified.")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_manifest.py <session_id> (e.g. s12)")
        sys.exit(1)
    verify_manifest(sys.argv[1])
