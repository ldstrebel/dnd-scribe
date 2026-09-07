#!/usr/bin/env python3
"""Upstream Audit Tool: Proper Nouns & Earth Elements Scanner.

Scans upstream raw indexed transcripts (sessions/data/index/s*-raw-indexed.md)
and clean transcripts (sessions/data/clean/s*-clean.md) to identify and flag:
1. Earth Nationalities, Languages, and Cultural Demonyms (English, Hawaiian, French, Greek, etc.)
2. Earth Institutions, Geography, and Places (Oxford, Cambridge, Hollywood, etc.)
3. Real-World Commercial Brands, Tech, and Pop Culture (Costco, Sharpie, Bluetooth, Wi-Fi, NFL, Ted Lasso, etc.)
4. Earth-Specific Historical / Cultural Titles (Sultan, Butler, Samurai, Viking, etc.)

For each occurrence:
- Preserves the exact raw line number (L####) and raw text.
- Checks whether the term leaked downstream into sN-clean-story.md or was adapted.
- Suggests in-world fantasy / arcanatech replacements.
- Exports structured data to sessions/data/index/sN-earth-elements.json and enriches sN-assumptions.json.
- Generates a human-readable master audit report: _ops/review/earth-elements-audit.md.

Usage:
    python sessions/_scripts/audit_earth_elements.py s1
    python sessions/_scripts/audit_earth_elements.py --all
    python sessions/_scripts/audit_earth_elements.py --all --sync-assumptions
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
INDEX_DIR = ROOT / "sessions" / "data" / "index"
CLEAN_DIR = ROOT / "sessions" / "data" / "clean"
REPORT_PATH = ROOT / "_ops" / "review" / "earth-elements-audit.md"

EARTH_PATTERNS = [
    (
        r"\b(english butler|english|british|american|french|italian|german|russian|asian|european|african|latin|roman|greek|spartan|trojan|australian|scottish|irish|japanese|chinese|hawaiian)\b",
        "Earth Nationality / Culture / Demonym",
        "Replace with in-world cultural demonyms (Harmony, Octoumba, Ash-Blood, Mizizi, Renali) or descriptive archetypes (e.g. 'courtly', 'insular islander', 'palace attendant')."
    ),
    (
        r"\b(oxfordian|oxford steam|oxford student|oxford|cambridge|harvard|yale|eiffel|big ben|hollywood|disney|broadway)\b",
        "Earth Place / Institution",
        "Replace with in-world scholarly institutions or styles (e.g. 'high-scholastic', 'imperial academy', 'grand amphitheater')."
    ),
    (
        r"\b(costco gatekeepers?|costco|sharpie|bluetooth|wifi|wi-fi|internet|cell phone|smartphone|nfl|super bowl|ted lasso|titanic|blackstone|black stone)\b",
        "Real-World Brand / Modern Tech / Pop Culture",
        "Paraphrase into arcanatech or logistical reality (e.g. 'strict manifest checkpoint with grease pencils', 'colossal dreadnought', 'frequency resonance', 'searing slab')."
    ),
    (
        r"\b(butler|sultan|caesar|tsar|samurai|ninja|cowboy|viking)\b",
        "Earth Historical Role / Out-of-Universe Title",
        "Adapt to in-world caste or profession (e.g. 'courtly majordomo', 'palace steward', 'sovereign warlord', 'drifter hunter', 'frontier scout')."
    ),
]

# Canonical in-universe exceptions that are allowed
CANONICAL_EXCEPTIONS = {
    "radio",  # Canonical arcanatech vacuum-tube / crystal radio in Vumbua
}


def scan_session_raw(session_id: str):
    """Scan a session's raw-indexed transcript and clean transcript for Earth terms."""
    raw_path = INDEX_DIR / f"{session_id}-raw-indexed.md"
    clean_path = CLEAN_DIR / f"{session_id}-clean.md"
    story_path = CLEAN_DIR / f"{session_id}-clean-story.md"

    if not raw_path.exists() and not clean_path.exists():
        return []

    raw_text = raw_path.read_text(encoding="utf-8") if raw_path.exists() else ""
    clean_text = clean_path.read_text(encoding="utf-8") if clean_path.exists() else ""
    story_text = story_path.read_text(encoding="utf-8") if story_path.exists() else ""

    findings = []
    seen_keys = set()
    line_pattern = re.compile(r"^(L\d+):\s*(?:\*\*(.*?)\*\*:?\s*)?(.*)$")

    # Pass 1: scan raw-indexed file
    for line in raw_text.splitlines():
        line = line.strip()
        m = line_pattern.match(line)
        if not m:
            continue

        raw_id, speaker, content = m.group(1), m.group(2) or "Unknown", m.group(3)
        raw_num = int(raw_id[1:])

        for pattern, category, guidance in EARTH_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                term = match.group(0)
                if term.lower() in CANONICAL_EXCEPTIONS:
                    continue

                key = (session_id, raw_num, term.lower())
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                # Check if this term leaked into downstream story text
                escaped_term = re.escape(term)
                leaked_matches = re.findall(rf"\b{escaped_term}\b", story_text, re.IGNORECASE)
                downstream_leaked = len(leaked_matches) > 0

                findings.append({
                    "session_id": session_id,
                    "source": "raw-indexed",
                    "raw_id": raw_id,
                    "raw_line": raw_num,
                    "speaker": speaker,
                    "term": term,
                    "category": category,
                    "guidance": guidance,
                    "raw_text": content,
                    "downstream_leaked": downstream_leaked,
                    "leak_count": len(leaked_matches) if downstream_leaked else 0
                })

    # Pass 2: scan sN-clean.md for any uncaptured stage notes or dialogue
    clean_line_num = 0
    for line in clean_text.splitlines():
        clean_line_num += 1
        line = line.strip()
        if not line:
            continue

        for pattern, category, guidance in EARTH_PATTERNS:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                term = match.group(0)
                if term.lower() in CANONICAL_EXCEPTIONS:
                    continue

                key = (session_id, f"clean-{clean_line_num}", term.lower())
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                escaped_term = re.escape(term)
                leaked_matches = re.findall(rf"\b{escaped_term}\b", story_text, re.IGNORECASE)
                downstream_leaked = len(leaked_matches) > 0

                findings.append({
                    "session_id": session_id,
                    "source": "clean-transcript",
                    "raw_id": f"clean:L{clean_line_num}",
                    "raw_line": clean_line_num,
                    "speaker": "Clean Transcript",
                    "term": term,
                    "category": category,
                    "guidance": guidance,
                    "raw_text": line,
                    "downstream_leaked": downstream_leaked,
                    "leak_count": len(leaked_matches) if downstream_leaked else 0
                })

    return findings


def sync_with_assumptions(session_id: str, findings: list):
    """Sync flagged Earth elements into sN-assumptions.json as structured review entries."""
    assumptions_path = INDEX_DIR / f"{session_id}-assumptions.json"
    if not assumptions_path.exists():
        return

    is_dict = False
    full_dict = {}
    try:
        raw_data = json.loads(assumptions_path.read_text(encoding="utf-8"))
        if isinstance(raw_data, dict):
            is_dict = True
            full_dict = raw_data
            assumptions = full_dict.get("assumptions", [])
        else:
            assumptions = raw_data
    except Exception:
        assumptions = []

    # Map existing assumption raw lines and terms
    existing_lines = set()
    for a in assumptions:
        if isinstance(a, dict):
            for rline in a.get("raw_lines", []):
                existing_lines.add(rline)

    added_count = 0
    # Group findings by raw line (only integer raw lines from raw-indexed)
    grouped = {}
    for f in findings:
        rline = f["raw_line"]
        if not isinstance(rline, int):
            continue
        if rline not in grouped:
            grouped[rline] = []
        grouped[rline].append(f)

    max_id = 0
    for a in assumptions:
        if isinstance(a, dict):
            aid = a.get("id", "")
            m = re.search(r"(\d+)", aid)
            if m:
                max_id = max(max_id, int(m.group(1)))

    for rline, flist in grouped.items():
        if rline in existing_lines:
            continue

        max_id += 1
        terms = list(set(f["term"] for f in flist))
        cats = list(set(f["category"] for f in flist))
        first = flist[0]

        entry = {
            "id": f"A-{max_id:03d}",
            "stage": "novelization",
            "scene_id": 1,
            "raw_lines": [rline],
            "type": "earth_realia",
            "assumption": (
                f"Speaker used Earth element/proper noun: {', '.join(terms)} ({', '.join(cats)}). "
                f"Guidance: {first['guidance']} "
                f"{'FLAG: Leaked into novel prose; needs in-world replacement.' if first['downstream_leaked'] else 'Omitted or adapted in-world.'}"
            ),
            "confidence": "low" if first["downstream_leaked"] else "medium",
            "raw_text": first["raw_text"],
            "review": {
                "status": "pending",
                "correction": ""
            }
        }
        assumptions.append(entry)
        added_count += 1

    if added_count > 0:
        if is_dict:
            full_dict["assumptions"] = assumptions
            out_data = full_dict
        else:
            out_data = assumptions
        assumptions_path.write_text(json.dumps(out_data, indent=2) + "\n", encoding="utf-8")
        print(f"[{session_id}] Added {added_count} earth-realia items to {assumptions_path.name}")


def generate_master_report(all_findings: list):
    """Generate markdown master audit report."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    leaks = [f for f in all_findings if f["downstream_leaked"]]
    adapted = [f for f in all_findings if not f["downstream_leaked"]]

    lines = [
        "# 🌍 Master Upstream Audit: Proper Nouns & Earth Elements",
        "",
        f"**Total Flagged Instances in Upstream Transcripts:** {len(all_findings)}  ",
        f"**Downstream Leaks in Novel Prose:** {len(leaks)}  ",
        f"**Adapted / Omitted Cleanly:** {len(adapted)}  ",
        "",
        "> [!IMPORTANT]",
        "> When DMs or players use Earth metaphors, pop-culture similes, or real-world demonyms at the table (e.g. 'English butler', 'Costco gatekeepers'), ",
        "> this audit preserves the raw audio transcript in the index while flagging items so authors can easily identify and translate them into in-world fantasy arcanatech.",
        "",
        "---",
        "",
        "## 🚨 Active Downstream Leaks (Requiring In-World Adaptation)",
        "",
    ]

    if not leaks:
        lines.append("*No active leaks detected in novel prose! All Earth elements cleanly adapted.*")
    else:
        lines.append("| Session | Raw Ref | Speaker | Flagged Term | Category | Novel Occurrences | In-World Replacement Guidance |")
        lines.append("|---|---|---|---|---|---|---|")
        for f in leaks:
            lines.append(
                f"| `{f['session_id']}` | `{f['raw_id']}` | **{f['speaker']}** | `{f['term']}` | {f['category']} | {f['leak_count']} | {f['guidance']} |"
            )

    lines += [
        "",
        "---",
        "",
        "## 📜 All Flagged Upstream Raw Elements by Session",
        ""
    ]

    sessions = sorted(list(set(f["session_id"] for f in all_findings)))
    for s in sessions:
        s_findings = [f for f in all_findings if f["session_id"] == s]
        lines.append(f"### {s.upper()} ({len(s_findings)} flagged items)")
        lines.append("| Source | Raw ID | Speaker | Flagged Term | Category | Downstream Status | Raw Transcript Line |")
        lines.append("|---|---|---|---|---|---|---|")
        for f in s_findings:
            status = "🔴 **LEAKED IN PROSE**" if f["downstream_leaked"] else "🟢 Adapted / Omitted"
            snippet = f["raw_text"][:85] + ("..." if len(f["raw_text"]) > 85 else "")
            snippet = snippet.replace("|", "\\|")
            lines.append(
                f"| {f['source']} | `{f['raw_id']}` | {f['speaker']} | `{f['term']}` | {f['category']} | {status} | {snippet} |"
            )
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Wrote Master Earth Elements Audit Report to {REPORT_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Audit proper nouns and Earth elements in transcripts.")
    parser.add_argument("session", nargs="?", default="s1", help="Session ID (e.g. s1, s2) or --all")
    parser.add_argument("--all", action="store_true", help="Scan all sessions")
    parser.add_argument("--sync-assumptions", action="store_true", help="Sync flagged items into sN-assumptions.json")
    args = parser.parse_args()

    if args.all:
        raw_files = sorted(INDEX_DIR.glob("*-raw-indexed.md"))
        sessions = [f.name.split("-")[0] for f in raw_files]
    else:
        sessions = [args.session]

    all_findings = []
    for s in sessions:
        findings = scan_session_raw(s)
        all_findings.extend(findings)

        # Write per-session JSON
        out_json = INDEX_DIR / f"{s}-earth-elements.json"
        out_json.write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")

        if args.sync_assumptions:
            sync_with_assumptions(s, findings)

    generate_master_report(all_findings)
    print(f"[DONE] Processed {len(sessions)} sessions, found {len(all_findings)} items.")


if __name__ == "__main__":
    main()
