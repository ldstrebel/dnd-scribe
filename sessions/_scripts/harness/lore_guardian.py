"""Lore and Entity Guardian (ProofreaderPro Model).

Validates canonical entity spelling, catches phonetic STT errors,
flags unknown invented names, and audits third-person past-tense consistency.
"""

import re
import difflib
from typing import List, Dict, Any, Tuple
from .config import load_canonical_entities, PHONETIC_REPLACEMENTS


# Common third-person present tense verbs that leak from TTRPG gameplay into narrative prose
PRESENT_TENSE_VERBS = {
    "says", "asks", "turns", "looks", "walks", "steps", "grins", "smiles",
    "watches", "notices", "reaches", "pulls", "pushes", "drops", "stands",
    "sits", "glances", "stumbles", "shrugs", "nods", "shakes", "peers",
    "leaps", "runs", "rushes", "points", "whispers", "shouts", "mutters"
}


class LoreGuardian:
    def __init__(self, phonetic_map: Dict[str, str] = None):
        entities = load_canonical_entities()
        self.pcs = set(entities["pcs"])
        self.npcs = set(entities["npcs"])
        self.locations = set(entities["locations"])
        self.all_canonical = self.pcs | self.npcs | self.locations

        # Lowercase map for fast lookup
        self.canonical_lower = {e.lower(): e for e in self.all_canonical}

        # Phonetic drift regexes
        self.phonetic_map = PHONETIC_REPLACEMENTS if phonetic_map is None else phonetic_map

        # Regex for dialogue vs narrative
        self.dialogue_strip_regex = re.compile(r'"[^"]*"|“[^”]*”')

    def audit_phonetic_drift(self, text: str) -> List[Dict[str, Any]]:
        """Finds known phonetic mishearings from audio transcription."""
        issues = []
        lines = text.splitlines()

        for line_num, line in enumerate(lines, start=1):
            if line.strip().startswith("<!--") or line.strip().startswith("#"):
                continue

            # Check each phonetic replacement
            for bad_term, proper_term in self.phonetic_map.items():
                pattern = rf"\b{re.escape(bad_term)}\b"
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    # For common words like "real", only flag if capitalized or in entity-like context
                    if bad_term == "real" and match.group(0) == "real":
                        continue  # "real life" is fine, but "Real said" or "looking at Real" is an error

                    issues.append({
                        "line": line_num,
                        "type": "PHONETIC_DRIFT",
                        "severity": "ERROR",
                        "found": match.group(0),
                        "suggested": proper_term,
                        "snippet": line[:100],
                        "message": f"Phonetic STT drift: '{match.group(0)}' should be '{proper_term}'."
                    })
        return issues

    def audit_tense_consistency(self, text: str) -> List[Dict[str, Any]]:
        """Checks that narrative prose outside quotes strictly adheres to past tense."""
        issues = []
        lines = text.splitlines()

        for line_num, line in enumerate(lines, start=1):
            if line.strip().startswith("<!--") or line.strip().startswith("#"):
                continue
            if not line.strip():
                continue

            # Strip out dialogue quotes so we don't flag present tense spoken by characters!
            prose_only = self.dialogue_strip_regex.sub(" ", line)

            # Check for present tense verbs linked to pronouns or character names
            # e.g., "Britt looks", "he turns", "Ignatius walks"
            for verb in PRESENT_TENSE_VERBS:
                pattern = rf"\b([A-Z][a-z]+|he|she|they|it)\s+{verb}\b"
                for match in re.finditer(pattern, prose_only):
                    subj = match.group(1)
                    issues.append({
                        "line": line_num,
                        "type": "TENSE_SLIPPAGE",
                        "severity": "WARN",
                        "subject": subj,
                        "verb": verb,
                        "snippet": line[:100],
                        "message": f"Present-tense slip in narrative prose: '{subj} {verb}'. Expected past tense."
                    })

        return issues

    def scan_text(self, text: str, filename: str = "text") -> Dict[str, Any]:
        phonetic_issues = self.audit_phonetic_drift(text)
        tense_issues = self.audit_tense_consistency(text)

        errors = [i for i in phonetic_issues if i["severity"] == "ERROR"]
        warnings = [i for i in phonetic_issues if i["severity"] == "WARN"] + tense_issues

        return {
            "filename": filename,
            "passed": len(errors) == 0,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings
        }
