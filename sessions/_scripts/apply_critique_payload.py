#!/usr/bin/env python3
"""
Critique Payload Ingestion Engine for D&D Scribe
Applies block-level anchor revisions from mobile & web reader critique feedback
to clean story markdown files, verifies parity, and updates Schema 2.0 manifests.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 stdout on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data: dict, p: Path):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def apply_critiques(payload_path: Path):
    payload = load_json(payload_path)
    session_id = payload.get("sessionId", "s1").lower().replace("session", "").replace("-", "")
    if not session_id.startswith("s"):
        session_id = f"s{session_id}"
        
    annotations = payload.get("annotations", [])
    print(f"📥 Ingesting {len(annotations)} critique annotation(s) for {session_id.upper()}...")
    
    story_path = Path(f"sessions/data/clean/{session_id}-clean-story.md")
    manifest_v2_path = Path(f"sessions/data/index/{session_id}-manifest-v2.json")
    
    if not story_path.exists():
        raise FileNotFoundError(f"Story file not found: {story_path}")
    if not manifest_v2_path.exists():
        raise FileNotFoundError(f"Web manifest not found: {manifest_v2_path}")
        
    story_text = story_path.read_text(encoding="utf-8")
    manifest_v2 = load_json(manifest_v2_path)
    blocks = {b["id"]: b for b in manifest_v2.get("blocks", [])}
    
    applied_count = 0
    for ann in annotations:
        block_id = ann.get("blockId")
        action = ann.get("action", "replace")
        orig_text = ann.get("originalText")
        rev_text = ann.get("revisedText")
        note = ann.get("critiqueNote", "")
        
        if action != "replace" or not rev_text:
            print(f"  ℹ️  Skipping non-replace annotation on {block_id}: {note}")
            continue
            
        target_block = blocks.get(block_id)
        if not target_block:
            print(f"  ⚠️  Block ID {block_id} not found in manifest.")
            continue
            
        block_text = target_block.get("text", "")
        if orig_text and orig_text in story_text:
            story_text = story_text.replace(orig_text, rev_text)
            applied_count += 1
            print(f"  ✅ Applied rewrite to {block_id}: '{orig_text[:30]}...' -> '{rev_text[:30]}...'")
        elif block_text in story_text:
            story_text = story_text.replace(block_text, rev_text)
            applied_count += 1
            print(f"  ✅ Applied full block rewrite to {block_id}")
        else:
            print(f"  ❌ Failed to match text for block {block_id}")
            
    if applied_count > 0:
        story_path.write_text(story_text, encoding="utf-8")
        print(f"\n💾 Saved updated story to {story_path}")
        
        print("🔄 Regenerating manifests and running verification gates...")
        subprocess.run([sys.executable, "sessions/_scripts/generate_web_manifest.py"], check=True)
        subprocess.run([sys.executable, "sessions/_scripts/verify_manifest.py", session_id], check=True)
        subprocess.run([sys.executable, "sessions/_scripts/verify_parity.py", session_id], check=True)
        print("🎉 Verification passed successfully!")
    else:
        print("No changes applied.")

def main():
    parser = argparse.ArgumentParser(description="Ingest Critique Payload")
    parser.add_argument("--payload", type=Path, required=True, help="Path to critique JSON payload")
    args = parser.parse_args()
    apply_critiques(args.payload)

if __name__ == "__main__":
    main()
