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

## 2.1 The Zero-Regex Dialogue & Origin-Time Provenance Law

* **Origin-Time Invariant:** Dialogue classification and speaker identity are established **at the point of creation** (in transcript indexing and modular prose block generation).
* **Zero Post-Hoc Guesswork:** Downstream tools (`generate_web_manifest.py`, TTS generators, EPUB compilers, Web Readers) must **NEVER** use regex, speech-verb parsers, or name searches on prose to infer or guess who is speaking.
* **Direct Provenance Lookup:**
  - In archival and creative blocks, text inside quotes (`"..."`) derives its speaker identity directly from the attached line anchor (`<!-- Lxxxx -->` or span `<!-- Lxxxx-Lyyyy -->`) mapped against `sN-session-config.json` and `sN-raw-indexed.md`.
  - Text outside quotes is unconditionally `speakerId: "narrator"`.
  - Violating this by adding regex heuristics or arbitrary fallbacks (`else: pierre`) is an architectural breach.

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

Every generated scene block must satisfy the 8-point standard:
1. **Full Dialogue Dramatization:** Quoted dialogue (`"..."`) with dedicated paragraphs per speaker change. Zero embedded italic dialogue summaries. Spoken lines inside quotes are immutable ground-truth.
2. **Sensory & Physical Anchoring:** Grounded physical mannerisms, environmental lighting, and tactile interactions.
3. **Comedic & Emotional Arcs:** Setup $\rightarrow$ Escalation $\rightarrow$ Punchline $\rightarrow$ Reaction preserved with full comedic timing.
4. **Mechanical Magic & World-Tech:** Vivid sensory descriptions of spellcraft, energy, technology, and terrain obstacles.
5. **Logical Causal Bridges:** Clear triggers and reactions without skipped causal steps.
6. **Line Traceability & Ledger Parity:** Modular line anchors (`<!-- Lxxxx -->`) and ledger comments (`<!-- LEDGER: rendered=[...] skipped=[...] -->`).
7. **Dwight Swain Motivation-Reaction Units (MRUs) in Action Staging:** In physical combat, sudden attacks, and peril, sequence beats neuro-physiologically: $\text{External Motivation} \longrightarrow \text{Visceral Sensation} \longrightarrow \text{Involuntary Reflex} \longrightarrow \text{Deliberate Action \& Speech}$. Never jump directly from incoming stimulus to spoken dialogue or tactical counters.
8. **Deep POV & Windowpane Prose Styling:** Eradicate cognitive sensory filter frames (*saw, heard, felt, noticed, wondered, realized*); make perceived phenomena act directly upon the narrative. Maintain syntactic cadence by limiting introductory participial phrases to $\le 1$ per 500 words. Strictly ban synthetic purple clichés (*"tapestry of"*, *"palpable tension"*, *"dance of blades"*).

---

## 4.1 The Dialectical Subagent Writers' Room (`DEC-025`)

To eradicate cognitive overload during drafting, split creative drafting into an adversarial subagent dialectic with grading sequestered strictly into the external Python suite:
1. **The Tabletop Grounding Prosecutor (`grounding-auditor`):** Governs raw line fidelity, player agency, and distinguishes player hypotheses from GM confirmations via `source-decisions.json`.
2. **The Campaign Arc & Macro-Lore Steward (`arc-steward`):** Governs multi-book cosmology and faction agendas under the **Negative-Only Mandate** (`DEC-010`, `DEC-025`) via `campaign/CAMPAIGN_ARC_LEDGER.md`. Never invents forward prophecies or ungrounded backstories.
3. **The Reader Experience & Continuity Modeler (`reader-advocate`):** Models the cognitive load of a reader who has never seen the stream; enforces the **"Declared, First, and Grounded"** law for all introduced lore terms and NPCs.
4. **The Craft & Deep-POV Dramatist (`craft-dramatist`):** Enforces Dwight Swain MRUs, windowpane styling, syntactic cadence, and voice differentiation.
5. **The Dynamic Pre-Flight Brief:** `python sessions/_scripts/print_writers_room.py sN` synthesizes state across the 4 foundational files without creating redundant fifth JSON files.
6. **The External Arbiter (Infallible Python Gates):** Subagents write and debate, but under no circumstances evaluate their own compliance. Pass/fail is enforced exclusively by deterministic Python scripts (`audit_arc_ledger.py`, `audit_reader_context.py`, `verify_parity.py`, `audit_semantic_grounding.py`, `verify_intent_parity.py`, `critique_prose.py`, `test_harness.py`).

---

## 5. Verification Suite Gates

Before finalizing any session novelization or storyboard:
1. `python sessions/_scripts/audit_arc_ledger.py` (100% Provenance Citation Grounding)
2. `python sessions/_scripts/audit_reader_context.py sN` (Declared, First, and Grounded Invariants)
3. `python sessions/_scripts/verify_manifest.py sN` (100% Monotonic Line Coverage & Sub-165 line block sizing)
4. `python sessions/_scripts/verify_parity.py sN` (100% Dialogue Ledger & Spans Fidelity, Canon Lore Guardrail)
5. `python sessions/_scripts/verify_intent_parity.py sN` (Double-Blind Intent Parity & Agency Guards)
6. `python .agents/skills/novel-critic/scripts/critique_prose.py sN` (Prose telemetry, zero Earth-leaks, talking heads scan, filter words & cadence)
7. `python novel/generate_epub.py` (Clean EPUB compilation)
8. `python sessions/_scripts/run_publishing_pipeline.py sN` (Dual-Track Scorecard & Creative Liberty Ledger)

---

## 6. Pipeline Discussions & Anti-Amnesia Mandate (`pipeline-steward`)

Whenever discussing, auditing, refactoring, or evaluating the publishing pipeline, publishing scripts, verification gates, or dual tracks:
1. **Mandatory Skill Activation:** Consult `.agents/skills/pipeline-steward/SKILL.md`.
2. **Consult Established Records First:** Read `.agents/skills/pipeline-steward/references/PIPELINE_DECISION_LEDGER.md` and `docs/pipeline_architecture.md` before responding. Anchor every discussion to the existing 15+ editions, 20 historical Failure Points (`FP-01` to `FP-20`), and established decision records (`DEC-001` to `DEC-025`).
3. **Strict Ban on Sycophancy & False Novelty:** Never react with empty praise (*"What a wonderful idea! Why didn't I think of that?"*) to established pipeline mechanics. Treat user prompts as critical signals on whether the architecture is being upheld, whether gates are slipping into rubber-stamping, or whether an existing compromise needs re-evaluation.
4. **Continuous Decision Logging:** Any agreed structural change or newly discovered trade-off must be logged directly into `PIPELINE_DECISION_LEDGER.md`.

