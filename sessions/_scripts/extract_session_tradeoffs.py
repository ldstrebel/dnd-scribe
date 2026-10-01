#!/usr/bin/env python3
"""
Targeted Trade-off & Creative Compromise Extractor
Extracts documented editorial compromises, authorial liberties, substantive skipped lines,
and high-risk decisions for an adversarial red-team audit.
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, List, Optional, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

def find_latest_session(base_dir: str) -> str:
    """Find the highest numbered session in sessions/config/."""
    cfg_dir = os.path.join(base_dir, "config")
    pattern = re.compile(r"^s(\d+)-session-config\.json$")
    highest = 1
    if os.path.exists(cfg_dir):
        for f in os.listdir(cfg_dir):
            m = pattern.match(f)
            if m:
                highest = max(highest, int(m.group(1)))
    return f"s{highest}"

def load_json(path: str) -> Optional[Dict[str, Any]]:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to parse {path}: {e}", file=sys.stderr)
    return None

def load_raw_lines(raw_path: str) -> Dict[int, str]:
    lines = {}
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                m = re.match(r"^L(\d+):\s*(.*)", line)
                if m:
                    lines[int(m.group(1))] = m.group(2)
    return lines

def extract_tradeoff_dossier(session_id: str, base_dir: str, prev_session_id: Optional[str] = None) -> Dict[str, Any]:
    session_id = session_id.lower()
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    cfg_path = os.path.join(base_dir, "config", f"{session_id}-session-config.json")
    intent_path = os.path.join(base_dir, "config", f"{session_id}-intent-contract.json")
    sd_path = os.path.join(base_dir, "data", "index", f"{session_id}-source-decisions.json")
    manifest_path = os.path.join(base_dir, "data", "index", f"{session_id}-manifest.json")
    if not os.path.exists(manifest_path):
        manifest_path = os.path.join(base_dir, "data", "index", f"{session_id}-manifest-v2.json")
    raw_path = os.path.join(base_dir, "data", "index", f"{session_id}-raw-indexed.md")
    blocks_authorial_dir = os.path.join(base_dir, "data", "clean", "blocks_authorial")
    blocks_tabletop_dir = os.path.join(base_dir, "data", "clean", "blocks")
    arc_ledger_path = os.path.join(root_dir, "campaign", "CAMPAIGN_ARC_LEDGER.md")

    cfg = load_json(cfg_path) or {}
    intent = load_json(intent_path) or {}
    sd = load_json(sd_path) or {}
    manifest = load_json(manifest_path) or {}
    raw_map = load_raw_lines(raw_path)

    # 1. Authorial Liberties
    raw_liberties = intent.get("authorial_liberties", intent.get("liberties", []))
    liberties_extracted = []
    for lib in raw_liberties:
        scene = lib.get("scene", "general").lower()
        scope = lib.get("scope", "")
        desc = lib.get("liberty", "")
        impact = lib.get("impact", "")
        boundary = lib.get("boundary", "")

        # Find matching Track B block if available
        cin_block_content = ""
        scene_match = re.search(r"scene-(\d+)", scene)
        if scene_match:
            sc_num = scene_match.group(1).zfill(2)
            c_file = os.path.join(blocks_authorial_dir, f"{session_id}-scene-{sc_num}.md")
            if os.path.exists(c_file):
                with open(c_file, "r", encoding="utf-8") as f:
                    cin_block_content = f.read()

        liberties_extracted.append({
            "scene": scene,
            "scope": scope,
            "liberty": desc,
            "impact": impact,
            "boundary": boundary,
            "sample_cinematic_prose": cin_block_content[:1000] if cin_block_content else "N/A"
        })

    # 2. Substantive Skip Exemptions
    raw_skips = cfg.get("legitimate_ooc_lore_skips", [])
    skips_extracted = []
    for sk in raw_skips:
        if isinstance(sk, dict):
            line_no = sk.get("line")
            reason = sk.get("reason", "")
            raw_text = raw_map.get(line_no, "Line not found in raw index")
            skips_extracted.append({
                "line": line_no,
                "reason": reason,
                "raw_text": raw_text
            })
        elif isinstance(sk, int):
            raw_text = raw_map.get(sk, "Line not found in raw index")
            skips_extracted.append({
                "line": sk,
                "reason": "Legacy numeric skip without explicit reason",
                "raw_text": raw_text
            })

    # 3. High-Risk or Omitted Source Decisions
    sd_decisions = sd.get("decisions", [])
    risky_decisions = []
    for d in sd_decisions:
        dest = d.get("destination", "")
        risk = d.get("risk", "low")
        if dest in ["omit", "evidence"] or risk in ["high", "medium"]:
            risky_decisions.append({
                "source_line": d.get("source_line"),
                "contributor": d.get("contributor"),
                "destination": dest,
                "risk": risk,
                "context": d.get("context", ""),
                "reason": d.get("reason", "")
            })

    # 4. Manifest Tension Telemetry
    bot_review = manifest.get("editorialForum", {}).get("initialBotReview", {})
    tradeoffs = bot_review.get("tradeOffs", [])
    nearest_risks = bot_review.get("nearestRisks", [])
    tomatometer = bot_review.get("tomatometer", None)
    popcornmeter = bot_review.get("popcornmeter", None)

    # 5. Campaign Arc & Milestone Context
    milestone_entry = ""
    if os.path.exists(arc_ledger_path):
        with open(arc_ledger_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Find Section 4 table row for this session
            m_row = re.search(rf"\|\s*{session_id.upper()}\s*\|.*", content, re.IGNORECASE)
            if m_row:
                milestone_entry = m_row.group(0)

    # 6. Previous Session Continuity Hooks (if specified)
    prev_context = {}
    if prev_session_id:
        p_cfg = load_json(os.path.join(base_dir, "config", f"{prev_session_id}-session-config.json")) or {}
        p_sd = load_json(os.path.join(base_dir, "data", "index", f"{prev_session_id}-source-decisions.json")) or {}
        prev_context = {
            "session_id": prev_session_id,
            "introduced_lore": p_cfg.get("session_lore_terms", []),
            "omitted_decisions_sample": [d for d in p_sd.get("decisions", []) if d.get("destination") == "omit"][:5]
        }

    return {
        "session_id": session_id,
        "title": cfg.get("title", ""),
        "authorial_liberties": liberties_extracted,
        "substantive_skips": skips_extracted,
        "risky_source_decisions": risky_decisions,
        "tension_telemetry": {
            "tomatometer": tomatometer,
            "popcornmeter": popcornmeter,
            "tradeoffs": tradeoffs,
            "nearest_risks": nearest_risks
        },
        "campaign_milestone": milestone_entry,
        "prev_session_context": prev_context
    }

def main():
    parser = argparse.ArgumentParser(description="Extract documented session trade-offs for red-team audit")
    parser.add_argument("session", nargs="?", default=None, help="Session ID (default: auto-detect latest)")
    parser.add_argument("--prev", default=None, help="Previous session ID for continuity analysis")
    parser.add_argument("--format", choices=["json", "summary"], default="summary", help="Output format")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_session = args.session or find_latest_session(base_dir)
    
    prev_session = args.prev
    if not prev_session:
        m = re.match(r"^s(\d+)$", target_session)
        if m and int(m.group(1)) > 1:
            prev_session = f"s{int(m.group(1)) - 1}"

    dossier = extract_tradeoff_dossier(target_session, base_dir, prev_session)

    if args.format == "json":
        print(json.dumps(dossier, indent=2))
        return

    # Print summary
    print(f"=" * 75)
    print(f"🎯 TRADE-OFF DOSSIER: {dossier['session_id'].upper()} ({dossier['title']})")
    print(f"=" * 75)
    print(f"• Authorial Liberties (Track B): {len(dossier['authorial_liberties'])}")
    for idx, l in enumerate(dossier['authorial_liberties'], 1):
        print(f"  {idx}. [{l['scene'].upper()}] Scope: {l['scope']}")
        print(f"     Liberty: {l['liberty']}")
        print(f"     Impact:  {l['impact']}")

    print(f"\n• Substantive Skip Exemptions (Track A): {len(dossier['substantive_skips'])}")
    for idx, s in enumerate(dossier['substantive_skips'], 1):
        print(f"  {idx}. L{s['line']}: \"{s['raw_text'][:60]}...\"")
        print(f"     Stated Reason: {s['reason']}")

    print(f"\n• High-Risk / Omitted Source Decisions: {len(dossier['risky_source_decisions'])}")
    for idx, d in enumerate(dossier['risky_source_decisions'][:5], 1):
        print(f"  {idx}. L{d['source_line']} ({d['contributor']}) -> {d['destination'].upper()} [Risk: {d['risk']}]")
        print(f"     Context: {d['context']}")

    t = dossier['tension_telemetry']
    print(f"\n• Tension Telemetry:")
    print(f"  Tomatometer: {t.get('tomatometer')}% | Popcornmeter: {t.get('popcornmeter')}%")
    print(f"  Active Trade-offs: {len(t.get('tradeoffs', []))} | Nearest Risks: {len(t.get('nearest_risks', []))}")
    print(f"=" * 75)

if __name__ == "__main__":
    main()
