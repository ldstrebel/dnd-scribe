# 🏛️ Architecture Specification: Deterministic & Independent Transcript-to-Publishing Pipeline

## Executive Overview
The **D&D Scribe Publishing Engine** transforms raw, chaotic tabletop RPG session recordings and multi-speaker transcripts into high-fidelity fantasy novels, audiobooks, and web manifests.

To guarantee that the pipeline remains **strictly independent, non-biased, and deterministic**, the system enforces an adversarial gate architecture where no drafting agent evaluates its own output. Prose generation is decoupled from verification, and mathematical invariants govern every transformation.

The publishing engine operates on a **Dual-Track Architecture**:
1. **Track A (Canonical Archival Cut):** 100% Monotonic line-by-line coverage, strict transcript parity, and comprehensive ledger accounting (`rendered=[...] skipped=[...]`).
2. **Track B (Authorial Cut):** Pacing-optimized, compacted scene set-pieces with coarse line spans (`<!-- Lxxxx-Lyyyy -->`) for rapid novelistic momentum while preserving core character emotion, voice, and lore anchors.

---

## 🗺️ Pipeline Architecture: Dual-Track Publishing Engine

```mermaid
flowchart TD
    subgraph S1["LANE 1: RAW INGESTION & GROUND TRUTH"]
        direction TB
        RAW_AUDIO["Raw Multi-Mic Audio / Discord"] --> STT["ASR / Whisper STT Engine"]
        STT --> RAW_MD["Raw Indexed Transcript<br/><code>sN-raw-indexed.md</code><br/><i>Immutable L#### Indices</i>"]
        CFG["Session Config<br/><code>sN-session-config.json</code><br/><i>Declared PCs, NPCs, Mics</i>"] -.-> CLEANER
        RAW_MD --> CLEANER["Transcript Cleaner & Speaker Auditor"]
    end

    subgraph S2["LANE 2: AUDIT & PARITY MATRIX"]
        direction TB
        CLEANER --> CLEAN_MD["Clean Attributed Transcript<br/><code>sN-clean.md</code><br/><i>Audited Turns & OOC Demarcation</i>"]
        CLEAN_MD --> TIER_SPLIT{"3-Tier Classification Gate"}
        TIER_SPLIT -->|"Tier A: Spoken"| TIER_A["In-World Spoken Dialogue<br/><code>**[[Speaker]] (PC/NPC):**</code>"]
        TIER_SPLIT -->|"Tier B: Action & Intent"| TIER_B["Tactical Intent & Lore<br/><i>Sensory manifest, spells, terrain</i>"]
        TIER_SPLIT -->|"Tier C: Pure Meta"| TIER_C["OOC Table Talk<br/><i>Wi-Fi drops, pizza, roll dice</i>"]
    end

    subgraph S3["LANE 3: DUAL-TRACK STORY GENERATION"]
        direction TB
        TIER_A & TIER_B --> DRAFTER_ARCH["Archival Drafter<br/><i>1:1 Line Fidelity</i>"]
        TIER_A & TIER_B --> DRAFTER_AUTH["Authorial Drafter<br/><i>Compacted Pacing & Spans</i>"]
        DRAFTER_ARCH --> BLOCKS_ARCH["Archival Blocks<br/><code>sN-scene-XX.md</code><br/><code>&lt;!-- Lxxxx --&gt;</code> Markers"]
        DRAFTER_AUTH --> BLOCKS_AUTH["Authorial Blocks<br/><code>sN-scene-XX-alt.md</code><br/><code>&lt;!-- Lxxxx-Lyyyy --&gt;</code> Spans"]
    end

    subgraph S4["LANE 4: ADVERSARIAL VERIFICATION SUITES"]
        direction TB
        BLOCKS_ARCH --> GATE_PARITY["Gate 1A: verify_parity.py<br/><i>100% Monotonic Ledger Invariant</i>"]
        BLOCKS_ARCH --> GATE_GROUND["Gate 2A: audit_semantic_grounding.py<br/><i>Token Overlap & Foreign Props</i>"]
        BLOCKS_ARCH --> GATE_CRITIC["Gate 3A: critique_prose.py<br/><i>Prose Telemetry & Earth-Leaks</i>"]
        
        BLOCKS_AUTH --> GATE_ALT["Authorial Suite: verify_alternate_scene.py<br/><i>3-Gate Deterministic Linter</i><br/>1. Entity & Relic Anchor Coverage<br/>2. Leak & Foreign Prop Barrier<br/>3. Span Provenance & Compression Bounds"]
        
        GATE_PARITY & GATE_GROUND & GATE_CRITIC --> PASS_ARCH{"Archival Pass?"}
        GATE_ALT --> PASS_AUTH{"Authorial Pass?"}
    end

    subgraph S5["LANE 5: DOWNSTREAM CONSUMPTION & READER"]
        direction TB
        PASS_ARCH -->|Pass 100%| MANIFEST_GEN["Schema 2.0 Web Manifest Engine<br/><code>generate_web_manifest.py</code>"]
        MANIFEST_GEN --> WEB_MANIFEST["Web Manifest: <code>sN-manifest-v2.json</code><br/><i>Sub-Block Segments (Narration / Dialogue)<br/>100% Verbatim Invariant Guarantee</i>"]
        WEB_MANIFEST --> GATE_MANIFEST_V2["Gate 4: verify_manifest.py<br/><i>Schema 2.0 Invariant 6 Gate<br/>0 Narrator Dialogue & Valid Colors</i>"]
        GATE_MANIFEST_V2 -->|Pass 100%| DNDWIKIS["Downstream Reader: <code>dndwikis</code> / <code>build_ebooks.py</code><br/><i>Side-by-Side Archival vs. Authorial Diff Inspector<br/>Multi-Voice Audio Synchronization</i>"]
        PASS_ARCH & PASS_AUTH -->|Pass 100%| EPUB_GEN["Dual Edition EPUB Assembler<br/><code>novel/generate_epub.py</code>"]
        EPUB_GEN --> EPUB_OUT["Production EPUBs<br/><i>Illustrated & Text-Only</i>"]
    end

    classDef raw fill:#1e293b,stroke:#475569,stroke-width:2px,color:#f8fafc;
    classDef gate fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#93c5fd;
    classDef check fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#fca5a5;
    classDef out fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#a7f3d0;

    class RAW_AUDIO,STT,RAW_MD,CFG raw;
    class CLEANER,CLEAN_MD,TIER_A,TIER_B,TIER_C,DRAFTER_ARCH,DRAFTER_AUTH,BLOCKS_ARCH,BLOCKS_AUTH gate;
    class GATE_PARITY,GATE_GROUND,GATE_CRITIC,GATE_ALT,PASS_ARCH,PASS_AUTH check;
    class MANIFEST_GEN,WEB_MANIFEST,EPUB_GEN,EPUB_OUT,DNDWIKIS out;
```

---

## ⚖️ How We Maintain Independence, Objectivity & Determinism

### 1. Separation of Concerns (Adversarial Decoupling)
* **The Drafter Never Grades Its Own Paper:** The LLM agents that draft or compress scenes do not write the verification scripts or pass/fail decisions.
* **Deterministic Mathematical Assertions:** Automated gates ([`verify_parity.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/verify_parity.py), [`audit_semantic_grounding.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/audit_semantic_grounding.py), [`verify_manifest.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/verify_manifest.py), [`verify_alternate_scene.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/verify_alternate_scene.py)) run pure Python algorithms with zero model hallucinations:
  $$	ext{Rendered Turns} \cup 	ext{Skipped Turns} = 	ext{All Expected Dialogue Turns}$$
  $$	ext{Rendered Turns} \cap 	ext{Skipped Turns} = \emptyset$$
  Every single line in the raw transcript must be mathematically accounted for in monotonic sequence.

### 2. Zero Hallucination & Anti-Drift Guardrails
* **High-Risk Foreign Prop Checker:** Flags any modern or foreign object introduced into prose that does not exist in the raw transcript window (e.g., cars, helicopters, trucks, laptops, smartphones).
* **Suspicious Cluster Skip Detection:** Automatically halts the pipeline if $\ge 5$ consecutive spoken lines are marked as `(ooc)` skips without justification, ensuring that casual character banter and worldbuilding cannot be silently dropped.
* **Semantic Token Overlap:** For every rendered marker `<!-- Lxxxx -->`, the auditor computes the set intersection of lemmatized, non-stopword tokens between the prose paragraph and a 7-line window in the raw transcript. If token overlap is 0, the build fails with `UNGROUNDED TURN`.

### 3. The 3-Gate Deterministic Alternate Scene Verifier (`verify_alternate_scene.py`)
For Track B (Authorial Cut scenes), we avoid non-deterministic sentiment analysis or arbitrary statistical thresholds. The verifier enforces 3 deterministic checks:
1. **Gate 1: Entity & Relic Anchor Coverage:** Asserts that 100% of active PCs, NPCs, and scene relics (e.g. "daughter's card", "cucumber mask", "pancakes", "limestone") from the archival scene appear in the alternate cut.
2. **Gate 2: Leak, Slang & Foreign Prop Scanner:** Reuses `LeakDetector`, `LoreGuardian`, and `HIGH_RISK_FOREIGN_PROPS` to guarantee zero modern realia or mechanics jargon.
3. **Gate 3: Span Provenance & Compression Integrity:** Validates that `<!-- Lxxxx-Lyyyy -->` spans are monotonically increasing, cover the scene boundary, and do not completely silence any active character from the conversation.

### 4. Downstream Verbatim Contract
* Downstream readers (`dndwikis`, EPUB readers, ElevenLabs TTS pipelines) require exact speaker coloring, line provenance, and sub-block segmentation without risking text mutation.
* **The 100% Verbatim Invariant:**
  $$\sum_{s \in \text{block.segments}} s.\text{text} \equiv \text{block}.\text{text}$$
  Decomposing a paragraph into `"narration"` and `"dialogue"` must reconstruct the original block character-for-character, preserving exact whitespace, em-dashes, and punctuation.

#### 5. The Zero-Regex Dialogue & Origin-Time Provenance Law
* **Origin-Time Invariant:** Dialogue classification and speaker identities are established **at creation time** during transcript cleaning/indexing (`sN-raw-indexed.md` / `sN-session-config.json`) and prose drafting (`<!-- Lxxxx -->`).
* **Zero Post-Hoc Guesswork:** Compilers, TTS generators, and manifest builders must **NEVER** use regex, speech-verb parsers, or text searches on prose to infer who spoke.
* **Direct Provenance Lookup:**
  - In archival and creative blocks, text inside quotes (`"..."`) derives its speaker identity directly from the attached line anchor (`<!-- Lxxxx -->` or span `<!-- Lxxxx-Lyyyy -->`) mapped against `sN-session-config.json` and `sN-raw-indexed.md`.
  - Text outside quotes is unconditionally `speakerId: "narrator"`.
* **Session Config Dialogue Dictionaries:** When the Game Master voices NPCs at the table, explicit `dialogue_speakers` dictionaries in `sessions/config/sN-session-config.json` map specific raw line numbers and block overrides to canonical character IDs (`gordon`, `nincy`, `attendant`, `mike`, `theodore`, `naomi`, `rosa`, `fates`, `clerk`, `anna`).
* **Line Marker Propagation:** In contiguous multi-paragraph dialogue turns where secondary paragraphs omit markers (to avoid duplicate markers in `verify_parity.py`), `generate_web_manifest.py` propagates the active `sourceLine` forward, ensuring that dialogue segments never have `sourceLine: null` or default to `"narrator"`.
* **Schema 2.0 Invariant 6 Enforcement:** [`verify_manifest.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/verify_manifest.py) mathematically asserts that 100% of segments with `type: "dialogue"` have `speakerId != "narrator"`, an integer `sourceLine > 0`, and a valid `#RRGGBB` hex color in `CHARACTER_REGISTRY`.

---

## 🔍 Post-Mortem & Failures Experienced (Cross-Referenced with [`CRITIQUE_LOG.md`](file:///d:/Code/dnd-scribe/CRITIQUE_LOG.md))

Our pipeline hardened through resolving real-world failures tracked in [`CRITIQUE_LOG.md`](file:///d:/Code/dnd-scribe/CRITIQUE_LOG.md) and [`sessions/data/critiques/CRITIQUE_LOG.md`](file:///d:/Code/dnd-scribe/sessions/data/critiques/CRITIQUE_LOG.md):

### 1. The "Green Ford Truck" Infiltration Failure (Session 3)
* **Reference:** [`CRITIQUE_LOG.md: PR Record #002`](file:///d:/Code/dnd-scribe/CRITIQUE_LOG.md#L35-L56)
* **Failure Mode:** In early drafting, an upstream agent hallucinated the party driving a modern green Ford farm truck on an asphalt highway to Raleigh, completely erasing the canonical interdimensional travel.
* **Tabletop Ground Truth:** The party entered the **Lost Roads via Theodore's maintenance shed**, met **Ally (Maiden of Persephone)**, and emerged inside the **North Carolina Museum of History broom closet**.
* **Remediation & Permanent Gate:**
  - Added the `HIGH_RISK_FOREIGN_PROPS` filter in [`audit_semantic_grounding.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/audit_semantic_grounding.py) scanning for modern anachronisms (`"truck"`, `"ford"`, `"chevy"`, `"smartphone"`).
  - Added Tier B Lore Drop tracking (`tier_b_pattern`) to prohibit skipping critical keywords (`"lost roads"`, `"maintenance shed"`, `"limestone stele"`).

### 2. Speech-to-Text Phonetic Accent Mergers (Session 1 & Session 3)
* **References:** 
  - *Versailles to Paris:* [`CRITIQUE_LOG.md: PR Record #001`](file:///d:/Code/dnd-scribe/CRITIQUE_LOG.md#L19-L32)
  - *Nincy vs. Nancy:* [`sessions/data/critiques/CRITIQUE_LOG.md: PR Record #003`](file:///d:/Code/dnd-scribe/sessions/data/critiques/CRITIQUE_LOG.md#L9-L24)
* **Failure Mode:** Automatic speech-to-text transcribed Pierre saying *"Versailles to Brittany"* because of hard French phonemes (*"Pair-ey"*), and transcribed the museum receptionist as *"Nancy"* despite her explicit dialogue: *"Nincy with an I... N-I-N-C-Y... Some people with my accent, they don't hear."*
* **Remediation & Permanent Gate:**
  - Created [`audit_transcript_gaps.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/audit_transcript_gaps.py) to harvest self-referential spelling patterns (`"with my accent"`, `"N-I-N-C-Y"`).
  - Introduced `PHONETIC_ALIASES` in [`audit_semantic_grounding.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/audit_semantic_grounding.py) so legitimate phonetic corrections pass semantic grounding with 100% confidence.

### 3. Micro-Chapter Fragmentation & Pacing Collapse (Session 2 & Session 3)
* **References:** 
  - *Micro-Chapter Bloat:* [`sessions/data/critiques/CRITIQUE_LOG.md: PR Record #003`](file:///d:/Code/dnd-scribe/sessions/data/critiques/CRITIQUE_LOG.md#L23)
* **Failure Mode:** Every 100-line scene block originally declared a `## CHAPTER` header. This fragmented single narrative conversations into 10–12 micro-chapters (some under 60 words), destroying reading momentum.
* **Remediation & Permanent Gate:**
  - Added Chapter Pacing & Word Count gates in [`novel/generate_epub.py`](file:///d:/Code/dnd-scribe/novel/generate_epub.py) and [`sessions/_scripts/harness/macro_auditor.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/harness/macro_auditor.py).
  - Emits **`[MICRO_CHAPTER_FRAGMENTATION]`** for chapters $< 250$ words and **`[EXCESSIVE_CHAPTER_SPLIT]`** for sessions with $> 6$ chapters.
  - Successfully consolidated Session 2 and Session 3 into 3 breathing novel chapters each (averaging 2,000–3,000 words).

### 4. False Uncoupling from Unicode Ligatures & Missing Tags
* **Failure Mode:** Raw transcripts generated with Unicode ligatures (`ﬁ` for $\text{fi}$, `ﬂ` for $\text{fl}$) caused string comparisons to fail on common words like `"figure"`, falsely triggering `UNGROUNDED TURN`. Additionally, players speaking without `(PC/NPC)` tags (e.g. `**Luke Foreman:**`) were ignored by older regex patterns.
* **Remediation:**
  - Upgraded [`clean_lines()`](file:///d:/Code/dnd-scribe/sessions/_scripts/audit_semantic_grounding.py#L40-L50) to normalize all input text with `unicodedata.normalize("NFKD", ...)`.
  - Expanded dialogue regex to capture all player/GM speech patterns: `^\*\*([^*]+?)(?:\s*\((PC|NPC)\))?:\*\*\s*(.+)$`.

### 5. Academic Architecture Theater & Broken Test Harness Foundation
* **Failure Mode:** Early design proposals included speculative "TF-IDF character voice affinity $\ge 0.85$" and "sentiment arc trajectory" gates that were non-deterministic and required an LLM to evaluate its own output. Meanwhile, the actual unit test runner (`test_harness.py`) was broken with `ModuleNotFoundError` due to malformed import paths (`sessions.scripts` vs `sessions._scripts`).
* **Remediation:**
  - Fixed Python packaging structure (`sessions/__init__.py`, `sessions/_scripts/__init__.py`) and bootstrapped `sys.path`.
  - Replaced speculative gates with the lean, deterministic 3-gate verifier (`verify_alternate_scene.py`).
  - Expanded test suite to 12 unit tests passing 100% in 0.024s.

### 6. Third-Person Player Intent Leaking into Spoken Dialogue (Session 4)
* **Reference:** [`CRITIQUE_LOG.md: PR Record #004`](file:///d:/Code/dnd-scribe/CRITIQUE_LOG.md#L20-L28)
* **Failure Mode:** Players narrate their character's emotions, theories, or mechanical actions in the 3rd person at the table (e.g., Sophie: *"Alfie is absolutely shook to his wooden core"* [L0390]; Luke: *"Pierre believes all Gorgons are essentially French..."* [L0459]). Drafting models wrapped these descriptions in quotation marks as spoken dialogue, resulting in characters bizarrely narrating their own internal state in the 3rd person.
* **Remediation & Permanent Gate:**
  - Enforced the **3rd-Person Table Intent vs. In-World Spoken Dialogue Barrier**: Player 3rd-person narrations must be novelized as Narrator Prose / physical blocking, strictly reserving quotation marks (`"..."`) for 1st/2nd-person in-world utterances.
  - Added 3rd-person self-reference pattern linter to `critique_prose.py`.

### 7. Multi-Speaker Paragraph Fusion & Dialogue Color Monopoly (Session 3 & Session 4)
* **References:**
  - *Curator Dialogue Bleed:* [`CRITIQUE_LOG.md: PR Record #005`](file:///d:/Code/dnd-scribe/CRITIQUE_LOG.md#L20-L28)
  - *Alfie / Pierre Action-Dialogue Fusion:* [`CRITIQUE_LOG.md: PR Record #004`](file:///d:/Code/dnd-scribe/CRITIQUE_LOG.md#L26-L28)
* **Failure Mode:** Bundling multiple character actions or lines into a single paragraph (e.g., Alfie's *Mage Hand* pot drop followed by Pierre's attendant dialogue; Alfie trying on a souvenir trucker hat followed by Pierre's dragon inquiry) causes the manifest builder to assign the whole block to a single speaker. On the Web Reader and ElevenLabs TTS, this turns Alfie's action into Pierre's blue speech bubble or voice.
* **Remediation & Permanent Gate:**
  - Enforced the **One Speaker Turn Per Paragraph Invariant**: Every change in speaking character or character action focus requires its own dedicated markdown paragraph.
  - Upgraded [`generate_web_manifest.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/generate_web_manifest.py) with granular segment parsing and alias fallback mappings for NPCs (`attendant`, `fates`, `nincy`).

### 8. Silent Speaker Fallback to Narrator on GM-Voiced NPCs (Sessions 1-4)
* **Failure Mode:** The Game Master voiced all NPCs in the raw transcripts (`**Luke Foreman:** "..."`). Because `load_raw_indexed_speakers` mapped `Luke Foreman` to `"narrator"`, quoted NPC dialogue silently inherited `speakerId: "narrator"` and displayed as gray narrator text in the web reader.
* **Remediation & Permanent Gate:**
  - Implemented origin-time `dialogue_speakers` dictionaries in `sessions/config/sN-session-config.json` linking GM line numbers to canonical character keys.
  - Added Invariant 6 automated gate in [`verify_manifest.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/verify_manifest.py) asserting that every segment with `type: "dialogue"` has `speakerId != "narrator"`, integer `sourceLine > 0`, and a valid `#RRGGBB` hex color.

### 9. Permissive Prefix Matching Masking Ungrounded Turns (The 4-Character Loophole)
* **Failure Mode:** `audit_semantic_grounding.py` previously checked `rw[:4] == pw[:4]`, causing any word sharing a 4-letter prefix to count as grounded (e.g. `star` matching `startled`, `with` matching `within`), yielding false 100% passes while masking completely ungrounded turns (e.g., S2 Scene 7 L1161 and L1249).
* **Remediation & Permanent Gate:**
  - Replaced the prefix check with exact token matching, inflectional suffix stripping (`-ing`, `-ed`, `-es`, `-ly`, `-tion`), and English consonant de-doubling (`dropp` $\rightarrow$ `drop`).
  - Added multi-marker span window expansion (`min(markers)-4` to `max(markers)+5`) for fused paragraph turns.

### 10. Hollow Parity Whitelists & Concrete Modern Realia Grounding
* **Failure Mode:** `verify_parity.py` previously audited an arbitrary 12-string vehicle whitelist that missed real-world props or produced false positives when transcript abbreviations were used (e.g., flagging `television` when raw transcript had `TV`, or flagging `airplane` when raw transcript had `flight 422`).
* **Remediation & Permanent Gate:**
  - Expanded `SUSPECT_VEHICLES_AND_TECH` across modern realia (`elevator`, `keycard`, `sedan`, `suv`, `laser`, `airplane`, `jetliner`, `cellphone`, `television`, `computer`, `satellite`).
  - Integrated `TECH_RAW_GROUNDING` semantic token aliases mapping prose terms back to transcript anchors.

### 11. Silent Zero-Exit Code in Developmental Editor / Prose Critic
* **Failure Mode:** `critique_prose.py` hardcoded a "PASS" in summary rows and exited with code 0 even when critical review issues occurred, allowing unaddressed editorial flaws to pass downstream.
* **Remediation & Permanent Gate:**
  - Upgraded `main()` to exit with `sys.exit(1)` on critical review failures.
  - Removed false positive on `"blinked"` in stutter detection.
  - Synchronized character voice telemetry with active Margin characters.

### 12. Speaker Misattribution via Marker Drag & Missing-Marker Fallback (Session 5)
* **Failure Mode:** In Session 5, 6 scene blocks suffered speaker misattributions (e.g. Block #8 having `pierre` speaking in prose but attributed to `dravin` in the manifest; Block #153 having `alfie` speaking in prose but attributed to `attendant`).
  - *Mechanism 1 (Marker Drag / Turn Inversion):* When Character A replies to Character B, attaching Character B's line marker (`<!-- L0120 -->`) or inverting markers caused the origin lookup in `generate_web_manifest.py` to blindly attribute Character A's line to Character B.
  - *Mechanism 2 (Missing Marker Fallback):* When a dialogue paragraph omitted a marker (to satisfy strict non-duplicate rules), `generate_web_manifest.py` fell back to `last_source_line` from a previous turn, silently inheriting an unrelated speaker (e.g. Alfie inheriting the museum attendant's line marker).
  - *Mechanism 3 (The Hollow Non-Narrator Gate):* `verify_manifest.py` asserted that `speakerId != "narrator"`, which verified that a quote had *a* speaker, but completely failed to verify whether the assigned speaker matched the character named in the prose dialogue tag.
* **Remediation & Permanent Gates:**
  1. **Dual-Layer In-Text Dialogue Tag Verification:** Upgraded [`generate_web_manifest.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/generate_web_manifest.py) with `detect_in_text_dialogue_speaker()`, checking unambiguous dialogue verbs and speech tags (`Pierre murmured`, `Eusacles asked`, `Alfie whispered`) before accepting an antecedent marker.
  2. **Automated Manifest Invariant 4:** Added Invariant 4 to [`verify_manifest.py`](file:///d:/Code/dnd-scribe/sessions/_scripts/verify_manifest.py), asserting semantic tag consistency. If the manifest assigns `speakerId: "dravin"` to a paragraph containing `"Pierre muttered"`, `verify_manifest.py` immediately throws a hard `SPEAKER MISATTRIBUTION` error and halts with exit code 1.

### 13. The Adaptation Boundary Law & Editorial Pushback Protocol
* **The Core Tension:** Traditional developmental editors and adversarial critics review prose as if it were a clean-slate original novel. They inevitably demand:
  - Deep philosophical interiority when a character receives a major revelation (e.g., Dravin learning Persephone is his mother).
  - Equal screen time and proactive agency for quiet players (e.g., eliminating Alfie's "luggage syndrome" while the player was passive).
  - Dramatic conflict and plot events injected into low-stakes travel turns.
* **The Law of Adaptation Boundary:**
  - Tabletop novelization is an **adaptation of real-world collaborative human play**, not an ungrounded generative sandbox.
  - If satisfying an editorial critique requires fabricating extensive net-new plot events, inventing unplayed dialogue, or inventing complex interior character arcs that never occurred at the table, **the agent MUST push back**.
  - Retroactively inventing major emotional decisions or plot developments creates devastating continuity breaks with future sessions (e.g. if the adapter invents deep angst about Persephone, but William Webb plays Dravin in Session 6 as entirely carefree or in denial).
* **The Pushback Protocol:**
  - **Track A (Tabletop Cut):** Remains 100% anchored to the transcript, honoring table silence, natural banter, and actual player pacing.
  - **Track B (Cinematic Cut):** Condenses dead air, heightens atmosphere, and stages physical action, but *strictly stops* at the boundary of player intent.
  - **Formal Editorial Pushback:** When a critique exceeds this boundary, the agent logs an official pushback statement:
    > *"Pushback: In order to adjust the narrative to satisfy this critique, the model would have to invent so much net-new content that it deviates from the tabletop ground truth and risks pre-empting or contradicting player choices in future sessions. This critique has been transferred to the **Upcoming Session Continuity Briefing** (`s(N+1)-context-briefing.md`) for the GM and players to address at the table, or recorded as a tabletop retcon requirement."*

---

## 🎯 Downstream Artifact Contracts

| Downstream Target | Primary File | Schema / Invariants Enforced |
| :--- | :--- | :--- |
| **Web Manifest Engine** | `sessions/data/index/sN-manifest-v2.json` | Schema 2.0 with sub-block `segments[]`. Decomposes mixed text into `"dialogue"` and `"narration"`. Invariant 6 asserted by `verify_manifest.py`: 0 narrator dialogue turns, integer `sourceLine > 0`, 100% character registry hex color matches, and exact verbatim text reconstruction check. |
| **EPUB Publishing** | `novel/the-margin-book-1-*.epub` | Dual editions (Illustrated & Text-Only). Strict chapter word count floors ($\ge 350$ words). Valid XHTML EPUB3 navigation. |
| **Audiobook & TTS Engine** | ElevenLabs Speech Pipeline | Granular speaker tagging per segment (`speakerId`). Exact quote boundary isolation eliminates cross-talk in multi-voice synthesis. |
| **Critique & Diff Inspector** | `dndwikis` / Web Diff Inspector | Monotonic line anchoring (`L0001`–`L9999`) and coarse line spans (`L0900-L0922`) allow readers to inspect side-by-side diffs between raw audio, archival prose, and authorial adaptations. |
