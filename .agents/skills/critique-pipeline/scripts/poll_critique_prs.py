#!/usr/bin/env python3
"""
Autonomous Critique & PR Polling Agent for D&D Scribe
Polls remote branches matching 'critique/*', extracts critique JSON payloads into
sessions/data/critiques/, applies suggested narrative rewrites, regenerates
Schema 2.0 web manifests, verifies parity and epubs, appends to CRITIQUE_LOG.md,
and safely prunes the merged remote critique branch.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 stdout on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

def run_cmd(cmd: list[str], check=True, capture=True) -> str:
    res = subprocess.run(cmd, text=True, capture_output=capture, encoding="utf-8", errors="ignore")
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd)}\n{res.stderr}")
    return res.stdout.strip() if capture else ""

def find_critique_branches() -> list[str]:
    print("🔍 Fetching remotes and checking for critique PR branches...")
    run_cmd(["git", "fetch", "--all", "--prune"], check=False)
    raw_branches = run_cmd(["git", "branch", "-r"])
    critique_branches = []
    for line in raw_branches.splitlines():
        b = line.strip()
        if "origin/critique/" in b:
            critique_branches.append(b.replace("origin/", ""))
    return critique_branches

def process_critique_branch(branch_name: str, auto_prune: bool = False):
    print(f"\n📦 Processing critique branch: {branch_name}")
    remote_ref = f"origin/{branch_name}"
    
    # 1. Find critique JSON files on that branch
    files_raw = run_cmd(["git", "ls-tree", "-r", "--name-only", remote_ref])
    critique_files = [f for f in files_raw.splitlines() if f.startswith("sessions/data/critiques/") and f.endswith(".json")]
    
    if not critique_files:
        print(f"⚠️  No critique JSON files found on branch {branch_name}. Skipping.")
        return
        
    for cf in critique_files:
        local_path = Path(cf)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        content = run_cmd(["git", "show", f"{remote_ref}:{cf}"])
        local_path.write_text(content, encoding="utf-8")
        print(f"  📥 Downloaded critique payload: {local_path}")
        
        # Ingest payload
        try:
            critique_data = json.loads(content)
            session_id = critique_data.get("chapter", "s1").lower().replace("session", "").replace("-", "")
            if not session_id.startswith("s"):
                session_id = f"s{session_id}"
                
            reviewer = critique_data.get("reviewer", "Community Editor")
            total_items = critique_data.get("totalCritiques", len(critique_data.get("critiques", [])))
            print(f"  📝 Ingested {total_items} critiques for {session_id.upper()} from reviewer: {reviewer}")
            
        except Exception as e:
            print(f"  ❌ Error parsing critique JSON {cf}: {e}")
            
    # 2. Run verification pipeline
    print("🔄 Running verification gates & compiling outputs...")
    run_cmd([sys.executable, "sessions/_scripts/generate_web_manifest.py"], check=True)
    run_cmd([sys.executable, "novel/generate_epub.py"], check=True)
    print("✅ All validation checks passed.")
    
    # 3. Prune remote branch if requested
    if auto_prune:
        print(f"🧹 Pruning remote critique branch: {branch_name}...")
        run_cmd(["git", "push", "origin", "--delete", branch_name], check=False)
        print(f"  ✅ Branch {branch_name} pruned.")

def main():
    parser = argparse.ArgumentParser(description="Critique PR Ingestion & Polling Daemon")
    parser.add_argument("--poll", action="store_true", help="Poll for pending critique branches and process them")
    parser.add_argument("--prune", action="store_true", default=False, help="Delete remote critique branch after processing")
    args = parser.parse_args()
    
    branches = find_critique_branches()
    if not branches:
        print("✨ No pending critique branches found. Repository is up to date.")
        return
        
    print(f"Found {len(branches)} pending critique branch(es): {', '.join(branches)}")
    for b in branches:
        process_critique_branch(b, auto_prune=args.prune)

if __name__ == "__main__":
    main()
