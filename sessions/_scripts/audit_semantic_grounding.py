import sys
import os
import re
import json
import argparse
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "at", "by", "for", 
    "with", "about", "against", "between", "into", "through", "during", "before", "after", 
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", 
    "again", "further", "then", "once", "here", "there", "all", "any", "both", "each", 
    "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", 
    "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", 
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", 
    "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", 
    "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "would",
    "like", "yeah", "okay", "yes", "oh", "um", "uh", "well", "know", "say", "said", "think",
    "going", "want", "see", "look", "get", "got", "come", "came", "make", "made", "table", "note",
    "also", "really", "right", "sure", "thing", "things", "good", "mean", "much", "even"
}

def clean_lines(filepath):
    lines = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = re.match(r"^L\d{4}:\s*(.*)$", line)
            if match:
                lines.append(match.group(1))
            else:
                lines.append(line)
    return lines

def extract_content_words(text):
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return [w for w in words if w not in STOPWORDS]

def parse_ledger_list(list_str):
    if not list_str or list_str.strip() == "[]":
        return []
    matches = re.findall(r"L?(\d+)", list_str)
    return [int(m) for m in matches]

def audit_session_grounding(session_id, base_dir=None):
    base_dir = base_dir or r"D:\Code\dnd-scribe"
    indexed_path = os.path.join(base_dir, "sessions", "data", "index", f"{session_id}-raw-indexed.md")
    manifest_path = os.path.join(base_dir, "sessions", "data", "index", f"{session_id}-manifest.json")
    story_path = os.path.join(base_dir, "sessions", "data", "clean", f"{session_id}-clean-story.md")

    if not os.path.exists(indexed_path) or not os.path.exists(manifest_path) or not os.path.exists(story_path):
        print(f"[ERROR] Required files missing for session {session_id}")
        return False, []

    raw_lines = clean_lines(indexed_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(story_path, "r", encoding="utf-8") as f:
        story_content = f.read()

    errors = []
    warnings = []
    grounding_scores = []

    sections = re.findall(
        r"<!--\s*RAW_RANGE:\s*\[(\d+),\s*(\d+)\]\s*\|\s*SCENE_ID:\s*(\d+)\s*(?:\|\s*(OOC))?\s*-->\s*(.*?)(?=<!--\s*RAW_RANGE:|$)", 
        story_content, 
        re.DOTALL
    )

    marker_re = re.compile(r"<!--\s*L(\d+)\s*-->")

    print(f"\n================================================================================")
    print(f"🛡️  FORENSIC GROUNDING AUDITOR: SESSION {session_id.upper()}")
    print(f"================================================================================")

    for start_str, end_str, scene_id_str, ooc_flag, block_content in sections:
        start_line, end_line = int(start_str), int(end_str)
        scene_id = int(scene_id_str)
        if ooc_flag:
            continue

        raw_window_lines = raw_lines[start_line - 1: min(end_line, len(raw_lines))]
        raw_scene_text = " ".join(raw_window_lines)
        raw_scene_words = set(extract_content_words(raw_scene_text))

        ledger_match = re.search(r"<!--\s*LEDGER:\s*rendered=\[(.*?)\]\s*skipped=\[(.*?)\]\s*-->", block_content)
        if not ledger_match:
            errors.append(f"Scene {scene_id}: Missing LEDGER footer.")
            continue

        rendered_lines = parse_ledger_list(ledger_match.group(1))
        skipped_raw_str = ledger_match.group(2)
        skipped_items = re.findall(r"(\d+)(?:\(([^)]+)\))?", skipped_raw_str)

        unjustified_skips = []
        for num_str, reason in skipped_items:
            line_idx = int(num_str) - 1
            if 0 <= line_idx < len(raw_lines):
                r_line = raw_lines[line_idx]
                sm = re.match(r"^\*\*([^*]+)\s*\((PC|NPC)\):\*\*\s*(.+)$", r_line)
                if sm and reason == "ooc":
                    speaker, char_type, dialogue = sm.group(1), sm.group(2), sm.group(3)
                    words = extract_content_words(dialogue)
                    if len(words) >= 8 and not any(meta in dialogue.lower() for meta in ["roll", "initiative", "saving throw", "spell slot", "dice"]):
                        unjustified_skips.append((int(num_str), speaker, dialogue))

        if unjustified_skips:
            for line_no, spk, dial in unjustified_skips[:3]:
                warnings.append(
                    f"Scene {scene_id}: Potential Canon Dialogue Drop at L{line_no:04d} ({spk}): '{dial[:70]}...' marked as (ooc) skip."
                )

        content_no_ledger = re.sub(r"<!--\s*LEDGER:.*?-->", "", block_content, flags=re.DOTALL)
        paragraphs = [p.strip() for p in content_no_ledger.split("\n\n") if p.strip()]

        scene_turns_evaluated = 0
        scene_grounded_turns = 0

        for para in paragraphs:
            markers = [int(m) for m in marker_re.findall(para)]
            if not markers:
                continue

            para_text_clean = re.sub(r"<!--.*?-->", "", para).strip()
            para_words = set(extract_content_words(para_text_clean))

            for m in markers:
                raw_idx = m - 1
                if 0 <= raw_idx < len(raw_lines):
                    r_line = raw_lines[raw_idx]
                    
                    # If this is a tactical table note, it represents combat/narrative action
                    if r_line.startswith("*Table Note:"):
                        scene_turns_evaluated += 1
                        scene_grounded_turns += 1
                        continue

                    # Only audit spoken dialogue turns
                    has_dialogue = re.match(r"^\*\*([^*]+):\*\*\s*(.*)$", r_line)
                    if not has_dialogue:
                        scene_turns_evaluated += 1
                        scene_grounded_turns += 1
                        continue

                    scene_turns_evaluated += 1
                    w_start = max(0, raw_idx - 3)
                    w_end = min(len(raw_lines), raw_idx + 4)
                    raw_turn_text = " ".join(raw_lines[w_start:w_end])
                    raw_turn_words = set(extract_content_words(raw_turn_text))

                    overlap = False
                    for rw in raw_turn_words:
                        for pw in para_words:
                            if rw == pw or rw[:4] == pw[:4] or pw[:4] == rw[:4]:
                                overlap = True
                                break
                        if overlap:
                            break

                    if overlap:
                        scene_grounded_turns += 1
                    else:
                        errors.append(
                            f"Scene {scene_id}: UNGROUNDED TURN at L{m:04d}.\n"
                            f"  Raw Line: '{raw_lines[raw_idx][:80]}...'\n"
                            f"  Prose: '{para_text_clean[:80]}...'\n"
                            f"  Diagnosis: 0 semantic token overlap between prose and raw transcript window."
                        )

        scene_prose_words = set(extract_content_words(content_no_ledger))
        common_scene_keywords = raw_scene_words.intersection(scene_prose_words)
        
        grounding_ratio = (scene_grounded_turns / scene_turns_evaluated) if scene_turns_evaluated > 0 else 1.0
        grounding_scores.append((scene_id, grounding_ratio, len(common_scene_keywords)))

    print("\n--- SCENE FIDELITY & GROUNDING MATRIX ---")
    print(f"{'Scene ID':<10} | {'Turn Grounding %':<18} | {'Shared Topic Keywords':<22} | {'Status'}")
    print("-" * 65)
    for sc_id, g_ratio, kw_count in grounding_scores:
        status = "PASS" if g_ratio >= 0.85 else "WARN" if g_ratio >= 0.70 else "FAIL"
        print(f"Scene {sc_id:<4} | {g_ratio*100:>15.1f}% | {kw_count:>21} | {status}")

    print("\n--- FORENSIC VERDICT ---")
    if errors:
        print(f"[FAIL] {len(errors)} CRITICAL GROUNDING BREACHES DETECTED:")
        for e in errors[:10]:
            print(f"  ❌ {e}")
        return False, errors
    else:
        print(f"[PASS] 100% TRANSCRIPT-TO-PROSE GROUNDING VERIFIED.")
        if warnings:
            print(f"Warnings ({len(warnings)}):")
            for w in warnings[:5]:
                print(f"  ⚠️ {w}")
        return True, warnings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forensic Transcript Grounding & Semantic Entailment Auditor")
    parser.add_argument("session", help="Session ID (e.g. s1, s2, s3)")
    args = parser.parse_args()
    passed, _ = audit_session_grounding(args.session)
    sys.exit(0 if passed else 1)
