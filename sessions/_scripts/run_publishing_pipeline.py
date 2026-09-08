#!/usr/bin/env python3
"""
Unified End-to-End Publishing Pipeline Runner
Executes the full D&D Scribe publishing cycle:
1. Fact-Checker Gate: audit_semantic_grounding.py & verify_parity.py
2. Developmental Editor Gate: critique_prose.py
3. Schema 2.0 Web Manifest: generate_web_manifest.py & verify_manifest.py
4. Dual EPUB Compiler: novel/generate_epub.py
"""

import sys
import os
import subprocess
import argparse

sys.stdout.reconfigure(encoding="utf-8")

def run_step(title, cmd):
    print(f"\n{'='*70}")
    print(f"▶️  STEP: {title}")
    print(f"{'='*70}")
    res = subprocess.run(cmd, text=True, capture_output=True, encoding="utf-8", errors="ignore")
    if res.stdout:
        print(res.stdout.strip())
    if res.returncode != 0:
        if res.stderr:
            print(f"❌ Error: {res.stderr.strip()}", file=sys.stderr)
        print(f"🛑 PIPELINE HALTED AT: {title}", file=sys.stderr)
        sys.exit(res.returncode)
    print(f"✅ {title} PASSED.")

def main():
    parser = argparse.ArgumentParser(description="Unified Publishing Pipeline Runner")
    parser.add_argument("sessions", nargs="*", default=["s1", "s2", "s3"], help="Session IDs to build (default: s1 s2 s3)")
    args = parser.parse_args()

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(root_dir)

    print("🚀 STARTING D&D SCRIBE PUBLISHING PIPELINE")
    print(f"Target Sessions: {', '.join(args.sessions).upper()}")

    # 1. Fact-Checking & Semantic Grounding Gates
    for s in args.sessions:
        run_step(f"Fact-Checker Semantic Entailment ({s.upper()})", [sys.executable, "sessions/_scripts/audit_semantic_grounding.py", s])
        run_step(f"Fact-Checker Parity & Ledger Integrity ({s.upper()})", [sys.executable, "sessions/_scripts/verify_parity.py", s])

    # 2. Developmental Editor Review Gate
    run_step("Developmental Editor & Prose Critic", [sys.executable, ".agents/skills/novel-critic/scripts/critique_prose.py"])

    # 3. Web Manifest Generation & Validation
    run_step("Schema 2.0 Web Manifest Builder", [sys.executable, "sessions/_scripts/generate_web_manifest.py"])
    for s in args.sessions:
        run_step(f"Web Manifest Validation ({s.upper()})", [sys.executable, "sessions/_scripts/verify_manifest.py", s])

    # 4. EPUB Compilation
    run_step("Dual Edition EPUB Assembler", [sys.executable, "novel/generate_epub.py"])

    print(f"\n{'='*70}")
    print("🏆 ALL PUBLISHING GATES PASSED: 100% CANONICAL & PRODUCTION READY")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
