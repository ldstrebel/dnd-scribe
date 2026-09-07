# Tabletop RPG to Novel & Graphic Novel Publishing Engine Guidelines

Always follow these rules when converting raw tabletop RPG transcripts into Sanderson-caliber fantasy novels, audiobooks, and graphic novel storyboards.

---

## 1. Ground-Truth Hierarchy

```
  ┌─────────────────────────────────────────────────────────┐
  │ 1. Raw Indexed Transcript (sessions/data/index/sN-raw-indexed.md) │
  │    Immutable L#### line indices with raw recording.      │
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 2. Session Config (sessions/config/sN-session-config.json)│
  │    Declared GM, players, and shared mic mappings.       │
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 3. Attributed Clean Transcript (sessions/data/clean/sN-clean.md) │
  │    100% audited speaker attributions, OOC boundaries,   │
  │    and verbatim dialogue turns.                         │
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 4. Modular Story Blocks (sessions/data/clean/blocks/sN-scene-XX.md) │
  │    Sanderson-caliber prose, full scene staging,         │
  │    proper quoted dialogue, and line markers (<!-- Lxxxx -->). │
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 5. Graphic Novel Storyboard (campaign/storyboards/sN-storyboard.md) │
  │    Visual panel descriptions, verified character tokens,│
  │    and baked verbatim dialogue bubbles.                 │
  └─────────────────────────────────────────────────────────┘
```

---

## 2. 3-Tier Line Categorization & Extraction (The Cardinal Rule)

Every raw line must be categorized during transcript cleaning:
1. **Tier A: In-World Spoken Dialogue (`**[[Speaker]] (PC/NPC):** "..."`)** — Pure in-universe spoken lines. Disentangle shared mics and attribute speakers accurately.
2. **Tier B: Player Action, Mechanical Context & GM Worldbuilding Intent (`*Player Action Intent:*`)** — Player and GM descriptions of physical actions, mechanical attempts, spell manifestations, device operations, and environmental descriptions.
   - **Rule:** Strip numeric dice rolls and DC math (`"DC 15"`, `"rolled a 12"`), but **MANDATORILY PRESERVE AND NOVELIZE** the sensory manifestations, spell descriptions, tool operations, and tactical intent into rich Narrator Prose and staged action.
3. **Tier C: Pure Technical Meta Table Talk (`*Table Note:*`)** — Wi-Fi drops, character sheet technical glitches, pizza orders, sports chatter, and out-of-game calendar scheduling.

---

## 3. Graphic Novel Storyboard Rules

*   **Never truncate page budgets:** Scale pages to the emotional and narrative weight of each scene (typically 3–5 pages per major scene).
*   **Mandatory Anti-Grid Layout Justification:** Storyboards must avoid repetitive grids. Vary dynamically across:
    - 1-Panel Splash / Overlay
    - 2-Panel Asymmetrical Splits (65/35, 50/50, 40/60)
    - 3-Panel Tiered Grids
    - 4-Panel Quad Grids
*   **Opening Style Token:**
    `Detailed 2D graphic novel style, clean expressive manga-style linework, crisp black ink outlines, cel-shaded color flats, cinematic volumetric lighting`
*   **Explicit Skin Tone & Physical Features:** Every character visual prompt MUST include explicit skin tone/color, silhouette, and attire to prevent AI image drift.
*   **No Name Leaks in Visual Descriptors:** Replace character names with physical description tokens in prompt bodies. Character names are only permitted inside verbatim quoted speech bubbles.
*   **Dialogue Locking:** Speech bubbles baked into artwork must come directly from clean story files without AI dialogue improvisation.

---

## 4. Prose Novelization Checklist

Every generated scene block must satisfy the 6-point standard:
1. **Full Dialogue Dramatization:** Quoted dialogue (`"..."`) with dedicated paragraphs per speaker change. Zero embedded italic dialogue summaries.
2. **Sensory & Physical Anchoring:** Grounded physical mannerisms, environmental lighting, and tactile interactions.
3. **Comedic & Emotional Arcs:** Setup $\rightarrow$ Escalation $\rightarrow$ Punchline $\rightarrow$ Reaction preserved with full comedic timing.
4. **Mechanical Magic & World-Tech:** Vivid sensory descriptions of spellcraft, energy, technology, and terrain obstacles.
5. **Logical Causal Bridges:** Clear triggers and reactions without skipped causal steps.
6. **Line Traceability & Ledger Parity:** Modular line anchors (`<!-- Lxxxx -->`) and ledger comments (`<!-- LEDGER: rendered=[...] skipped=[...] -->`).

---

## 5. Verification Suite Gates

Before finalizing any session novelization or storyboard:
1. `python sessions/_scripts/verify_manifest.py sN` (100% Monotonic Line Coverage & Sub-165 line block sizing)
2. `python sessions/_scripts/verify_parity.py sN` (100% Dialogue Ledger & Spans Fidelity)
3. `python .agents/skills/novel-critic/scripts/critique_prose.py sN` (Prose telemetry, zero Earth-leaks, talking heads scan)
4. `python novel/generate_epub.py` (Clean EPUB compilation)
