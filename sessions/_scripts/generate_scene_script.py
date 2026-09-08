#!/usr/bin/env python3
"""
Multi-Voice Scene Script Generator (The Margin: The Stolen Weave)
----------------------------------------------------------------
Parses session manifests (e.g. s1-manifest-v2.json) and clean novelized story markdown,
decomposing every passage into sequential verbatim Narration and Dialogue voice segments
with character-specific voice models, ElevenLabs IDs, and phonetic TTS tuning.

Outputs:
  - Audio Manifest JSON: sessions/data/audio/s{N}-scene-script.json (and campaign/audio/s{N}/)
  - Screenplay / Production Voice Script: sessions/data/audio/s{N}-scene-script.md

Usage:
  python generate_scene_script.py --session 1
  python generate_scene_script.py --all
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Root Directories
DEFAULT_ROOT = Path("D:/Code/dnd-scribe")
INDEX_DIR = DEFAULT_ROOT / "sessions" / "data" / "index"
CLEAN_DIR = DEFAULT_ROOT / "sessions" / "data" / "clean"
AUDIO_DATA_DIR = DEFAULT_ROOT / "sessions" / "data" / "audio"
CAMPAIGN_AUDIO_DIR = DEFAULT_ROOT / "campaign" / "audio"

# Character Voice Model Registry for The Margin: The Stolen Weave
VOICE_REGISTRY = {
    "narrator": {
        "name": "Narrator",
        "type": "narrator",
        "voice_id": "onwK4e9ZLuTAKqWW03F9",  # George / Epic Narrator preset
        "model_id": "eleven_multilingual_v2",
        "tone": "Evocative, atmospheric urban fantasy narration with deliberate cinematic pacing",
        "stability": 0.55,
        "similarity_boost": 0.85,
        "style": 0.20
    },
    "pierre": {
        "name": "Pierre",
        "type": "character",
        "voice_id": "CYw3kZ02Hs0563khs1Fj",  # Dave / Young male with European warmth
        "model_id": "eleven_multilingual_v2",
        "tone": "Youthful French student, gentle accent, slight edge of Gorgon hiss when tense",
        "stability": 0.45,
        "similarity_boost": 0.80,
        "style": 0.35
    },
    "dravin": {
        "name": "Prof. Edward Dravin",
        "type": "character",
        "voice_id": "N2lVS1w4EtoT3dr4eOWO",  # Callum / Scholarly gravelly resonance
        "model_id": "eleven_multilingual_v2",
        "tone": "Distinguished Stanford professor, erudite, gravelly, intellectual composure masking dark necromantic resonance",
        "stability": 0.60,
        "similarity_boost": 0.82,
        "style": 0.25
    },
    "eusacles": {
        "name": "Eusacles",
        "type": "character",
        "voice_id": "TX3LPaxmHKxFdv7VOQHJ",  # Liam / Charming raspy quick-talking gambler
        "model_id": "eleven_multilingual_v2",
        "tone": "Charming, raspy Las Vegas cardshark, quick-talking swagger carrying the quiet chill of Thanatos",
        "stability": 0.40,
        "similarity_boost": 0.78,
        "style": 0.45
    },
    "alfie": {
        "name": "Alfie",
        "type": "character",
        "voice_id": "yoZ06aMxZJJ28mfd3POQ",  # Sam / Punchy raspy delivery
        "model_id": "eleven_multilingual_v2",
        "tone": "Sharp, energetic Cockney voice, high spirited, miniature driftwood duelist with a punchy delivery",
        "stability": 0.35,
        "similarity_boost": 0.85,
        "style": 0.50
    },
    "theodore": {
        "name": "Theodore (Teddy)",
        "type": "npc",
        "voice_id": "VR6AewLTigWG4xSOukaG",  # Arnold / Weathered grandfatherly frontiersman
        "model_id": "eleven_multilingual_v2",
        "tone": "Warm, weathered 19th-century frontier surveyor, patient, grandfatherly Margin caretaker",
        "stability": 0.65,
        "similarity_boost": 0.80,
        "style": 0.15
    },
    "naomi": {
        "name": "Naomi",
        "type": "npc",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Sarah / Crisp analytical female
        "model_id": "eleven_multilingual_v2",
        "tone": "Sharp, observant timeline investigator, quick and analytical",
        "stability": 0.50,
        "similarity_boost": 0.80,
        "style": 0.25
    },
    "rosa": {
        "name": "Rosa",
        "type": "npc",
        "voice_id": "ThT5KcBeYPX3keUQqHPh",  # Dorothy / Grounded matronly
        "model_id": "eleven_multilingual_v2",
        "tone": "Steadfast, nurturing cabin matron, grounded and protective",
        "stability": 0.60,
        "similarity_boost": 0.80,
        "style": 0.20
    },
    "fates": {
        "name": "The Three Fates",
        "type": "npc",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel / Ethereal calm triad
        "model_id": "eleven_multilingual_v2",
        "tone": "Ancient, ethereal, interlocking cosmic loom weavers with chilling certainty",
        "stability": 0.70,
        "similarity_boost": 0.85,
        "style": 0.10
    },
    "beast": {
        "name": "Shadow Beast",
        "type": "npc",
        "voice_id": "bIHbv24MWmeRgasZH58o",  # Will / Deep menacing guttural raspy
        "model_id": "eleven_multilingual_v2",
        "tone": "Guttural, raspy planar predator, voice layered with ink and tearing paper",
        "stability": 0.30,
        "similarity_boost": 0.85,
        "style": 0.60
    },
    "anchor": {
        "name": "News Anchor",
        "type": "npc",
        "voice_id": "ErXwobaYiN019PkySvjV",  # Antoni / Radio broadcast timbre
        "model_id": "eleven_multilingual_v2",
        "tone": "Monotone emergency radio broadcast timbre, slightly compressed AM filter",
        "stability": 0.75,
        "similarity_boost": 0.75,
        "style": 0.05
    },
    "passenger": {
        "name": "Bus Passenger",
        "type": "npc",
        "voice_id": "MF3mGyEYCl7XYWbV9V6O",  # Elli / Panicked shout
        "model_id": "eleven_multilingual_v2",
        "tone": "Frantic, breathless commuter yelling during sudden dimensional transition",
        "stability": 0.25,
        "similarity_boost": 0.75,
        "style": 0.70
    },
    "thomas": {
        "name": "Thomas (Guard)",
        "type": "npc",
        "voice_id": "ZQe5CZPfIWgwIDPjrhkn",  # James / Gruff night watchman
        "model_id": "eleven_multilingual_v2",
        "tone": "Alert, gruff museum night watchman, authoritative and startled",
        "stability": 0.50,
        "similarity_boost": 0.80,
        "style": 0.30
    },
    "nancy": {
        "name": "Nancy (Guard)",
        "type": "npc",
        "voice_id": "oWAxZDxUJAwQ20x1WMrq",  # Nicole / Crisp gallery security
        "model_id": "eleven_multilingual_v2",
        "tone": "Crisp museum gallery security officer",
        "stability": 0.55,
        "similarity_boost": 0.80,
        "style": 0.25
    },
    "clerk": {
        "name": "Gas Station Clerk",
        "type": "npc",
        "voice_id": "g5CIjZEefAph4nQFvHAz",  # Ethan / Tired laconic clerk
        "model_id": "eleven_multilingual_v2",
        "tone": "Tired, laconic attendant who has seen too many strange travelers",
        "stability": 0.60,
        "similarity_boost": 0.75,
        "style": 0.15
    },
    "mike": {
        "name": "Mike",
        "type": "npc",
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",  # George / Gatekeeper
        "model_id": "eleven_multilingual_v2",
        "tone": "Gatekeeper of the Lost Roads, calm and guarded",
        "stability": 0.55,
        "similarity_boost": 0.80,
        "style": 0.20
    }
}

# Phonetic Dictionary for Fantasy Proper Nouns & Setting Terms
GLOBAL_PHONETIC_MAP = {
    "Eusacles": "Yoo-suh-kleez",
    "Dravin": "Dray-vin",
    "Thanatos": "Than-uh-toss",
    "Aether": "Ether",
    "aether": "ether",
    "Gorgon": "Gor-gon",
    "gorgon": "gor-gon",
    "Moirai": "Moy-rye",
    "Clotho": "Kloh-thoh",
    "Lachesis": "Lak-uh-sis",
    "Atropos": "At-ruh-pos",
    "The Margin": "The Mar-jin",
    "Margin": "Mar-jin",
    "Stolen Weave": "Stolen Weev"
}

def apply_phonetics(text: str, speaker_id: str) -> str:
    """Generates pronunciation-optimized phonetic text for ElevenLabs speech synthesis."""
    tts_text = text
    for word, phonetic in GLOBAL_PHONETIC_MAP.items():
        pattern = r'(?<![A-Za-z0-9])' + re.escape(word) + r'(?![A-Za-z0-9])'
        tts_text = re.sub(pattern, phonetic, tts_text)
    return tts_text

def decompose_block_to_segments(block: dict, block_index: int, session_num: int) -> list:
    """
    Decomposes a single prose block into sequential Narration and Dialogue voice segments.
    Guarantee: Concatenating segment['text'] reproduces block['text'] verbatim 100%.
    """
    text = block.get("text", "")
    speaker_id = block.get("speakerId", "narrator").lower().strip()
    block_id = block.get("id", f"s{session_num:02d}_b{block_index:03d}")
    scene = block.get("scene", 1)

    matches = list(re.finditer(r'"([^"]+)"', text))
    if not matches:
        # Pure narration block
        tts = apply_phonetics(text, "narrator")
        voice_prof = VOICE_REGISTRY.get("narrator", {})
        return [{
            "segment_id": f"{block_id}_s01",
            "block_id": block_id,
            "block_index": block_index,
            "scene": scene,
            "speaker_id": "narrator",
            "speaker_name": voice_prof.get("name", "Narrator"),
            "segment_type": "narration",
            "voice_id": voice_prof.get("voice_id", "narrator_epic_cinematic"),
            "voice_profile": voice_prof,
            "text": text,
            "tts_text": tts
        }]

    segments = []
    curr = 0
    seg_idx = 1

    dialogue_spk_id = speaker_id if speaker_id != "narrator" else "alfie"
    dialogue_voice = VOICE_REGISTRY.get(dialogue_spk_id, VOICE_REGISTRY.get("narrator"))
    narr_voice = VOICE_REGISTRY.get("narrator")

    for m in matches:
        start, end = m.span()
        # Lead-in narration
        if start > curr:
            narr_text = text[curr:start]
            segments.append({
                "segment_id": f"{block_id}_s{seg_idx:02d}",
                "block_id": block_id,
                "block_index": block_index,
                "scene": scene,
                "speaker_id": "narrator",
                "speaker_name": narr_voice.get("name", "Narrator"),
                "segment_type": "narration",
                "voice_id": narr_voice.get("voice_id", "narrator_epic_cinematic"),
                "voice_profile": narr_voice,
                "text": narr_text,
                "tts_text": apply_phonetics(narr_text, "narrator")
            })
            seg_idx += 1

        # Spoken dialogue quote
        quote_text = text[start:end]
        segments.append({
            "segment_id": f"{block_id}_s{seg_idx:02d}",
            "block_id": block_id,
            "block_index": block_index,
            "scene": scene,
            "speaker_id": dialogue_spk_id,
            "speaker_name": dialogue_voice.get("name", dialogue_spk_id.title()),
            "segment_type": "dialogue",
            "voice_id": dialogue_voice.get("voice_id", "character_voice"),
            "voice_profile": dialogue_voice,
            "text": quote_text,
            "tts_text": apply_phonetics(quote_text, dialogue_spk_id)
        })
        seg_idx += 1
        curr = end

    # Trailing narration
    if curr < len(text):
        trailing_text = text[curr:]
        segments.append({
            "segment_id": f"{block_id}_s{seg_idx:02d}",
            "block_id": block_id,
            "block_index": block_index,
            "scene": scene,
            "speaker_id": "narrator",
            "speaker_name": narr_voice.get("name", "Narrator"),
            "segment_type": "narration",
            "voice_id": narr_voice.get("voice_id", "narrator_epic_cinematic"),
            "voice_profile": narr_voice,
            "text": trailing_text,
            "tts_text": apply_phonetics(trailing_text, "narrator")
        })

    return segments

def generate_session_script(session_num: int, output_dir: Path = None) -> dict:
    manifest_path = INDEX_DIR / f"s{session_num}-manifest-v2.json"
    if not manifest_path.exists():
        print(f"❌ Error: Manifest file not found: {manifest_path}")
        return {}

    print(f"\n=======================================================")
    print(f"🎬 Generating Scene Script for Session {session_num}")
    print(f"   Manifest: {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    blocks = manifest_data.get("blocks", [])
    print(f"   Loaded {len(blocks)} prose blocks")

    all_segments = []
    verbatim_errors = 0

    for idx, b in enumerate(blocks, 1):
        segs = decompose_block_to_segments(b, idx, session_num)
        # Parity check
        reconstructed = "".join(s["text"] for s in segs)
        if reconstructed != b.get("text", ""):
            print(f"⚠️ Parity Warning in block {b.get('id')}: Reconstructed text does not match!")
            verbatim_errors += 1
        all_segments.extend(segs)

    if verbatim_errors == 0:
        print(f"   ✅ Verbatim Parity Check Passed: 100% text match across all {len(blocks)} blocks!")
    else:
        print(f"   ❌ {verbatim_errors} parity errors detected!")

    dialogue_segs = [s for s in all_segments if s["segment_type"] == "dialogue"]
    narr_segs = [s for s in all_segments if s["segment_type"] == "narration"]

    # Speaker Breakdown
    speaker_counts = {}
    for s in all_segments:
        sp = s["speaker_name"]
        speaker_counts[sp] = speaker_counts.get(sp, 0) + 1

    print(f"   Total Voice Segments   : {len(all_segments)}")
    print(f"   Spoken Dialogue Lines  : {len(dialogue_segs)}")
    print(f"   Narrative Prose Beats  : {len(narr_segs)}")
    print(f"   Unique Voices Active   : {len(speaker_counts)}")

    # Build Output Payload
    script_payload = {
        "campaign": "The Margin: The Stolen Weave",
        "session": session_num,
        "totalBlocks": len(blocks),
        "totalSegments": len(all_segments),
        "dialogueSegments": len(dialogue_segs),
        "narrationSegments": len(narr_segs),
        "voiceCast": {
            sp_id: prof for sp_id, prof in VOICE_REGISTRY.items()
            if prof["name"] in speaker_counts
        },
        "speakerDistribution": speaker_counts,
        "segments": all_segments
    }

    # Save JSON Manifest
    target_dirs = [AUDIO_DATA_DIR, CAMPAIGN_AUDIO_DIR / f"s{session_num}"]
    if output_dir:
        target_dirs.append(output_dir)

    for out_d in target_dirs:
        out_d.mkdir(parents=True, exist_ok=True)
        json_path = out_d / f"s{session_num}-scene-script.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(script_payload, f, indent=2, ensure_ascii=False)
        print(f"   💾 Saved Audio JSON: {json_path}")

    # Generate Screenplay Markdown
    md_lines = [
        f"# THE MARGIN: THE STOLEN WEAVE",
        f"## Session {session_num} Multi-Voice Production Voice Script",
        "",
        f"> **Total Blocks:** {len(blocks)} | **Voice Segments:** {len(all_segments)} | **Dialogue:** {len(dialogue_segs)} | **Narration:** {len(narr_segs)}",
        "",
        "### 🎙️ Voice Cast Breakdown",
        "| Character / Role | Speaker Key | ElevenLabs Voice ID | Delivery Tone | Lines |",
        "|---|---|---|---|---|"
    ]

    for sp_name, count in sorted(speaker_counts.items(), key=lambda x: -x[1]):
        # find matching voice registry entry
        matching_prof = next((p for p in VOICE_REGISTRY.values() if p["name"] == sp_name), {})
        v_id = matching_prof.get("voice_id", "-")
        tone = matching_prof.get("tone", "-")
        sp_key = next((k for k, p in VOICE_REGISTRY.items() if p.get("name") == sp_name), sp_name.lower())
        md_lines.append(f"| **{sp_name}** | `{sp_key}` | `{v_id}` | {tone} | **{count}** |")

    md_lines.extend(["", "---", "", "### 🎬 Voice Script (Sequential Production Order)", ""])

    curr_scene = None
    for s in all_segments:
        if s["scene"] != curr_scene:
            curr_scene = s["scene"]
            md_lines.append(f"\n#### 📍 SCENE {curr_scene}\n")

        clean_text = s["text"].strip()
        if s["segment_type"] == "dialogue":
            # Strip quotes for clean screenplay dialogue
            quote_stripped = clean_text.strip('"').strip('“').strip('”')
            md_lines.append(f"**[{s['speaker_name'].upper()}]** `({s['segment_id']})`  \n> \"{quote_stripped}\"\n")
        else:
            md_lines.append(f"*[{s['speaker_name']}]* `({s['segment_id']})`  \n*{clean_text}*\n")

    for out_d in target_dirs:
        md_path = out_d / f"s{session_num}-scene-script.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        print(f"   📜 Saved Screenplay Markdown: {md_path}")

    return script_payload

def main():
    parser = argparse.ArgumentParser(description="Multi-Voice Scene Script Generator")
    parser.add_argument("--session", type=int, choices=[1, 2, 3], help="Session number (1, 2, or 3)")
    parser.add_argument("--all", action="store_true", help="Generate scripts for all sessions (1, 2, 3)")
    parser.add_argument("--output-dir", type=Path, help="Optional custom output directory")

    args = parser.parse_args()

    sessions = []
    if args.all:
        sessions = [1, 2, 3]
    elif args.session:
        sessions = [args.session]
    else:
        sessions = [1, 2, 3]

    for s in sessions:
        generate_session_script(s, args.output_dir)

    print("\n🎉 Multi-Voice Scene Script generation complete!")

if __name__ == "__main__":
    main()
