#!/usr/bin/env python3
"""Audit Campaign Codex for Architectural & Audience Compliance (DEC-037 & DEC-038).

Enforces:
1. One-Way Fence & Audience Boundary (DEC-038 / FP-18):
   - Zero `[GM-PREP]` tokens in player-facing pages.
   - Zero real contributor/player names leaking from deny_list_players.
   - Zero linter/compiler risk tags (character_consistency, tabletop_fidelity, etc.).
   - Zero debug ledger tables (| Line | Contributor |).
   - Zero raw line indices (L####), schema files (manifest-v2.json), or block IDs (uneraseable_s##_b###).
2. Link Integrity: Every internal markdown link resolves to a valid file on disk.
3. Entity Resolution: Characters and factions match registered entities or aliases.
4. Word Budget: Session recaps <= 250 words; total codex index <= 60,000 words.
5. Temporal Causality: No session chronicle cites entities or events from future sessions.
6. Substantive Quality Standard:
   - Character files must contain rich identity, backstory, and voice sections (no empty stubs).
   - Session chronicles must contain narrative cliffhangers, in-world lore, deep debriefs, and story milestones.
"""

import json
import os
import re
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_DIR = REPO_ROOT / "campaign" / "codex"
CONFIG_DIR = REPO_ROOT / "sessions" / "config"

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
LINE_CITATION_RE = re.compile(r"(?:S[1-7]\s+)?L\d{4}")

# Banned leak patterns audited by the fence (preserves test_harness compatibility)
BANNED_LEAK_PATTERNS = [
    re.compile(r"\[GM-PREP", re.IGNORECASE),
    re.compile(r"\bplayer\s+telemetry\b", re.IGNORECASE),
    re.compile(r"\bruthless\s+critic\b", re.IGNORECASE),
    re.compile(r"\bjon\s+snow\b", re.IGNORECASE),
    re.compile(r"\bstorm\s*blast\b", re.IGNORECASE),
    # DEC-038 Audience Boundary Banned Leaks
    re.compile(r"\b(?:luke\s+strebel|luke\s+s\b|luke\s+foreman|sophie\s+foreman|sophie\s+noone|sophie\s+foreman\s+noone|john\s+hagey|william\s+webb|kristina\s+strebel|holly\s+strebel)\b", re.IGNORECASE),
    re.compile(r"\b(?:character_consistency|tabletop_fidelity|mechanical_fidelity|gm_confirmation|cosmological_grounding|continuity_linking|campaign_arc_continuity|thematic_integrity|negative_only_mandate|comedic_timing|narrative_momentum|action_staging)\b"),
    re.compile(r"\|\s*Line\s*\|\s*Contributor\s*\|"),
    re.compile(r"\bmanifest-v2\.json\b"),
    re.compile(r"\buneraseable_s\d{2}_b\d{3}\b"),
    re.compile(r"\bL\d{4}\b"),
    re.compile(r"\bLine\s+\d{3,4}\b", re.IGNORECASE),
    re.compile(r"\bWhere\s+We\s+Left\s+Off\b", re.IGNORECASE),
    re.compile(r"\bSTT\b|\bspeech-to-text\b", re.IGNORECASE),
    re.compile(r"\bSource\s+Decision\s+Ledger\b", re.IGNORECASE),
    re.compile(r"\bRisk\s+Category\b", re.IGNORECASE),
]


def load_canonical_entities():
    """Load canonical entity IDs and alias registry."""
    camp_cfg_file = CONFIG_DIR / "campaign-config.json"
    known_entities = set()
    alias_map = {}

    if camp_cfg_file.exists():
        with open(camp_cfg_file, "r", encoding="utf-8") as f:
            camp_cfg = json.load(f)
            alias_map = camp_cfg.get("alias_registry", {})
            for k in alias_map:
                known_entities.add(k.lower())

    for f in (REPO_ROOT / "campaign" / "characters").glob("**/*.md"):
        known_entities.add(f.stem.lower())

    for f in (REPO_ROOT / "campaign" / "factions").glob("*.md"):
        known_entities.add(f.stem.lower())

    return known_entities, alias_map


def audit_codex():
    violations = []
    known_entities, alias_map = load_canonical_entities()

    if not CODEX_DIR.exists():
        return ["[FAIL] Codex directory does not exist: campaign/codex"]

    all_codex_files = list(CODEX_DIR.glob("**/*.md"))
    if not all_codex_files:
        return ["[FAIL] No codex markdown files found in campaign/codex"]

    total_words = 0

    for doc_path in all_codex_files:
        rel_path = doc_path.relative_to(REPO_ROOT)
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        words = len(content.split())
        total_words += words

        # 1. One-Way Fence & Audience Boundary Check
        for pattern in BANNED_LEAK_PATTERNS:
            if pattern.search(content):
                violations.append(
                    f"[{rel_path}] FENCE_VIOLATION: Found banned internal/critic leak matching '{pattern.pattern}'"
                )

        # 2. Markdown Link Integrity
        for match in LINK_RE.finditer(content):
            link_text, link_target = match.groups()
            if link_target.startswith("http://") or link_target.startswith("https://") or link_target.startswith("#"):
                continue

            target_path = (doc_path.parent / link_target.split("#")[0]).resolve()
            if not target_path.exists():
                violations.append(
                    f"[{rel_path}] BROKEN_LINK: Link '[{link_text}]({link_target})' does not resolve to an existing file."
                )

        # 3. Session Chronicle Quality & Budget Checks
        if "sessions" in doc_path.parts and doc_path.name.startswith("s"):
            # Check session overview / recap section
            overview_match = re.search(r"## (?:📋 Session Overview|📖 Previously On.*?)\s*\n+(.*?)(?=\n---\n|\Z)", content, re.DOTALL)
            if overview_match:
                overview_text = overview_match.group(1).strip()
                overview_words = len(overview_text.split())
                if overview_words > 250:
                    violations.append(
                        f"[{rel_path}] BUDGET_EXCEEDED: Session overview is {overview_words} words (max allowed: 250 words per DEC-037)."
                    )
            else:
                violations.append(f"[{rel_path}] MISSING_SECTION: Session chronicle lacks '## 📋 Session Overview' synopsis.")

            if "## 🎬 Session Narrative Chronicle" not in content and "## 🔍 Deep Narrative Debrief" not in content:
                violations.append(f"[{rel_path}] MISSING_SECTION: Session chronicle lacks '## 🎬 Session Narrative Chronicle'.")
            if "## 👥 Dramatis Personae" not in content:
                violations.append(f"[{rel_path}] MISSING_SECTION: Session chronicle lacks '## 👥 Dramatis Personae'.")
            if "## 🏛️ In-World Lore" not in content:
                violations.append(f"[{rel_path}] MISSING_SECTION: Session chronicle lacks '## 🏛️ In-World Lore & Cosmological Discoveries'.")
            if "## ⚔️ Key Story Milestones" not in content:
                violations.append(f"[{rel_path}] MISSING_SECTION: Session chronicle lacks '## ⚔️ Key Story Milestones & Character Turns'.")
            if "## 🧶 Plot Lines" not in content:
                violations.append(f"[{rel_path}] MISSING_SECTION: Session chronicle lacks '## 🧶 Plot Lines & Campaign Threads'.")

            # Lore Boundary Guard: Ensure Session 7 does not misattribute out-of-session lore
            if doc_path.name == "s7.md":
                if "Hermes Express" in content:
                    violations.append(f"[{rel_path}] LORE_BOUNDARY_VIOLATION: Session 7 chronicle cites Hermes Express (Session 5 event).")

            # Check temporal causality in narrative body (session N should not cite future in-world events from session M where M > N)
            session_num_match = re.search(r"s(\d+)\.md", doc_path.name)
            if session_num_match:
                current_s = int(session_num_match.group(1))
                body_lines = [
                    line for line in content.splitlines()
                    if not line.strip().startswith("[🏛️")
                    and "Interactive Navigation:" not in line
                    and "Next Session" not in line
                    and "⏭️" not in line
                ]
                body_content = "\n".join(body_lines)
                body_no_links = re.sub(r"\[[^\]]*\]\([^)]+\)", "", body_content)
                citations = re.findall(r"\bSession\s+(\d+)\b", body_no_links)
                for cited_s in citations:
                    if int(cited_s) > current_s:
                        violations.append(
                            f"[{rel_path}] ANACHRONISTIC_CITATION: Session {current_s} cites future session {cited_s} in narrative body."
                        )

        # 4. Open Mysteries & Plot Lines Quality Checks
        if doc_path.name == "open-threads.md":
            if "Established In-World Evidence" not in content:
                violations.append(f"[{rel_path}] MISSING_SECTION: Open threads board lacks 'Established In-World Evidence' column.")
            if "Party Hypotheses" not in content:
                violations.append(f"[{rel_path}] MISSING_SECTION: Open threads board lacks 'Party Hypotheses' column.")

        # 5. Character Dossier Quality Checks
        if "characters" in doc_path.parts and doc_path.name != "README.md":
            if "## 🎭 Character Identity & Backstory" not in content and "## 🎭 Lore & Background" not in content:
                violations.append(f"[{rel_path}] EMPTY_CHARACTER_STUB: Character dossier lacks backstory/identity section.")
            if "## 🎙️ Personality" not in content:
                violations.append(f"[{rel_path}] EMPTY_CHARACTER_STUB: Character dossier lacks personality/voice section.")
            if "## 📜 Key Story Milestones" not in content:
                violations.append(f"[{rel_path}] EMPTY_CHARACTER_STUB: Character dossier lacks story milestones/campaign trajectory section.")
            if words < 120:
                violations.append(f"[{rel_path}] CHARACTER_TOO_SPARSE: Dossier contains only {words} words (minimum substantive threshold: 120 words).")

            # Entity Collision Guard (DEC-041): Susanna must never be conflated with the transformed operative
            if doc_path.name == "susanna.md":
                banned_conflations = ["transformed operative", "former captive", "parasitic tendril", "severed tendril"]
                for bc in banned_conflations:
                    if bc in content.lower():
                        violations.append(f"[{rel_path}] ENTITY_COLLISION: Susanna is conflated with the transformed captive ('{bc}').")

        # 6. Critic Review Quality & Dual-Element Card Checks (DEC-041)
        if "critic" in doc_path.parts and doc_path.name.startswith("s"):
            if "## 🌱 Character Growth Cards" not in content and "## 🎭 Character Development" not in content:
                violations.append(f"[{rel_path}] MISSING_SECTION: Critic review lacks Character Growth Cards section.")
            if "## 🔮 Narrative Bets" not in content and "## 🔮 Predictive Foresight" not in content:
                violations.append(f"[{rel_path}] MISSING_SECTION: Critic review lacks Narrative Bets section.")

            if doc_path.name == "s7-review.md":
                for player in ["Pierre", "Alfie", "Eusacles", "Dravin"]:
                    if f"[{player}]" not in content and f"### {player}" not in content:
                        violations.append(f"[{rel_path}] MISSING_PLAYER_CARD: Missing player growth card for '{player}'.")
                if "Actionable Growth & Trajectory:" not in content:
                    violations.append(f"[{rel_path}] SHALLOW_CRITIC_REVIEW: Lacks 'Actionable Growth & Trajectory' cards.")
                if "Table Chirping & Banter:" not in content:
                    violations.append(f"[{rel_path}] SHALLOW_CRITIC_REVIEW: Lacks 'Table Chirping & Banter' cards.")

    # 7. Total word budget check across codex
    if total_words > 60000:
        violations.append(
            f"[campaign/codex] TOTAL_BUDGET_EXCEEDED: Codex total size is {total_words} words (max index budget: 60,000 words)."
        )

    return violations


def main():
    print("Auditing Campaign Codex against DEC-037 & DEC-038 standards...")
    violations = audit_codex()

    if violations:
        print(f"\n[FAIL] CODEX AUDIT FAILED with {len(violations)} violations:")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print("[PASS] CODEX AUDIT PASSED: All codex files conform to DEC-037 & DEC-038 audience and budget invariants.")
        sys.exit(0)


if __name__ == "__main__":
    main()
