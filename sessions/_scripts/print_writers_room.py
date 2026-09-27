#!/usr/bin/env python3
"""Print Writers' Room Dynamic Brief (DEC-025).

Assembles a unified, read-only pre-flight brief for the dialectical subagent
writers' room without creating a redundant fifth JSON file. Pulls live state
directly from:
  1. sessions/config/sN-session-config.json
  2. sessions/data/index/sN-source-decisions.json (or sessions/config/)
  3. sessions/config/sN-intent-contract.json
  4. campaign/CAMPAIGN_ARC_LEDGER.md

Enforces the Negative-Only mandate for Arc Steward and the 'Declared, First,
Grounded' contract for Reader Advocate.
"""

import os
import sys
import json
import argparse

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def load_json_safe(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"_error": str(e)}
    return None


def print_writers_room(session_id, base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    session_id = session_id.lower()
    sid_upper = session_id.upper()

    # 1. Load Session Config
    cfg_path = os.path.join(base_dir, "sessions", "config", f"{session_id}-session-config.json")
    session_cfg = load_json_safe(cfg_path) or {}

    # 2. Load Source Decisions
    sd_path_idx = os.path.join(base_dir, "sessions", "data", "index", f"{session_id}-source-decisions.json")
    sd_path_cfg = os.path.join(base_dir, "sessions", "config", f"{session_id}-source-decisions.json")
    sd_data = load_json_safe(sd_path_idx) or load_json_safe(sd_path_cfg) or {}

    # 3. Load Intent Contract
    ic_path = os.path.join(base_dir, "sessions", "config", f"{session_id}-intent-contract.json")
    ic_data = load_json_safe(ic_path) or {}

    # 4. Load Campaign Arc Ledger
    ledger_path = os.path.join(base_dir, "campaign", "CAMPAIGN_ARC_LEDGER.md")
    arc_ledger_exists = os.path.exists(ledger_path)

    print("=" * 72)
    print(f"🖋️  DIALECTICAL WRITERS' ROOM BRIEF: {sid_upper}")
    print("=" * 72)

    # -------------------------------------------------------------------------
    # Role 1: Grounding Auditor (Tabletop Grounding Prosecutor)
    # -------------------------------------------------------------------------
    print("\n[ROLE 1: GROUNDING AUDITOR] Tabletop Grounding & Evidence Ledger")
    cutoff = session_cfg.get("session_cutoff", {})
    if cutoff:
        print(f"  • Hard Boundary Cutoff: Line L{cutoff.get('line', 0)} (GM call: L{cutoff.get('gm_call_line', 0)})")
        print(f"    Reason: {cutoff.get('reason', 'N/A')}")
    else:
        print("  • Hard Boundary Cutoff: None specified in session-config.")

    decisions = sd_data.get("decisions", [])
    print(f"  • High-Risk Forensic Turns Audited: {len(decisions)}")
    risk_counts = {}
    for d in decisions:
        r = d.get("risk", "unclassified")
        risk_counts[r] = risk_counts.get(r, 0) + 1

    for r, count in sorted(risk_counts.items()):
        print(f"    - {r}: {count} turns")

    hypotheses = [d for d in decisions if d.get("risk") == "player_hypothesis"]
    if hypotheses:
        print("  • Guarded Player Hypotheses (Must NOT be staged as confirmed truth):")
        for h in hypotheses[:5]:
            print(f"    * L{h.get('source_line')}: {h.get('contributor')} - '{h.get('function')}' ({h.get('reason')[:60]}...)")
        if len(hypotheses) > 5:
            print(f"    * ... and {len(hypotheses) - 5} more.")

    # -------------------------------------------------------------------------
    # Role 2: Arc Steward (Campaign Arc & Macro-Lore Steward - Negative-Only)
    # -------------------------------------------------------------------------
    print("\n[ROLE 2: ARC STEWARD] Macro-Lore & Cosmology (Negative-Only Mandate)")
    if arc_ledger_exists:
        print(f"  • Campaign Arc Ledger: Active ({ledger_path})")
        print("  • Negative-Only Constraints:")
        print("    * Fragments: Usually physical relics (S4 L0348, S5 L1055); unanchored events open inquiry (S5 L1052-1054).")
        print("    * Timeline Mechanics: Edits manifest via living ink and Fates; Reductors operate under veil.")
        print("    * Agency & Retcon Ban: Do NOT fabricate future acts or invent ungrounded curses/pacts.")
    else:
        print("  • WARNING: campaign/CAMPAIGN_ARC_LEDGER.md not found.")

    # -------------------------------------------------------------------------
    # Role 3: Reader Advocate (Reader Experience & Introduction Modeler)
    # -------------------------------------------------------------------------
    print("\n[ROLE 3: READER ADVOCATE] Context & Introduction Mechanics (Declared, First, Grounded)")
    lore_terms = session_cfg.get("session_lore_terms", [])
    npcs = session_cfg.get("npcs", [])

    print(f"  • Session Lore Terms Declared: {len(lore_terms)}")
    for t in lore_terms:
        if isinstance(t, dict):
            print(f"    * '{t.get('term')}' -> introduced in Scene {t.get('introduced_scene', 1)}")
        else:
            print(f"    * '{t}' -> introduced in Scene 1 (default)")

    print(f"  • NPCs Declared: {len(npcs)}")
    for n in npcs:
        if isinstance(n, dict):
            print(f"    * '{n.get('name')}' -> introduced in Scene {n.get('introduced_scene', 1)}")
        else:
            print(f"    * '{n}' -> introduced in Scene 1 (default)")

    # -------------------------------------------------------------------------
    # Role 4: Craft Dramatist (Craft & Deep-POV Dramatist)
    # -------------------------------------------------------------------------
    print("\n[ROLE 4: CRAFT DRAMATIST] Deep-POV, Voice Differentiation & Action Beats")
    contract_clauses = ic_data.get("liberties", ic_data.get("clauses", []))
    print(f"  • Intent Contract Liberties: {len(contract_clauses)} items")
    for cl in contract_clauses[:3]:
        desc = cl.get("description", cl.get("intent", str(cl)))
        print(f"    * {desc[:80]}")
    print("  • Craft Checklist:")
    print("    1. Dedicated paragraphs per speaker change; immutable quoted dialogue.")
    print("    2. Dwight Swain MRUs in action beats (Motivation -> Sensation -> Reflex -> Deliberate Action).")
    print("    3. Zero sensory filter frames ('saw', 'felt', 'wondered'); windowpane cadence.")

    # -------------------------------------------------------------------------
    # Python Arbiter Gates
    # -------------------------------------------------------------------------
    print("\n[EXTERNAL ARBITER] Automated Verification Gates")
    print("  • Gate 1: audit_arc_ledger.py (100% citation grounding in raw transcripts & GM prep)")
    print("  • Gate 2: audit_reader_context.py (Declared, First, and Grounded invariants)")
    print("  • Gate 3: verify_manifest.py (100% monotonic line coverage & sub-165 line block size)")
    print("  • Gate 4: verify_parity.py (100% dialogue attribution & ledger parity)")
    print("  • Gate 5: verify_intent_parity.py (Double-blind intent & agency guards)")
    print("  • Gate 6: critique_prose.py (Prose telemetry, zero Earth-leaks, talking heads scan)")
    print("=" * 72)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print Dialectical Writers' Room brief for session.")
    parser.add_argument("session_id", help="Session ID (e.g., s5)")
    args = parser.parse_args()
    print_writers_room(args.session_id)
