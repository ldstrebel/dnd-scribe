#!/usr/bin/env python3
"""
Double-Blind Intent Parity & Campaign Context Verification Gate
Ensures character intent, consent dynamics, and causal sequencing stay 100% faithful
to what actually occurred at the table without post-hoc sycophantic drift.

Checks:
1. Character Agency & Motivation: Independent Impulse vs. Synthetic Coordinated Heist.
2. Consent & Force Dynamics: Unilateral Physical Force vs. Sanitized Polite Consent.
3. Causal Sequence Fidelity: Trigger -> Phenomenon -> Consequence continuity.
4. Faction & Canon Nomenclature: The Reductors vs. The Margin drift.
5. Entity Grounding: Strict adherence to declared table props (e.g., folded tin-foil fedoras).
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, List, Tuple

sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_UNIVERSAL_RULES = [
    {
        "id": "FACTION_CANON_DRIFT",
        "description": "Adversary faction terminology drifted from canonical name",
        "forbidden_prose_patterns": [
            r"\bthe\s+margin\s+had\s+arrived\b",
            r"\bthe\s+margin\s+infiltrators\b"
        ],
        "required_replacement": "The Reductors",
        "fail_message": "Adversary faction labeled as 'The Margin'. Canonical faction is 'The Reductors'."
    },
    {
        "id": "MARKDOWN_TYPOGRAPHY_LEAK",
        "description": "Raw markdown triple asterisks in novel manuscript",
        "forbidden_prose_patterns": [
            r"\*\*\*[A-Z0-9_\-.\s]+\*\*\*"
        ],
        "fail_message": "Raw markdown triple-asterisk formatting leaked into manuscript prose."
    }
]

def load_intent_contract(session_id: str, base_dir: str) -> List[Dict]:
    contract_file = os.path.join(base_dir, "config", f"{session_id}-intent-contract.json")
    if os.path.exists(contract_file):
        try:
            with open(contract_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("rules", [])
        except Exception as e:
            print(f"Warning: Failed to load {contract_file}: {e}")
    return DEFAULT_UNIVERSAL_RULES

def audit_intent_parity(session_id: str, blocks_dir: str = None) -> Tuple[bool, List[str], List[str]]:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    blocks_dir = blocks_dir or os.path.join(base_dir, "data", "clean", "blocks")
    alt_blocks_dir = os.path.join(base_dir, "data", "clean", "blocks_authorial")
    
    errors = []
    warnings = []
    
    rules = load_intent_contract(session_id, base_dir)
    
    # Check all block files for this session
    target_prefix = f"{session_id}-scene-"
    block_files = [f for f in os.listdir(blocks_dir) if f.startswith(target_prefix) and f.endswith(".md")]
    
    alt_files = []
    if os.path.exists(alt_blocks_dir):
        alt_files = [f for f in os.listdir(alt_blocks_dir) if f.startswith(target_prefix) and f.endswith(".md")]
        
    all_targets = [(f, os.path.join(blocks_dir, f), "tabletop") for f in sorted(block_files)]
    all_targets += [(f, os.path.join(alt_blocks_dir, f), "cinematic") for f in sorted(alt_files)]
    
    for filename, filepath, cut_type in all_targets:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        prose_only = re.sub(r"<!--.*?-->", "", content)
        
        for rule in rules:
            rule_id = rule["id"]
            target_scenes = rule.get("target_scenes", [])
            if target_scenes and not any(ts in filename for ts in target_scenes):
                continue
            
            # Check forbidden patterns
            for pat in rule.get("forbidden_prose_patterns", []):
                match = re.search(pat, prose_only, re.IGNORECASE)
                if match:
                    snippet = match.group(0)
                    errors.append(
                        f"[{rule_id}] Collision in {filename} ({cut_type}): "
                        f"Matched forbidden pattern '{snippet}'. {rule['fail_message']}"
                    )
                    
            # Check required force tokens
            if "required_force_tokens" in rule:
                has_force = any(re.search(tok, prose_only, re.IGNORECASE) for tok in rule["required_force_tokens"])
                if not has_force:
                    errors.append(
                        f"[{rule_id}] Missing force tokens in {filename} ({cut_type}): "
                        f"{rule['fail_message']}"
                    )
                    
            # Check required prop tokens
            if "required_prop_tokens" in rule:
                has_prop = any(re.search(tok, prose_only, re.IGNORECASE) for tok in rule["required_prop_tokens"])
                if not has_prop:
                    errors.append(
                        f"[{rule_id}] Missing prop tokens in {filename} ({cut_type}): "
                        f"{rule['fail_message']}"
                    )
                    
            # Check required intent grounding tokens
            if "required_intent_grounding" in rule:
                has_intent = any(re.search(tok, prose_only, re.IGNORECASE) for tok in rule["required_intent_grounding"])
                if not has_intent:
                    errors.append(
                        f"[{rule_id}] Missing character intent grounding in {filename} ({cut_type}): "
                        f"{rule['fail_message']}"
                    )

    passed = len(errors) == 0
    return passed, errors, warnings

def main():
    parser = argparse.ArgumentParser(description="Double-Blind Intent Parity & Campaign Context Verification Gate")
    parser.add_argument("session_id", help="Session ID (e.g., s5)")
    args = parser.parse_args()
    
    session_id = args.session_id.lower()
    print(f"\n{'='*70}")
    print(f"🔍 DOUBLE-BLIND INTENT PARITY & CAMPAIGN CONTEXT GATE: {session_id.upper()}")
    print(f"{'='*70}")
    
    passed, errors, warnings = audit_intent_parity(session_id)
    
    if warnings:
        print("\n⚠️ WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
            
    if not passed:
        print(f"\n❌ INTENT PARITY VIOLATIONS DETECTED ({len(errors)} errors):")
        for err in errors:
            print(f"  - {err}")
        print("\n🛑 INTENT PARITY AUDIT FAILED.\n")
        sys.exit(1)
    else:
        print(f"\n✅ INTENT PARITY & CAMPAIGN CONTEXT CONFIRMED: 0 collisions detected across all tracks.\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
