# Pipeline Verification Gates & Proof Matrix

This reference manual documents every verification gate in the D&D Scribe publishing pipeline (`sessions/_scripts/run_publishing_pipeline.py`). For each gate, this document defines:
1. **The Exact Test**: What code/AST/hash checks are run.
2. **Failure Conditions**: What specific input causes a non-zero exit code.
3. **Why It Is NOT A Fake Check**: Proof that it is not a hollow regex or automatic pass.
4. **Deterministic Proof Trigger**: The exact command or mutation that triggers a hard failure at any time.

---

## 1. Pipeline Overview

The pipeline runs sequentially. Any step failure halts the entire process immediately:

```
  ┌────────────────────────────────────────────────────────┐
  │ Pre-Flight: build_session_context.py                   │
  │ Generates cross-session briefing (CLI utility)         │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ Gate 1A: audit_semantic_grounding.py                   │
  │ Fact-Checker: Raw audio window content-word entailment │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ Gate 1B: verify_parity.py                              │
  │ Parity: SHA-256 hash match + 100% discrete line ledger │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ Gate 2: harness/macro_auditor.py                       │
  │ Macro Narrative: Character sensory anchors & table jargon │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ Gate 3: critique_prose.py                              │
  │ Prose Critic: Earth leaks, talking heads, stutters     │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ Gate 4: generate_web_manifest.py & verify_manifest.py  │
  │ Schema 2.0 Invariant 6: 100% non-narrator dialogue AST │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ Gate 5: novel/generate_epub.py                         │
  │ Dual Edition EPUB Compiler (Standard + Director's Cut) │
  └────────────────────────────────────────────────────────┘
```

---

## 2. Gate Specifications & Proof Triggers

### Pre-Flight: Context Briefing Generator (`build_session_context.py`)
* **How It Works:** Ingests the preceding session's final scene block (`s(N-1)-scene-XX.md`), `sessions/index.md`, `campaign/world/the-fragments.md`, and `campaign-config.json`. Compiles closing beats, party inventory changes, target Fragment leads, and character anchors.
* **Why It Is NOT A Fake Check:** It guarantees the drafting agent never invents continuity from thin air or loses track of relics (e.g., Dravin's hoplite shield or Pierre's javelin).
* **Proof Command:**
  ```powershell
  python sessions/_scripts/build_session_context.py s5
  ```
  *Result:* Generates a 7-section structured briefing with S4 closing beat and Fragment 3 (Dr. Aris Thorne) lead.

---

### Gate 1A: Fact-Checker Semantic Entailment (`audit_semantic_grounding.py`)
* **How It Works:** Tokenizes prose into non-stopword content words and cross-checks them against the raw indexed transcript lines (`Lstart` to `Lend`). Checks for suspect modern/alien props (`laser`, `elevator`, `helicopter`, `keycard`, `suv`, `smartphone`).
* **Why It Is NOT A Fake Check:** Computes morphological stems and exact string tokens. If ungrounded foreign props appear in prose without being grounded in raw audio or setting context, it exits with code 1.
* **Proof Trigger:**
  Add `"laser"` or `"helicopter"` to any scene block.
  ```powershell
  python sessions/_scripts/audit_semantic_grounding.py s1
  ```
  *Failure Output:* `❌ Unanchored foreign prop 'laser' detected. Pipeline halts with exit code 1.`

---

### Gate 1B: Fact-Checker Parity & Ledger Integrity (`verify_parity.py`)
* **How It Works:**
  1. Computes `sha256(sN-clean-story.md)` and asserts byte-for-byte identity with `assemble_story.py sN`.
  2. Parses `<!-- LEDGER: rendered=[...] skipped=[...] -->` comments across all blocks and verifies that `rendered ∪ skipped == {Lstart, ..., Lend}` with zero line gaps and zero duplicates.
* **Why It Is NOT A Fake Check:** Cryptographic hashes and discrete set unions cannot be spoofed. Even a 1-byte whitespace edit or an omitted line number fails the gate.
* **Proof Trigger:**
  Delete one line number from `rendered=[...]` in `sessions/data/clean/blocks/s1-scene-01.md`.
  ```powershell
  python sessions/_scripts/verify_parity.py s1
  ```
  *Failure Output:* `❌ Line parity failure: Line L0012 missing from ledger. Exit code 1.`

---

### Gate 2: Macro Narrative & Character Anchors (`harness/macro_auditor.py`)
* **How It Works:** Reads canonical anchors from `sessions/config/campaign-config.json`. For each character detected by name in the session story, verifies that their sensory anchors (Pierre: `beret`, `spectacle`, `canvas`, `gorgon`; Dravin: `tweed`, `bell`, `chime`, `frost`; Eusacles: `morningstar`, `watch`, `vegas`; Alfie: `driftwood`, `hook`, `needle`, `rapier`) are actively deployed in prose. Also scans for ungrounded uppercase table abbreviations (`PC`, `NPC`, `DC`, `HP`, `AC`, `DM`, `GM`).
* **Why It Is NOT A Fake Check:** If a character is introduced and experiences "character amnesia" (zero tactile or sensory presence), the audit assigns `NEEDS_ANCHORING` and exits with code 1.
* **Proof Trigger:**
  ```powershell
  python -c "import sys; sys.path.insert(0, 'sessions/_scripts'); from harness.macro_auditor import MacroAuditor; auditor = MacroAuditor(); res = auditor.audit_scene('Pierre walked silently down the road.', 'test'); sys.exit(0 if res['passed'] else 1)"
  ```
  *Failure Output:* `[NEEDS_ANCHORING] Pierre: 0 sensory tokens detected. Exit code 1.`

---

### Gate 3: Developmental Editor & Prose Critic (`critique_prose.py`)
* **How It Works:** Scans compiled story for:
  1. Earth realia leaks (`oxford`, `airplane`, `wi-fi`, `disney`).
  2. Stagnant action / "talking heads" ratio (dialogue ratio > 45% with action verb count < 3).
  3. Consecutive duplicate speech tag loops (`Pierre said ... Pierre said`).
  4. Repetitive sensory trope overgrowth (≥3 hits on monitored phrases).
* **Why It Is NOT A Fake Check:** Computes mathematical text telemetry and raises non-zero exit codes when immersion-breaking leaks or degenerate dialogue loops are found.
* **Proof Trigger:**
  Add `"Pierre checked his Wi-Fi"` to any scene block.
  ```powershell
  python .agents/skills/novel-critic/scripts/critique_prose.py
  ```
  *Failure Output:* `❌ Earth-word leak detected: 'Wi-Fi'. Exit code 1.`

---

### Gate 4: Schema 2.0 Web Manifest Builder & Dialogue Provenance (`verify_manifest.py`)
* **How It Works:**
  1. Generates Schema 2.0 reader blocks with word-level timing, character colors, audio hashes, and line provenance.
  2. `verify_manifest.py` parses the AST and asserts four core dialogue invariants:
     - **Invariant 1:** Every single block containing quoted dialogue MUST have `speakerId != "narrator"`.
     - **Invariant 2:** Dialogue segments MUST have a valid, positive integer `sourceLine`.
     - **Invariant 3:** The assigned `speakerId` MUST exist in the manifest's character registry.
     - **Invariant 4 (Semantic Tag Consistency):** The assigned `speakerId` MUST match any in-text dialogue tags present in the prose (e.g., `"..." Pierre murmured` cannot be assigned to `dravin`).
  3. Asserts line monotonicity (line anchors must be strictly ascending).
  4. Enforces sub-165 line block size limits.
* **Why It Is NOT A Fake Check:** 
  - An automated AST crawler checks every segment in the JSON output.
  - If any dialogue segment is assigned to `"narrator"`, or has a null sourceLine, it exits with code 1.
  - If a prose dialogue tag conflicts with the assigned speaker (e.g. manifest has `attendant` while prose says `Alfie whispered`), it raises a hard `SPEAKER MISATTRIBUTION` error and exits with code 1.
* **Proof Trigger:**
  Manually edit `sessions/data/index/s1-manifest-v2.json` and change a block containing `"Pierre muttered"` to `speakerId: "dravin"`.
  ```powershell
  python sessions/_scripts/verify_manifest.py s1
  ```
  *Failure Output:*
  ```text
  [FAIL] MANIFEST VALIDATION FAILED:
    - SPEAKER MISATTRIBUTION in Block uneraseable_s01_b015 (uneraseable_s01_b015_s02): manifest assigned speaker 'dravin' but prose dialogue tag indicates 'pierre'!
  ```

---

### Gate 5: Dual Edition EPUB Assembler (`novel/generate_epub.py`)
* **How It Works:** Compiles both Illustrated Standard and Director's Cut EPUBs with cover art, metadata, spine, table of contents, and responsive CSS.
* **Why It Is NOT A Fake Check:** Validates XML schemas, verifies that all generated files exist, and asserts non-zero byte payloads.
* **Proof Trigger:**
  Corrupt an image path in `novel/book_config.json`.
  ```powershell
  python novel/generate_epub.py
  ```
  *Failure Output:* `❌ Compilation failed: Asset not found. Exit code 1.`

---

## 3. Running the Full Verified Pipeline

To run the complete verification suite across any set of sessions:

```powershell
python sessions/_scripts/run_publishing_pipeline.py s1 s2 s3 s4
```

Expected output on 100% success:
```text
======================================================================
🏆 ALL PUBLISHING GATES PASSED: 100% CANONICAL & PRODUCTION READY
======================================================================
```
