"""Assemble sN-clean-story.md from per-scene block files.

Reads the manifest for scene order and OOC flags, pulls non-OOC blocks from
sessions/data/clean/blocks/sN-scene-XX.md, emits OOC scenes as bare
RAW_RANGE marker lines, merges per-scene assumption logs into
sessions/data/index/sN-assumptions.json, and writes the canonical
story file. Fails loudly if a required block file is missing or its
RAW_RANGE header disagrees with the manifest.

Usage: python assemble_story.py s12 --title "SESSION TITLE"
"""

import argparse
import json
import os
import re
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("session_id")
    ap.add_argument("--title", default=None, help="Top-level # title for the story")
    ap.add_argument("--no-lint", action="store_true", help="Skip editorial harness linter pass")
    ap.add_argument("--no-parity", action="store_true", help="Skip transcript parity verification pass")
    ap.add_argument("--manifest", default=None, help="Override manifest path (pipeline isolation)")
    ap.add_argument("--blocks-dir", default=None, help="Override blocks directory (pipeline isolation)")
    ap.add_argument("--out", default=None, help="Override story output path")
    ap.add_argument("--assumptions-out", default=None, help="Override assumptions output path")
    args = ap.parse_args()
    sid = args.session_id

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = args.manifest or os.path.join(base, "data", "index", f"{sid}-manifest.json")
    blocks_dir = args.blocks_dir or os.path.join(base, "data", "clean", "blocks")
    out_path = args.out or os.path.join(base, "data", "clean", f"{sid}-clean-story.md")
    assumptions_out = args.assumptions_out or os.path.join(base, "data", "index", f"{sid}-assumptions.json")

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    errors = []
    parts = []
    assumptions = []

    root_dir = os.path.dirname(base)
    book_cfg_path = os.path.join(root_dir, "novel", "book_config.json")
    book_cfg = {}
    if os.path.exists(book_cfg_path):
        try:
            with open(book_cfg_path, "r", encoding="utf-8") as bf:
                book_cfg = json.load(bf)
        except Exception:
            pass

    author_name = book_cfg.get("author", "The Table")
    campaign_name = book_cfg.get("campaign", "Tabletop Campaign")
    genre_name = ", ".join(book_cfg.get("subjects", ["Fantasy", "Tabletop RPG"]))

    if args.title:
        parts.append(
            "---\n"
            f'title: "{args.title}"\n'
            f'author: "{author_name}"\n'
            f'campaign: "{campaign_name}"\n'
            f'genre: "{genre_name}"\n'
            "---\n\n"
            f"# {args.title.upper()}\n"
        )

    for block in manifest["scene_blocks"]:
        scene_id = block["scene_id"]
        start, end = block["line_range"]
        if block.get("ooc", False):
            parts.append(f"<!-- RAW_RANGE: [{start}, {end}] | SCENE_ID: {scene_id} | OOC -->\n")
            continue

        block_path = os.path.join(blocks_dir, f"{sid}-scene-{scene_id:02d}.md")
        if not os.path.exists(block_path):
            errors.append(f"MISSING BLOCK FILE: {block_path}")
            continue
        with open(block_path, encoding="utf-8") as f:
            content = f.read().strip()

        m = re.match(
            r"<!--\s*RAW_RANGE:\s*\[(\d+),\s*(\d+)\]\s*\|\s*SCENE_ID:\s*(\d+)\s*-->",
            content,
        )
        if not m:
            errors.append(f"BLOCK {scene_id}: missing/malformed RAW_RANGE header")
        elif (int(m.group(1)), int(m.group(2)), int(m.group(3))) != (start, end, scene_id):
            errors.append(
                f"BLOCK {scene_id}: header [{m.group(1)}, {m.group(2)}] scene {m.group(3)} "
                f"disagrees with manifest [{start}, {end}] scene {scene_id}"
            )
        if "LEDGER:" not in content:
            errors.append(f"BLOCK {scene_id}: missing LEDGER footer")
        parts.append(content + "\n")

        a_path = os.path.join(blocks_dir, f"{sid}-scene-{scene_id:02d}-assumptions.json")
        if os.path.exists(a_path):
            try:
                with open(a_path, encoding="utf-8") as f:
                    entries = json.load(f)
                if isinstance(entries, list):
                    assumptions.extend(entries)
                else:
                    errors.append(f"ASSUMPTIONS {scene_id}: not a JSON array")
            except json.JSONDecodeError as e:
                errors.append(f"ASSUMPTIONS {scene_id}: invalid JSON ({e})")

    if errors:
        print("[FAIL] ASSEMBLY ABORTED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    try:
        tmp_out = out_path + ".tmp"
        with open(tmp_out, "w", encoding="utf-8") as f:
            f.write("\n".join(parts))
        os.replace(tmp_out, out_path)
    except Exception:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(parts))

    # surface the assembled story in novel/sessions/ for easy access
    import shutil
    novel_dir = os.path.join(os.path.dirname(base), "novel", "sessions")
    os.makedirs(novel_dir, exist_ok=True)
    shutil.copyfile(out_path, os.path.join(novel_dir, f"{sid}-story.md"))

    for i, a in enumerate(assumptions, 1):
        a["id"] = f"A-{i:03d}"
    tmp_assumptions = assumptions_out + ".tmp"
    with open(tmp_assumptions, "w", encoding="utf-8") as f:
        json.dump(assumptions, f, indent=2)
    os.replace(tmp_assumptions, assumptions_out)

    print(f"[OK] Wrote {out_path} ({len(manifest['scene_blocks'])} scenes) [atomic]")
    print(f"[OK] Wrote {assumptions_out} ({len(assumptions)} assumptions) [atomic]")

    # 1. Parity Audit Gate
    if not args.no_parity:
        try:
            from verify_parity import verify_parity
            passed, p_errs, p_warns = verify_parity(
                sid, manifest_path=manifest_path, story_path=out_path,
                blocks_dir=blocks_dir)
            if not passed:
                print(f"[FAIL] Parity check failed with {len(p_errs)} errors.")
        except ImportError:
            try:
                from sessions.scripts.verify_parity import verify_parity
                passed, p_errs, p_warns = verify_parity(
                    sid, manifest_path=manifest_path, story_path=out_path,
                    blocks_dir=blocks_dir)
                if not passed:
                    print(f"[FAIL] Parity check failed with {len(p_errs)} errors.")
            except Exception as e:
                print(f"[WARN] Could not run parity verification: {e}")

    # 2. Editorial Linter Gate
    if not args.no_lint:
        try:
            from harness.cli import run_full_lint, print_report_card
            report = run_full_lint(out_path)
            print_report_card(report, verbose=False)
        except ImportError:
            try:
                from sessions.scripts.harness.cli import run_full_lint, print_report_card
                report = run_full_lint(out_path)
                print_report_card(report, verbose=False)
            except Exception as e:
                print(f"[WARN] Could not run editorial linter: {e}")


if __name__ == "__main__":
    main()
