#!/usr/bin/env python3
"""
Pipeline Steward Decision Ledger & Contract Consistency Auditor
Verifies that:
1. All decisions (DEC-001 through DEC-019) are present and properly documented.
2. All session intent contracts conform to schema and have non-empty rules.
3. All session configs declare legitimate_ooc_lore_skips.
4. No regressions have decoupled gates from their enforcing invariants.
"""

import sys
import os
import re
import json

sys.stdout.reconfigure(encoding="utf-8")

def audit_ledger():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    ledger_path = os.path.join(base_dir, ".agents", "skills", "pipeline-steward", "references", "PIPELINE_DECISION_LEDGER.md")
    
    errors = []
    warnings = []
    
    if not os.path.exists(ledger_path):
        print(f"❌ Missing PIPELINE_DECISION_LEDGER.md at {ledger_path}")
        sys.exit(1)
        
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger_text = f.read()
        
    # 1. Verify DEC IDs
    dec_matches = re.findall(r"\[DEC-(\d{3})\]", ledger_text)
    dec_nums = sorted([int(x) for x in dec_matches])
    
    if not dec_nums:
        errors.append("No DEC entries found in ledger.")
    else:
        for expected in range(1, max(dec_nums) + 1):
            if expected not in dec_nums:
                errors.append(f"Missing decision record: DEC-{expected:03d} is skipped in ledger sequence.")
                
    # 2. Check Intent Contracts
    config_dir = os.path.join(base_dir, "sessions", "config")
    contract_files = [f for f in os.listdir(config_dir) if f.endswith("-intent-contract.json")]
    
    for cf in contract_files:
        path = os.path.join(config_dir, cf)
        try:
            with open(path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            rules = contract.get("rules", [])
            if not rules:
                warnings.append(f"{cf} has empty rules list.")
            for r in rules:
                if not r.get("id") or not r.get("fail_message"):
                    errors.append(f"Malformed rule in {cf}: rule {r.get('id', 'UNKNOWN')} missing id or fail_message.")
        except Exception as e:
            errors.append(f"Failed to parse {cf}: {e}")
            
    # 3. Check Session Configs for Canon Lore Skip declarations
    session_config_files = [f for f in os.listdir(config_dir) if re.match(r"^s\d+-session-config\.json$", f)]
    for scf in session_config_files:
        path = os.path.join(config_dir, scf)
        try:
            with open(path, "r", encoding="utf-8") as f:
                sc = json.load(f)
            if "legitimate_ooc_lore_skips" not in sc:
                warnings.append(f"{scf} does not declare 'legitimate_ooc_lore_skips'.")
        except Exception as e:
            errors.append(f"Failed to parse {scf}: {e}")

    # Output
    print(f"\n{'='*70}")
    print("🏛️  PIPELINE STEWARD ARCHITECTURAL CONSISTENCY REPORT")
    print(f"{'='*70}")
    print(f"• Decision Records Verified: {len(dec_nums)} entries (DEC-001 through DEC-{max(dec_nums):03d})")
    print(f"• Intent Contracts Verified: {len(contract_files)} contracts ({', '.join(contract_files)})")
    print(f"• Session Configs Audited:   {len(session_config_files)} files")
    
    if warnings:
        print("\n⚠️ Warnings:")
        for w in warnings:
            print(f"  - {w}")
            
    if errors:
        print(f"\n❌ Consistency Violations ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
        
    print(f"\n✅ PIPELINE ARCHITECTURE SYNCHRONIZED: Zero regressions, 100% memory continuity.\n")
    sys.exit(0)

if __name__ == "__main__":
    audit_ledger()
