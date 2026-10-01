#!/usr/bin/env python3
"""Audit Campaign Arc Ledger for Provenance Compliance (DEC-025, DEC-028).

Enforces that every statement of cosmology, faction dynamics, character
traits, and session milestones in CAMPAIGN_ARC_LEDGER.md carries an explicit,
verifiable citation tag:
  - [ESTABLISHED: S# L####]
  - [GM-PREP: path/to/doc]
  - [OPEN: S# L####]

Validates Markdown table rows in Section 4 (Session Milestone Registry):
  - Ensures milestones and key factions have valid citations.
  - Verifies cited lines fall within in-world session bounds (DEC-028).
  - Checks completeness across active campaign sessions.
  - Scopes celestial and major faction cross-references.
"""

import os
import re
import sys
import json
import argparse

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

# Canonical campaign factions & celestial entities that MUST be tracked in Section 2
CANONICAL_MACRO_ENTITIES = [
    "fates",
    "three fates",
    "reductor",
    "reductors",
    "margin warden",
    "margin wardens",
    "hermes",
    "persephone",
]


def load_manifest_safe(base_dir, session_id):
    """Load session manifest if available."""
    path = os.path.join(base_dir, "sessions", "data", "index", f"{session_id.lower()}-manifest.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def audit_arc_ledger(base_dir=None, target_session=None):
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

    # 2. Section Bullet & Table Provenance Check
    in_substantive_section = False
    current_section = "Header"
    claims_audited = 0
    valid_citations = 0
    has_milestone_section = False
    found_milestone_sessions = set()

    # Cache loaded manifests
    manifest_cache = {}

    def get_manifest(sid):
        sid = sid.lower()
        if sid not in manifest_cache:
            manifest_cache[sid] = load_manifest_safe(base_dir, sid)
        return manifest_cache[sid]

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith("## "):
            current_section = stripped[3:].strip()
            in_substantive_section = any(
                token in current_section for token in [
                    "Cosmology", "Factions", "Character", "Milestone", "Threads", "Questions"
                ]
            )
            if "Milestone" in current_section:
                has_milestone_section = True
            continue

        if not in_substantive_section:
            continue

        # Check A: Markdown Table rows in Section 4 (Milestone Registry)
        if "Milestone" in current_section and stripped.startswith("|"):
            # Match session table rows: | **S1** | ...
            m_row = re.match(r"^\|\s*\*\*([sS]\d+)\*\*\s*\|(.+)$", stripped)
            if m_row:
                sid_raw = m_row.group(1).lower()
                found_milestone_sessions.add(sid_raw)
                cells = [c.strip() for c in stripped.split("|")[1:-1]]

                # Ensure minimum expected columns: Session, Setting, Relic, Milestone, Key Factions
                if len(cells) >= 5:
                    milestone_text = cells[3]
                    factions_text = cells[4]

                    for col_label, cell_text in [
                        ("Milestone & Tactical Resolution", milestone_text),
                        ("Key Factions Present", factions_text),
                    ]:
                        # Skip if explicitly marked 'None' without narrative claims
                        if cell_text.lower() in ["none", "n/a", "-"]:
                            continue

                        claims_audited += 1
                        tags = PROVENANCE_TAG_RE.findall(cell_text)
                        if not tags:
                            errors.append(
                                f"Line {i} in '{current_section}': [UNSOURCED_MILESTONE_CLAIM] Session {sid_raw.upper()} "
                                f"{col_label} lacks provenance tag: '{cell_text[:60]}...'."
                            )
                        else:
                            valid_citations += len(tags)
                            # Line Range & In-World Bounds Validation (Milestone 1A)
                            for tag_type, tag_body in tags:
                                if tag_type == "ESTABLISHED":
                                    for m_line in re.finditer(r"(S\d+)\s+L(\d+)(?:-L(\d+))?", tag_body):
                                        ref_sid = m_line.group(1).lower()
                                        start_l = int(m_line.group(2))
                                        end_l = int(m_line.group(3)) if m_line.group(3) else start_l

                                        manifest = get_manifest(ref_sid)
                                        if manifest:
                                            total_lines = manifest.get("total_raw_lines", 0)
                                            if start_l > total_lines or end_l > total_lines:
                                                errors.append(
                                                    f"Line {i}: [MILESTONE_CITES_PHANTOM_LINE] Session {ref_sid.upper()} citation "
                                                    f"L{start_l:04d}-L{end_l:04d} exceeds total raw lines ({total_lines})."
                                                )
                                            else:
                                                non_ooc = [b for b in manifest.get("scene_blocks", []) if not b.get("ooc", False)]
                                                if non_ooc:
                                                    in_min = min(b["line_range"][0] for b in non_ooc)
                                                    in_max = max(b["line_range"][1] for b in non_ooc)
                                                    if start_l < in_min or end_l > in_max:
                                                        errors.append(
                                                            f"Line {i}: [MILESTONE_OUT_OF_BOUNDS] Session {ref_sid.upper()} citation "
                                                            f"L{start_l:04d}-L{end_l:04d} falls outside in-world session bounds ([L{in_min:04d}, L{in_max:04d}])."
                                                        )
            continue

        # Check B: Look for bullet claims
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

    # 3. Session Milestone Coverage Check (Milestone 1A)
    # Assert completeness across all sessions that have manifests in sessions/data/index/
    if has_milestone_section:
        manifest_dir = os.path.join(base_dir, "sessions", "data", "index")
        if os.path.exists(manifest_dir):
            discovered_sessions = []
            for fname in os.listdir(manifest_dir):
                m_fname = re.match(r"^(s\d+)-manifest\.json$", fname.lower())
                if m_fname:
                    discovered_sessions.append(m_fname.group(1))
            for exp_s in sorted(discovered_sessions):
                if exp_s not in found_milestone_sessions:
                    errors.append(f"[MISSING_SESSION_MILESTONE] Section 4 lacks milestone entry for {exp_s.upper()}.")

    # 4. Scoped Canonical Entity Cross-Reference Check (Milestone 1C)
    # Extracts Section 2 text to confirm canonical macro-factions/celestials are tracked
    section_2_text = ""
    in_sec_2 = False
    for line in lines:
        if line.strip().startswith("## "):
            sec_name = line.strip()[3:].strip()
            in_sec_2 = "Factions" in sec_name or "Celestial" in sec_name
            continue
        if in_sec_2:
            section_2_text += line.lower() + "\n"

    sessions_to_check = [target_session.lower()] if target_session else sorted(list(found_milestone_sessions))
    for s_id in sessions_to_check:
        cfg_path = os.path.join(base_dir, "sessions", "config", f"{s_id}-session-config.json")
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    s_cfg = json.load(f)
                
                # Check NPCs and lore terms against CANONICAL_MACRO_ENTITIES
                for npc in s_cfg.get("npcs", []):
                    name = (npc.get("name") if isinstance(npc, dict) else str(npc)).lower()
                    for macro_token in CANONICAL_MACRO_ENTITIES:
                        if macro_token in name and macro_token not in section_2_text:
                            errors.append(
                                f"[CANONICAL_ENTITY_NOT_IN_LEDGER] Session {s_id.upper()} introduces canonical entity "
                                f"'{name}', but '{macro_token}' is missing from Section 2 of CAMPAIGN_ARC_LEDGER.md."
                            )

                for lore in s_cfg.get("session_lore_terms", []):
                    term = (lore.get("term") if isinstance(lore, dict) else str(lore)).lower()
                    for macro_token in CANONICAL_MACRO_ENTITIES:
                        if macro_token in term and macro_token not in section_2_text:
                            errors.append(
                                f"[CANONICAL_ENTITY_NOT_IN_LEDGER] Session {s_id.upper()} declares lore term "
                                f"'{term}', but '{macro_token}' is missing from Section 2 of CAMPAIGN_ARC_LEDGER.md."
                            )
            except Exception:
                pass

    print("======================================================================")
    print("📜 CAMPAIGN ARC LEDGER AUDIT REPORT (DEC-025, DEC-028)")
    print("======================================================================")
    print(f"• Claims Audited:     {claims_audited}")
    print(f"• Valid Citations:    {valid_citations}")
    print(f"• Milestones Audited: {len(found_milestone_sessions)} sessions")
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
    parser = argparse.ArgumentParser(description="Audit Campaign Arc Ledger (DEC-025, DEC-028).")
    parser.add_argument("session", nargs="?", default=None, help="Optional session ID (e.g. s2)")
    parser.add_argument("--session", dest="opt_session", default=None, help="Optional session ID flag")
    args = parser.parse_args()

    target = args.opt_session or args.session
    passed, errs, warns = audit_arc_ledger(target_session=target)
    sys.exit(0 if passed else 1)
