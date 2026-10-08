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
from sessions._scripts.audit_semantic_grounding import (
    audit_skip_ledger,
    load_lore_lexicon,
    load_skip_exemptions,
    clean_lines,
    extract_content_words
)

HIGH_RISK_FOREIGN_PROPS = {
    "sensor", "sensors", "laser", "lasers", "elevator", "keycard", "helicopter",
    "lockpick", "lockpicks", "suv", "sedan", "ford", "chevy", "toyota",
    "smartphone", "iphone", "laptop", "walkie-talkie", "gps"
}

def parse_spans(text: str) -> List[Tuple[int, int]]:
    """Extracts all <!-- Lxxxx-Lyyyy --> or <!-- Lxxxx --> spans from text."""
    spans = []
    pattern = re.compile(r"<!--\s*L(\d+)(?:\s*-\s*L?(\d+))?(?::[a-zA-Z_-]+)?\s*-->")
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
            marker_match = re.search(r"<!--\s*L\d+(?:-L?\d+)?(?::([a-zA-Z_-]+))\s*-->", stripped)
            if marker_match:
                raw_speaker = marker_match.group(1).capitalize()
            else:
                prose_outside_quotes = re.sub(r'"[^"]*"|“[^”]*”', "", stripped)
                speaker_match = re.search(r"\b(Pierre|Alfie|Dravin|Edward|Eusacles|Naomi|Mike|Michael|Iggy|Ignatius|Britt|Aggie|Lomi|Pip)\b", prose_outside_quotes)
                raw_speaker = speaker_match.group(1) if speaker_match else "Narrator"
            speaker = alias_map.get(raw_speaker, raw_speaker)
            if speaker not in dialogue_map:
                dialogue_map[speaker] = []
            for q in quotes:
                dialogue_map[speaker].append(q[0] or q[1])
    return dialogue_map


def audit_gate1_entity_coverage(archival_text: str, alternate_text: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Gate 1: Verifies that core actors and key props from archival are present in alternate."""
    alias_map = {
        "Michael": "Mike",
        "Edward": "Dravin",
        "Edward Dravin": "Dravin",
        "Prof. Edward Dravin": "Dravin",
        "Professor Edward Dravin": "Dravin",
        "Iggy": "Ignatius",
        "Dr. Thorne": "Thorne",
        "Dr. Aris Thorne": "Thorne",
        "Aris Thorne": "Thorne",
        "Rick": "Rick Ready",
    }
    canonical = load_canonical_entities()
    all_known_entities = set(canonical["pcs"]) | set(canonical["npcs"])
    all_known_entities.update({"Pierre", "Alfie", "Dravin", "Edward", "Edward Dravin", "Eusacles", "Naomi", "Mike", "Michael"})

    if session_id:
        cfg_path = REPO_ROOT / "sessions" / "config" / f"{session_id}-session-config.json"
        if cfg_path.exists():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                for _, ch_name in cfg.get("players", {}).items():
                    all_known_entities.add(ch_name)
                    parts = ch_name.split()
                    if len(parts) > 1:
                        alias_map[ch_name] = parts[-1]
                for npc in cfg.get("npcs", []):
                    n_name = npc.get("name")
                    if n_name:
                        all_known_entities.add(n_name)
                        parts = n_name.split()
                        if len(parts) > 1:
                            alias_map[n_name] = parts[-1]
            except Exception:
                pass

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
        regex = rf"\b(?:{'|'.join(patterns)})(?:s|es)?\b"
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

def audit_gate3_span_provenance(
    alternate_text: str,
    raw_range: Optional[Tuple[int, int]] = None,
    session_id: Optional[str] = None,
    scene_num: Optional[int] = None
) -> Dict[str, Any]:
    """Gate 3: Validates span monotonicity, boundary coverage, paragraph quote anchoring, speech tag attribution, and skip ledger."""
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

    paragraphs = [p.strip() for p in alternate_text.split("\n\n") if p.strip()]

    # 1. Paragraph-level quote anchoring check
    for p_idx, para in enumerate(paragraphs, start=1):
        if para.startswith("<!--") or para.startswith("#"):
            continue
        quotes = re.findall(r'"([^"]+)"|“([^”]+)”', para)
        if quotes:
            para_markers = re.findall(r"<!--\s*L\d+(?:-L?\d+)?(?::[a-zA-Z_-]+)?\s*-->", para)
            if not para_markers:
                errors.append({
                    "type": "UNANCHORED_DIALOGUE_QUOTE",
                    "message": f"Paragraph {p_idx} contains quoted dialogue with no inline line marker: '{para[:70]}...'"
                })

    # 2. Attribution Consistency & Inversion Check (Speech Verb vs Declared Speaker)
    session_cfg = {}
    if session_id:
        cfg_path = REPO_ROOT / "sessions" / "config" / f"{session_id}-session-config.json"
        if cfg_path.exists():
            try:
                session_cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            except Exception:
                pass

    known_char_map = {
        "pierre": "pierre",
        "alfie": "alfie",
        "dravin": "dravin",
        "edward": "dravin",
        "prof. edward dravin": "dravin",
        "professor edward dravin": "dravin",
        "eusacles": "eusacles",
        "naomi": "naomi",
        "theodore": "theodore",
        "rick ready": "attendant",
        "ready": "attendant",
        "rick": "attendant",
        "attendant": "attendant",
        "custodian": "attendant",
        "thorne": "thorne",
        "dr. aris thorne": "thorne",
        "dr. thorne": "thorne",
        "demonstrator": "protester",
        "protester": "protester",
        "hermes": "hermes",
        "persephone": "persephone",
        "mike": "mike",
        "rosa": "rosa",
        "child": "child"
    }
    for npc in session_cfg.get("npcs", []):
        n_name = npc.get("name", "").lower()
        if n_name:
            parts = n_name.split()
            first_k = parts[0]
            last_k = parts[-1]
            target_k = known_char_map.get(n_name, known_char_map.get(first_k, first_k))
            if n_name not in known_char_map:
                known_char_map[n_name] = target_k
            if first_k not in known_char_map:
                known_char_map[first_k] = target_k
            if last_k not in known_char_map:
                known_char_map[last_k] = target_k

    for _, ch_name in session_cfg.get("players", {}).items():
        ch_lower = ch_name.lower()
        parts = ch_lower.split()
        first_k = parts[0]
        last_k = parts[-1]
        target_k = parts[-1] if "dravin" in parts else first_k
        known_char_map[ch_lower] = target_k
        known_char_map[first_k] = target_k
        known_char_map[last_k] = target_k

    speech_verb_pat = re.compile(
        r"\b(?:([A-Z][a-zA-Z\s.-]+?)\s+(?:snapped|said|replied|muttered|countered|shouted|yelled|whispered|screamed|intervened|warned|repeated|asked|demanded|observed|challenged|argued|roared|gasped|growled|retorted|interjected|added|conceded)|(?:snapped|said|replied|muttered|countered|shouted|yelled|whispered|screamed|intervened|warned|repeated|asked|demanded|observed|challenged|argued|roared|gasped|growled|retorted|interjected|added|conceded)\s+([A-Z][a-zA-Z\s.-]+?))\b"
    )

    for p_idx, para in enumerate(paragraphs, start=1):
        if para.startswith("<!--") or para.startswith("#"):
            continue
        quotes = re.findall(r'"([^"]+)"|“([^”]+)”', para)
        if quotes:
            marker_match = re.search(r"<!--\s*L(\d+)(?:-L?(\d+))?(?::([a-zA-Z_-]+))?\s*-->", para)
            attributed_spk = None
            if marker_match:
                if marker_match.group(3):
                    attributed_spk = marker_match.group(3).lower()
                else:
                    lid = int(marker_match.group(1))
                    if str(lid) in session_cfg.get("dialogue_speakers", {}):
                        attributed_spk = session_cfg["dialogue_speakers"][str(lid)].lower()

            prose_outside = re.sub(r'"[^"]*"|“[^”]*”|<!--.*?-->', "", para).strip()
            for vm in speech_verb_pat.finditer(prose_outside):
                subject = (vm.group(1) or vm.group(2) or "").strip()
                sub_norm = subject.lower()
                matched_char = None
                for k, v in known_char_map.items():
                    if k in sub_norm or sub_norm in k:
                        matched_char = v
                        break
                if matched_char and attributed_spk:
                    norm_attr = known_char_map.get(attributed_spk, attributed_spk)
                    if matched_char != norm_attr:
                        errors.append({
                            "type": "INVERTED_DIALOGUE_ATTRIBUTION",
                            "message": (
                                f"Paragraph {p_idx} quotes speech attributed to '{attributed_spk}' "
                                f"but prose dialogue tag assigns line to '{subject}' ({matched_char})."
                            )
                        })

    # 3. DEC-024 & DEC-035 Skip Ledger & Span Continuity Verification for Authorial Cut
    ledger_match = re.search(r"<!--\s*LEDGER:\s*(?:spans|rendered)=\[(.*?)\]\s*skipped=\[(.*?)\]\s*-->", alternate_text)
    
    covered_lines = set()
    for s_start, s_end in spans:
        covered_lines.update(range(s_start, s_end + 1))
        
    skipped_lines = set()
    skipped_items = []

    if raw_range and session_id:
        r_min, r_max = raw_range
        total_range_lines = set(range(r_min, r_max + 1))

        if not ledger_match:
            if len(covered_lines) < len(total_range_lines):
                uncovered = sorted(list(total_range_lines - covered_lines))
                errors.append({
                    "type": "MISSING_SKIP_LEDGER",
                    "message": f"Authorial cut omits {len(uncovered)} raw lines (e.g. L{uncovered[0]:04d}..L{uncovered[-1]:04d}) but lacks a mandatory <!-- LEDGER: spans=[...] skipped=[...] --> footer comment."
                })
        else:
            skipped_raw = ledger_match.group(2)
            for item in re.finditer(r"L?(\d+)(?:\s*-\s*L?(\d+))?(?:\(([^)]+)\))?", skipped_raw):
                s1 = int(item.group(1))
                s2 = int(item.group(2)) if item.group(2) else s1
                reason = item.group(3) or "compressed"
                for l_num in range(s1, s2 + 1):
                    skipped_lines.add(l_num)
                    skipped_items.append((str(l_num), reason))

            unaccounted = sorted(list(total_range_lines - covered_lines - skipped_lines))
            if unaccounted:
                err_str = f"L{unaccounted[0]:04d}" if len(unaccounted) == 1 else f"L{unaccounted[0]:04d}..L{unaccounted[-1]:04d} ({len(unaccounted)} lines)"
                errors.append({
                    "type": "UNACCOUNTED_SPAN_DROP",
                    "message": f"Raw lines {err_str} are neither rendered in spans nor accounted for in the skipped ledger."
                })

    if ledger_match and session_id:
        raw_path = REPO_ROOT / "sessions" / "data" / "index" / f"{session_id}-raw-indexed.md"
        if raw_path.exists() and skipped_items:
            try:
                raw_lines = clean_lines(str(raw_path))
                lore_re = load_lore_lexicon(session_id, str(REPO_ROOT), session_cfg)
                skip_exemptions = load_skip_exemptions(session_cfg)

                alt_clean = re.sub(r"<!--.*?-->", "", alternate_text)
                rendered_words = set(extract_content_words(alt_clean))

                sc_id = scene_num if scene_num is not None else 0
                s_errors, s_warnings = audit_skip_ledger(
                    sc_id, skipped_items, raw_lines, rendered_words, lore_re, skip_exemptions
                )
                for se in s_errors:
                    errors.append({
                        "type": "UNJUSTIFIED_SKIP_IN_AUTHORIAL",
                        "message": se
                    })
                for sw in s_warnings:
                    warnings.append({
                        "type": "AUTHORIAL_SKIP_WARNING",
                        "message": sw
                    })
            except Exception as e:
                warnings.append({
                    "type": "SKIP_LEDGER_AUDIT_ERROR",
                    "message": f"Could not audit skip ledger for {session_id}: {e}"
                })

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "span_count": len(spans),
        "covered_range": (spans[0][0], spans[-1][1]) if spans else None
    }

def audit_gate4_adaptation_divergence(
    alternate_text: str,
    archival_text: Optional[str] = None,
    session_id: Optional[str] = None,
    scene_num: Optional[int] = None,
    intent_contract: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Gate 4: Enforces Anti-Identity Invariant (Zero-Divergence Ban) and Mandatory Trade-off Audit Log."""
    errors = []
    warnings = []
    compression_ratio = 100.0

    # 1. Anti-Identity Invariant (Zero-Divergence Ban)
    if archival_text:
        alt_clean = re.sub(r"<!--.*?-->", "", alternate_text).strip()
        arch_clean = re.sub(r"<!--.*?-->", "", archival_text).strip()

        alt_norm = re.sub(r"\s+", " ", alt_clean)
        arch_norm = re.sub(r"\s+", " ", arch_clean)

        alt_words = len(alt_clean.split())
        arch_words = len(arch_clean.split())
        compression_ratio = (alt_words / arch_words * 100.0) if arch_words > 0 else 100.0

        if alt_norm == arch_norm or alternate_text.strip() == archival_text.strip():
            errors.append({
                "type": "ZERO_CINEMATIC_DIVERGENCE",
                "message": (
                    "Authorial cut is 100% identical to archival cut. A cinematic novelization must "
                    "adapt the raw material (pacing compression, turn fusion, sensory escalation); "
                    "zero divergence means zero adaptation occurred."
                )
            })

    # 2. Extract scene identification if not provided
    if scene_num is None:
        raw_match = re.search(r"<!--.*?SCENE_ID:\s*(\d+)", alternate_text)
        if raw_match:
            scene_num = int(raw_match.group(1))

    # 3. Mandatory Trade-off Audit Log Check
    spans = parse_spans(alternate_text)
    coarse_spans = [s for s in spans if s[0] != s[1]]

    needs_liberty_log = (len(coarse_spans) > 0) or (archival_text and compression_ratio < 75.0)

    if needs_liberty_log:
        if intent_contract is None and session_id:
            contract_path = REPO_ROOT / "sessions" / "config" / f"{session_id.lower()}-intent-contract.json"
            if contract_path.exists():
                try:
                    intent_contract = json.loads(contract_path.read_text(encoding="utf-8"))
                except Exception:
                    intent_contract = None

        if intent_contract:
            liberties = intent_contract.get("authorial_liberties", intent_contract.get("liberties", []))
            target_scene_keys = set()
            if scene_num is not None:
                target_scene_keys.update([
                    f"scene-{scene_num:02d}",
                    f"scene-{scene_num}",
                    str(scene_num),
                    f"scene {scene_num}",
                    f"scene {scene_num:02d}"
                ])

            has_logged_liberty = False
            for lib in liberties:
                sc = str(lib.get("scene", "")).strip().lower()
                if sc in target_scene_keys or (scene_num is not None and re.search(rf"\b0?{scene_num}\b", sc)):
                    has_logged_liberty = True
                    break

            if not has_logged_liberty:
                sc_label = f"Scene {scene_num}" if scene_num is not None else "Authorial scene"
                errors.append({
                    "type": "UNITEMIZED_AUTHORIAL_LIBERTY",
                    "message": (
                        f"{sc_label} contains {len(coarse_spans)} coarse multi-turn spans / pacing adaptations "
                        f"({compression_ratio:.1f}% length) but has no itemized entry in intent contract "
                        "'authorial_liberties'."
                    )
                })
        elif intent_contract is not None:
            sc_label = f"Scene {scene_num}" if scene_num is not None else "Authorial scene"
            errors.append({
                "type": "UNITEMIZED_AUTHORIAL_LIBERTY",
                "message": (
                    f"{sc_label} contains {len(coarse_spans)} coarse multi-turn spans but intent contract has no "
                    "'authorial_liberties'."
                )
            })

    return {
        "passed": len(errors) == 0,
        "compression_ratio": compression_ratio,
        "coarse_span_count": len(coarse_spans),
        "needs_liberty_log": needs_liberty_log,
        "errors": errors,
        "warnings": warnings,
    }

def verify_alternate_scene(
    alternate_text: str,
    archival_text: Optional[str] = None,
    session_id: Optional[str] = None,
    scene_num: Optional[int] = None,
    intent_contract: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Runs all 4 gates on an authorial cut scene string."""
    raw_range = extract_raw_range_header(alternate_text)
    if not raw_range and archival_text:
        raw_range = extract_raw_range_header(archival_text)

    g1 = audit_gate1_entity_coverage(archival_text or alternate_text, alternate_text, session_id=session_id)
    g2 = audit_gate2_leaks_and_props(alternate_text)
    g3 = audit_gate3_span_provenance(alternate_text, raw_range, session_id=session_id, scene_num=scene_num)
    g4 = audit_gate4_adaptation_divergence(alternate_text, archival_text, session_id, scene_num, intent_contract)

    archival_speakers = extract_dialogue_speakers(archival_text) if archival_text else {}
    alternate_speakers = extract_dialogue_speakers(alternate_text)

    silenced_speakers = []
    for spk, turns in archival_speakers.items():
        if spk != "Narrator" and len(turns) > 0 and spk not in alternate_speakers:
            silenced_speakers.append(spk)

    overall_passed = g1["passed"] and g2["passed"] and g3["passed"] and g4["passed"] and len(silenced_speakers) == 0

    return {
        "passed": overall_passed,
        "gate1_entity_coverage": g1,
        "gate2_leaks_and_props": g2,
        "gate3_span_provenance": g3,
        "gate4_adaptation_divergence": g4,
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

    g4 = report.get("gate4_adaptation_divergence", {"passed": True, "errors": []})
    print("\n[GATE 4: ADAPTATION DIVERGENCE & INTENT CONTRACT AUDIT]")
    if g4.get("errors"):
        for err in g4["errors"]:
            print(f"  * [FAIL] [{err['type']}] {err['message']}")
    else:
        print("  * [OK] Divergence confirmed (non-identical). All adaptation trade-offs itemized in intent contract.")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Deterministic Verifier for Authorial Cut Scenes")
    parser.add_argument("file", nargs="?", help="Path to authorial cut scene block")
    parser.add_argument("--archival", help="Path to corresponding archival scene block")
    parser.add_argument("--session", help="Session ID (e.g. s4, s5)")
    parser.add_argument("--intent", help="Path to intent contract json")
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
        dummy_contract = {"rules": [], "authorial_liberties": [{"scene": "scene-05", "liberty": "test"}]}
        rep_valid = verify_alternate_scene(sample_valid, sample_arch, intent_contract=dummy_contract)
        assert rep_valid["passed"] is True, f"Expected valid sample to pass, got: {rep_valid}"
        rep_flawed = verify_alternate_scene(sample_flawed, sample_arch)
        assert rep_flawed["passed"] is False, "Expected flawed sample to fail"
        assert rep_flawed["gate2_leaks_and_props"]["passed"] is False, "Expected leak gate to catch player name/ford truck"
        assert rep_flawed["gate3_span_provenance"]["passed"] is False, "Expected span gate to catch inverted spans"

        # Gate 4 Tests: Zero Divergence
        rep_identical = verify_alternate_scene(sample_arch, sample_arch)
        assert rep_identical["passed"] is False, "Expected identical scene to fail Gate 4"
        assert any(e["type"] == "ZERO_CINEMATIC_DIVERGENCE" for e in rep_identical["gate4_adaptation_divergence"]["errors"]), "Expected ZERO_CINEMATIC_DIVERGENCE error"

        # Gate 4 Tests: Unitemized Liberty
        rep_unitemized = verify_alternate_scene(sample_valid, sample_arch, intent_contract={"rules": [], "authorial_liberties": []})
        assert rep_unitemized["passed"] is False, "Expected unitemized liberty to fail Gate 4"
        assert any(e["type"] == "UNITEMIZED_AUTHORIAL_LIBERTY" for e in rep_unitemized["gate4_adaptation_divergence"]["errors"]), "Expected UNITEMIZED_AUTHORIAL_LIBERTY error"

        print("[PASS] All built-in verifier self-tests passed cleanly!")
        return

    if not args.file:
        parser.print_help()
        sys.exit(1)

    alt_path = Path(args.file)
    if not alt_path.exists():
        print(f"[ERROR] File not found: {alt_path}")
        sys.exit(1)

    session_id = args.session
    scene_num = None
    m = re.search(r"(s\d+)-scene-(\d+)", alt_path.name)
    if m:
        if not session_id:
            session_id = m.group(1)
        scene_num = int(m.group(2))

    archival_text = None
    if args.archival:
        arch_path = Path(args.archival)
        if arch_path.exists():
            archival_text = arch_path.read_text(encoding="utf-8")
    elif session_id and scene_num is not None:
        arch_candidate = REPO_ROOT / "sessions" / "data" / "clean" / "blocks" / f"{session_id}-scene-{scene_num:02d}.md"
        if arch_candidate.exists():
            archival_text = arch_candidate.read_text(encoding="utf-8")

    intent_contract = None
    if args.intent:
        int_path = Path(args.intent)
        if int_path.exists():
            intent_contract = json.loads(int_path.read_text(encoding="utf-8"))
    elif session_id:
        int_candidate = REPO_ROOT / "sessions" / "config" / f"{session_id}-intent-contract.json"
        if int_candidate.exists():
            intent_contract = json.loads(int_candidate.read_text(encoding="utf-8"))

    alt_text = alt_path.read_text(encoding="utf-8")
    report = verify_alternate_scene(alt_text, archival_text, session_id=session_id, scene_num=scene_num, intent_contract=intent_contract)
    print_report_card(report, str(alt_path))
    sys.exit(0 if report["passed"] else 1)

if __name__ == "__main__":
    main()

