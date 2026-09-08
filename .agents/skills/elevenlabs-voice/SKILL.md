---
name: elevenlabs-voice
description: Multi-voice speech synthesis and per-voice API key routing for D&D Scribe audiobook and web reader generation.
---

# 🎙️ ElevenLabs Multi-Voice Synthesis Skill

The `elevenlabs-voice` skill synthesizes novelized D&D campaign sessions into broadcast-grade multi-voice audiobooks and interactive audio blocks for the web reader.

---

## 🏗️ Architecture & Features

1. **Schema 2.0 Manifest Ingestion:**
   Consumes `sessions/data/index/sX-manifest-v2.json` containing granular blocks (`b001`, `b002`...) with character speaker tags (`speakerId: "pierre"`, `"dravin"`, `"alfie"`, `"eusacles"`, `"narrator"`, etc.).

2. **Per-Voice API Key Routing:**
   Allows mapping a distinct ElevenLabs API key per character voice (e.g. player subscriptions or character quotas) or falling back to a shared master key:
   - `ELEVENLABS_API_KEY_DRAVIN`
   - `ELEVENLABS_API_KEY_PIERRE`
   - `ELEVENLABS_API_KEY_EUSACLES`
   - `ELEVENLABS_API_KEY_ALFIE`
   - `ELEVENLABS_API_KEY_NARRATOR`
   - `ELEVENLABS_API_KEY_NPC`
   - Fallback: `ELEVENLABS_API_KEY`

3. **Block-Level Caching:**
   Synthesized MP3 chunks are saved to `audio/cache/{block_id}.mp3`. Re-runs skip already generated audio unless `--force` is provided, preventing redundant token/quota consumption.

4. **Master Audio Stitching:**
   Concatenates all session blocks into seamless full-session audiobooks (`audio/dist/{session_id}-audiobook.mp3`) or chapter-level tracks.

5. **Dry-Run Audits:**
   Calculates exact character and word count quotas per speaker and checks API key readiness without making network calls.

---

## ⚙️ Voice Configuration (`config/voice_config.json`)

Character voice settings (voice ID, stability, similarity boost, style, and API key environment variable) are defined in `config/voice_config.json`.

```json
{
  "defaultModelId": "eleven_multilingual_v2",
  "defaultApiKeyEnv": "ELEVENLABS_API_KEY",
  "voices": {
    "narrator": {
      "name": "Narrator",
      "voiceId": "nPczCjzI2devNBz1zQrb",
      "apiKeyEnv": "ELEVENLABS_API_KEY_NARRATOR",
      "settings": { "stability": 0.60, "similarity_boost": 0.75, "style": 0.20, "use_speaker_boost": true }
    },
    "dravin": {
      "name": "Prof. Edward Dravin",
      "voiceId": "JBFqnCBsd6RMkjVDRZzb",
      "apiKeyEnv": "ELEVENLABS_API_KEY_DRAVIN",
      "settings": { "stability": 0.65, "similarity_boost": 0.80, "style": 0.15, "use_speaker_boost": true }
    }
  }
}
```

---

## 🚀 Commands & Usage

### 1. Quota & Key Readiness Dry Run
```powershell
python .agents/skills/elevenlabs-voice/scripts/synthesize_audio.py --dry-run
```

### 2. Synthesize Single Session
```powershell
python .agents/skills/elevenlabs-voice/scripts/synthesize_audio.py --session s1 --synthesize --stitch --update-manifest
```

### 3. Synthesize Single Character
```powershell
python .agents/skills/elevenlabs-voice/scripts/synthesize_audio.py --session s1 --voice dravin --synthesize
```

### 4. Force Re-synthesis of Stale Audio
```powershell
python .agents/skills/elevenlabs-voice/scripts/synthesize_audio.py --session s1 --synthesize --force
```
