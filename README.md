# 🖋️ D&D Scribe: Tabletop RPG to Novel Publishing Engine

**D&D Scribe** is a high-fidelity publishing pipeline and orchestration engine designed to convert raw Tabletop RPG session recordings into Sanderson-caliber fantasy novels, graphic novel storyboards, and multi-voice audiobooks with 100% auditable provenance.

---

## 🧭 Branch Index & Campaign Registry

| Branch | Status | Campaign | Game Master | Setting / Description |
|---|:---:|---|---|---|
| **[`uneraseable`](https://github.com/ldstrebel/dnd-scribe/tree/uneraseable)** | **Active** | *The Margin: The Stolen Weave* | Luke Foreman (`Luke F`) | Modern Mythic / Urban Fantasy (Three Fates, demigods, and reality-warping fragments) |
| **[`archive/vumbua`](https://github.com/ldstrebel/dnd-scribe/tree/archive/vumbua)** | **Archived** | *Vumbua: Volume 1 (The Basalt Run)* | Luke Strebel (`Luke S`) | Daggerheart High Fantasy (Complete 13-session Volume 1 chronicle with 100% verified manifests & EPUBs) |
| **[`archive/volume-1-reindexed`](https://github.com/ldstrebel/dnd-scribe/tree/archive/volume-1-reindexed)** | **Archived** | *Vumbua: Volume 1 (Reindexed)* | Luke Strebel (`Luke S`) | Mirror archive of the reindexed Volume 1 master |
| **`main`** | **Engine** | *Agnostic Core Framework* | — | Reusable engine, validation harness, editorial linters, and skill synchronization |

---

## 🏛️ Pipeline Architecture & Ground-Truth Hierarchy

```
  ┌─────────────────────────────────────────────────────────┐
  │ 1. Raw Indexed Audio / Transcript (sessions/data/index/sN-raw-indexed.md) │
  │    Immutable L#### line indices with verbatim table turns. │
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 2. Session Config (sessions/config/sN-session-config.json)│
  │    Declared GM, players, and shared mic decompositions. │
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 3. Modular Story Blocks (sessions/data/clean/blocks/sN-scene-XX.md) │
  │    Sanderson-caliber prose, full scene staging,         │
  │    verbatim quoted dialogue, and line markers (<!-- Lxxxx -->). │
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 4. Parity Verification & Story Assembly                  │
  │    sessions/_scripts/verify_parity.py                   │
  │    sessions/_scripts/assemble_story.py                  │
  └────────────────────────────┬────────────────────────────┘
                               │
                               ├──────────────────────────┐
                               ▼                          ▼
  ┌─────────────────────────────────────────────────────────┐ ┌───────────────────────────────────────┐
  │ 5. Adversarial Novel Critic & EPUB Generator            │ │ 6. Graphic Novel Storyboard & Audio   │
  │    .agents/skills/novel-critic/                         │ │    campaign/storyboards/              │
  │    novel/generate_epub.py                               │ │    sessions/_scripts/generate_audiobook│
  └─────────────────────────────────────────────────────────┘ └───────────────────────────────────────┘
```

---

## 🛡️ Verification Suite Gates

Before committing any session novelization:
1. **Manifest Integrity:** `python sessions/_scripts/verify_manifest.py sN` (100% Monotonic Line Coverage & Sub-165 line block sizing)
2. **Dialogue Ledger Parity:** `python sessions/_scripts/verify_parity.py sN` (100% Dialogue Ledger & Spans Fidelity)
3. **Adversarial Novel Critic:** `python .agents/skills/novel-critic/scripts/critique_prose.py sN` (Prose telemetry, zero meta-leaks, talking heads scan)
4. **EPUB3 Compilation:** `python novel/generate_epub.py` (Clean EPUB3 generation for Illustrated and Text-Only editions)

---

## 🚀 Bootstrapping a New Campaign

1. Create a new campaign branch from `main`:
   ```bash
   git checkout -b campaign/<campaign-name>
   ```
2. Configure your campaign in `novel/book_config.json`:
   ```json
   {
     "title": "Campaign Title",
     "series": "Chronicles",
     "author": "The Table",
     "campaign": "Campaign Name (GM: Name)",
     "setting_type": "fantasy"
   }
   ```
3. Populate player character dossiers in `campaign/characters/pcs/` and world lore in `campaign/world/`.
4. Place raw session transcripts in `sessions/data/raw/s1-raw.md` and follow the pipeline!

---

## 📄 License
MIT License. Built for tabletop storytellers, Game Masters, and authors everywhere.
