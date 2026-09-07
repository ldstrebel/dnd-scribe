"""Vumbua Editorial Harness CLI.

Provides unified command-line access to all editorial linters,
style analytics, lore auditing, and session inspection.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict, Any

from .config import get_repo_root, get_sessions_dir
from .leak_detector import LeakDetector
from .echo_detector import EchoDetector
from .style_analyzer import StyleAnalyzer
from .lore_guardian import LoreGuardian
from .macro_auditor import MacroAuditor


def run_full_lint(filepath: str, verbose: bool = False) -> Dict[str, Any]:
    """Runs all editorial engines including macro narrative audit on a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        return {"passed": False, "errors": [f"File not found: {filepath}"]}

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    leak_det = LeakDetector()
    echo_det = EchoDetector()
    style_an = StyleAnalyzer()
    lore_grd = LoreGuardian()
    macro_aud = MacroAuditor()

    leak_res = leak_det.scan_text(content, filename=path.name)
    echo_res = echo_det.scan_text(content, filename=path.name)
    style_res = style_an.generate_style_report(content, filename=path.name)
    lore_res = lore_grd.scan_text(content, filename=path.name)
    macro_res = macro_aud.audit_scene(content, scene_title=path.stem)

    all_errors = leak_res["violations"] + lore_res["errors"]
    all_warnings = echo_res["warnings"] + style_res["warnings"] + lore_res["warnings"]

    # Add any ungrounded macro flags to warnings
    for flag in macro_res.get("ungrounded_flags", []):
        all_warnings.append({
            "type": "UNGROUNDED_LORE",
            "severity": "WARN",
            "line": 1,
            "message": flag
        })

    passed = len(all_errors) == 0

    return {
        "filename": path.name,
        "filepath": str(path),
        "passed": passed,
        "error_count": len(all_errors),
        "warning_count": len(all_warnings),
        "errors": all_errors,
        "warnings": all_warnings,
        "leak_report": leak_res,
        "echo_report": echo_res,
        "style_report": style_res,
        "lore_report": lore_res,
        "macro_report": macro_res
    }


def print_report_card(report: Dict[str, Any], verbose: bool = False):
    """Prints a structured ASCII report card."""
    fn = report["filename"]
    passed = report["passed"]
    status_str = "[PASS] PASSED" if passed else "[FAIL] FAILED"

    print("=" * 70)
    print(f"  PUBLISHING ENGINE EDITORIAL AUDIT REPORT: {fn}")
    print(f"  STATUS: {status_str}")
    print(f"  ERRORS: {report['error_count']} | WARNINGS: {report['warning_count']}")
    print("=" * 70)

    # 1. Pacing & Style Summary
    style = report.get("style_report", {})
    pacing = style.get("pacing", {})
    ratio = style.get("dialogue_ratio", {})
    sensory = style.get("sensory_palette", {})

    if pacing.get("sentence_count", 0) > 0:
        print("\n[STORY METRICS & PACING]")
        print(f"  * Word Count: {ratio.get('total_words', 0):,} words")
        print(f"  * Sentence Count: {pacing.get('sentence_count', 0)}")
        print(f"  * Mean Sentence Length: {pacing.get('mean_length', 0)} words (StdDev: {pacing.get('std_dev', 0)})")
        print(f"  * Dialogue vs Narrative: {ratio.get('dialogue_pct', 0)}% Dialogue / {ratio.get('narrative_pct', 0)}% Narrative")
        print(f"  * Sensory Registers Covered: {sensory.get('covered_registers', 0)}/5 registers ({sensory.get('total_hits', 0)} hits)")

    # Character Empathy & Anchoring (Macro Narrative Layer)
    macro = report.get("macro_report", {})
    anchors = macro.get("character_anchors", [])
    if anchors:
        print("\n[CHARACTER EMPATHY & COLD-READER ANCHORS]")
        for a in anchors:
            status_tag = "[ANCHORED]" if a["anchored"] else "[NEEDS ANCHOR]"
            kw_preview = f" (tokens: {', '.join(a['keywords_found'][:4])})" if a["keywords_found"] else ""
            print(f"  * {a['character']}: {status_tag} - {a['empathy_core']}{kw_preview}")

    # 2. Hard Errors (Must be fixed)
    if report["errors"]:
        print("\n[HARD ERRORS - BUILD BLOCKERS]")
        for idx, err in enumerate(report["errors"], 1):
            line_str = f"Line {err.get('line', '?')}"
            err_type = err.get("type", "ERROR")
            msg = err.get("message", "")
            print(f"  {idx}. [{err_type}] {line_str}: {msg}")
            if "snippet" in err:
                print(f"     Snippet: \"{err['snippet'].strip()}\"")

    # 3. Stylistic Warnings
    if report["warnings"]:
        print(f"\n[STYLISTIC WARNINGS & EDITORIAL SUGGESTIONS ({len(report['warnings'])})]")
        display_warnings = report["warnings"] if verbose else report["warnings"][:8]
        for idx, warn in enumerate(display_warnings, 1):
            line_str = f"Line {warn.get('line', '?')}"
            w_type = warn.get("type", "WARN")
            msg = warn.get("message", "")
            print(f"  {idx}. [{w_type}] {line_str}: {msg}")

        if not verbose and len(report["warnings"]) > 8:
            print(f"  ... and {len(report['warnings']) - 8} more warnings. (Run with --verbose to view all)")

    print("=" * 70)


def cmd_lint(args):
    report = run_full_lint(args.file, verbose=args.verbose)
    print_report_card(report, verbose=args.verbose)
    if not report["passed"]:
        sys.exit(1)


def cmd_audit(args):
    sessions_dir = get_sessions_dir()
    story_path = sessions_dir / "data" / "clean" / f"{args.session_id}-clean-story.md"

    if not story_path.exists():
        print(f"Error: Story file not found at {story_path}", file=sys.stderr)
        sys.exit(1)

    report = run_full_lint(str(story_path), verbose=args.verbose)
    print_report_card(report, verbose=args.verbose)
    if not report["passed"]:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Vumbua Editorial Harness CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Lint subcommand
    p_lint = subparsers.add_parser("lint", help="Lint an individual markdown story or block file")
    p_lint.add_argument("file", help="Path to markdown file")
    p_lint.add_argument("--verbose", "-v", action="store_true", help="Show all warnings")
    p_lint.set_defaults(func=cmd_lint)

    # Audit subcommand
    p_audit = subparsers.add_parser("audit", help="Audit a compiled session story (e.g. s12)")
    p_audit.add_argument("session_id", help="Session ID (e.g. s12)")
    p_audit.add_argument("--verbose", "-v", action="store_true", help="Show all warnings")
    p_audit.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
