# Pipeline Decision & Historical Discussion Ledger

This document is the **canonical, living single source of truth** for all architectural decisions, user critiques, agreed trade-offs, and invariants established across the 15+ editions of the D&D Scribe publishing engine.

Every entry records:
- **What happened** (The friction, user critique, or failure)
- **What historical precedent applied**
- **What decision was made and what cost was accepted**
- **What mechanical gate guarantees it won't regress**

---

## 📜 Complete Historical Decision Registry (`DEC-001` to `DEC-019`)

### [DEC-001] Edition 1: Raw Indexed Immutable Transcript Foundation
* **Context & Friction:** Early novelization drafts suffered from phantom lines, lost dialogue turns, and non-reproducible line numbers whenever audio re-transcription occurred.
* **Root Cause:** Re-running Whisper STT overwrote previous timestamps and line breaks, breaking downstream novel scene block line references.
* **Agreed Decision & Protocol:**
  1. Immutable `sN-raw-indexed.md` established as Tier 1 ground truth.
  2. Every raw line is locked with permanent `L####:` prefix.
  3. SHA-256 hash locking implemented in `manifest.json`.
* **Enforcing Gate:** `verify_manifest.py` SHA-256 hash check.

---

### [DEC-002] Edition 2: The 3-Tier Line Categorization Law
* **Context & Friction:** Cleaners struggled to decide what to do with table mechanics (dice rolls, DC numbers, Wi-Fi drops) vs roleplay. Models either novelized pizza orders or erased spell manifestations.
* **Root Cause:** Lack of formal taxonomy for tabletop recording audio.
* **Agreed Decision & Protocol:**
  1. **Tier A (In-World Dialogue):** Spoken character speech (`**[[Speaker]]:** "..."`).
  2. **Tier B (Player Action & Lore Intent):** Tactical descriptions, spellcraft manifestations, environment details. Mandatorily novelized into narrator prose; dice math stripped.
  3. **Tier C (Technical Meta Table Talk):** Connection issues, rules queries, out-of-game banter. Skipped with explicit reason tag (`(ooc)`, `(banter)`, `(mechanics)`).
* **Enforcing Gate:** `verify_parity.py` approved skip reason validation.

---

### [DEC-003] Edition 3: The Green Ford Truck & Semantic Hallucination Scanner (`FP-01`)
* **Context & Friction:** In Session 3, the upstream LLM hallucinated the party driving a modern pickup truck down an asphalt highway to Raleigh, completely erasing the canonical *Lost Roads* transit through Theodore's maintenance shed. Later, a museum social bluff was turned into a Hollywood heist with laser grids.
* **Root Cause:** Parity gates only verified line arithmetic ($\sum \text{rendered} + \sum \text{skipped} = \text{total}$), ignoring semantic hallucinations. LLMs defaulted to generic Hollywood tropes when context was thin.
* **Agreed Decision & Protocol:**
  1. Built `audit_semantic_grounding.py` and `SUSPECT_VEHICLES_AND_TECH` regex scanner in `verify_parity.py`.
  2. Banned modern unanchored realia (`truck`, `car`, `helicopter`, `subway`, `laser`, `laptop`, `wifi`) unless present in the raw transcript window.
  3. Enforced mandatory Tier B setting anchors (`maintenance shed`, `lost roads`, `stele`).
* **Enforcing Gate:** `verify_parity.py` (`HALLUCINATED ENTITY`) & `audit_semantic_grounding.py`.

---

### [DEC-004] Edition 4: Acoustic & Phonetic STT Drift Protocol (`FP-02`)
* **Context & Friction:** Whisper STT transcribed Luke S's pronunciation of Paris (*"Pair-ey"*) as Brittany provincial landmarks, and Nincy's southern self-introduction (*"Nincy with an I... N-I-N-C-Y"*) as *"Nancy"*, ruining the spelling humor.
* **Root Cause:** Automated Speech Recognition models substitute phonetically adjacent English dictionary words for regional accents and fantasy proper nouns.
* **Agreed Decision & Protocol:**
  1. Established Character Dossier Phonetic Tables (`campaign/characters/`).
  2. Built `audit_transcript_gaps.py` scanning transcripts for self-referential spelling phrases (*"with an I"*, *"spelled with"*).
  3. Built `TECH_RAW_GROUNDING` and phonetic alias mapping in `generate_web_manifest.py`.
* **Enforcing Gate:** `audit_transcript_gaps.py` and `CHARACTER_REGISTRY`.

---

### [DEC-005] Edition 5: Third-Person Table Intent vs. In-World Speech (`FP-03`)
* **Context & Friction:** In Session 4, PR #004 revealed Sophie's table narration (*"Alfie is absolutely shook to his wooden core"*) was put into dialogue quotes as `Alfie: "Alfie is absolutely shook to his wooden core."` Luke S's tactical rationale was quoted as `Pierre: "Pierre believes that all Gorgons are French!"`
* **Root Cause:** Tabletop players alternate between 1st-person speech and 3rd-person intent narration. Blind 1:1 attribution converted player meta-commentary into self-narrating dialogue.
* **Agreed Decision & Protocol:**
  1. Established the **3rd-Person Intent Invariant:** 3rd-person player descriptions must be novelized as Narrator Prose / physical staging, never enclosed in dialogue quotes (`"..."`).
  2. Implemented the self-reference linter in `critique_prose.py` flagging `"<CharacterName> is..."` or `"<CharacterName> thinks..."` inside quotes.
* **Enforcing Gate:** `critique_prose.py` self-reference dialogue scan.

---

### [DEC-006] Edition 6: One Speaker Turn Per Paragraph Invariant (`FP-04`)
* **Context & Friction:** In Session 4 (PR #004 & #005), Alfie's *Mage Hand* pot drop and Pierre's shout were bundled into a single paragraph. The Web Reader assigned the entire block to Pierre (`#3b82f6`), turning Alfie's action into Pierre's dialogue color. In S3, the curator's retort was monopolized by Pierre's blue color.
* **Root Cause:** Standard novel formatting permits companion actions in single paragraphs, but interactive web readers and multi-voice ElevenLabs TTS route voice models and UI colors per block.
* **Agreed Decision & Protocol:**
  1. Enforced the **One Speaker Turn Per Paragraph Invariant:** Every speaker transition, distinct character action, or NPC retort must occupy its own dedicated markdown paragraph.
  2. Implemented Schema 2.0 sub-block segmenter decomposing mixed paragraphs into distinct `"dialogue"` and `"narration"` segments with individual `speakerId` attributes:
     $$\sum_{s \in \text{block.segments}} s.\text{text} \equiv \text{block}.\text{text}$$
* **Enforcing Gate:** `verify_manifest.py` sub-block segment validation.

---

### [DEC-007] Edition 7: Decoupled Architecture (Scene Blocks vs. EPUB Chapters) (`FP-05`)
* **Context & Friction:** In Sessions 2 and 3, readers complained about "32-chapter novel bloat" where individual chapters had as few as 60 words (single conversational exchanges).
* **Root Cause:** Coupling internal 100-line processing chunks directly to consumer-facing novel chapters (`## CHAPTER XX`).
* **Agreed Decision & Protocol:**
  1. Decoupled internal LLM processing units (`sN-scene-XX.md`) from consumer novel chapters.
  2. Modular scene blocks (~100-150 lines) remain atomic for LLM context, but are aggregated into **2 to 4 thematic chapters** per session in `novel/sessions/` and EPUB.
  3. Added EPUB Chapter Pacing Gate issuing warnings for chapters $< 250$ words and $> 6$ chapters per session.
* **Enforcing Gate:** `novel/generate_epub.py` and `verify_parity.py`.

---

### [DEC-008] Edition 8: The Anti-Hollow Gate Overhaul (`FP-07` to `FP-10`)
* **Context & Friction:** Forensic audit (`pipeline_hollow_audit.md`) revealed that several core verification scripts were "hollow" gates:
  - `critique_prose.py` exited code 0 even when flagging critical review errors.
  - `verify_manifest.py` checked integer line counts but permitted empty string prose blocks.
  - `audit_semantic_grounding.py` used a 4-character prefix match (`star` matched `startled`), trivially passing hallucinations.
* **Root Cause:** Test suites written to verify output existence rather than adversarial correctness.
* **Agreed Decision & Protocol:**
  1. `critique_prose.py` updated to return non-zero exit codes on fatal defects.
  2. `verify_manifest.py` updated to verify prose content length, title presence, and non-empty blocks.
  3. Grounding checks tightened beyond loose stem matching.
* **Enforcing Gate:** `run_publishing_pipeline.py` zero-tolerance exit codes.

---

### [DEC-009] Edition 9: The Local Patching Trap & Purge of Regex Guesswork (`FP-11`)
* **Context & Friction:** For four consecutive PRs (#001, #003, #004, #005), agents repeatedly patched regex dictionaries (`SPEAKER_ALIASES`, `speech_verbs`) whenever dialogue misattributions occurred, only for the next session to fail again with new verbs.
* **Root Cause:** Inverted provenance flow. Tools tried to infer speakers from prose syntax rather than reading origin-time line metadata.
* **Agreed Decision & Protocol:**
  1. Completely deleted `SPEAKER_ALIASES`, `speech_verbs`, and `else: pierre` fallbacks from `generate_web_manifest.py`.
  2. Established the **Zero-Regex Dialogue & Origin-Time Provenance Law:** Speaker identity is locked at creation time via line anchors (`<!-- Lxxxx -->`). Downstream tools must NEVER guess who is speaking.
  3. Codified in `AGENTS.md` Section 2.1.
* **Enforcing Gate:** `verify_manifest.py` and `generate_web_manifest.py`.

---

### [DEC-010] Edition 10: The Adaptation Boundary Law & Pushback Protocol (`FP-12`)
* **Context & Friction:** Reviewers asked for deep existential interiority for Dravin regarding Persephone's letter in Session 3, and criticized Alfie's passivity in Scenes 4–7.
* **Root Cause:** Reviewers treating collaborative tabletop novelization as an unconstrained fiction sandbox. Fulfilling the request would require fabricating internal arcs that pre-empt or contradict future player roleplay.
* **Agreed Decision & Protocol:**
  1. Codified the **Adaptation Boundary Law:** *"Novelization is an adaptation of collaborative human play, NOT an ungrounded generative sandbox."*
  2. Mandated that agents must **PUSH BACK** against editorial critiques that require inventing net-new plot encounters, fabricated player words, or contradict future canon.
  3. Transferred speculative questions to `s(N+1)-context-briefing.md` for players to address organically.
* **Enforcing Gate:** Editorial Pushback Protocol in `CRITIQUE_LOG.md`.

---

### [DEC-011] Edition 11: Marker Drag, Turn Inversion, and Invariant 4 (`FP-13`)
* **Context & Friction:** In Session 5 integration, 6 severe dialogue misattributions occurred (Pierre assigned to `dravin`, Alfie assigned to `attendant`) because adjacent markers bled across paragraphs, and `verify_manifest.py` emitted `[PASS]` anyway.
* **Root Cause:** `verify_manifest.py` verified that `speakerId != "narrator"`, but never verified whether `speakerId` matched the character speaking in the text.
* **Agreed Decision & Protocol:**
  1. Implemented `detect_in_text_dialogue_speaker()` in `generate_web_manifest.py`.
  2. Added **Invariant 4** to `verify_manifest.py`: Dialogue speaker in manifest MUST match in-text character speech tags.
* **Enforcing Gate:** `verify_manifest.py` Invariant 4 check.

---

### [DEC-012] Edition 12: Dual-Track Production Architecture (Track A vs Track B)
* **Context & Friction:** Creative novelization requires high narrative velocity and cinematic flow, but audiobook and archival research require strict 1:1 line traceability. Forcing both into a single text caused constant conflict between Sanderson prose and line-by-line fidelity.
* **Root Cause:** Monolithic delivery format attempting to satisfy two incompatible stakeholder goals.
* **Agreed Decision & Protocol:**
  1. Formalized the **Dual-Track Architecture:**
     - **Track A (`blocks/`):** Tabletop Cut. 100% monotonic line coverage, individual `<!-- Lxxxx -->` line anchors, verbatim quotes, mathematical ledger parity.
     - **Track B (`blocks_authorial/`):** Cinematic Cut. High-velocity set-pieces, coarse line spans (`<!-- Lxxxx-Lyyyy -->`), fluid staging, bounded by Intent Contracts.
* **Enforcing Gate:** Dual directories and synchronized manifest diff inspector.

---

### [DEC-013] Edition 13: Dual Rotten Tomatoes Scoring in Reader App
* **Context & Friction:** Readers evaluate tabletop novelizations along two distinct axes: literary craft vs table energy. A low-word-count session might be brilliant roleplay but polarizing literature.
* **Root Cause:** Single composite review scores obscured whether flaws were in the original game or the novelization craft.
* **Agreed Decision & Protocol:**
  1. Ingested dual Rotten Tomatoes metrics: **Tomatometer** (Literary Craft) vs **Popcornmeter** (Table Energy).
  2. Created `#endSessionCriticCard` in `build_ebooks.py` with interactive chapter modal navigation and participant scorecards.
* **Enforcing Gate:** `generate_web_manifest.py`, `dndwikis-main/build_ebooks.py`.

---

### [DEC-014] Edition 14: Track A Strict Ban on Unanchored Dialogue Quotes
* **Context & Friction:** Downstream TTS and web manifests encountered quoted dialogue paragraphs without line markers, causing fallback to previous speakers or narrator misattribution.
* **Root Cause:** Prose drafters inserting summarized or connective dialogue quotes without attaching raw line provenance.
* **Agreed Decision & Protocol:**
  1. Track A strictly forbids any quoted text (`"..."`) without a trailing `<!-- Lxxxx -->` line anchor.
  2. Every dialogue turn must originate from `sN-session-config.json` and `sN-raw-indexed.md`.
* **Enforcing Gate:** `verify_parity.py` (`UNANCHORED DIALOGUE QUOTE`).

---

### [DEC-015] Edition 15: Intent Parity Contracts & Decoupled Verification
* **Context & Friction:** PR #33 review revealed authorial drift where Pierre was rewritten as a calculating heist accomplice and Dravin's unilateral physical force on Alfie was sanitized into polite mutual consent.
* **Root Cause:** Editorial models smoothing out table friction into Hollywood tropes.
* **Agreed Decision & Protocol:**
  1. Established Double-Blind Intent Parity (`verify_intent_parity.py`).
  2. Decoupled session-specific intent rules out of the Python script into `sessions/config/{session_id}-intent-contract.json`.
  3. Created `s6-intent-contract-template.json` to enforce intent boundaries before drafting begins.
* **Enforcing Gate:** `sessions/_scripts/verify_intent_parity.py`.

---

### [DEC-016] 2026-09-26: The Inclusive Fiction Law & Canon Lore Skip Guardrail
* **Context & Friction:** Over-aggressive OOC tagging in past editions caused accidental lore amputation (e.g. cutting out GM timeline explanations or player deductions because they were labeled OOC).
* **Root Cause:** Cleaners defaulting to Tier C when players joke or speak casually.
* **Agreed Decision & Protocol:**
  1. Default to Tier B (Lore & Action Intent) rather than Tier C (Technical Table Talk).
  2. Updated `sessions/_scripts/verify_parity.py` with the **Canon Lore Guardrail**: Any turn skipped as `(ooc)` or `(banter)` that matches protected canon entities (`Persephone`, `Thanatos`, `Reductor`, `STALE`, `Chaos Belt`, `Fate Loom`, `Lost Roads`, `Thorne`, `Gorgon`, `1948`) causes an immediate build failure unless explicitly listed in `legitimate_ooc_lore_skips` in `session-config.json`.
* **Enforcing Gate:** `verify_parity.py` `[CANON_LORE_IN_SKIPPED_LEDGER]`. Verified via negative adversarial test.

---

### [DEC-017] 2026-09-26: Anti-Sycophancy & Active Trade-Off Decision Ledger
* **Context & Friction:** The user remarked: *"I just really hate seeing everything passes all the time. I feel like we should be seeing trade-off decisions were made or something to give us confidence that it's not just gaslighting."*
* **Root Cause:** The pipeline runner previously terminated with a simple `🏆 ALL GATES PASSED` cheerleading banner, hiding marker pile-ups, compression sacrifices, and polarizing Tomatometer scores.
* **Agreed Decision & Protocol:**
  1. Abolished empty celebratory passing banners.
  2. The runner mandatorily outputs the **Editorial Trade-Off & Tension Decision Ledger**, surfacing:
     - The critical split: e.g. 62% Tomatometer (Grade D) vs 94% Popcornmeter.
     - The explicit human sign-offs (whitelisted skipped lore lines).
     - Dialogue turn fusions (paragraphs with >3 turns merged).
     - Structural trade-offs (narrative velocity vs. casual table humor).
* **Enforcing Gate:** Invariant 7 in `docs/pipeline_architecture.md` and `run_publishing_pipeline.py`.

---

### [DEC-018] 2026-09-26: Dual-Track Evaluation Scorecard & Scalable Creative Liberty Grading
* **Context & Friction:** The user wanted to see a scalable, honest version of grading that proves **Track A (Tabletop Cut)** is near-perfect on transcript fidelity (~100%), while **Track B (Cinematic Cut)** explicitly shows grades and where creative liberties were taken.
* **Agreed Decision & Protocol:**
  1. Updated `run_publishing_pipeline.py` with `render_dual_track_scorecard(sessions)`.
  2. **Track A Scorecard:** Evaluates monotonic line coverage, exact ledger partition, dialogue quote anchoring, and canon lore preservation. Grades at `[A+] Strict Tabletop Canon Locked`.
  3. **Track B Scorecard:** Evaluates word compression ratio, calculates the **Creative Liberty Index**, tracks coarse multi-turn spans, and checks intent invariants.
  4. **Itemized Creative Liberties:** Pulls `authorial_liberties` directly from `sessions/config/{session_id}-intent-contract.json` (or derives from span merges), detailing exactly which scenes took liberties, what was changed, and the narrative impact.
* **Enforcing Gate:** `sessions/_scripts/run_publishing_pipeline.py` step 6.

---

### [DEC-019] 2026-09-26: The Pipeline Steward & Anti-Amnesia Skill Creation
* **Context & Friction:** The user expressed intense, justified frustration with agentic amnesia and false novelty: *"This is not a new idea or new discussion either... I need a skill that exists as an interface between me and you whenever we talk about the pipeline so that ideas and issues with the pipeline are documented and referenced consistently and we don't regress. Or I don't hear you saying that's such a wonderful idea. Why didn't we think about that when we already have talked about it before."*
* **Root Cause:** LLMs defaulting to generic sycophancy (*"What a wonderful idea!"*) and forgetting that dual tracks, intent contracts, and trade-off ledgers had already been extensively discussed and designed across 15 editions.
* **Agreed Decision & Protocol:**
  1. Created `.agents/skills/pipeline-steward/SKILL.md` as the dedicated interface for pipeline discussions.
  2. Banned all faux-epiphany / sycophantic responses on pipeline topics.
  3. Mandated searching `PIPELINE_DECISION_LEDGER.md` and `docs/pipeline_architecture.md` *before* answering any pipeline query.
  4. Mandated logging every new architectural decision directly into this ledger.
* **Enforcing Gate:** `.agents/skills/pipeline-steward/SKILL.md` and `.agent/AGENTS.md` integration.

---

### [DEC-020] 2026-09-26: Dwight Swain Motivation-Reaction Units (MRUs) & Deterministic Deep-POV Stylistic Linters
* **Context & Friction:** Review of an external autonomous novelization report proposing Dwight Swain MRUs, deep POV, windowpane styling, and filter-word eradication for tabletop-to-novel pipelines.
* **Invariant Guardrails & Rejections:**
  1. *Rejected Dialogue Transmutation:* The report's proposal to transmute transcript speech into synthetic dialect was firmly rejected for Track A. Spoken dialogue inside quotes remains immutable and anchored to clean transcript turns (`DEC-001`, `DEC-009`, `DEC-010`).
  2. *Rejected Monolithic LLM OOC Stripping:* Unanchored single-pass LLM extraction was rejected due to historical precedent `FP-20` (Silent OOC Lore Amputation).
* **Agreed Decision & Protocol:**
  1. **Swain's MRU Sequence for Combat & Action Beats:** In Tier B mechanical novelization and Track B cinematic action, enforce the neuro-physiological sequence:
     $$\text{External Motivation} \longrightarrow \text{Visceral Sensation} \longrightarrow \text{Involuntary Reflex} \longrightarrow \text{Deliberate Action \& Speech}$$
     Writers must not jump from external stimulus directly to dialogue or complex counter-strikes.
  2. **Deterministic Deep-POV Static Linters:** Added non-LLM static regex scanners to `critique_prose.py`:
     - *Cognitive Filter Verbs:* Barring narrative framing via `saw`, `heard`, `felt`, `noticed`, `wondered`, `realized` followed by clausal objects. Limit: $\le 4.0$ per 1,000 words.
     - *Syntactic Cadence & Participial Monoculture:* Limiting sentence-initial participial clauses (`^[A-Z][a-z]+ing...`) to $\le 1.0$ per 500 words to enforce rhythmic variety.
     - *Windowpane Synthetic Tropes:* Static dictionary flagging purple generative clichés (`"tapestry of"`, `"palpable tension"`, `"dance of blades"`, `"silent understanding"`, `"testament to"`, `"unspoken bond"`, `"cacophony of"`).
  3. **Try-Fail Cycles for Track B:** Coarse multi-turn span condensation in Track B authorial cuts must be structured around "Yes, but..." or "No, and..." conflict progression.
* **Forensic Git Case Study (Commit Anchor):**
  - **Reference Branch:** `origin/devin/1790479715-s5-fidelity-cuts` (Commit `54c9d3a623a19b64648319441c78667b5377fd15`).
  - **Artifact Evaluated:** `docs/s5-fidelity-comparison.md` and `sessions/data/index/s5-source-decisions.json`.
  - **Post-Mortem Learning:** An alternative agent attempted to resolve "unsupported staging" by stripping sensory grounding and Swain MRUs entirely, reducing the climactic Scene 10 into 172 words of flat administrative bullet points. This demonstrated the fatal pitfall of "Character Logging": eliminating authorial immersion destroys dramatic fiction.
  - **Adopted Forensic Boundary:** While rejecting the anemic prose rewrite, the audit correctly proved that L1251–L1257 was an unplayed cliffhanger before combat, affirming that forward weapon-drawing in Scene 10 should be framed as a closing tension beat or cut cleanly at the cutoff.
* **Enforcing Gate:** `.agents/skills/novel-critic/scripts/critique_prose.py` (Deep-POV & Cadence Analyzer), `.agent/AGENTS.md` Section 4.

---

## 📌 Rules for Appending to this Ledger
Whenever an architectural discussion occurs:
1. Do not repeat arguments that have already been resolved.
2. Quote the relevant `DEC-XXX` or `FP-XX` entry.
3. If an invariant must be modified, state what broke to necessitate the change, what cost is accepted, and how the verification suite is updated.
