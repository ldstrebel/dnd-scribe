#!/usr/bin/env python3
"""Audit Campaign Arc Ledger for Provenance Compliance (DEC-025).

Enforces that every statement of cosmology, faction dynamics, character
traits, and session milestones in CAMPAIGN_ARC_LEDGER.md carries an explicit,
verifiable citation tag:
  - [ESTABLISHED: S# L####]
  - [GM-PREP: path/to/doc]
  - [OPEN: S# L####]

Fails loudly if any claim is unsourced or if speculative future plot
leaks into ground-truth sections.
"""

import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PROVENANCE_TAG_RE = re.compile(
    r"\[(ESTABLISHED|GM-PREP|OPEN):\s*([^\]]+)\]"
)

BANNED_SPECULATIVE_TOKENS = [
    r"\bAct\s+(?:III|IV|V|3|4|5)\b",
    r"\bsecret Gorgon curse\b",
    r"\bnecrotic threshold pact\b",
    r"\bdivine truth-sight\b",
    r"\bSiege of the Margin\b",
    r"\bFate Loom infiltration\b",
]


def audit_arc_ledger(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    ledger_path = os.path.join(base_dir, "campaign", "CAMPAIGN_ARC_LEDGER.md")
    if not os.path.exists(ledger_path):
        return False, [f"Missing arc ledger at: {ledger_path}"], []

    with open(ledger_path, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []
    warnings = []
    lines = content.splitlines()

    # 1. Banned Speculative Plot / Lore Drift Check
    for i, line in enumerate(lines, 1):
        for pattern in BANNED_SPECULATIVE_TOKENS:
            m = re.search(pattern, line, re.IGNORECASE)
            if m:
                errors.append(
                    f"Line {i}: [UNAUTHORIZED_SPECULATION] Found ungrounded term or fabricated future plot "
                    f"'{m.group(0)}' in arc ledger! Future arcs must not be planted (DEC-010, DEC-025)."
                )

    # 2. Section Bullet Provenance Check
    in_substantive_section = False
    current_section = "Header"
    claims_audited = 0
    valid_citations = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith("## "):
            current_section = stripped[3:].strip()
            in_substantive_section = any(
                token in current_section for token in [
                    "Cosmology", "Factions", "Character", "Milestone", "Threads", "Questions"
                ]
            )
            continue

        if not in_substantive_section:
            continue

        # Look for bullet claims
        if re.match(r"^(\*|-|\d+\.)\s+", stripped):
            # Ignore parent category headers that end with a colon (sub-bullets carry the citations)
            if stripped.endswith(":") or stripped.endswith(":**"):
                continue

            # Ignore sub-bullets that are just bold headers with no assertions (e.g. "* **1. Alfie...**")
            if re.match(r"^(\*|-|\d+\.)\s+\*\*\d+\.\s+[^:]+\*\*$", stripped):
                continue

            claims_audited += 1
            tags = PROVENANCE_TAG_RE.findall(stripped)
            if not tags:
                errors.append(
                    f"Line {i} in '{current_section}': [UNSOURCED_ARC_CLAIM] Bullet lacks provenance tag: "
                    f"'{stripped[:70]}...'. Must cite [ESTABLISHED: S# L####], [GM-PREP: path], or [OPEN: S# L####]."
                )
            else:
                valid_citations += len(tags)

    print("======================================================================")
    print("📜 CAMPAIGN ARC LEDGER AUDIT REPORT (DEC-025)")
    print("======================================================================")
    print(f"• Claims Audited:     {claims_audited}")
    print(f"• Valid Citations:    {valid_citations}")
    print(f"• Status:             {'[PASS] PASSED' if not errors else '[FAIL] FAILED'}")

    if errors:
        print(f"\n[FAIL] {len(errors)} PROVENANCE BREACHES DETECTED:")
        for e in errors:
            print(f"  ❌ {e}")
        return False, errors, warnings
    else:
        print(f"\n[PASS] 100% Provenance Grounding Confirmed across all {claims_audited} campaign claims.")
        return True, [], warnings


if __name__ == "__main__":
    passed, errs, warns = audit_arc_ledger()
    sys.exit(0 if passed else 1)
