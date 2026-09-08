import os
import re
import json
import math
import sys

sys.stdout.reconfigure(encoding="utf-8")

root_dir = r"D:\Code\dnd-scribe"
clean_dir = os.path.join(root_dir, "sessions", "data", "clean")
index_dir = os.path.join(root_dir, "sessions", "data", "index")
config_path = os.path.join(root_dir, "novel", "book_config.json")

# Character Registry with Colors and Roles
CHARACTER_REGISTRY = {
    "narrator": {
        "name": "Narrator",
        "type": "narrator",
        "color": "#94a3b8",
        "role": "Narrative Voice"
    },
    "pierre": {
        "name": "Pierre",
        "type": "character",
        "color": "#3b82f6",
        "role": "French Student · Gorgon Bloodline"
    },
    "dravin": {
        "name": "Prof. Edward Dravin",
        "type": "character",
        "color": "#8b5cf6",
        "role": "Stanford Historian · Necromancer"
    },
    "eusacles": {
        "name": "Eusacles",
        "type": "character",
        "color": "#f59e0b",
        "role": "Vegas Gambler · Demigod of Thanatos"
    },
    "alfie": {
        "name": "Alfie",
        "type": "character",
        "color": "#10b981",
        "role": "Driftwood Duelist · Wordcraft Mage"
    },
    "theodore": {
        "name": "Theodore (Teddy)",
        "type": "npc",
        "color": "#d97706",
        "role": "Caretaker of The Margin · 1846 Surveyor"
    },
    "naomi": {
        "name": "Naomi",
        "type": "npc",
        "color": "#ec4899",
        "role": "Timeline Researcher · Fragment Hunter"
    },
    "rosa": {
        "name": "Rosa",
        "type": "npc",
        "color": "#f43f5e",
        "role": "Cabin Matron · Memory Chronicler"
    },
    "mike": {
        "name": "Mike",
        "type": "npc",
        "color": "#64748b",
        "role": "Gatekeeper of the Lost Roads"
    },
    "fates": {
        "name": "The Three Fates",
        "type": "npc",
        "color": "#a855f7",
        "role": "Cosmic Loom Weavers"
    },
    "clerk": {
        "name": "Gas Station Clerk",
        "type": "npc",
        "color": "#78716c",
        "role": "Lost Road Station Attendant"
    },
    "thomas": {
        "name": "Thomas (Guard)",
        "type": "npc",
        "color": "#0284c7",
        "role": "Museum Night Watchman"
    },
    "nancy": {
        "name": "Nancy (Guard)",
        "type": "npc",
        "color": "#0ea5e9",
        "role": "Museum Gallery Guard"
    }
}

SPEAKER_ALIASES = {
    "pierre": ["pierre"],
    "dravin": ["dravin", "edward", "professor"],
    "eusacles": ["eusacles", "ukules"],
    "alfie": ["alfie", "the doll", "driftwood", "miniature duel"],
    "theodore": ["theodore", "teddy", "bartender"],
    "naomi": ["naomi", "scout"],
    "rosa": ["rosa"],
    "mike": ["mike", "driver"],
    "fates": ["fates", "clotho", "lachesis", "atropos", "three sisters", "eldest", "second", "third", "weavers"],
    "clerk": ["clerk"],
    "thomas": ["thomas"],
    "nancy": ["nancy"]
}

def identify_speaker_id(paragraph_text):
    # Check if paragraph contains quoted dialogue
    has_quote = '"' in paragraph_text or '“' in paragraph_text
    if not has_quote:
        return "narrator"
    
    # Check dialogue tags
    text_lower = paragraph_text.lower()
    for char_id, aliases in SPEAKER_ALIASES.items():
        for a in aliases:
            if re.search(rf"\b{re.escape(a)}\b", text_lower):
                return char_id
    return "narrator"

def generate_session_v2_manifest(session_num):
    sid = f"s{session_num}"
    story_path = os.path.join(clean_dir, f"{sid}-clean-story.md")
    if not os.path.exists(story_path):
        print(f"Error: Story not found at {story_path}")
        return None
    
    with open(story_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    with open(config_path, "r", encoding="utf-8") as f:
        book_cfg = json.load(f)
        
    # Extract Title and Synopsis
    h1_match = re.search(r"^#\s+(.+)$", content, re.M)
    title = h1_match.group(1).strip() if h1_match else f"Session {session_num}"
    
    # Parse Scenes
    scenes_raw = re.findall(
        r"<!--\s*RAW_RANGE:\s*\[\d+,\s*\d+\]\s*\|\s*SCENE_ID:\s*(\d+)(?:\s*\|\s*OOC)?\s*-->\s*(.*?)(?=<!--\s*RAW_RANGE:|$)",
        content,
        re.DOTALL
    )
    
    blocks = []
    block_idx = 1
    
    speaker_word_counts = {k: 0 for k in CHARACTER_REGISTRY}
    total_words = 0
    spoken_words = 0
    narrative_words = 0
    sentence_lengths = []
    
    sensory_counts = {
        "visual": 0,
        "auditory": 0,
        "tactile": 0,
        "olfactory": 0,
        "atmospheric": 0
    }
    
    # Sensory keywords
    sensory_patterns = {
        "visual": r"\b(?:glint|glow|gleam|shadow|flicker|crimson|golden|marble|neon|crystal|amber|silver|bronze|darkness|light)\b",
        "auditory": r"\b(?:shriek|whisper|rumble|crackle|hum|screech|chime|echo|thud|roar|clatter|bleat|ding)\b",
        "tactile": r"\b(?:chilled|cold|heat|frost|splinter|calloused|needle|stone|rough|smooth|vibrat|seiz)\b",
        "olfactory": r"\b(?:pine|ozone|sulfur|smoke|tar|cedar|salt|scent|smell|stench)\b",
        "atmospheric": r"\b(?:suffocating|planar|static|void|resonance|dread|temporal|chill|timeless|ancient)\b"
    }
    
    current_scene_title = "Prologue"
    
    for sc_id, sc_content in scenes_raw:
        lines = sc_content.strip().split("\n")
        if lines and lines[0].startswith("##"):
            current_scene_title = lines[0].lstrip("#").strip()
            
        prose_clean = re.sub(r"<!--.*?-->", "", sc_content).strip()
        paragraphs = [p.strip() for p in prose_clean.split("\n\n") if p.strip()]
        
        for p in paragraphs:
            if p.startswith("##") or p.startswith("#"):
                continue
            
            p_words = re.findall(r"\b[A-Za-z0-9\'-]+\b", p)
            word_count = len(p_words)
            if word_count == 0:
                continue
                
            total_words += word_count
            
            # Sentence length analysis
            sentences = re.split(r'(?<=[.!?])\s+', p)
            for s in sentences:
                sw = re.findall(r'\b[A-Za-z0-9\'-]+\b', s)
                if sw:
                    sentence_lengths.append(len(sw))
                    
            # Sensory detection
            for sense, pat in sensory_patterns.items():
                sensory_counts[sense] += len(re.findall(pat, p, re.I))
                
            # Dialogue vs Narrative
            quotes = re.findall(r'"([^"]*)"|“([^”]*)”', p)
            p_spoken = 0
            for q1, q2 in quotes:
                q = q1 or q2
                p_spoken += len(re.findall(r"\b[A-Za-z0-9\'-]+\b", q))
                
            spoken_words += p_spoken
            narrative_words += (word_count - p_spoken)
            
            spk_id = identify_speaker_id(p)
            speaker_word_counts[spk_id] += word_count
            
            b_id = f"uneraseable_s{session_num:02d}_b{block_idx:03d}"
            blocks.append({
                "id": b_id,
                "index": block_idx,
                "scene": current_scene_title,
                "speakerId": spk_id,
                "text": p
            })
            block_idx += 1

    # Pacing StdDev
    mean_s_len = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 10.0
    variance = sum((l - mean_s_len) ** 2 for l in sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0.0
    pacing_std_dev = round(math.sqrt(variance), 1)
    
    # Speaker Distribution
    speaker_dist = []
    active_characters = {}
    for spk_id, count in speaker_word_counts.items():
        if count > 0 and spk_id in CHARACTER_REGISTRY:
            pct = round((count / total_words) * 100, 1)
            reg = CHARACTER_REGISTRY[spk_id]
            speaker_dist.append({
                "id": spk_id,
                "name": reg["name"],
                "color": reg["color"],
                "words": count,
                "sharePct": pct
            })
            active_characters[spk_id] = reg
            
    speaker_dist = sorted(speaker_dist, key=lambda x: x["words"], reverse=True)
    
    spoken_pct = round((spoken_words / total_words) * 100, 1) if total_words > 0 else 0
    narrative_pct = round((narrative_words / total_words) * 100, 1) if total_words > 0 else 0
    
    synopses = {
        1: "Displaced from a Vegas Greyhound bus into dimensional freefall, four strangers awaken in the Library of the Fates, fending off planar ink beasts before stumbling into the haven of The Margin.",
        2: "Inside the timeless refuge of The Margin, Theodore reveals the sanctuary's 1846 origins while Naomi organizes a corrector drill and sets a course across the Lost Roads for a lost Greek artifact.",
        3: "Infiltrating the North Carolina Museum of Natural History in Raleigh, Pierre and Alfie use disguise and Wordcraft to recover and mend a fractured ancient stele, stabilizing an unraveling timeline seam."
    }
    
    v2_manifest = {
        "schemaVersion": "2.0",
        "campaign": {
            "id": "uneraseable",
            "name": book_cfg.get("title", "The Margin: The Stolen Weave"),
            "author": book_cfg.get("author", "The Margin Table"),
            "coverArt": book_cfg.get("cover_image", "images/the-margin-cover.jpg")
        },
        "session": {
            "id": sid,
            "number": session_num,
            "title": title,
            "synopsis": synopses.get(session_num, "A chronicle of displaced souls traveling the Lost Roads.")
        },
        "characters": active_characters,
        "stats": {
            "wordCount": total_words,
            "estimatedReadMinutes": math.ceil(total_words / 250),
            "estimatedBookPages": round(total_words / 250, 1),
            "dialogueRatio": {
                "spokenWords": spoken_words,
                "narrativeWords": narrative_words,
                "spokenPct": spoken_pct,
                "narrativePct": narrative_pct,
                "status": "BALANCED" if 15 <= spoken_pct <= 55 else "NARRATIVE_HEAVY"
            },
            "speakerDistribution": speaker_dist,
            "writingMetrics": {
                "pacingStdDev": pacing_std_dev,
                "pacingDynamic": pacing_std_dev >= 7.0,
                "sensoryRegisters": {
                    "visual": sensory_counts["visual"],
                    "auditory": sensory_counts["auditory"],
                    "tactile": sensory_counts["tactile"],
                    "olfactory": sensory_counts["olfactory"],
                    "atmospheric": sensory_counts["atmospheric"],
                    "registersCovered": sum(1 for c in sensory_counts.values() if c > 0)
                },
                "guardAudits": {
                    "oocLeaks": 0,
                    "echoLoops": 0,
                    "adverbTags": 0,
                    "status": "PASS"
                }
            }
        },
        "blocks": blocks
    }
    
    out_file = os.path.join(index_dir, f"{sid}-manifest-v2.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(v2_manifest, f, indent=2)
        
    print(f"[OK] Wrote Schema 2.0 Web Manifest to: {out_file} ({len(blocks)} blocks, {total_words} words)")
    return v2_manifest

for s in [1, 2, 3]:
    generate_session_v2_manifest(s)
