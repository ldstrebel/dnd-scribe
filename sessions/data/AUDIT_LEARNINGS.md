# 🛡️ D&D Scribe: Audit Failure Points, Root Causes & Upstream Learnings

This document is the persistent, canonical registry of all novelization pipeline failure modes, historical incidents, automated detection rules, and upstream drafting guidelines. It ensures that the engineering team and LLM authoring agents never repeat past hallucination patterns.

---

## 📊 Summary Failure Point Matrix

| Failure ID | Phase Origin | Root Cause | Example Historical Breach | Pipeline Detection Rule | Upstream Mitigation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FP-01** | Raw -> Index | **Abstract Storyboard Tropification** | S3: Summarized social bluff as generic "Museum Heist", leading drafting model to invent Hollywood sensor-lifting. | Semantic stem overlap check on dialogue turns; foreign prop detector. | Manifest must record `exact_quote` and `tabletop_action` instead of generic trope summaries. |
| **FP-02** | Index -> Draft | **Synthetic Integer Line Stamping** | S2: Stamped `L0404`, `L0406` on hallucinated campfire exposition; S3: Stamped `L1620` on fake magnetic sensors. | `audit_semantic_grounding.py`: Hard fail if token overlap is 0% between prose and raw speaker window. | Prompt rule: Markers can only be attached to paragraphs containing the actual speaker's words/actions. |
| **FP-03** | Drafting | **Premature Resolution / False Escape** | S3: Invented immediate sprint back to Theodore's shed at the Margin, erasing the 6:00 PM closing cliffhanger. | Scene boundary check; unanchored entity scan (*Theodore*, *Margin* in Raleigh scenes); dropped dialogue check on Nancy's closing line. | Grounding anchor: The scene must terminate at the exact final tabletop turn (L1656). |
| **FP-04** | Storyboard -> Prose | **Spatial & Physical Misplacement** | S3: Placed arrival in an interior broom closet instead of the standalone storage annex in the far parking lot. | Spatial entity scan; raw window verification (*parking lot*, *sedans*, *sunlight*). | Prompt rule: Always establish the physical environment from the DM's exact setting description. |
| **FP-05** | Ledger Creation | **Canon Dialogue Smuggling via OOC Skips** | S1: Marked in-character Pierre & Eusacles dialogue as `(ooc)` skips to avoid rendering difficult dialogue. | Dropped canon dialogue audit in `audit_semantic_grounding.py`: Flags `(ooc)` skips with >= 8 non-stopword content words. | Distinguish true OOC (`(banter)`, `(rules)`, `(mechanics)`) from canon dialogue (`(compressed)`). |
| **FP-06** | Drafting | **Over-Compression & Micro-Paragraph Choppiness** | S3: Compressed Pierre and Alfie's 30-turn planning dialogue into two dry 1-sentence paragraphs. | Style linter checks paragraph cadence and consecutive repetitive subject starts (*"Pierre examined... Pierre examined..."*). | Expand character deduction and tactical planning with dialogue turns and physical blocking. |
| **FP-07** | Drafting | **Dialogue Bluff Flattening** | S3: Compressed Pierre's extended French intern comedic bluff into a single unadorned dialogue line. | Pacing & dialogue density scanner; feedback ledger review. | Preserve the humor, personality quirks, and character beats of social interaction turns. |
| **FP-08** | Clean -> Draft | **3rd-Person Player Intent Leaking into Spoken Dialogue** | S4: Sophie's table description (*"Alfie is shook to his wooden core"*) quoted as Alfie's dialogue; Luke's Gorgon theory quoted as Pierre's line. | `critique_prose.py` 3rd-person self-reference regex scanner (`"<Name> is...", "<Name> feels..."` inside quotes). | 3rd-person table descriptions must be novelized as Narrator Prose / physical action, never placed inside dialogue quotes. |
| **FP-09** | Drafting -> Manifest | **Multi-Speaker Paragraph Fusion & Color Bleed** | S4: Alfie's Mage Hand pot drop fused into Pierre's dialogue block; Pierre asking about dragons fused into Alfie's trucker hat block. | Paragraph-level multi-speaker detector; `generate_web_manifest.py` single-speaker bubble monopoly check. | One Speaker Turn Per Paragraph Invariant: Every character dialogue turn or distinct character focus requires its own paragraph. |
| **FP-10** | Audio -> STT / Clean | **Phonetic Transcription Corruption & Accent Drift** | S1: French "Pair-ey" transcribed as "Brittany"; S3: Southern "Nincy" transcribed as "Nancy", breaking receptionist banter. | Dossier phonetic alias check; character introduction spelling audit. | Build explicit phonetic lookup tables in `campaign/characters/` and speaker alias maps in manifest generator. |
| **FP-11** | Clean -> EPUB | **Chapter Architecture Fragmentation (Micro-Chaptering)** | S3: 10 individual 100-line blocks each given `## CHAPTER` headers, creating 200-word single-scene chapters. | EPUB compiler linter (`EXCESSIVE_CHAPTER_SPLIT` warning when chapters > 4 per session). | Decouple modular 100-line processing blocks from overarching thematic novel chapters (2-4 per session). |
| **FP-12** | Raw -> Draft | **Mechanics-As-Dialogue (Anime Spell Shouts)** | S1: Characters shouting literal D&D spell names (*"Chill Touch!"*, *"Toll the Dead!"*) like battle cries. | Linter for raw mechanic names in dialogue strings without spellcraft narrative staging. | Translate table mechanics declarations into somatic gestures, atmospheric resonance, and in-world incantations. |
| **FP-13** | Manifest -> Web | **Silent Speaker Fallback to Narrator on GM NPCs** | S1-S4: GM voicing Gordon, Nincy, Mike, Theodore mapped to "narrator", causing speech bubbles to display as gray narrator text. | `verify_manifest.py` Invariant 6: Strict assertion that every `type: "dialogue"` has `speakerId != "narrator"` and valid character color. | Declare canonical `dialogue_speakers` line mappings and block overrides in `sN-session-config.json`. |
| **FP-14** | Prose -> Manifest | **Mid-Block Multi-Paragraph Line Marker Loss** | S1-S4: Multi-paragraph dialogue without intermediate anchors had subsequent paragraphs default to `sourceLine: null` and fallback to narrator. | Manifest generator validates that contiguous speaker dialogue blocks inherit active turn `sourceLine`. | Propagate active `sourceLine` across unanchored multi-paragraph dialogue turns. |
| **FP-15** | Verifier Gate | **Permissive Prefix Matching Masking Ungrounded Turns** | S2: Permissive `rw[:4] == pw[:4]` prefix check allowed ungrounded turns (L1161, L1249) to pass with fake 100% scores. | `audit_semantic_grounding.py` morphological stemming with inflection stripping and consonant de-doubling. | Evaluate turns with exact morphological tokens and multi-marker paragraph span windows (`min(markers)-4` to `max(markers)+5`). |
| **FP-16** | Verifier Gate | **Arbitrary Entity Whitelists vs. Genuine Setting Grounding** | S1, S4: Hardcoded 12-string vehicle whitelist missed realia or flagged legitimate synonyms (`television` vs `tv`, `airplane` vs `flight`). | `verify_parity.py` expanded `SUSPECT_VEHICLES_AND_TECH` paired with `TECH_RAW_GROUNDING` alias dictionaries. | Map colloquial modern prose synonyms to raw transcript anchors. |

---

## 🔍 Detailed Root-Cause Analyses & Guardrails

### 🛑 FP-01: Abstract Storyboard Tropification
- **The Breakdown:** During early indexing, an LLM summarizes a 200-line chaotic segment with a high-level Hollywood phrase (e.g., *"The party executes a heist at the museum"*). Downstream drafting models gravitate toward the trope rather than reading the raw dialogue, hallucinating laser grids, glass cutters, and security badges.
- **Upstream Guardrail for Indexers:**
  1. Never summarize player action using movie tropes.
  2. Record the **exact mechanism used by the players** (e.g., *"Pierre runs a social bluff pretending to be a French intern with a pull-string toy"*).
  3. Include 2-3 key verbatim anchor phrases in the manifest.

---

### 🛑 FP-02: Synthetic Integer Line Stamping (The Integer Illusion)
- **The Breakdown:** When a drafting agent invents text, it blindly appends a line number from the scene range (e.g., `<!-- L1620 -->`) so that the arithmetic in `verify_parity.py` balances.
- **The Fix:** `audit_semantic_grounding.py` extracts the text at `L1620` and checks speaker identity, word stems, and named entities. If the model attached `<!-- L1620 -->` to a sentence with zero relationship to what was spoken at that line, it triggers an immediate build failure.

---

### 🛑 FP-03: Premature Resolution & Cliffhanger Erasure
- **The Breakdown:** The model feels a subconscious pressure to "wrap up" a chapter neatly with the party returning safely to their home base, accidentally writing an imaginary escape that never happened.
- **Upstream Guardrail for Writers:**
  - Tabletop sessions frequently end on tense, unresolved cliffhangers (e.g., sirens blaring, security shutters falling, guards reaching for alarm buttons).
  - **Rule:** Never resolve a conflict or return characters to base unless the DM explicitly narrated the return before the session ended.

---

### 🛑 FP-04: Spatial & Physical Misplacement
- **The Breakdown:** Translating an interdimensional doorway as leading directly into an interior room rather than an exterior outbuilding.
- **Upstream Guardrail for Writers:**
  - The DM's initial description of terrain, lighting, and exterior doors sets the physical coordinate system.
  - In Session 3, Dravin specifically propped the annex door open so the party wouldn't get locked out while crossing the parking lot to the main museum. If the characters were already inside, this action would be nonsensical.

---

### 🛑 FP-05: Canon Dialogue Smuggling via OOC Skips
- **The Breakdown:** When players engage in long, rambling comedic banter, models sometimes find it easier to mark all 30 lines as `(ooc)` skips and write a generic summary sentence.
- **Upstream Guardrail for Writers:**
  - **Dramatic Adaptation Freedom:** Writers are encouraged to compress 30 lines of banter into 2-3 sharp, witty dialogue lines.
  - **Correct Ledger Tagging:** If lines are compressed into literature, they must be marked as `(compressed)` or `(banter)`, not `(ooc)`. The auditor flags any `(ooc)` skip that contains substantive character dialogue.

---

### 🛑 FP-06: Over-Compression & Micro-Paragraph Choppiness
- **The Breakdown:** In an attempt to avoid hallucinating props, drafting agents over-compress rich 30-turn planning segments into 1-2 sentence paragraphs with repetitive sentence structures (*"Pierre examined... Pierre examined..."*).
- **Upstream Guardrail for Writers:**
  - Character deductions and collaborative planning should be depicted through active dialogue and physical interaction with the scene.
  - Vary sentence openings and ensure paragraphs carry rhythmic narrative momentum.

### 🛑 FP-07: Dialogue Bluff Flattening
- **The Breakdown:** Reducing a 40-turn extended comedic social encounter (such as Pierre's first-day intern bluff) to a single dry statement loses the table's unique humor and character voice.
- **Upstream Guardrail for Writers:**
  - Retain character mispronunciations, geographical confusions, and the antagonist NPC's vanity/pride.
  - Maintain the balance between tension and tabletop wit.

---

### 🛑 FP-08: 3rd-Person Player Intent Leaking into Spoken Dialogue
- **The Breakdown:** Players at the table frequently describe their character's emotions, theories, and mechanical intents in the 3rd person (e.g., *"Alfie is absolutely shook to his wooden core,"* *"Pierre thinks Gorgons are French"*). Naive drafting agents wrapped these turns in quotation marks as in-character speech, resulting in characters bizarrely narrating their own internal state in the 3rd person like sportscasters.
- **Upstream Guardrail for Writers:**
  1. Distinguish 1st/2nd-person in-world spoken dialogue (`"..."`) from 3rd-person intent descriptions.
  2. Novelize 3rd-person intent descriptions into **Narrator Prose, physiological reactions, or physical blocking** (e.g., *Alfie stood frozen, his carved cedar joints trembling beneath his coat*).
  3. Never place `<Character Name> is...` or `<Character Name> thinks...` inside quoted speech bubbles.

---

### 🛑 FP-09: Multi-Speaker Paragraph Fusion & Color Monopoly
- **The Breakdown:** Fusing multiple character actions or lines into a single paragraph (e.g., Alfie casting *Mage Hand* to drop a pot followed immediately by Pierre's attendant rescue quip) causes downstream manifest generators and TTS engines to assign the entire paragraph block to a single `speakerId`. On the web reader, this turns Alfie's action into Pierre's blue dialogue bubble.
- **Upstream Guardrail for Writers:**
  1. **One Speaker Turn Per Paragraph Invariant:** Every speaker transition, distinct character action focus, or NPC dialogue retort must be placed in its own dedicated markdown paragraph.
  2. Never bundle one character's action in the same paragraph as another character's quoted dialogue.

---

### 🛑 FP-10: Phonetic Speech-to-Text & Regional Accent Drift
- **The Breakdown:** Speech-to-text models (e.g., Whisper) struggle with heavy accents (French, Cockney, Southern drawl) and unfamiliar proper nouns. Examples include French *"Pair-ey"* (Paris) transcribed as *"Brittany"*, and Southern receptionist *"Nincy"* transcribed as *"Nancy"*, stripping away the humor of her spelling correction.
- **Upstream Guardrail for Writers:**
  1. Cross-reference character introductions in raw indexed transcripts against `campaign/characters/` dossiers.
  2. Maintain a phonetic correction dictionary in downstream alias matchers (`generate_web_manifest.py`).

---

### 🛑 FP-11: Chapter Architecture Fragmentation (Micro-Chaptering)
- **The Breakdown:** Generating an EPUB where each ~100-line processing block is titled `## CHAPTER XX` created 32 single-sentence / 200-word chapters for a 4-session book, destroying novelistic flow and reader immersion.
- **Upstream Guardrail for Writers:**
  1. **Decouple Processing Blocks from Novel Chapters:** Use modular blocks (`sN-scene-XX.md`) for atomic audio and context window generation, but aggregate them into **2 to 4 substantial thematic chapters** per session in the EPUB.
  2. Use scene break ornaments (`---` / `<hr class="ornament"/>`) to demarcate scene shifts within chapters.

---

### 🛑 FP-12: Mechanics-As-Dialogue (Anime Spell Shouts)
- **The Breakdown:** When players declare actions at the table (*"I cast Chill Touch!"*, *"Toll the Dead!"*), drafting models had characters shout the literal 5e spell names out loud as dialogue.
- **Upstream Guardrail for Writers:**
  1. Translate mechanical spell declarations into visceral sensory manifestations, necrotic chill, runic hums, and in-world Latinate/archaic incantations.
  2. Never have a serious dramatic character scream raw D&D PHB mechanics as combat dialogue.

---

### 🛑 FP-13: Silent Speaker Fallback to Narrator on GM-Voiced NPCs
- **The Breakdown:** In raw indexed transcripts, the GM voices all NPCs (e.g., `**Luke Foreman:** "We are sent to resolve the subjects at hand..."`). Because `load_raw_indexed_speakers` mapped `Luke Foreman` to `"narrator"`, downstream manifest generation parsed in-character NPC quotes as `speakerId: "narrator"`. On the web reader, this caused character speech to display in dull gray narrator colors instead of canonical character colors (Gordon purple, Nincy pink, Theodore amber).
- **Upstream Guardrail for Indexers & Engineers:**
  1. Declare explicit `dialogue_speakers` line mappings in `sN-session-config.json` linking GM line numbers to canonical character registry keys.
  2. `verify_manifest.py` Invariant 6 strictly asserts that 100% of segments with `type: "dialogue"` have `speakerId != "narrator"` and a valid character hex color.

---

### 🛑 FP-14: Mid-Block Multi-Paragraph Line Marker Loss
- **The Breakdown:** When a single character speaks for multiple paragraphs, prose authors place the `<!-- Lxxxx -->` line marker only on the final paragraph (or opening paragraph) to comply with `verify_parity.py`'s rule against duplicate turn markers. Earlier manifest generators treated unanchored paragraphs as having `source_line: None` and silently fell back to `"narrator"`.
- **Upstream Guardrail for Manifest Builders:**
  1. Implement line marker propagation across contiguous paragraphs within the same scene. If a dialogue paragraph lacks an explicit anchor, it inherits the active scene/turn `sourceLine` from the preceding turn.

---

### 🛑 FP-15: Permissive Prefix Matching Masking Ungrounded Turns (The 4-Character Loophole)
- **The Breakdown:** `audit_semantic_grounding.py` previously checked `rw[:4] == pw[:4]`, causing any word sharing a 4-letter prefix to count as grounded (e.g., `star` matching `startled`, `with` matching `within`). This generated false 100% pass rates while masking completely ungrounded turns (e.g. S2 Scene 7 where L1161 and L1249 had zero token overlap with the prose).
- **Upstream Guardrail for Verifiers:**
  1. Enforce strict morphological stemming with inflection stripping (`-ing`, `-ed`, `-es`, `-ly`, `-tion`) and English consonant de-doubling (`dropp` $\rightarrow$ `drop`).
  2. For fused-marker paragraphs (`<!-- L0330 --> <!-- L0343 -->`), evaluate the entire raw transcript span across all markers (`min(markers)-4` to `max(markers)+5`).

---

### 🛑 FP-16: Arbitrary Entity Whitelists vs. Genuine Setting Grounding
- **The Breakdown:** `verify_parity.py` previously used a static 12-string vehicle list that missed modern tech or flagged legitimate colloquial expressions (e.g., flagging `television` when the transcript had `TV`, or flagging `airplane` when the transcript had `flight 422`).
- **Upstream Guardrail for Verifiers:**
  1. Expand the suspect realia check across common modern anachronisms (`elevator`, `keycard`, `sedan`, `suv`, `laser`, `airplane`, `jetliner`, `cellphone`, `television`, `computer`, `satellite`).
  2. Provide `TECH_RAW_GROUNDING` alias dictionaries that map prose terms back to raw transcript synonyms (`television` $\leftrightarrow$ `tv`, `airplane` $\leftrightarrow$ `flight`, `sedan` $\leftrightarrow$ `car`/`parking`).

---

## ⚖️ Guidelines for Downstream Creative Dramatic Freedom

To ensure downstream writers have the freedom to write gripping, elevated prose without triggering false audit alarms:

1. **Sensory & Atmospheric Description is Free:** Writers are fully empowered to add sensory texture (*"amber lantern light," "pine knots," "air-conditioned atrium," "smell of ozone"*).
2. **Mechanics-to-Narrative Translation is Encouraged:** Translating a `Nat 20 Divine Sense` into *"A natural twenty flared in his blood, revealing the consecrated refuge shrouded by the Mist"* is 100% compliant.
3. **Dialogue Compression is Supported:** Converting 15 turns of rules discussion into a single polished in-character line is welcomed, provided the core claim and speaker attribution are preserved.
4. **World-State Entities Must Be Grounded:** Never introduce new vehicles, high-tech security systems, or foreign NPCs without grounding in the raw transcript.