# 🏛️ Master Pipeline Architecture, Decision Codex & Historical Failure Registry
**D&D Scribe Publishing Engine: From Raw Audio to Literary Fantasy Novels & Interactive Web Readers**

---

## 1. Executive Overview

The **D&D Scribe Publishing Engine** transforms raw, chaotic tabletop RPG session recordings and multi-speaker transcripts into high-fidelity fantasy novels, audiobooks, and web manifests.

To guarantee that the pipeline remains **strictly independent, non-biased, and deterministic**, the system enforces an adversarial gate architecture where no drafting agent evaluates its own output. Prose generation is decoupled from verification, and mathematical invariants govern every transformation.

The publishing engine operates on a **Dual-Track Architecture**:
1. **Track A (The Tabletop Cut / Archival):** 100% Monotonic line-by-line coverage, strict transcript parity, zero unanchored dialogue quotes, and comprehensive ledger accounting (`rendered=[...] skipped=[...]`).
2. **Track B (The Cinematic Cut / Authorial):** Pacing-optimized, compacted scene set-pieces with coarse line spans (`<!-- Lxxxx-Lyyyy -->`) for rapid novelistic momentum while preserving core character emotion, voice, and lore anchors.

Both cuts are compiled into **Schema 2.0 Web Manifests** and published into the interactive **Web Reader (`uneraseable.html`)**, where readers can toggle between lenses or view side-by-side synchronized diffs against the raw transcript.

---

## 2. Chronological Pipeline Evolution: Editions 1 Through 15

Over the course of 15 iterative editions, the pipeline has evolved from fragile scripts into an adversarial publishing engine:

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │ EDITIONS 1–3: The Prototype Era (Sessions 1 & 2)                       │
  │ • Raw Whisper STT output -> Direct novelization.                      │
  │ • Post-hoc regexes guessing who spoke ("said", "asked").               │
  │ • Major failures: Green Ford truck hallucinations, French accent       │
  │   transcription errors ("Pair-ey" -> "Brittany"), phonetic collapses.  │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ EDITIONS 4–6: The Modular Indexing Era (Session 3)                     │
  │ • Introduced monotonic L#### line indexing and 100-line scene blocks.  │
  │ • Crisis: Micro-chapter fragmentation (every 100 lines = a chapter!).  │
  │ • The "Integer Illusion": Agents stamping fake line numbers on fantasy.│
  │ • Created early verify_parity.py and semantic stem overlap checks.     │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ EDITIONS 7–9: The Multi-Speaker & Formatting Era (Session 4)           │
  │ • The Multi-Speaker Bubble Monopoly: Alfie's action colored blue as    │
  │   Pierre because both were in one paragraph.                           │
  │ • 3rd-Person intent leaks: Players describing feelings in 3rd person   │
  │   getting wrapped in quotation marks like sportscasters.              │
  │ • Silent narrator fallbacks on GM-voiced NPCs.                         │
  │ • Invariant established: One Speaker Turn Per Paragraph.               │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ EDITIONS 10–12: The "Hollow Test" Audit & Packaging Crisis             │
  │ • Discovered "Hollow Tests": 4-character stem matching (star/startled) │
  │   and 12-vehicle whitelists giving fake 100% passes.                   │
  │ • critique_prose.py silently exited 0 even on major review failures.   │
  │ • Academic architecture theater (TF-IDF voice vectors) replaced with   │
  │   deterministic mathematical ledger checks.                            │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ EDITIONS 13–14: The Zero-Regex Law & Schema 2.0 Web Reader             │
  │ • The "Local Patching Loop" amnesia: Agents adding aliases to regexes  │
  │   instead of querying origin metadata.                                 │
  │ • Purged ALL post-hoc regex speech parsers. Codified Section 2.1:      │
  │   The Zero-Regex Dialogue & Origin-Time Provenance Law.                │
  │ • Launched Schema 2.0 Web Manifests with sub-block segments, diff     │
  │   inspector, and dual-cut reader integration.                          │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ EDITION 15 (Current): The Intent, Agency & Anti-Amputation Era (S5)    │
  │ • PR #33 Post-Mortem: Hollywood heist competency bias (Pierre's trash   │
  │   tantrum) and polite consent sanitization (Dravin seizing Alfie).    │
  │ • The "Character Dogma" Trap: Prohibiting universal psychology rules   │
  │   in favor of line-level transcript assertions.                        │
  │ • The Destructive OOC Amputation Trap: Inverting the OOC presumption   │
  │   so table lore and player deductions are never thrown into the trash. │
  │ • Rotten Tomatoes Critic UI overhaul: Tomatometer vs Popcornmeter,     │
  │   Campaign Trajectory & Arc Impact, and Chapters Modal integration.    │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Comprehensive Failure Point Catalog (FP-01 Through FP-20)

Every failure mode below represents a hard-won engineering lesson. The pipeline must actively prevent their recurrence.

### 🛑 FP-01: Abstract Storyboard Tropification (The "Hollywood Heist" Trap)
* **The Failure:** During early indexing or drafting, an LLM summarizes a messy, chaotic roleplay segment using a generic cinematic trope (e.g. *"The party executes a coordinated heist"*). Downstream drafting models gravitate toward the trope, hallucinating laser grids, glass cutters, conspiratorial winks, and synchronized teamwork where none existed.
* **Historical Breach:** Session 3 museum entry; Session 5 Pierre framed as running a "coordinated distraction" with "French diplomacy" while Dravin steals keys.
* **Table Ground Truth:** Pierre (Luke S) was throwing an authentic Parisian fit over classical masonry being placed next to an olive-drab plastic trash bin with pigeon droppings. Dravin merely opportunistically pickpocketed keys while Pierre shouted.
* **Permanent Invariant:** Manifests and scene blocks must record the **exact declared player mechanism**, never generic movie tropes. No synthetic collusion or heist teamwork may be added if players acted on independent impulses.

### 🛑 FP-02: "Polite Consent" Sanitization of Unilateral Force
* **The Failure:** LLMs have an innate bias toward cozy collaboration. When a player declares an aggressive, jarring, or non-consensual physical action, the model instinctively softens it—inserting mutual nods, tender glances, or unspoken understanding to make the protagonist "likeable."
* **Historical Breach:** Session 5 Scene 10: Dravin was written as *"glancing down tenderly at Alfie; Alfie nodded solemnly"* before entering the 1948 trial vision.
* **Table Ground Truth:** Dravin never asked. William Webb simply declared that Dravin seized Alfie around the waist and smashed him face-first into the iron binder, while Alfie kicked and shouted *"Not again! Not me again!"* in sheer terror.
* **Permanent Invariant:** Player mechanical declarations involving force, grabbing, or unilateral action must be staged with **unflinching physical friction**. Mutual consent must never be inserted where the table had none.

### 🛑 FP-03: The Destructive OOC Amputation Trap (Lore Erasure)
* **The Failure:** Over-aggressive "Out-of-Character" filters that treat casual table conversational syntax as "OOC trash," dumping critical GM worldbuilding, timeline clues, and player deductions into the skipped ledger.
* **The Reality:** 70% of the deepest campaign lore is spoken in casual conversational voice at the table (e.g. the GM explaining timeline ink variants; players deducing faction conspiracies).
* **The Architectural Rule:** **Being too soft on OOC is far less damaging than being too aggressive.** Casual table chatter naturally gets abstracted into narrative description and action during prose translation. But when lore is cut at the intake, it is deleted from the novel forever.
* **Permanent Invariant (The Inclusive Fiction Law):** Every line touching the game is **Tier B (Worldbuilding, Action Intent, Deduction)** by default. Only pure real-world logistics (mic checks, pizza, Wi-Fi, calendar dates) can be marked Tier C. If a skipped line contains canon entity nouns (*Thorne, Reductor, Gorgon, 1948, binder*), `verify_parity.py` immediately halts with a fatal build error.

### 🛑 FP-04: The "Character Dogma" Trap (Universal Psychology Rules)
* **The Failure:** When a narrative error is caught, reacting by inventing sweeping, universal behavioral laws (e.g. *"Rule 1: Pierre will never leave Dravin alone"*).
* **The Flaw:** This mistakes a specific causal event in a specific scene for a permanent character constraint. Characters are dynamic, emergent, and messy; imposing artificial psychological absolutes paralyzes future authoring and ignores the actual transcript.
* **Permanent Invariant (Line-Level Grounding):** Never write universal behavioral dogma rules. Write **Line-Level Provenance Assertions** that verify whether the prose honors what was actually declared on that specific turn in the audio.

### 🛑 FP-05: The "Local Patching" Amnesia Loop & The Zero-Regex Law
* **The Failure:** Whenever a dialogue speaker was misattributed on the web reader, agents added an alias to `SPEAKER_ALIASES` or a verb to `speech_verbs`, saw the local test pass, and declared victory. This reinforced the broken premise that downstream tools should use regex to "guess" who spoke.
* **Permanent Invariant (Section 2.1 of AGENTS.md):**
  * Speaker attribution is established **at creation time** in `sN-session-config.json` and inline markers (`<!-- Lxxxx:speaker -->`).
  * Downstream tools (`generate_web_manifest.py`, TTS generators, EPUB compilers, Web Readers) must **NEVER** use regex, speech-verb parsers, or name searches on prose to infer or guess who is speaking.
  * Quoted text derives its speaker directly from the line anchor. Text outside quotes is unconditionally `speakerId: "narrator"`.

### 🛑 FP-06: The "Hollow Test" Trap (The 4-Character Loophole & Whitelists)
* **The Failure:** Tests that verify file existence, line arithmetic, or trivial string overlaps while completely missing semantic reality.
  * *The 4-Character Stem Loophole:* `audit_semantic_grounding.py` matching `rw[:4] == pw[:4]` allowed `star` to match `startled`, yielding 100% false green passes on completely ungrounded scenes.
  * *The 12-String Whitelist:* `verify_parity.py` checking only 12 hardcoded vehicle strings (`truck`, `ford`, `chevy`), missing any other invented tech.
  * *Silent Zero-Exits:* `critique_prose.py` printing `EDITORIAL CORRECTION REQUIRED` but exiting with code 0, allowing broken prose to sail through the pipeline.
* **Permanent Invariant:** Every gate must be genuinely adversarial. Exact morphological token matching with inflection stripping replaces stem slicing. Linters must `sys.exit(1)` on failures.

### 🛑 FP-07: The "Integer Illusion" (Synthetic Line Stamping)
* **The Failure:** When a drafting agent hallucinates prose, it blindly appends a line number from the scene range (e.g., `<!-- L1620 -->`) so that the arithmetic in `verify_parity.py` balances.
* **Permanent Invariant:** Markers can only be attached to paragraphs containing the actual speaker's words or declared actions. Semantic token overlap checks verify that the prose shares vocabulary with the raw speaker turn.

### 🛑 FP-08: Stale Entity Carryover Across Setting Boundaries
* **The Failure:** Reusing global character keys across different geographic locations (e.g. attributing the Pennsylvania university department host in S5 to `attendant`, a museum employee from North Carolina in S3).
* **Permanent Invariant:** `verify_parity.py` validates that all character keys belong strictly to that session's declared local setting in `sN-session-config.json`.

### 🛑 FP-09: Chronological Inversion at Thresholds (Visions & Combat)
* **The Failure:** Struggling to stage simultaneous actions (e.g., an internal psychic vision ending while external enemies kick down doors), resulting in flattened sequential prose that scrambles triggers and consequences.
* **Historical Breach:** S5 Scene 10: Dravin whispering *"Sorry, Alfie"* after combat started, rather than before slamming him into the binder to trigger the vision.
* **Permanent Invariant:** Causality must flow strictly: Trigger $\rightarrow$ Sensory Manifestation $\rightarrow$ Consequence $\rightarrow$ Reaction.

### 🛑 FP-10: Multi-Speaker Paragraph Fusion & Dialogue Color Bleed
* **The Failure:** Bundling multiple character actions or lines into a single paragraph causes manifest builders and TTS engines to assign the entire block to one speaker (e.g., Alfie's *Mage Hand* action colored blue as Pierre).
* **Permanent Invariant (One Speaker Turn Per Paragraph):** Every change in speaking character or distinct character action focus requires its own dedicated markdown paragraph.

### 🛑 FP-11: 3rd-Person Player Intent Leaking into Spoken Dialogue
* **The Failure:** Wrapping players' 3rd-person table descriptions (*"Alfie is shook to his wooden core"*, *"Pierre thinks Gorgons are French"*) in quotation marks, making characters bizarrely narrate their own emotions in the 3rd person like sportscasters.
* **Permanent Invariant:** 3rd-person descriptions must be novelized as Narrator Prose / physical blocking. Quotation marks are strictly reserved for 1st/2nd-person in-world utterances.

### 🛑 FP-12: Silent Speaker Fallback to Narrator on GM-Voiced NPCs
* **The Failure:** Because the GM voices all NPCs, raw transcripts attribute lines to the GM (`Luke Foreman`). If unmapped, quoted dialogue silently defaulted to `speakerId: "narrator"` and displayed as gray narrator text.
* **Permanent Invariant (Invariant 6):** `verify_manifest.py` mathematically asserts that 100% of segments with `type: "dialogue"` have `speakerId != "narrator"`, integer `sourceLine > 0`, and a valid `#RRGGBB` hex color.

### 🛑 FP-13: Phonetic Transcription Drift & Regional Accents
* **The Failure:** Speech-to-text engines corrupting dialect names (French *"Pair-ey"* $\rightarrow$ *"Brittany"*; Southern *"Nincy"* $\rightarrow$ *"Nancy"*), breaking character identity.
* **Permanent Invariant:** Explicit phonetic aliases in session configs and semantic grounding tools.

### 🛑 FP-14: Micro-Chapter Fragmentation & Word-Count Floors
* **The Failure:** Generating a new `## CHAPTER` for every 100-line processing block, fragmenting the story into 12 tiny 200-word snippets and destroying reading momentum.
* **Permanent Invariant:** Modular 100-line blocks are decoupled from thematic novel chapters. EPUB compilers enforce a minimum chapter floor ($\ge 350$ words) and flag sessions with $> 6$ chapters.

### 🛑 FP-15: Mechanics-As-Dialogue (Anime Spell Shouts)
* **The Failure:** Characters shouting literal D&D game rules (*"Chill Touch!"*, *"Toll the Dead!"*, *"I cast Wordcraft!"*) as battle cries.
* **Permanent Invariant:** Game mechanics must be translated into sensory manifestations (somatic gestures, atmospheric pressure drops, smell of ozone, resonance of iron), stripping dice math and spell names.

### 🛑 FP-16: Spatial & Physical Misplacement
* **The Failure:** Translating an interdimensional doorway as leading directly into an interior room rather than an exterior outbuilding, making physical character actions (like propping open an exterior door) nonsensical.
* **Permanent Invariant:** The GM's initial environmental description sets the physical coordinate system.

### 🛑 FP-17: Premature Resolution & Cliffhanger Erasure
* **The Failure:** LLMs feeling pressure to "wrap up" chapters neatly with characters returning safely home, erasing raw table cliffhangers (e.g. sirens blaring, security gates slamming).
* **Permanent Invariant:** A scene block must terminate at the exact final tabletop turn declared in the index.

### 🛑 FP-18: Raw Markdown Syntax Leaks
* **The Failure:** Raw formatting tokens (`***STALE.***`, `### Header`, `__bold__`) escaping into novel manuscript prose.
* **Permanent Invariant:** Automated syntax regex linter in `critique_prose.py` scanning for unparsed markdown tokens in published prose.

### 🛑 FP-19: Setting-Blunt Vocabulary Blacklists
* **The Failure:** Leak detectors blindly flagging real in-universe modern props (e.g. an aisle `microphone` in a modern Pennsylvania university amphitheater) because the blacklist was designed for medieval high fantasy.
* **Permanent Invariant:** Setting-aware dielectric profiles distinguishing modern world realia from out-of-character tabletop technical chatter (`zoom`, `wi-fi`, `discord`, `dice`).

### 🛑 FP-20: The Adaptation Boundary Law & Editorial Pushback Protocol
* **The Failure:** Developmental editors demanding extensive net-new interior character arcs, equal dialogue share for passive players, or dramatic conflict during quiet travel turns.
* **The Core Tension:** Tabletop novelization is an **adaptation of collaborative human play**, not an ungrounded generative sandbox. Inventing unplayed emotional decisions creates devastating continuity breaks with future sessions.
* **Permanent Invariant:**
  * **Track A:** 100% faithful to table pacing, silence, and banter.
  * **Track B:** Pacing compression stops strictly at the boundary of declared player intent.
  * When a critique demands fabricating net-new plot or pre-empting future player choices, the agent **must log a formal Editorial Pushback Statement** rather than inventing fiction.

---

## 4. The 7 Non-Negotiable Pipeline Invariants (The Engine Laws)

1. **Law 1: The Zero-Regex Provenance Law (AGENTS.md §2.1):** Speaker attribution is established at origin time via line markers mapped to session config. Downstream tools never use regex to infer speakers.
2. **Law 2: Monotonic Line Coverage & Zero Unanchored Quotes (Track A):** Line markers must appear in strictly ascending order (`inline_markers[i] < inline_markers[i+1]`). Quoted dialogue without trailing line markers is strictly illegal in Track A.
3. **Law 3: 100% Raw Line Ledger Accounting:** Every line in `sN-raw-indexed.md` must be accounted for as `rendered` or `skipped` ($\text{rendered} \cup \text{skipped} = \text{total}$; $\text{rendered} \cap \text{skipped} = \emptyset$).
4. **Law 4: The Inclusive Fiction Law:** Every line touching the game is Tier B by default. Only real-world logistics can be skipped as Tier C. Skipped turns containing canonical lore nouns trigger immediate fatal build errors.
5. **Law 5: The Line-Level Grounding Law:** Never assert universal character dogmas. Assert line-level fidelity against declared player turns.
6. **Law 6: The Unflinching Staging Law:** Unilateral physical force and inter-party friction must never be softened into polite mutual consent or synthetic heist collusion.
7. **Law 7: The Adaptation Boundary Law:** Tabletop canon is fixed. When editorial critique demands fabricating unplayed plot or pre-empting player choices, log an official pushback statement.

---

## 5. Verification Suite Architecture & Tool Matrix

```
  ┌────────────────────────────────────────────────────────┐
  │ 1. verify_parity.py sN                                 │
  │    • Monotonic line ordering in Track A.               │
  │    • Zero unanchored dialogue quotes.                  │
  │    • 100% Ledger parity (rendered + skipped = total).  │
  │    • Canon noun check on skipped lines (Anti-Lore Drop)│
  │    • Setting-scoped entity validation (Anti-Stale NPC).│
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 2. verify_intent_parity.py sN                          │
  │    • Validates against sN-intent-contract.json.        │
  │    • Zero sanitized consent on unilateral force.       │
  │    • Zero synthetic heist collusion on friction beats. │
  │    • Faction & prop terminology fidelity.              │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 3. macro_auditor.py sN                                 │
  │    • PC Sensory & physical register checks.            │
  │    • Cold-reader lore & grounding anchors.             │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 4. critique_prose.py sN                                │
  │    • Setting-aware dielectric tech linter.             │
  │    • Zero raw markdown typography leaks.               │
  │    • Zero talking-head stagnant scenes.                │
  │    • Zero robotic speech tag stutters.                 │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 5. generate_web_manifest.py sN                         │
  │    • Origin-time sub-block segment decomposition.      │
  │    • 100% verbatim reconstruction invariant.           │
  │    • Injects dynamic editorial forum & scorecards.     │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 6. verify_manifest.py sN                               │
  │    • Exact SHA-256 block tiling.                       │
  │    • Invariant 6: 0 narrator dialogue turns, integer   │
  │      sourceLine > 0, 100% hex color match.             │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 7. novel/generate_epub.py                              │
  │    • Dual Edition EPUB Assembler (Illustrated & Text). │
  │    • Minimum chapter word count floor (>= 350 words).  │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 8. dndwikis-main/build_ebooks.py                       │
  │    • Consumes manifest editorial forum dynamically.    │
  │    • Renders Dual Rotten Tomatoes scorecards.          │
  │    • Interactive Chapters modal with Critic chapter.   │
  │    • Side-by-side synchronized Diff Inspector.         │
  └────────────────────────────────────────────────────────┘
```

---

## 6. Session 6+ Production Runbook & Pre-Flight Checklist

Before drafting any session:
1. **Index & Clean:** Generate `sN-raw-indexed.md` with immutable `L####` line numbers.
2. **Configure Entities & Contract:** Create `sN-session-config.json` with local NPCs and `sN-intent-contract.json` declaring:
   - *Unilateral Actions* (e.g. Dravin grabbing Alfie $\rightarrow$ forbid polite consent).
   - *Friction Points* (e.g. Pierre's architectural outrage $\rightarrow$ forbid coordinated heist).
   - *Mandatory Lore Reveals* (e.g. altered 1948 trial ledger ink).
3. **Draft Dual Tracks:**
   - **Track A (`blocks/`):** 100% monotonic line coverage, zero unanchored quotes, Tier B lore novelized into prose.
   - **Track B (`blocks_authorial/`):** Compacted set-pieces, coarse line spans, bound by Intent Contract.
4. **Run Full Verification Pipeline:**
   ```powershell
   python sessions/_scripts/run_publishing_pipeline.py sN
   ```
5. **Compile Web Readers & Inspect Diffs:**
   ```powershell
   python dndwikis-main/build_ebooks.py
   ```
   Open `uneraseable-sN.html` and verify the Chapters modal, Rotten Tomatoes dual cards, and synchronized Diff Inspector.

---

## 7. The Anti-Sycophancy & Active Trade-Off Principle

```
  ┌────────────────────────────────────────────────────────┐
  │ THE FRICTIONLESS "ALL PASS" ILLUSION (SYCOPHANCY BUG)   │
  │ A test harness that only prints green checkmarks hides  │
  │ editorial compromises and creates false confidence.    │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ THE EDITORIAL TRADE-OFF & TENSION DECISION LEDGER      │
  │ • Reader Reception Polarization (Tomatometer vs Popcorn)│
  │ • Explicit Human Whitelist Sign-Offs (Skipped Lore)    │
  │ • Turn Fusion Density (Paragraph Marker Pile-Ups)      │
  │ • Stance Costs (Compression vs Slice-of-Life Humor)    │
  │ • Active Editorial Vulnerability Watchlist             │
  └────────────────────────────────────────────────────────┘
```

1. **Every Novelization Incurs Real Costs:**
   You cannot compress a 3-hour tabletop recording (1,200+ raw lines) into a tight 10,000-word chapter without making painful sacrifices.
2. **Surfacing the Trade-offs at Build Time:**
   `run_publishing_pipeline.py` must never end with empty cheerleading (`🏆 ALL PASSED`). It mandatorily renders the **Editorial Trade-Off & Tension Decision Ledger**, displaying:
   - The critical split (e.g. 62% Tomatometer vs 94% Popcornmeter).
   - The exact whitelisted dialogue skips that required human review (e.g. `[134, 434, 458, 459, 463, 491]` for S5 Chaos Belt jokes).
   - The places where fragmented table talk was fused into literary speeches (e.g. 8 paragraphs with up to 7 turns merged).
   - The structural stance costs (e.g. heavy narrative compression sacrificing casual banter for pacing).

---

## 8. The Anti-Amnesia Pipeline Steward & Decision Ledger (`pipeline-steward`)

To prevent multi-session context loss, sycophantic looping (*"What a wonderful idea! Why didn't I think of that?"*), and regressions to previously resolved bugs across pipeline iterations:

1. **Canonical Living Decision Ledger (`PIPELINE_DECISION_LEDGER.md`):**
   - Located at `.agents/skills/pipeline-steward/references/PIPELINE_DECISION_LEDGER.md`.
   - Documents every architectural decision (`DEC-001` through `DEC-020`), failure points addressed (`FP-01` through `FP-20`), trade-offs accepted, and active verification gates.
2. **Automated Architectural Consistency Auditor (`audit_decision_ledger.py`):**
   - Runs automatically as **Step 0 (Pre-Flight)** in `run_publishing_pipeline.py`.
   - Validates that all DEC records are intact, all session intent contracts parse properly, and all session configs maintain consistent whitelists.
3. **The Anti-Amnesia Protocol (`.agent/AGENTS.md` Section 6):**
   - Mandates that any agent discussing, refactoring, or auditing the publishing pipeline must first consult `pipeline-steward` and cite established decision records before responding.
   - Forbids false novelty or amnesia when recurring trade-offs (e.g. dual-track cuts, micro-chapter splits, or OOC banter exclusions) arise.

---

## 9. Repository Branch Topology & Git Provenance Architecture

To prevent campaign collisions and maintain a clean separation between the generic publishing framework and specific story manuscripts:

```
  ┌────────────────────────────────────────────────────────┐
  │ main (The Campaign-Agnostic Engine Framework)          │
  │ • Core tools, linters, and verification gates.         │
  │ • pipeline-steward, decision codex, and agent rules.   │
  │ • Universal double-blind intent contract templates.    │
  └───────────────────────────┬────────────────────────────┘
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
  ┌────────────────────────┐      ┌────────────────────────┐
  │ uneraseable (Campaign) │      │ archive/* (Past Worlds)│
  │ • Transcripts (S1-S5)  │      │ • archive/vumbua       │
  │ • Blocks & EPUB outputs│      │ • archive/volume-1-... │
  │ • Manifests & dossiers │      │ • Preserved prototypes │
  └────────────────────────┘      └────────────────────────┘
```

1. **`main` (Framework Baseline):**
   - Serves as the clean upstream template for any TTRPG campaign.
   - Contains zero campaign-specific raw transcripts or private game audio.
   - Houses the master verification harness, the `pipeline-steward` skill, and general documentation.
2. **`<campaign-branch>` (e.g. `uneraseable`):**
   - Active workspace for a specific tabletop campaign and its published book(s).
   - Contains raw transcripts, indexed turn ledgers, modular scene blocks, web manifests, and compiled EPUBs.
3. **`archive/<campaign>` (e.g. `archive/vumbua`):**
   - Frozen snapshots of completed campaigns or legacy structural experiments.
4. **The Commit-Anchor Invariant for Post-Mortems:**
   - Feature and agent branches (e.g. `devin/*` or `critique/*`) are ephemeral and subject to deletion/pruning.
   - Any architectural post-mortem citing an alternative implementation or PR escape must record **both the branch name and the immutable commit SHA** (e.g., `devin/1790479715-s5-fidelity-cuts` at `54c9d3a`).

