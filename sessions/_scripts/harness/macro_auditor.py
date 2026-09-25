"""Macro Narrative & Reader Auditor.

Cross-references novelized scenes and compiled sessions against the Campaign Narrative Bible
and campaign-config.json to audit character empathy anchors, cold-reader grounding,
and sensory signatures.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

try:
    from .config import get_character_anchors, get_repo_root, get_sessions_dir
except (ImportError, ValueError):
    from config import get_character_anchors, get_repo_root, get_sessions_dir


class MacroAuditor:
    def __init__(self):
        self.char_anchors = get_character_anchors()

    def audit_scene(self, text: str, scene_title: str = "Scene", is_full_session: bool = False) -> Dict[str, Any]:
        """Audits character anchors, empathy markers, and cold-reader grounding.
        
        Args:
            text: Markdown content of the scene or session.
            scene_title: Identifier for reporting.
            is_full_session: Set True when auditing a compiled multi-chapter session.
        """
        # Strip comments for anchor and abbreviation scanning
        clean_text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        text_lower = clean_text.lower()
        active_characters = []
        anchor_reports = []

        # Identify which core PCs appear in this scene/session
        for char_key, data in self.char_anchors.items():
            name = data["name"]
            # Look for character name in text (match exact word)
            if re.search(rf"\b{re.escape(name)}\b", clean_text):
                active_characters.append(name)
                # Check for sensory/empathy keywords
                found_keywords = [kw for kw in data["keywords"] if re.search(rf"\b{re.escape(kw)}\b", text_lower)]
                # In full session, require at least 2 distinct keywords; in single scene, at least 1 keyword
                required_count = 2 if is_full_session else 1
                has_sensory_anchor = len(found_keywords) >= required_count

                anchor_reports.append({
                    "character": name,
                    "empathy_core": data["empathy_core"],
                    "keywords_found": found_keywords,
                    "anchored": has_sensory_anchor,
                    "status": "PASS" if has_sensory_anchor else "NEEDS_ANCHORING"
                })

        # Check for potential ungrounded table abbreviations outside quotes
        prose_only = re.sub(r'"[^"]*"|“[^”]*”', " ", clean_text)
        ungrounded_flags = []
        for abbrev in ["pc", "npc", "dc", "hp", "ac", "dm", "gm"]:
            matches = list(re.finditer(rf"\b{re.escape(abbrev.upper())}\b", prose_only))
            for m in matches:
                ungrounded_flags.append(f"Ungrounded table abbreviation '{abbrev.upper()}' at char index {m.start()}")

        # Check for micro-chapter fragmentation in single scene blocks (only if not a full session)
        if not is_full_session:
            chapter_matches = list(re.finditer(r"^##\s+CHAPTER\s+.*$", clean_text, re.M))
            if len(chapter_matches) > 1:
                ungrounded_flags.append(
                    f"Multiple chapter headers ({len(chapter_matches)}) found in a single scene block. Only one chapter heading allowed per scene block."
                )

        passed = len(ungrounded_flags) == 0 and (
            len(anchor_reports) == 0 or all(r["anchored"] for r in anchor_reports)
        )

        return {
            "scene_title": scene_title,
            "characters_present": active_characters,
            "character_anchors": anchor_reports,
            "ungrounded_flags": ungrounded_flags,
            "passed": passed
        }

    def audit_session(self, session_id: str, repo_root: Path = None) -> Dict[str, Any]:
        """Audits a full compiled session story file (e.g. s1-clean-story.md)."""
        root = repo_root or get_repo_root()
        story_path = root / "sessions" / "data" / "clean" / f"{session_id}-clean-story.md"

        if not story_path.exists():
            return {
                "session_id": session_id,
                "passed": False,
                "errors": [f"Story file not found: {story_path}"]
            }

        with open(story_path, "r", encoding="utf-8") as f:
            content = f.read()

        res = self.audit_scene(content, scene_title=f"{session_id.upper()} Full Story", is_full_session=True)
        res["session_id"] = session_id
        res["filepath"] = str(story_path)
        return res

    def format_reader_card(self, audit_data: Dict[str, Any], scene_id: int = 0) -> str:
        """Formats an actionable review report card."""
        title = audit_data.get("scene_title", f"Scene {scene_id:02d}")
        lines = [
            f"### 📋 Macro Narrative & Reader Audit ({title})",
            "",
            "#### 👤 Character Empathy & Physical Anchoring:",
        ]

        if not audit_data.get("character_anchors"):
            lines.append("  - No core player characters present.")
        else:
            for r in audit_data["character_anchors"]:
                status_icon = "✅" if r["anchored"] else "❌"
                kw_str = ", ".join(r["keywords_found"]) if r["keywords_found"] else "none"
                lines.append(f"  - {status_icon} **{r['character']}**: [{r['status']}]")
                lines.append(f"    * Core: {r['empathy_core']}")
                lines.append(f"    * Sensory tokens detected: `{kw_str}`")

        lines.append("")
        lines.append("#### 📖 Cold-Reader Grounding & Lore Filter:")
        if audit_data.get("ungrounded_flags"):
            for flag in audit_data["ungrounded_flags"]:
                lines.append(f"  - ❌ {flag}")
        else:
            lines.append("  - ✅ Zero ungrounded table abbreviations or unanchored jargon.")

        lines.append("")
        return "\n".join(lines)


def main():
    """CLI runner for direct invocation: python macro_auditor.py s1 or python macro_auditor.py --file <path>"""
    if len(sys.argv) < 2:
        print("Usage: python -m harness.macro_auditor <session_id> or --file <path>")
        sys.exit(1)

    auditor = MacroAuditor()

    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Usage: python -m harness.macro_auditor --file <path_to_scene.md>")
            sys.exit(1)
        file_path = Path(sys.argv[2])
        if not file_path.exists():
            print(f"File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        text = file_path.read_text(encoding="utf-8")
        result = auditor.audit_scene(text, scene_title=file_path.stem, is_full_session=False)
        print(auditor.format_reader_card(result))
        if not result["passed"]:
            print(f"❌ Macro Narrative Audit FAILED for {file_path.name}", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"✅ Macro Narrative Audit PASSED for {file_path.name}")
            sys.exit(0)

    session_id = sys.argv[1].lower()
    result = auditor.audit_session(session_id)

    print(auditor.format_reader_card(result))

    if not result["passed"]:
        print(f"❌ Macro Narrative Audit FAILED for {session_id.upper()}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✅ Macro Narrative Audit PASSED for {session_id.upper()}")
        sys.exit(0)


if __name__ == "__main__":
    main()
