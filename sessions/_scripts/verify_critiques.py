"""verify_critiques.py

Deterministic Gate: Human Reader Critique Blocker (DEC-031).

Ensures that any human editorial review feedback (e.g. from eBook or Web Reader PRs)
ingested into `sN-source-decisions.json` as `status: open` blocks the publishing pipeline
until every critique item is explicitly resolved and documented.
"""

import sys
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

def audit_critiques(session_id: str) -> dict:
    config_path = REPO_ROOT / "sessions" / "config" / f"{session_id}-source-decisions.json"
    if not config_path.exists():
        return {"session_id": session_id, "exists": False, "passed": True, "open_count": 0, "critiques": []}

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {
            "session_id": session_id,
            "exists": True,
            "passed": False,
            "error": f"JSON parse error in {config_path.name}: {e}",
            "open_count": 1,
            "critiques": []
        }

    critiques = data.get("critiques", [])
    open_items = [c for c in critiques if c.get("status", "open") == "open"]
    resolved_items = [c for c in critiques if c.get("status") == "resolved"]

    return {
        "session_id": session_id,
        "exists": True,
        "passed": len(open_items) == 0,
        "total_count": len(critiques),
        "open_count": len(open_items),
        "resolved_count": len(resolved_items),
        "open_items": open_items,
        "resolved_items": resolved_items
    }

def print_critique_report(report: dict):
    s_id = report["session_id"].upper()
    print("=" * 70)
    print(f"  HUMAN CRITIQUE RESOLUTION AUDIT: {s_id}")
    status_str = "[PASS] ALL CRITIQUES RESOLVED" if report["passed"] else "[FAIL] OPEN CRITIQUES BLOCKING"
    print(f"  STATUS: {status_str}")
    print("=" * 70)

    if not report["exists"]:
        print(f"  * No source-decisions config found for {s_id} (0 critiques logged). [PASS]")
        return

    if report.get("error"):
        print(f"  * [ERROR] {report['error']}")
        return

    print(f"  * Total Logged Critiques: {report['total_count']}")
    print(f"  * Resolved Critiques:     {report['resolved_count']}")
    print(f"  * Open Blocking Items:    {report['open_count']}")

    if report["open_items"]:
        print(f"\n  [!] THE FOLLOWING {report['open_count']} HUMAN CRITIQUE ITEMS ARE CURRENTLY OPEN:")
        for item in report["open_items"]:
            c_id = item.get("id", "unknown")
            pr = item.get("pr_number", "N/A")
            block = item.get("block_id", "N/A")
            src_line = f"L{item['source_line']:04d}" if item.get("source_line") else "N/A"
            spk = item.get("speaker", "Unknown")
            comment = item.get("comment", "")
            print(f"    • [{c_id}] (PR #{pr} | {block} | {src_line} | {spk}):")
            print(f"      \"{comment}\"")
        print("\n  [ACTION REQUIRED] Address the feedback in Track A / Track B prose, update resolution_notes,")
        print("  and set 'status': 'resolved' in sN-source-decisions.json before publishing.")

def main():
    parser = argparse.ArgumentParser(description="Audit human editorial critique resolution status.")
    parser.add_argument("session", nargs="?", default="s5", help="Session ID (e.g. s5)")
    args = parser.parse_args()

    report = audit_critiques(args.session)
    print_critique_report(report)
    sys.exit(0 if report["passed"] else 1)

if __name__ == "__main__":
    main()
