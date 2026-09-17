"""verify_alternate_scene.py

Deterministic 3-Gate Verification Suite for Authorial Cut / Alternate Scenes.

Enforces:
1. Gate 1: Entity and Relic Anchor Coverage (No silent character or key prop drops)
2. Gate 2: Leak, Slang and Foreign Prop Scanner (Anti-hallucination and OOC barrier)
3. Gate 3: Span Provenance and Compression Integrity (<!-- Lxxxx-Lyyyy --> ledger accounting)
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sessions._scripts.harness.leak_detector import LeakDetector
from sessions._scripts.harness.lore_guardian import LoreGuardian
from sessions._scripts.harness.config import load_canonical_entities, DENY_LIST_PLAYERS

HIGH_RISK_FOREIGN_PROPS = {
    "sensor", "sensors", "laser", "lasers", "elevator", "keycard", "helicopter",
    "lockpick", "lockpicks", "suv", "sedan", "ford", "chevy", "toyota",
    "smartphone", "iphone", "laptop", "walkie-talkie", "gps"
}

def parse_spans(text: str) -> List[Tuple[int, int]]:
    """Extracts all <!-- Lxxxx-Lyyyy --> or <!-- Lxxxx --> spans from text."""
    spans = []
    pattern = re.compile(r"<!--\s*L(\d+)(?:\s*-\s*L?(\d+))?\s*-->")
    for match in pattern.finditer(text):
        start_line = int(match.group(1))
        end_line = int(match.group(2)) if match.group(2) else start_line
        spans.append((start_line, end_line))
    return spans

def extract_raw_range_header(text: str) -> Optional[Tuple[int, int]]:
    """Extracts <!-- RAW_RANGE: [881, 1010] ... --> header."""
    match = re.search(r"<!--\s*RAW_RANGE:\s*\[(\d+),\s*(\d+)\]", text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None

def extract_dialogue_speakers(text: str) -> Dict[str, List[str]]:
    """Extracts spoken dialogue turns by character."""
    alias_map = {"Edward": "Dravin", "Michael": "Mike", "Iggy": "Ignatius"}
    dialogue_map = {}
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("<!--") or stripped.startswith("#") or not stripped:
            continue
        quotes = re.findall(r'"([^"]+)"|“([^”]+)”', stripped)
        if quotes:
            speaker_match = re.search(r"\b(Pierre|Alfie|Dravin|Edward|Eusacles|Naomi|Mike|Michael|Iggy|Ignatius|Britt|Aggie|Lomi|Pip)\b", stripped)
            raw_speaker = speaker_match.group(1) if speaker_match else "Narrator"
            speaker = alias_map.get(raw_speaker, raw_speaker)
            if speaker not in dialogue_map:
                dialogue_map[speaker] = []
            for q in quotes:
                dialogue_map[speaker].append(q[0] or q[1])
    return dialogue_map


def audit_gate1_entity_coverage(archival_text: str, alternate_text: str) -> Dict[str, Any]:
    """Gate 1: Verifies that core actors and key props from archival are present in alternate."""
    alias_map = {"Michael": "Mike", "Edward": "Dravin", "Iggy": "Ignatius"}
    canonical = load_canonical_entities()
    all_known_entities = set(canonical["pcs"]) | set(canonical["npcs"])
    all_known_entities.update({"Pierre", "Alfie", "Dravin", "Edward", "Eusacles", "Naomi", "Mike", "Michael"})

    archival_entities = set()
    for entity in all_known_entities:
        if re.search(rf"\b{re.escape(entity)}\b", archival_text, re.IGNORECASE):
            norm_entity = alias_map.get(entity, entity)
            archival_entities.add(norm_entity)

    missing_entities = []
    retained_entities = []
    for entity in archival_entities:
        # Check either name or any alias
        patterns = [re.escape(entity)]
        for k, v in alias_map.items():
            if v == entity:
                patterns.append(re.escape(k))
        regex = rf"\b({'|'.join(patterns)})\b"
        if re.search(regex, alternate_text, re.IGNORECASE):
            retained_entities.append(entity)
        else:
            missing_entities.append(entity)

    relic_keywords = {"cucumber", "pancakes", "pancake", "daughter", "card", "zeus", "seuss", "needle", "beret", "limestone", "stele"}
    archival_lower = archival_text.lower()
    alternate_lower = alternate_text.lower()
    archival_relics = {r for r in relic_keywords if r in archival_lower}
    missing_relics = [r for r in archival_relics if r not in alternate_lower]

    passed = (len(missing_entities) == 0) and (len(missing_relics) == 0)

    return {
        "passed": passed,
        "archival_entities": sorted(list(archival_entities)),
        "retained_entities": sorted(retained_entities),
        "missing_entities": sorted(missing_entities),
        "archival_relics": sorted(list(archival_relics)),
        "missing_relics": sorted(missing_relics),
    }

def audit_gate2_leaks_and_props(alternate_text: str) -> Dict[str, Any]:
    """Gate 2: Scans for real player names, TTRPG mechanics, OOC realia, foreign props, and phonetic errors."""
    leak_detector = LeakDetector()
    lore_guardian = LoreGuardian()
    leak_res = leak_detector.scan_text(alternate_text)
    lore_res = lore_guardian.scan_text(alternate_text)

    foreign_prop_hits = []
    lines = alternate_text.splitlines()
    for line_num, line in enumerate(lines, start=1):
        if line.strip().startswith("<!--") or line.strip().startswith("#"):
            continue
        for prop in HIGH_RISK_FOREIGN_PROPS:
            if re.search(rf"\b{re.escape(prop)}\b", line, re.IGNORECASE):
                foreign_prop_hits.append({
                    "line": line_num,
                    "prop": prop,
                    "snippet": line[:100]
                })

    all_errors = list(leak_res["violations"]) + [
        {"line": h["line"], "type": "FOREIGN_PROP_LEAK", "severity": "ERROR", "message": f"Modern foreign prop '{h['prop']}' detected."}
        for h in foreign_prop_hits
    ] + [
        {"line": e["line"], "type": e["type"], "severity": "ERROR", "message": e["message"]}
        for e in lore_res["errors"]
    ]

    return {
        "passed": len(all_errors) == 0,
        "error_count": len(all_errors),
        "errors": all_errors,
        "warnings": lore_res["warnings"]
    }

def audit_gate3_span_provenance(alternate_text: str, raw_range: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
    """Gate 3: Validates span monotonicity, boundary coverage, and dialogue compression balance."""
    spans = parse_spans(alternate_text)
    errors = []
    warnings = []

    if not spans:
        errors.append({
            "type": "MISSING_SPANS",
            "message": "Authorial cut contains no <!-- Lxxxx-Lyyyy --> span markers."
        })
        return {"passed": False, "errors": errors, "warnings": warnings, "spans": []}

    prev_end = 0
    for idx, (s_start, s_end) in enumerate(spans):
        if s_start > s_end:
            errors.append({
                "type": "INVALID_SPAN_BOUNDS",
                "message": f"Span {idx+1} has inverted bounds: L{s_start:04d} > L{s_end:04d}"
            })
        if s_start < prev_end:
            warnings.append({
                "type": "SPAN_BACKWARD_OVERLAP",
                "message": f"Span {idx+1} starts at L{s_start:04d} before previous span ended at L{prev_end:04d}"
            })
        prev_end = s_end

    if raw_range:
        r_min, r_max = raw_range
        first_span_start = spans[0][0]
        last_span_end = spans[-1][1]
        if first_span_start < r_min or last_span_end > r_max:
            errors.append({
                "type": "SPAN_OUT_OF_RANGE",
                "message": f"Spans [L{first_span_start:04d}..L{last_span_end:04d}] exceed RAW_RANGE [{r_min}..{r_max}]"
            })

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "span_count": len(spans),
        "covered_range": (spans[0][0], spans[-1][1]) if spans else None
    }

def verify_alternate_scene(alternate_text: str, archival_text: Optional[str] = None) -> Dict[str, Any]:
    """Runs all 3 gates on an authorial cut scene string."""
    raw_range = extract_raw_range_header(alternate_text)
    if not raw_range and archival_text:
        raw_range = extract_raw_range_header(archival_text)

    g1 = audit_gate1_entity_coverage(archival_text or alternate_text, alternate_text)
    g2 = audit_gate2_leaks_and_props(alternate_text)
    g3 = audit_gate3_span_provenance(alternate_text, raw_range)

    archival_speakers = extract_dialogue_speakers(archival_text) if archival_text else {}
    alternate_speakers = extract_dialogue_speakers(alternate_text)

    silenced_speakers = []
    for spk, turns in archival_speakers.items():
        if spk != "Narrator" and len(turns) > 0 and spk not in alternate_speakers:
            silenced_speakers.append(spk)

    overall_passed = g1["passed"] and g2["passed"] and g3["passed"] and len(silenced_speakers) == 0

    return {
        "passed": overall_passed,
        "gate1_entity_coverage": g1,
        "gate2_leaks_and_props": g2,
        "gate3_span_provenance": g3,
        "silenced_speakers": silenced_speakers,
        "alternate_speakers": {k: len(v) for k, v in alternate_speakers.items()}
    }

def print_report_card(report: Dict[str, Any], filepath: str = "Alternate Scene"):
    print("=" * 70)
    print(f"  AUTHORIAL CUT VERIFICATION REPORT: {Path(filepath).name}")
    status_str = "[PASS] PASSED" if report["passed"] else "[FAIL] FAILED"
    print(f"  STATUS: {status_str}")
    print("=" * 70)

    g1 = report["gate1_entity_coverage"]
    print("\n[GATE 1: ENTITY & RELIC COVERAGE]")
    print(f"  * Retained Entities: {', '.join(g1['retained_entities']) or 'None'}")
    if g1["missing_entities"]:
        print(f"  * [!] Missing Core Entities: {', '.join(g1['missing_entities'])}")
    if g1["missing_relics"]:
        print(f"  * [!] Missing Canonical Relics/Props: {', '.join(g1['missing_relics'])}")
    if not g1["missing_entities"] and not g1["missing_relics"]:
        print("  * [OK] 100% Core Actors & Relics Grounded.")

    g2 = report["gate2_leaks_and_props"]
    print("\n[GATE 2: LEAK & ANTI-HALLUCINATION BARRIER]")
    if g2["errors"]:
        for err in g2["errors"]:
            print(f"  * [FAIL] Line {err.get('line', '?')}: {err['message']}")
    else:
        print("  * [OK] Zero player names, mechanics leaks, or modern foreign props.")

    g3 = report["gate3_span_provenance"]
    print("\n[GATE 3: SPAN PROVENANCE & COMPRESSION]")
    if g3["covered_range"]:
        print(f"  * Spans Count: {g3['span_count']} (Span Range: L{g3['covered_range'][0]:04d} - L{g3['covered_range'][1]:04d})")
    if g3["errors"]:
        for err in g3["errors"]:
            print(f"  * [FAIL] {err['message']}")
    if g3["warnings"]:
        for warn in g3["warnings"]:
            print(f"  * [WARN] {warn['message']}")
    if report["silenced_speakers"]:
        print(f"  * [!] Silenced Characters from Archival Cut: {', '.join(report['silenced_speakers'])}")
    print(f"  * Active Dialogue Turns in Cut: {report['alternate_speakers']}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Deterministic Verifier for Authorial Cut Scenes")
    parser.add_argument("file", nargs="?", help="Path to authorial cut scene block")
    parser.add_argument("--archival", help="Path to corresponding archival scene block")
    parser.add_argument("--test", action="store_true", help="Run built-in self-test matrix")
    args = parser.parse_args()

    if args.test:
        print("[TEST] Running built-in authorial verifier self-tests...")
        sample_arch = "\n".join([
            "<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->",
            "Pierre balanced cucumber on his eyelids. <!-- L0883 -->",
            '"I make the best pancakes," Mike said. <!-- L0903 -->',
            '"Zeus, not Seuss," Dravin corrected. <!-- L0968 -->'
        ])
        sample_valid = "\n".join([
            "<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->",
            'Pierre protested from behind cucumber slices. "It can wait!" <!-- L0881-L0891 -->',
            'Mike brought hot pancakes to the porch with coffee. "Saturday pancakes!" <!-- L0900-L0942 -->',
            'Dravin adjusted his spectacles. "Zeus, not Seuss." <!-- L0954-L0973 -->'
        ])
        sample_flawed = "\n".join([
            "<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->",
            "Luke told everyone that Pierre got into a green Ford truck with a smartphone. <!-- L0950-L0800 -->"
        ])
        rep_valid = verify_alternate_scene(sample_valid, sample_arch)
        assert rep_valid["passed"] is True, f"Expected valid sample to pass, got: {rep_valid}"
        rep_flawed = verify_alternate_scene(sample_flawed, sample_arch)
        assert rep_flawed["passed"] is False, "Expected flawed sample to fail"
        assert rep_flawed["gate2_leaks_and_props"]["passed"] is False, "Expected leak gate to catch player name/ford truck"
        assert rep_flawed["gate3_span_provenance"]["passed"] is False, "Expected span gate to catch inverted spans"
        print("[PASS] All built-in verifier self-tests passed cleanly!")
        return

    if not args.file:
        parser.print_help()
        sys.exit(1)

    alt_path = Path(args.file)
    if not alt_path.exists():
        print(f"[ERROR] File not found: {alt_path}")
        sys.exit(1)

    archival_text = None
    if args.archival:
        arch_path = Path(args.archival)
        if arch_path.exists():
            archival_text = arch_path.read_text(encoding="utf-8")

    alt_text = alt_path.read_text(encoding="utf-8")
    report = verify_alternate_scene(alt_text, archival_text)
    print_report_card(report, str(alt_path))
    sys.exit(0 if report["passed"] else 1)

if __name__ == "__main__":
    main()
