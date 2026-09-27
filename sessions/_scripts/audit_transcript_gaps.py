#!/usr/bin/env python3
"""Audit transcript dialogue turns against novelization prose to detect omitted interjections,
turn order discrepancies, and dropped character beats.

Usage: python3 audit_transcript_gaps.py [session_id]
"""
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

ROOT = Path(__file__).resolve().parent.parent.parent

def main() -> None:
    session = sys.argv[1] if len(sys.argv) > 1 else "s12"
    raw_path = ROOT / "sessions" / "data" / "index" / f"{session}-raw-indexed.md"
    manifest_path = ROOT / "sessions" / "data" / "index" / f"{session}-manifest.json"
    
    if not raw_path.exists() or not manifest_path.exists():
        print(f"[ERROR] Missing raw index or manifest for {session}")
        sys.exit(1)
        
    raw_lines = {}
    for line in raw_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^L(\d+):\s*(.*)", line)
        if m:
            l_num = int(m.group(1))
            raw_lines[l_num] = m.group(2)
            
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    
    # Load session config for declared players/GM
    cfg_path = ROOT / "sessions" / "config" / f"{session}-session-config.json"
    declared_speakers = set()
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            if "game_master" in cfg and "person" in cfg["game_master"]:
                declared_speakers.add(cfg["game_master"]["person"])
            if "players" in cfg:
                for person, pc_name in cfg["players"].items():
                    declared_speakers.add(person)
                    declared_speakers.add(pc_name)
        except Exception:
            pass

    print(f"==================================================")
    print(f"[AUDIT] DIALOGUE TURN GAP & PHONETIC AUDIT: {session.upper()}")
    print(f"==================================================")
    
    # 1. Phonetic Clarification & Name Correction Harvester
    phonetic_patterns = [
        r"(?:my name is|call me|named|name's)\s+([A-Za-z]+)\s+with an?\s+([A-Za-z])",
        r"\b([A-Z](?:-[A-Z]){2,})\b",
        r"(?:spelled|spelling is)\s+([A-Za-z\-]+)",
        r"(?:not\s+([A-Za-z]+),\s+(?:it's|is)\s+([A-Za-z]+))",
        r"(?:with my accent[,\s]+they don't hear)",
    ]
    phonetic_findings = []
    for l_num, text in raw_lines.items():
        for p in phonetic_patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                phonetic_findings.append((l_num, text.strip(), m.group(0)))
                break

    if phonetic_findings:
        print("\n🔍 [PHONETIC DECLARATIONS & NAME CLARIFICATIONS DETECTED]")
        for l_num, full_t, match_s in phonetic_findings:
            print(f"  * L{l_num:04d}: '{match_s}' -> {full_t[:80]}...")
        print("  💡 Verify that character dossiers and manifest aliases reflect the speaker's true intent.\n")

    # 2. Dropped In-Character Turns
    total_gaps = 0
    for scene in manifest.get("scene_blocks", []):
        scene_id = scene["scene_id"]
        ledger = scene.get("dialogue_ledger", [])
        if not ledger or scene.get("ooc", False):
            continue
            
        rendered_nums = sorted([item["line"] if isinstance(item, dict) else item for item in ledger])
        if not rendered_nums:
            continue
            
        min_l, max_l = min(rendered_nums), max(rendered_nums)
        
        skipped_player_turns = []
        for l_num in range(min_l, max_l + 1):
            if l_num not in rendered_nums and l_num in raw_lines:
                txt = raw_lines[l_num]
                # Flag lines spoken by declared players/PCs containing dialogue
                is_speaker = False
                if declared_speakers:
                    is_speaker = any(f"**{spk}**" in txt or f"**{spk}:**" in txt for spk in declared_speakers)
                else:
                    is_speaker = bool(re.match(r"^\*\*([^*]+):\*\*", txt))

                if is_speaker:
                    # Ignore pure dice/roll table chatter
                    if not any(m in txt.lower() for m in ["roll", "initiative", "saving throw", "d20", "d4", "d6", "character sheet"]):
                        skipped_player_turns.append((l_num, txt))
                    
        if skipped_player_turns:
            print(f"[SCENE {scene_id}: {scene['title']}] Potential Omitted Turns:")
            for l_num, txt in skipped_player_turns[:3]:
                print(f"  - L{l_num:04d}: {txt[:90]}")
            total_gaps += len(skipped_player_turns)
                
    if total_gaps == 0:
        print("[PASS] ZERO OMITTED PLAYER DIALOGUE TURNS DETECTED!")
    else:
        print(f"\n[INFO] {total_gaps} candidate player dialogue turns skipped between rendered bounds.")

if __name__ == "__main__":
    main()
