#!/usr/bin/env python3
"""
Pre-Flight Session Context Packet Builder.

Assembles an immutable narrative context briefing packet for any session (e.g. s5)
by connecting:
1. Preceding session cliffhanger & party state (from previous session final scene block)
2. Cumulative campaign synopsis (from sessions/index.md)
3. Active Fragment leads & timeline edits (from campaign/world/the-fragments.md)
4. Character physical anchors, voice profiles, and inventory (from campaign/characters/pcs/ & campaign-config.json)
5. STT phonetic pitfalls & deny-lists (from campaign-config.json)
6. Running motifs and table humor patterns

Usage:
    python sessions/_scripts/build_session_context.py s5
    python sessions/_scripts/build_session_context.py s5 --out sessions/data/clean/blocks/s5-context-briefing.md
"""

import sys
import os
import re
import json
import glob
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def load_campaign_config(repo_root: Path) -> dict:
    cfg_path = repo_root / "sessions" / "config" / "campaign-config.json"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_previous_session_id(session_id: str) -> str:
    m = re.match(r"^s(\d+)$", session_id.lower())
    if m:
        num = int(m.group(1))
        if num > 1:
            return f"s{num - 1}"
    return ""


def get_final_scene_block(repo_root: Path, prev_session_id: str) -> tuple[str, str]:
    """Finds the final scene block file for the preceding session and returns (filename, content)."""
    blocks_dir = repo_root / "sessions" / "data" / "clean" / "blocks"
    pattern = str(blocks_dir / f"{prev_session_id}-scene-*.md")
    files = sorted(glob.glob(pattern))
    if not files:
        return "", ""
    last_file = Path(files[-1])
    with open(last_file, "r", encoding="utf-8") as f:
        return last_file.name, f.read()


def extract_session_synopsis(repo_root: Path, session_id: str) -> str:
    """Extracts synopsis of a session from sessions/index.md."""
    index_path = repo_root / "sessions" / "index.md"
    if not index_path.exists():
        return ""
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Look for session heading like "## Session 4: ..." or "### Session 4"
    m_num = re.search(r"\d+", session_id)
    if not m_num:
        return ""
    num_str = m_num.group(0)

    pattern = rf"(?:##|###)\s+Session\s+{num_str}[:\s].*?(?=(?:##|###)\s+Session|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return ""


def load_character_dossiers(repo_root: Path) -> dict:
    pcs_dir = repo_root / "campaign" / "characters" / "pcs"
    dossiers = {}
    if pcs_dir.exists():
        for f in sorted(pcs_dir.glob("*.md")):
            if f.name.startswith("."):
                continue
            with open(f, "r", encoding="utf-8") as file:
                dossiers[f.stem] = file.read().strip()
    return dossiers


def load_fragments(repo_root: Path) -> str:
    frag_path = repo_root / "campaign" / "world" / "the-fragments.md"
    if frag_path.exists():
        with open(frag_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def build_briefing(session_id: str, repo_root: Path) -> str:
    prev_id = get_previous_session_id(session_id)
    camp_cfg = load_campaign_config(repo_root)
    char_anchors = camp_cfg.get("character_anchors", {})
    phonetics = camp_cfg.get("phonetic_replacements", {})
    deny_players = camp_cfg.get("deny_list_players", [])
    deny_mechanics = camp_cfg.get("deny_list_mechanics", [])

    prev_synopsis = extract_session_synopsis(repo_root, prev_id) if prev_id else ""
    last_block_name, last_block_text = get_final_scene_block(repo_root, prev_id) if prev_id else ("", "")
    fragments_text = load_fragments(repo_root)
    pc_dossiers = load_character_dossiers(repo_root)

    # Clean the last block text to remove ledgers for readability
    clean_last_block = re.sub(r"<!--.*?-->", "", last_block_text).strip()
    last_paragraphs = [p.strip() for p in clean_last_block.split("\n\n") if p.strip()]
    closing_beat_snippet = "\n\n".join(last_paragraphs[-4:]) if last_paragraphs else "(No preceding block found)"

    lines = [
        f"# 🧭 Pre-Flight Context Briefing: Session {session_id.upper()}",
        f"> **Generated automatically** by `build_session_context.py` for authorial grounding & cross-session continuity.",
        "",
        "---",
        "",
        "## 1. 🔄 Previous Session Continuity & Immediate Cliffhanger",
    ]

    if prev_id:
        lines.extend([
            f"- **Preceding Session:** `{prev_id.upper()}`",
            f"- **Final Scene Block:** `{last_block_name}`",
            "",
            "### 🏁 Exact Closing Beat of Preceding Session:",
            "```markdown",
            closing_beat_snippet,
            "```",
            "",
        ])
        if prev_synopsis:
            lines.extend([
                f"### 📜 Preceding Session Official Synopsis ({prev_id.upper()}):",
                prev_synopsis,
                "",
            ])
    else:
        lines.append("- *This is Session 1 (Opening of Campaign). No prior session continuity exists.*")

    lines.extend([
        "---",
        "",
        "## 2. 🧩 Active Campaign Quests & Fragment Leads",
        "```markdown",
        fragments_text if fragments_text else "No fragment file found.",
        "```",
        "",
        "### 🎯 Active Target Fragment for this Arc:",
        "- **Fragment 1 (Resolved in S3/S4):** Greek Inscription Tablet (*Beckon/Beacon*) secured from NC Museum of History.",
        "- **Fragment 3 (CURRENT TARGET):** The Mad Doctor's Tour / Dr. Aris Thorne medical anomalies tour across college campuses.",
        "- **Route Taken:** The *Forgotten Trail* (wilderness Lost Road leading to West Virginia university stops).",
        "",
        "---",
        "",
        "## 3. 👤 Character Sensory Anchors & Physical Grounding",
        "Every active character MUST exhibit their sensory/physical anchors in their scenes:",
        "",
    ])

    for ckey, cdata in char_anchors.items():
        kw_list = ", ".join([f"`{kw}`" for kw in cdata.get("keywords", [])])
        lines.extend([
            f"### **{cdata['name']}**",
            f"- **Empathy Core:** {cdata['empathy_core']}",
            f"- **Sensory Anchor Keywords:** {kw_list}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## 4. 🎒 Party Relics & Inventory Changes (from Prior Sessions)",
        "- **Pierre:** Heavy canvas rucksack, 3 scrolls from the Library of the Fates, spare wire spectacles, woolen beret, recovered Greek stele Fragment, and newly acquired bronze javelin (hoping for Zeus lightning modification).",
        "- **Prof. Edward Dravin:** Tweed coat, tarnished silver bell, Stanford lecture notes, spectroscopic lenses, and newly acquired hoplite shield from NC Museum (currently being inspected for latent enchantments).",
        "- **Alfie:** Driftwood body, seashell button eyes, fishing-hook hand, sewing-needle rapier, sailcloth vest, and oversized souvenir museum ballcap.",
        "- **Eusacles:** Denim jacket, aviator sunglasses, enchanted watch-chain morningstar, divine Thanatos senses (rejoining party).",
        "",
        "---",
        "",
        "## 5. 🎙️ Phonetic Pitfalls & STT Mishearings to Watch For",
        "Automated transcription tools frequently mangle these in-world terms into English words:",
        "",
        "| Spoken Sound / STT Error | Canonical Term | Notes |",
        "|---|---|---|",
    ])

    for bad_tok, good_tok in sorted(phonetics.items()):
        lines.append(f"| `{bad_tok}` | **{good_tok}** | Auto-correct to `{good_tok}` |")

    lines.extend([
        "",
        "---",
        "",
        "## 6. 🚫 Deny-Lists (Zero Tolerance in Novelized Prose)",
        "",
        "### ❌ Tabletop Mechanics (Novelize into sensory manifestation):",
        ", ".join([f"`{m}`" for m in sorted(list(deny_mechanics)[:18])]) + " ...",
        "",
        "### ❌ Real-World / OOC Realia (Strip from narrative):",
        ", ".join([f"`{r}`" for r in sorted(list(camp_cfg.get('deny_list_realia', []))[:15])]) + " ...",
        "",
        "### ❌ Real Player Names (Must strictly map to character names):",
        ", ".join([f"`{p}`" for p in sorted(list(deny_players)[:12])]) + " ...",
        "",
        "---",
        "",
        "## 7. 🎭 Running Motifs & Comedic Dynamic Rules",
        "1. **Pierre's French Defensiveness:** Rationalizes everything through polite Parisian etiquette, true-crime fandom, and claiming *'what happens in Vegas stays in Vegas'*, while secretly dreading the golden petrifying glare behind his wire spectacles.",
        "2. **Dravin's Academic Rationalization:** Analyzes cosmic horrors and museum theft as *'returning artifacts to their original mythological use, ipso facto'*.",
        "3. **Alfie's Miniature Feistiness:** Perched on shoulders, Cockney sailor swagger, defensive about her size and her souvenir museum hat, wielding Wordcraft with chaotic glee.",
        "4. **Eusacles' Irreverent Pragmatism:** Cynical Vegas gambler, blunt problem-solver, swinging his five-dollar watch-chain morningstar while complaining about being far from roulette tables.",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Pre-Flight Session Context Briefing Generator")
    parser.add_argument("session", help="Target session ID (e.g. s5)")
    parser.add_argument("--out", "-o", help="Optional output filepath to save markdown")
    args = parser.parse_args()

    repo_root = get_repo_root()
    session_id = args.session.lower()
    briefing = build_briefing(session_id, repo_root)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(briefing)
        print(f"✅ Context briefing saved to: {out_path}")
    else:
        print(briefing)


if __name__ == "__main__":
    main()
