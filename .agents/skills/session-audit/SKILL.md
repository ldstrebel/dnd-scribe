---
name: session-audit
description: Auditing, fixing, and maintaining parity across raw transcripts, clean attributed transcripts, novelized story blocks, and storyboards.
---

# Session Audit & Novelization Skill (Ebook Standard)

Use this skill when auditing session transcripts, cleaning dialogue, novelizing session chapters, or running post-mortems on prose quality and transcript fidelity.

---

## 🏛️ Ground-Truth Hierarchy

```
  ┌─────────────────────────────────────────────────────────┐
  │ 1. Raw Indexed Transcript (data/index/sN-raw-indexed.md)│
  │    Immutable L#### line indices with raw audio.         │
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
  │ 3. Attributed Clean Transcript (clean/sN-clean.md)      │
  │    100% audited speaker attributions, table talk OOC    │
  │    declarations, turn stitching, and storyboard splices.│
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 4. Novelized Story Blocks (clean/blocks/sN-scene-XX.md)  │
  │    Sanderson-caliber prose, full scene staging,         │
  │    proper quoted dialogue, and line markers (<!-- Lxxxx -->).│
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 5. Graphic Novel Storyboard (storyboards/sN-storyboard.md)│
  │    Visual panel descriptions, verified profile tokens, │
  │    and baked verbatim dialogue bubbles.                │
  └─────────────────────────────────────────────────────────┘
```

---

## 🚫 Comprehensive Failure Modes & Post-Mortem Register

### 1. Gist-Level Manifest Truncation
* **Symptom:** High-value character dialogue, comedic beats, or world-tech explanations present in raw audio vanish from the novelization.
* **Root Cause:** Compressing raw transcript turns into summary bullets. Downstream prose generators never see the skipped turns.
* **Prevention:** Every spoken turn must be tracked in the manifest ledger and accounted for in prose.

### 2. Heuristic Keyword Coarseness
* **Symptom:** Audit tools report `[PASS]` even though critical spoken exchanges are completely missing.
* **Root Cause:** Checking binary keyword presence rather than verbatim line-by-line dialogue representation.
* **Prevention:** Never rely on regex matchers alone. Conduct granular scene-by-scene dialogue audits.

### 3. Fused Interjections & Turn Order Compression
* **Symptom:** Rapid speaker alternation gets collapsed into a single speaker's continuous monologue, dropping interjections.
* **Root Cause:** Skipping interjections as "table chatter".
* **Prevention:** Read multi-speaker clusters holistically. Every interjection must have its own prose beat.

### 4. OOC Table Talk vs. In-World Character Banter Misclassification
* **Symptom:** Real in-world banter stripped as table talk, or OOC meta questions novelized into in-universe canon.
* **Prevention:** Config-gated attribution with explicit `ooc_ranges` and `ooc_lines` declaring table talk with real names.

### 5. STT Phonetic Mishearings & Entity Name Drift
* **Symptom:** Character/location names mangled by speech-to-text algorithms.
* **Prevention:** Cross-reference every entity against `characters/` and `campaign/` dossiers before writing scene blocks.

### 6. Clipped STT Lines Rendered as Stylistic Ellipsis
* **Symptom:** Incomplete STT lines rendered as intentional trailing-off rather than resolving the full sentence.
* **Prevention:** Flag all syntactically incomplete lines with `[CLIPPED]` and reconstruct intent from surrounding context.

### 7. Tier B Player Narration Rendered as Tier A In-World Dialogue
* **Symptom:** Player talking about their character in third person (*"Britt is just zoned"*) gets quoted as in-world speech.
* **Prevention:** Convert Tier B third-person player intent into vivid narrator prose and character action.

### 8. The "Dialogue-Dense Scene" Compression Trap
* **Symptom:** Scenes with 3+ simultaneous speakers compressed to a single-voice monologue.
* **Prevention:** In multi-speaker scenes (e.g. tactical planning, debates, chaotic combat), write every speaker interjection as a separate paragraph with its own action beat.

### 9. Vision / Flashback POV Inversion
* **Symptom:** Ancestral or mystical visions written as first-person possession rather than secondhand memories viewed through ancient eyes.
* **Prevention:** Clearly frame visions and flashbacks through the observer's physical perspective and emotional anchor.

### 10. Embedded / Italicized Summary Dialogue Anti-Pattern
* **Symptom:** Spoken dialogue is stripped of quotation marks and buried into running narrative sentences with em-dashes and italics.
* **Root Cause:** Attempting to summarize conversational pacing rather than dramatizing the scene.
* **Prevention:** **STRICT BAN ON EMBEDDED ITALIC DIALOGUE.** All spoken character lines MUST be formatted as standard quoted dialogue (`"..."`) with proper paragraph breaks, dialogue tags, and physical beats.

### 11. Truncated Comedic Timing & Lost Character Dynamics
* **Symptom:** Comedic setups, escalations, punchlines, and physical slapstick are flattened into a single passive sentence.
* **Root Cause:** Treating comedic exchanges as "minor filler" rather than essential characterization.
* **Prevention:** Comedic beats must receive full scene staging: **Setup $\rightarrow$ Escalation $\rightarrow$ Punchline $\rightarrow$ Reaction**.

### 12. Player Game-State Clarification Rendered as In-World Character Dialogue
* **Symptom:** A player asking the GM an environmental or game-state question (*"Is the door open?"*, *"Can I see the bridge?"*) is rendered literally as spoken in-universe character dialogue.
* **Root Cause:** Treating all speech on a player's microphone as in-character speech without recognizing game-state clarification queries.
* **Prevention:** Translate player environment/state questions into sensory prose observations and character focus, not spoken dialogue by a character looking right at the object.

### 13. Anachronistic Naming in Memory Sequences
* **Symptom:** Using proper character names in narrative descriptions during secondhand memory sequences when the watching characters have never met or heard these ancient figures.
* **Prevention:** Use pure physical/clan descriptors for all ancient or unknown figures in narrative prose. Only use spoken names if they are declared in-universe.

### 14. Dialogue Paraphrase & Summary Compression (The "Told, Not Shown" Trap)
* **Symptom:** Key verbal exchanges are summarized into a narrator sentence rather than written out as active dialogue.
* **Root Cause:** Prioritizing word economy over character voice and emotional immersion.
* **Prevention:** If characters speak in the raw audio, write out the verbatim dialogue lines with emotional cadence and micro-actions.

### 15. Broken Sequential Cause-and-Effect Bridges
* **Symptom:** An action or line happens without the prerequisite trigger.
* **Prevention:** Trace every conversation as an unbroken causal chain: **Trigger $\rightarrow$ Reaction $\rightarrow$ Resolution**.

### 16. Dropped World-Media & Atmospheric Broadcasts
* **Symptom:** Radio broadcasts, speaker horns, public speeches, and ambient environmental announcements are omitted.
* **Prevention:** Always scan raw audio and session planning materials for in-universe media broadcasts and integrate them into the physical scene environment.

### 17. Omission of Post-Session Thematic Reflections
* **Symptom:** Profound out-of-character GM/player discussions regarding core campaign themes are discarded as mere "table talk."
* **Prevention:** Channel deep OOC thematic insights into rich, philosophical narrative prose and character epiphanies during chapter resolutions.

### 18. Mechanical Context & Spell/Ability Descriptions Truncated as "Table Talk"
* **Symptom:** When a player or GM discusses mechanics (e.g. describing how a spell looks, how an arcanatech device operates, somatic components, environmental difficulty reasons, or how a character's ability manifests in the fiction), the entire exchange is discarded as meta table talk, stripping the novel of vivid sensory details and tactical action.
* **Root Cause:** Equating all mechanical talk with useless OOC chatter.
* **Prevention:** Strip the numeric dice rolls and DC numbers (`"DC 15"`, `"Roll 12"`), but **MANDATORILY EXTRACT AND NOVELIZE the physical descriptions, sensory manifestations, tool operations, and tactical intent into rich Narrator Prose and staged action beats.**

---

## ✍️ The Ebook Standard: Mandatory Novelization Checklist

Every generated scene block (`clean/blocks/sN-scene-XX.md`) and compiled story chapter must satisfy this 6-point standard before being marked complete:

1. **Full Dialogue Dramatization**:
   - All spoken lines formatted with double quotes (`"..."`).
   - Every speaker change gets a dedicated paragraph.
   - Zero embedded italic dialogue summaries.

2. **Sensory & Physical Anchoring**:
   - Include distinct physical mannerisms, tactile tool interactions, environmental lighting, and distinct character silhouettes.

3. **Complete Comedic & Emotional Arcs**:
   - Multi-speaker banter preserved with full setup, timing, escalation, and reactions intact.

4. **Deep World-Building & Mechanical Magic**:
   - Fully describe world-tech, elemental physics, somatic gestures, and magical manifestations.

5. **Logical Causal Continuity**:
   - Every character action and reaction must have an explicit in-world trigger.

6. **Line Traceability & Ledger Parity**:
   - Every scene must contain line anchors (`<!-- Lxxxx -->`) mapping back to `sN-raw-indexed.md` and a clean ledger comment at the bottom.
