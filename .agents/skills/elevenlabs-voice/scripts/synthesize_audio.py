#!/usr/bin/env python3
"""
ElevenLabs Multi-Voice Synthesis Pipeline for D&D Scribe
Reads Schema 2.0 Web Manifests (sX-manifest-v2.json), routes speaker blocks to
distinct voice IDs and per-voice API keys, caches audio segments, and stitches
them into chapter and session audiobooks.
"""

import argparse
import glob
import json
import os
import sys
import time
from pathlib import Path
import urllib.request
import urllib.error

# Ensure UTF-8 stdout on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "voice_config.json"
DEFAULT_MANIFEST_DIR = Path("sessions/data/index")
DEFAULT_CACHE_DIR = Path("audio/cache")
DEFAULT_OUTPUT_DIR = Path("audio/dist")

def load_voice_config(config_path: Path):
    if not config_path.exists():
        raise FileNotFoundError(f"Voice config not found at: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def resolve_voice_for_speaker(speaker_id: str, config: dict) -> dict:
    voice_map = config.get("voices", {})
    if speaker_id in voice_map:
        return voice_map[speaker_id]
    if speaker_id == "narrator":
        return voice_map.get("narrator", {})
    default_npc = config.get("defaultNpcVoice", {})
    if default_npc:
        return {
            "name": speaker_id.capitalize(),
            "voiceId": default_npc.get("voiceId"),
            "apiKeyEnv": default_npc.get("apiKeyEnv", "ELEVENLABS_API_KEY_NPC"),
            "modelId": default_npc.get("modelId", "eleven_multilingual_v2"),
            "settings": default_npc.get("settings", {}),
            "description": f"Generic NPC voice fallback for {speaker_id}"
        }
    return voice_map.get("narrator", {})

def get_api_key_for_speaker(speaker_id: str, voice_cfg: dict, config: dict):
    default_env = config.get("defaultApiKeyEnv", "ELEVENLABS_API_KEY")
    specific_env = voice_cfg.get("apiKeyEnv", default_env)
    
    key = os.environ.get(specific_env)
    if key:
        return key, specific_env
        
    fallback_key = os.environ.get(default_env)
    if fallback_key:
        return fallback_key, default_env
        
    return None, specific_env

def estimate_duration_seconds(word_count: int, wpm: int = 155):
    return (word_count / wpm) * 60.0

def run_dry_run(manifest_files, config, filter_speaker=None):
    print("=" * 105)
    print("🎙️  ELEVENLABS MULTI-VOICE SYNTHESIS: DRY RUN AUDIT & QUOTA ESTIMATE")
    print("=" * 105)
    
    default_model = config.get("defaultModelId", "eleven_multilingual_v2")
    
    total_blocks = 0
    total_words = 0
    total_chars = 0
    speaker_stats = {}
    
    for manifest_path in manifest_files:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            
        blocks = manifest.get("blocks", [])
        for b in blocks:
            speaker_id = b.get("speakerId", "narrator")
            if filter_speaker and speaker_id != filter_speaker:
                continue
                
            text = b.get("text", "").strip()
            word_count = b.get("wordCount", len(text.split()))
            char_count = len(text)
            block_id = b.get("id", "unknown")
            
            total_blocks += 1
            total_words += word_count
            total_chars += char_count
            
            if speaker_id not in speaker_stats:
                v_cfg = resolve_voice_for_speaker(speaker_id, config)
                api_key, env_name = get_api_key_for_speaker(speaker_id, v_cfg, config)
                speaker_stats[speaker_id] = {
                    "name": v_cfg.get("name", speaker_id.capitalize()),
                    "voiceId": v_cfg.get("voiceId", "MISSING"),
                    "modelId": v_cfg.get("modelId", default_model),
                    "envVar": env_name,
                    "hasKey": bool(api_key),
                    "blocks": 0,
                    "words": 0,
                    "chars": 0,
                    "cached": 0
                }
                
            cached_path = DEFAULT_CACHE_DIR / f"{block_id}.mp3"
            is_cached = cached_path.exists() and cached_path.stat().st_size > 0
            
            speaker_stats[speaker_id]["blocks"] += 1
            speaker_stats[speaker_id]["words"] += word_count
            speaker_stats[speaker_id]["chars"] += char_count
            if is_cached:
                speaker_stats[speaker_id]["cached"] += 1

    print(f"Manifests Analyzed: {len(manifest_files)}")
    print(f"Total Blocks: {total_blocks:,} | Total Words: {total_words:,} | Total Characters: {total_chars:,}")
    print(f"Estimated Total Audio Runtime: {estimate_duration_seconds(total_words) / 60.0:.1f} minutes\n")
    
    print("-" * 105)
    print(f"{'SPEAKER':<12} | {'VOICE NAME':<20} | {'VOICE ID':<22} | {'KEY ENV VAR':<26} | {'KEY STATUS':<10} | {'BLOCKS':<7} | {'CHARS':<8} | {'CACHED'}")
    print("-" * 105)
    
    for spk, stats in sorted(speaker_stats.items(), key=lambda x: x[1]["chars"], reverse=True):
        key_status = "[READY]" if stats["hasKey"] else "[MISSING]"
        cached_str = f"{stats['cached']}/{stats['blocks']}"
        print(f"{spk:<12} | {stats['name']:<20} | {stats['voiceId']:<22} | {stats['envVar']:<26} | {key_status:<10} | {stats['blocks']:<7} | {stats['chars']:<8,} | {cached_str}")
        
    print("-" * 105)
    print("\n💡 To synthesize audio for characters:")
    print("   1. Set individual keys (e.g. $env:ELEVENLABS_API_KEY_DRAVIN = 'sk-...') or global $env:ELEVENLABS_API_KEY")
    print("   2. Run: python .agents/skills/elevenlabs-voice/scripts/synthesize_audio.py --session s1 --synthesize --stitch\n")

def call_elevenlabs_api(text: str, voice_id: str, model_id: str, settings: dict, api_key: str):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": settings
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        if resp.status == 200:
            return resp.read()
        else:
            raise RuntimeError(f"ElevenLabs API returned HTTP {resp.status}")

def synthesize_session(manifest_path: Path, config: dict, force: bool = False, filter_speaker = None, update_manifest: bool = False):
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    session_id = manifest.get("session", {}).get("id", manifest_path.stem)
    blocks = manifest.get("blocks", [])
    default_model = config.get("defaultModelId", "eleven_multilingual_v2")
    
    DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🚀 Starting Audio Synthesis for Session: {session_id} ({len(blocks)} blocks)")
    
    manifest_updated = False
    for idx, b in enumerate(blocks, 1):
        block_id = b.get("id", f"{session_id}_b{idx:03d}")
        speaker_id = b.get("speakerId", "narrator")
        
        if filter_speaker and speaker_id != filter_speaker:
            continue
            
        text = b.get("text", "").strip()
        if not text:
            continue
            
        cache_file = DEFAULT_CACHE_DIR / f"{block_id}.mp3"
        if cache_file.exists() and cache_file.stat().st_size > 0 and not force:
            print(f"  [{idx}/{len(blocks)}] [{speaker_id}] {block_id} -> Cached ({cache_file.stat().st_size / 1024:.1f} KB)")
            if update_manifest and b.get("audioUrl") != f"audio/cache/{block_id}.mp3":
                b["audioUrl"] = f"audio/cache/{block_id}.mp3"
                manifest_updated = True
            continue
            
        v_cfg = resolve_voice_for_speaker(speaker_id, config)
        voice_id = v_cfg.get("voiceId")
        if not voice_id:
            print(f"  ⚠️  Skipping {block_id}: No voiceId configured for {speaker_id}")
            continue
            
        api_key, env_name = get_api_key_for_speaker(speaker_id, v_cfg, config)
        if not api_key:
            print(f"  ❌ Missing API Key in {env_name} for voice {speaker_id}")
            continue
            
        model_id = v_cfg.get("modelId", default_model)
        settings = v_cfg.get("settings", {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        })
        
        print(f"  🎙️  [{idx}/{len(blocks)}] Synthesizing {block_id} ({speaker_id}, {len(text)} chars) using voice {voice_id}...")
        try:
            audio_data = call_elevenlabs_api(text, voice_id, model_id, settings, api_key)
            with open(cache_file, "wb") as f_out:
                f_out.write(audio_data)
            print(f"      ✅ Saved {cache_file.name} ({len(audio_data) / 1024:.1f} KB)")
            
            if update_manifest:
                b["audioUrl"] = f"audio/cache/{block_id}.mp3"
                manifest_updated = True
                
            time.sleep(0.1)
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8', errors='ignore')
            print(f"      ❌ HTTP Error {e.code} on {block_id}: {err_msg}")
        except Exception as ex:
            print(f"      ❌ Unexpected Error on {block_id}: {ex}")
            
    if manifest_updated:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"\n📝 Updated {manifest_path} with audio metadata.")

def stitch_session_audio(manifest_path: Path):
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    session_id = manifest.get("session", {}).get("id", manifest_path.stem)
    blocks = manifest.get("blocks", [])
    
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_session_mp3 = DEFAULT_OUTPUT_DIR / f"{session_id}-audiobook.mp3"
    
    print(f"\n🧵 Stitching {len(blocks)} audio blocks into: {out_session_mp3}...")
    
    total_bytes = 0
    missing_count = 0
    with open(out_session_mp3, "wb") as f_out:
        for b in blocks:
            block_id = b.get("id")
            cache_file = DEFAULT_CACHE_DIR / f"{block_id}.mp3"
            if cache_file.exists() and cache_file.stat().st_size > 0:
                with open(cache_file, "rb") as f_in:
                    chunk = f_in.read()
                    f_out.write(chunk)
                    total_bytes += len(chunk)
            else:
                missing_count += 1
                
    if missing_count > 0:
        print(f"  ⚠️  Stitching complete with {missing_count} missing block(s). File size: {total_bytes / (1024 * 1024):.2f} MB")
    else:
        print(f"  ✅ Successfully stitched 100% of blocks. Master file: {out_session_mp3} ({total_bytes / (1024 * 1024):.2f} MB)")

def main():
    parser = argparse.ArgumentParser(description="ElevenLabs Voice Synthesis for D&D Scribe")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to voice_config.json")
    parser.add_argument("--session", type=str, help="Target session (e.g., s1, s2, s3, or all)")
    parser.add_argument("--voice", type=str, help="Filter synthesis to a specific character speakerId")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Audit character quotas and keys without calling API")
    parser.add_argument("--synthesize", action="store_true", default=False, help="Execute audio synthesis")
    parser.add_argument("--stitch", action="store_true", default=False, help="Stitch blocks into master session audio")
    parser.add_argument("--force", action="store_true", default=False, help="Re-synthesize cached blocks")
    parser.add_argument("--update-manifest", action="store_true", default=False, help="Update manifest with audioUrl metadata")
    
    args = parser.parse_args()
    config = load_voice_config(args.config)
    
    if args.session and args.session.lower() != "all":
        s_id = args.session.lower().replace("session", "").replace("-", "")
        if not s_id.startswith("s"):
            s_id = f"s{s_id}"
        manifest_files = [DEFAULT_MANIFEST_DIR / f"{s_id}-manifest-v2.json"]
    else:
        manifest_files = sorted(DEFAULT_MANIFEST_DIR.glob("*-manifest-v2.json"))
        
    if not manifest_files:
        print(f"❌ No manifests found in {DEFAULT_MANIFEST_DIR}")
        sys.exit(1)
        
    if args.dry_run or (not args.synthesize and not args.stitch):
        run_dry_run(manifest_files, config, filter_speaker=args.voice)
        return
        
    if args.synthesize:
        for mf in manifest_files:
            synthesize_session(mf, config, force=args.force, filter_speaker=args.voice, update_manifest=args.update_manifest)
            
    if args.stitch:
        for mf in manifest_files:
            stitch_session_audio(mf)

if __name__ == "__main__":
    main()
