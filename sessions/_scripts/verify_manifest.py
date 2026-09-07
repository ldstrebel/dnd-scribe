import sys
import os
import json
import hashlib

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

    # Output report
    if errors:
        print("[FAIL] MANIFEST VALIDATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("[PASS] MANIFEST VALIDATION PASSED: Hash matches, blocks tile exactly, line limits respected.")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_manifest.py <session_id> (e.g. s12)")
        sys.exit(1)
    verify_manifest(sys.argv[1])
