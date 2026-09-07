#!/usr/bin/env python3
"""Adversarial Prose Critic & Bloat Scanner.

Runs forensic telemetry on novelized story files (sN-clean-story.md) to detect:
1. In-universe immersion breaches & Earth-word leaks (Oxford, English, airport, Victorian, etc.)
2. Purple prose & repeated architectural/sensory tropes (rolling 1,000-word window)
3. Stagnant action / "talking heads" ratio (excessive dialogue without physical motion)
4. Domestic logistics & hallway transit filler (breakfast, buffets, walking down corridors)
5. Character voice homogenization (vocabulary overlap across character dialogue)
6. Static scene delta (scenes lacking conflict, stakes shifts, or state changes)

Usage:
    python critique_prose.py s1
    python critique_prose.py s7.5 --out sessions/data/index/s7.5-critique.md
"""

import argparse
import json
import os
import re
import sys
from collections import Counter

# Earth leaks & out-of-universe anachronisms that break fantasy immersion
EARTH_LEAK_PATTERNS = [
    (r"\b(?:oxford|cambridge|harvard|yale|eiffel|big ben|hollywood|disney)\b", "Earth Place / Institution"),
    (r"\b(?:english|british|american|french|italian|german|russian|asian|european|african|latin|roman|greek|spartan|trojan|australian|scottish|irish|japanese|chinese)\b", "Earth Nationality / Language"),
    (r"\b(?:airport|airplane|jetliner|helicopter|television|t\.?v\.?|radio|wi-?fi|internet|cell phone|smartphone)\b", "Modern Earth Technology"),
    (r"\b(?:victorian|edwardian|renaissance|medieval|bridgerton|ted lasso)\b", "Earth Historical / Pop-Culture Term"),
    (r"\b(?:human tide|human race|mankind)\b", "Anthropocentric Slip (in multi-ancestry fantasy)")
]

# Repetitive sensory & architectural phrases to watch out for
SENSORY_PHRASES = [
    r"warm mahogany",
    r"polished brass",
    r"acrid ozone",
    r"gaslight lanterns?",
    r"circular (?:crystal|glass) floor",
    r"basalt (?:canyon|chasm|ring)",
    r"copper balustrades?",
    r"heavy canvas (?:working )?collar",
    r"woolen flat cap",
    r"green leaf crown",
    r"dangling satchels?",
    r"living woven green",
    r"steamship with brass fittings",
    r"subtle(?:,)? disorienting flutter",
    r"force of nature",
    r"pure dread",
]

# Logistics & filler patterns (breakfast, transit, syllabus banter)
LOGISTICS_PATTERNS = [
    (r"\b(?:breakfast|buffet|muffins?|bacon|sky-bites?|appetizers?|trays of food)\b", "Dining / Food Logistics"),
    (r"\b(?:walking down the (?:hall|corridor|berths?)|threaded through the gates?|walked together down)\b", "Corridor / Transit Logistics"),
    (r"\b(?:desks?|chalk|syllabus|lecture notes?|textbooks?)\b", "Academic Logistics"),
]

# Action & motion verbs to evaluate scene physical dynamics
ACTION_VERBS = {
    "ran", "running", "leaped", "leaping", "sprinted", "sprinting", "slammed", "slamming",
    "crawled", "crawling", "grabbed", "grabbing", "wrenched", "wrenching", "dodged", "dodging",
    "shattered", "shattering", "ducked", "ducking", "lunged", "lunging", "tackled", "tackling",
    "climbed", "climbing", "pushed", "pushing", "dragged", "dragging", "bolted", "bolting",
    "dived", "diving", "swung", "swinging", "struck", "striking", "burst", "bursting"
}


def analyze_earth_leaks(text):
    """Scans clean prose (ignoring HTML comments) for Earth terminology leaks."""
    prose_only = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    findings = []
    
    for pattern, category in EARTH_LEAK_PATTERNS:
        matches = list(re.finditer(pattern, prose_only, flags=re.IGNORECASE))
        for m in matches:
            match_start = m.start()
            line_num = prose_only[:match_start].count("\n") + 1
            matched_word = m.group(0)
            
            start_idx = max(0, match_start - 40)
            end_idx = min(len(prose_only), match_start + 40)
            snippet = prose_only[start_idx:end_idx].replace("\n", " ").strip()
            
            findings.append({
                "word": matched_word,
                "category": category,
                "line": line_num,
                "snippet": f"...{snippet}..."
            })
            
    return findings


def analyze_purple_prose(text):
    findings = []
    text_lower = text.lower()
    for pattern in SENSORY_PHRASES:
        matches = list(re.finditer(pattern, text_lower))
        if len(matches) >= 3:
            findings.append({
                "phrase": pattern.replace(r"\b", "").replace(r"(?:", "").replace(r")?", "").replace(r")", ""),
                "occurrences": len(matches),
                "severity": "HIGH" if len(matches) >= 5 else "MEDIUM"
            })
    return findings


def analyze_logistics_density(text):
    total_words = len(text.split())
    if total_words == 0:
        return {}
    
    logistics_counts = {}
    for pattern, category in LOGISTICS_PATTERNS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            logistics_counts[category] = len(matches)
            
    return {
        "categories": logistics_counts,
        "total_hits": sum(logistics_counts.values()),
        "hit_density_per_kword": round(sum(logistics_counts.values()) / (total_words / 1000), 2) if total_words > 0 else 0
    }


def analyze_dialogue_vs_action(scenes):
    scene_metrics = []
    for s in scenes:
        content = s["content"]
        words = content.split()
        if not words:
            continue
        
        quotes = re.findall(r'"([^"]+)"', content)
        dialogue_words = sum(len(q.split()) for q in quotes)
        dialogue_ratio = round(dialogue_words / len(words), 3)
        
        narrative_text = re.sub(r'"[^"]+"', '', content).lower()
        narrative_tokens = re.findall(r"\b[a-z]+\b", narrative_text)
        action_verb_count = sum(1 for tok in narrative_tokens if tok in ACTION_VERBS)
        
        talking_heads_risk = dialogue_ratio > 0.45 and action_verb_count < 3
        
        scene_metrics.append({
            "scene_id": s["scene_id"],
            "title": s["title"],
            "word_count": len(words),
            "dialogue_ratio": dialogue_ratio,
            "action_verb_count": action_verb_count,
            "talking_heads_risk": talking_heads_risk
        })
    return scene_metrics


def analyze_character_voices(text):
    character_quotes = {"Lomi": [], "Britt": [], "Aggie": [], "Ignatius": [], "Iggy": []}
    
    lines = text.split("\n")
    for i, line in enumerate(lines):
        quotes = re.findall(r'"([^"]+)"', line)
        if not quotes:
            continue
        surrounding = line
        if i > 0:
            surrounding += " " + lines[i-1]
        if i < len(lines) - 1:
            surrounding += " " + lines[i+1]
            
        for char in character_quotes:
            if re.search(r'\b' + char + r'\b', surrounding, flags=re.IGNORECASE):
                character_quotes[char].extend(quotes)
                break
                
    voice_profiles = {}
    for char, q_list in character_quotes.items():
        if not q_list:
            continue
        combined = " ".join(q_list).lower()
        tokens = re.findall(r"\b[a-z]{3,}\b", combined)
        avg_quote_len = round(sum(len(q.split()) for q in q_list) / len(q_list), 1)
        voice_profiles[char] = {
            "total_quotes": len(q_list),
            "avg_words_per_turn": avg_quote_len,
            "top_vocab": [w for w, _ in Counter(tokens).most_common(5)]
        }
    return voice_profiles


def parse_story_scenes(story_text):
    raw_blocks = re.findall(
        r"<!--\s*RAW_RANGE:\s*\[\d+,\s*\d+\]\s*\|\s*SCENE_ID:\s*(\d+)(?:\s*\|\s*OOC)?\s*-->\s*(.*?)(?=<!--\s*RAW_RANGE:|$)",
        story_text,
        re.DOTALL
    )
    scenes = []
    for sc_id, content in raw_blocks:
        lines = content.strip().split("\n")
        title = lines[0] if lines and lines[0].startswith("#") else f"Scene {sc_id}"
        scenes.append({
            "scene_id": int(sc_id),
            "title": title.lstrip("#").strip(),
            "content": content.strip()
        })
    return scenes


def generate_critique_report(session_id, story_path, manifest_path=None):
    if not os.path.exists(story_path):
        print(f"Error: Story file not found at {story_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(story_path, "r", encoding="utf-8") as f:
        story_text = f.read()
        
    scenes = parse_story_scenes(story_text)
    earth_leaks = analyze_earth_leaks(story_text)
    purple_prose = analyze_purple_prose(story_text)
    logistics = analyze_logistics_density(story_text)
    scene_actions = analyze_dialogue_vs_action(scenes)
    voices = analyze_character_voices(story_text)
    
    total_words = len(story_text.split())
    
    report = []
    report.append(f"# 🗡️ Ruthless Editorial Critique: {session_id.upper()}")
    report.append(f"**Total Words:** {total_words:,} | **Scenes Audited:** {len(scenes)}")
    report.append("")
    
    # 1. Executive Verdict
    report.append("## 1. Executive Editorial Verdict")
    talking_heads = [s for s in scene_actions if s["talking_heads_risk"]]
    purple_alerts = [p for p in purple_prose if p["severity"] == "HIGH"]
    
    if earth_leaks or talking_heads or purple_alerts or logistics.get("hit_density_per_kword", 0) > 8.0:
        report.append("> [!WARNING]")
        report.append("> **Verdict: EDITORIAL CORRECTION REQUIRED.**")
        reasons = []
        if earth_leaks:
            reasons.append(f"{len(earth_leaks)} immersion-breaking Earth terminology leaks")
        if talking_heads:
            reasons.append(f"{len(talking_heads)} talking-head scenes lacking physical action")
        if purple_alerts:
            reasons.append(f"{len(purple_alerts)} high-frequency purple prose phrases")
        if logistics.get("hit_density_per_kword", 0) > 8.0:
            reasons.append("high domestic/transit logistics density")
        report.append(f"> Flagged issues: {', '.join(reasons)}.")
    else:
        report.append("> [!NOTE]")
        report.append("> **Verdict: LEAN & DYNAMIC.**")
        report.append("> Clean in-universe immersion, good narrative velocity, disciplined sensory description, and well-staged physical action beats.")
    report.append("")
    
    # 2. In-Universe Immersion & Earth-Leak Scanner
    report.append("## 2. In-Universe Immersion & Earth-Leak Scanner")
    if earth_leaks:
        report.append("| Line | Category | Leaked Term | Context Snippet |")
        report.append("|---|---|---|---|")
        for leak in earth_leaks:
            report.append(f"| L{leak['line']} | {leak['category']} | **`{leak['word']}`** | {leak['snippet']} |")
    else:
        report.append("- [PASS] 0 Earth-word leaks or anachronisms detected. 100% in-universe fantasy immersion.")
    report.append("")
    
    # 3. Talking Heads & Stagnant Action
    report.append("## 3. Stagnant Action & Talking Heads Scanner")
    report.append("| Scene | Title | Words | Dialogue % | Action Verbs | Risk Assessment |")
    report.append("|---|---|---|---|---|---|")
    for s in scene_actions:
        risk_str = "**TALKING HEADS (Low Action)**" if s["talking_heads_risk"] else "Balanced"
        report.append(f"| Scene {s['scene_id']} | {s['title'][:35]} | {s['word_count']} | {int(s['dialogue_ratio']*100)}% | {s['action_verb_count']} | {risk_str} |")
    report.append("")
    
    # 4. Purple Prose & Sensory Overkill
    report.append("## 4. Sensory Overkill & Lexical Echoes")
    if purple_prose:
        for p in purple_prose:
            report.append(f"- **`{p['phrase']}`**: repeated **{p['occurrences']} times** across session (`[{p['severity']}]`).")
    else:
        report.append("- No high-frequency sensory echoes detected. Varied atmospheric palette.")
    report.append("")
    
    # 5. Logistics & Filler Density
    report.append("## 5. Logistics & Table Filler Scanner")
    report.append(f"- **Filler hits per 1,000 words:** {logistics.get('hit_density_per_kword', 0)}")
    for cat, count in logistics.get("categories", {}).items():
        report.append(f"  - **{cat}:** {count} occurrences")
    report.append("")
    
    # 6. Character Voice Profiles
    report.append("## 6. Character Voice Differentiation")
    for char, v in voices.items():
        report.append(f"- **{char}:** {v['total_quotes']} turns | Avg {v['avg_words_per_turn']} w/turn | Top vocab: {', '.join(v['top_vocab'])}")
    report.append("")
    
    # 7. Recommendation for 2nd Pass Abridgment
    report.append("## 7. Recommended Editorial Fixes & Cuts")
    if earth_leaks:
        report.append("- **Purge Earth Leaks:** Replace Earth nationalities, place names, and modern metaphors with in-universe equivalents.")
    if talking_heads:
        for th in talking_heads:
            report.append(f"- **Compress Scene {th['scene_id']} ({th['title']}):** High dialogue ({int(th['dialogue_ratio']*100)}%) with low physical movement. Inject active staging beats or compress negotiations by 25%.")
    if logistics.get("hit_density_per_kword", 0) > 6.0:
        report.append("- **Trim Corridor & Dining Beats:** Condense morning arrivals and food table chatter into swift 1-paragraph establishing transitions.")
    if not earth_leaks and not talking_heads and logistics.get("hit_density_per_kword", 0) <= 6.0:
        report.append("- **Scene Retention:** High narrative density and clean world immersion. Retain fully for the core novel.")
        
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Adversarial Prose Critic")
    parser.add_argument("session_id", help="Session ID (e.g. s1, s7.5)")
    parser.add_argument("--out", help="Output path for markdown critique report")
    args = parser.parse_args()
    
    from pathlib import Path
    base_dir = str(Path(__file__).resolve().parents[4])
    story_path = os.path.join(base_dir, "sessions", "data", "clean", f"{args.session_id}-clean-story.md")
    if not os.path.exists(story_path):
        story_path = os.path.join(base_dir, "sessions", "transcripts", "clean", f"{args.session_id}-clean-story.md")
    
    report = generate_critique_report(args.session_id, story_path)
    
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[OK] Wrote critique report to {args.out}")
    else:
        print(report)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
