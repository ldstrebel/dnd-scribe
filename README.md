# 🖋️ Uneraseable: Tabletop-to-Novel Publishing Engine

**Uneraseable** is an automated, high-fidelity pipeline for transforming raw Tabletop RPG session recordings and transcripts into Sanderson-caliber fantasy novels, illustrated graphic novel storyboards, and multi-voice audiobooks.

---

## 🏛️ Architecture & Pipeline

```
  Raw Audio / STT Transcripts
              │
              ▼
   [ 1. Indexing & Attribution ]  ───> sessions/data/index/sN-manifest.json
              │
              ▼
   [ 2. Two-Editor Cleaning ]     ───> sessions/data/clean/sN-clean.md
              │
              ▼
   [ 3. Scene Block Drafting ]    ───> sessions/data/clean/blocks/sN-scene-XX.md
              │
              ▼
   [ 4. Story Assembly & Audit ]  ───> sessions/data/clean/sN-clean-story.md
              │
              ├───> [ 5. Novel Critic Telemetry ]
              ├───> [ 6. EPUB3 Compilation ]     ───> novel/[book]-illustrated.epub
              └───> [ 7. Audio Manifest & TTS ]   ───> audio/segments/
```

---

## 📁 Repository Structure

* `campaign/`: Worldbuilding, factions, locations, NPC/PC dossiers, and session prep.
  * `characters/pcs/`: Player character dossiers and visual prompt tokens.
  * `characters/npcs/`: Non-player character profiles with metadata tags.
  * `factions/`: In-universe factions, guilds, and factions.
  * `locations/`: Key geography, cities, and architecture tokens.
  * `world/`: Magic systems, world-tech, history, and cosmology.
* `sessions/`: Transcripts, indexing ledgers, and modular scene blocks.
  * `data/raw/`: Raw STT audio transcripts (`sN-raw.md`).
  * `data/index/`: Line-indexed raw transcripts and manifest files (`sN-manifest.json`).
  * `data/clean/blocks/`: Modular Sanderson-standard scene blocks (`sN-scene-XX.md`).
  * `_scripts/`: Verification linters, story assemblers, and audiobook generator.
* `novel/`: Book configuration, styling, and EPUB compiler.
  * `book_config.json`: Centralized book title, subtitle, author, and metadata.
  * `generate_epub.py`: EPUB3 generator for Illustrated and Text-Only editions.
* `.agents/skills/`:
  * `novel-critic/`: Adversarial prose telemetry, bloat auditor, and talking-heads scanner.
  * `session-audit/`: Line-by-line transcript parity and ledger verification.
  * `storyboard-audit/`: Graphic novel panel auditing and visual drift prevention.

---

## 🚀 Quick Start: Adding a New Campaign Session

### 1. Add Raw Transcript
Place your raw session STT transcript into `sessions/data/raw/s1-raw.md`.

### 2. Build Session Index & Manifest
Generate line-indexed transcript `sessions/data/index/s1-raw-indexed.md` and define scene boundaries in `sessions/data/index/s1-manifest.json`.

### 3. Verify Manifest Integrity
```powershell
python sessions/_scripts/verify_manifest.py s1
```

### 4. Draft Scene Blocks
Draft modular story blocks in `sessions/data/clean/blocks/s1-scene-01.md` with line anchors (`<!-- Lxxxx -->`) and ledger footer.

### 5. Verify Parity & Assemble Story
```powershell
python sessions/_scripts/verify_parity.py s1
python sessions/_scripts/assemble_story.py s1 --title "SESSION TITLE"
```

### 6. Run Novel Critic & Compile EPUB
```powershell
python .agents/skills/novel-critic/scripts/critique_prose.py s1
python novel/generate_epub.py
```

---

## 📄 License
MIT License. Built for tabletop storytellers, Game Masters, and authors everywhere.
