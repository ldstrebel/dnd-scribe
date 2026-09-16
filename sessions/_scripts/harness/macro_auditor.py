"""Macro Narrative & Reader Auditor.

Cross-references individual scene blocks against the Campaign Narrative Bible
(campaign/prep/campaign-narrative-bible.md) to audit character empathy anchors,
cold-reader grounding, and sensory signatures.
"""

import re
from pathlib import Path
from typing import Dict, Any, List


from .config import get_character_anchors


class MacroAuditor:
    def __init__(self):
        self.char_anchors = get_character_anchors()

    def audit_scene(self, text: str, scene_title: str = "Scene") -> Dict[str, Any]:
        """Audits character anchors, empathy markers, and cold-reader grounding."""
        text_lower = text.lower()
        active_characters = []
        anchor_reports = []

        # Identify which core PCs appear in this scene
        for char_key, data in self.char_anchors.items():
            name = data["name"]
            # Look for character name in text
            if re.search(rf"\b{re.escape(name)}\b", text):
                active_characters.append(name)
                # Check for sensory/empathy keywords
                found_keywords = [kw for kw in data["keywords"] if re.search(rf"\b{re.escape(kw)}\b", text_lower)]
                has_sensory_anchor = len(found_keywords) >= 2

                anchor_reports.append({
                    "character": name,
                    "empathy_core": data["empathy_core"],
                    "keywords_found": found_keywords,
                    "anchored": has_sensory_anchor,
                    "status": "PASS" if has_sensory_anchor else "NEEDS_ANCHORING"
                })

        # Check for potential ungrounded table abbreviations
        ungrounded_flags = []
        for abbrev in ["pc", "npc", "dc", "hp", "ac", "dm", "gm"]:
            # Check for standalone uppercase abbreviations outside quotes
            matches = re.finditer(rf"\b{re.escape(abbrev.upper())}\b", text)
            for m in matches:
                ungrounded_flags.append(f"Ungrounded table abbreviation '{abbrev.upper()}' at char index {m.start()}")

        # Check for micro-chapter fragmentation in single scene blocks
        chapter_matches = list(re.finditer(r"^##\s+CHAPTER\s+.*$", text, re.M))
        if len(chapter_matches) > 1:
            ungrounded_flags.append(f"Multiple chapter headers ({len(chapter_matches)}) found in a single scene block. Only one chapter heading allowed per scene block.")

        return {
            "scene_title": scene_title,
            "characters_present": active_characters,
            "character_anchors": anchor_reports,
            "ungrounded_flags": ungrounded_flags,
            "passed": len(ungrounded_flags) == 0 and all(r["anchored"] for r in anchor_reports)
        }

    def format_reader_card(self, audit_data: Dict[str, Any], scene_id: int) -> str:
        """Formats an actionable Layer 2 & Layer 3 review report card."""
        lines = [
            f"### 📋 Scene {scene_id:02d} Narrative & Reader Audit ({audit_data['scene_title']})",
            "",
            "#### 👤 Character Empathy & Physical Anchoring:",
        ]

        if not audit_data["character_anchors"]:
            lines.append("  - No core player characters present in scene.")
        else:
            for r in audit_data["character_anchors"]:
                status_icon = "✅" if r["anchored"] else "⚠️"
                kw_str = ", ".join(r["keywords_found"]) if r["keywords_found"] else "none"
                lines.append(f"  - {status_icon} **{r['character']}**: [{r['status']}]")
                lines.append(f"    * Core: {r['empathy_core']}")
                lines.append(f"    * Sensory tokens detected: `{kw_str}`")

        lines.append("")
        lines.append("#### 📖 Cold-Reader Grounding & Lore Filter:")
        if audit_data["ungrounded_flags"]:
            for flag in audit_data["ungrounded_flags"]:
                lines.append(f"  - ❌ {flag}")
        else:
            lines.append("  - ✅ Zero ungrounded table abbreviations or unanchored jargon.")

        lines.append("")
        return "\n".join(lines)
