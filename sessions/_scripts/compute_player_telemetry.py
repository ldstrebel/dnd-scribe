#!/usr/bin/env python3
"""
Deterministic per-player telemetry from the immutable raw indexed transcript (DEC-037, Phase C0/C1).

Measures *only* what can be counted: words, turns, turn lengths and airtime share per
declared speaker. It produces NO grades, NO scores and NO judgments. Speaker identity comes
exclusively from the raw ``**Label:**`` of each line mapped through ``sN-session-config.json``
(Zero-Regex Dialogue Law / DEC-009: the label is parsed structurally, prose is never inspected).

Honesty rules:
  * Absent players (config ``absent_players``) are reported as ``no_data`` - never zero-filled.
  * Raw labels that are neither GM nor a declared player are reported as ``unmappedSpeakers``.
  * Declared shared mics are surfaced as a caveat because per-person attribution is then impure.
  * Scope is the *whole raw file*, including pre-game and table talk; it is airtime, not
    in-fiction spotlight.

Usage:  python sessions/_scripts/compute_player_telemetry.py s7
"""

import json
import os
import re
import statistics
import sys
from typing import Dict, List, Optional

ROW_RE = re.compile(r"^L(\d+):\s*\*\*(.+?):\*\*\s*(.*)$")
SHORT_TURN_WORDS = 3

SCHEMA = "playerTelemetry/1"
SCOPE = "full raw transcript incl. pre-game and table talk (airtime, not in-fiction spotlight)"


def _word_count(text: str) -> int:
    return len(text.split())


def compute_player_telemetry(raw_text: str, session_cfg: dict, session_id: str = "") -> dict:
    players: Dict[str, str] = session_cfg.get("players", {}) or {}
    absent: Dict[str, str] = session_cfg.get("absent_players", {}) or {}
    players = {lbl: ch for lbl, ch in players.items() if lbl not in absent}
    gm_cfg = session_cfg.get("game_master", {}) or {}
    gm_person = gm_cfg.get("person")
    shared_mics = session_cfg.get("shared_mics", {}) or {}

    turns: Dict[str, List[int]] = {}
    total_lines = 0
    for line in raw_text.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        total_lines += 1
        label = m.group(2).strip()
        turns.setdefault(label, []).append(_word_count(m.group(3)))

    all_words = sum(sum(v) for v in turns.values())
    player_words_total = sum(sum(turns.get(lbl, [])) for lbl in players)

    def _pct(n: int, d: int) -> Optional[float]:
        return round(100.0 * n / d, 1) if d else None

    def _stats(label: str) -> dict:
        t = turns.get(label, [])
        words = sum(t)
        return {
            "label": label,
            "words": words,
            "turns": len(t),
            "wordsPerTurn": round(words / len(t), 1) if t else None,
            "medianTurnWords": statistics.median(t) if t else None,
            "shortTurnPct": _pct(sum(1 for x in t if x <= SHORT_TURN_WORDS), len(t)),
            "sharePctOfAllWords": _pct(words, all_words),
        }

    player_rows = []
    for label, character in players.items():
        row = _stats(label)
        row["character"] = character
        row["status"] = "present" if row["turns"] else "declared_but_silent"
        row["sharePctOfPlayerWords"] = _pct(row["words"], player_words_total)
        player_rows.append(row)
    player_rows.sort(key=lambda r: r["words"], reverse=True)

    absent_rows = [{"label": lbl, "character": ch, "status": "no_data"} for lbl, ch in absent.items()]

    known = set(players) | set(absent) | ({gm_person} if gm_person else set())
    unmapped = [
        {"label": lbl, "words": sum(v), "turns": len(v)}
        for lbl, v in turns.items()
        if lbl not in known
    ]
    unmapped.sort(key=lambda r: r["words"], reverse=True)

    caveats = []
    if shared_mics:
        caveats.append("shared_mics declared: per-person attribution is impure for the listed labels")
    if unmapped:
        caveats.append("unmapped speaker labels present: airtime shares exclude them from player shares")
    if gm_person and gm_person not in turns:
        caveats.append("declared GM label never appears in raw transcript")

    gm_row = _stats(gm_person) if gm_person and gm_person in turns else None

    return {
        "schema": SCHEMA,
        "session": session_id,
        "scope": SCOPE,
        "rawRowsParsed": total_lines,
        "totalWords": all_words,
        "gm": gm_row,
        "players": player_rows,
        "absentPlayers": absent_rows,
        "unmappedSpeakers": unmapped,
        "sharedMics": shared_mics,
        "caveats": caveats,
    }


def load_and_compute(root_dir: str, session_num: int) -> Optional[dict]:
    sid = f"s{session_num}"
    raw_path = os.path.join(root_dir, "sessions", "data", "index", f"{sid}-raw-indexed.md")
    cfg_path = os.path.join(root_dir, "sessions", "config", f"{sid}-session-config.json")
    if not (os.path.exists(raw_path) and os.path.exists(cfg_path)):
        return None
    with open(raw_path, "r", encoding="utf-8") as f:
        raw = f.read()
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return compute_player_telemetry(raw, cfg, sid)


def main():
    if len(sys.argv) < 2:
        print("usage: compute_player_telemetry.py sN")
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    num = int(sys.argv[1].lower().lstrip("s"))
    result = load_and_compute(root, num)
    if result is None:
        print(f"No raw-indexed transcript or session config for s{num}")
        sys.exit(1)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
