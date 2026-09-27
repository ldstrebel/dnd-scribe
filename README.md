# 🖋️ D&D Scribe: Campaign-Agnostic TTRPG Publishing Engine

**D&D Scribe** is an automated, adversarial publishing engine for transforming raw Tabletop RPG session recordings and multi-speaker transcripts into Sanderson-caliber epic fantasy novels, interactive web readers, and multi-voice audiobooks.

---

## 🏛️ Architecture & Verification Pipeline

The publishing engine operates on an adversarial gate architecture where no drafting agent grades its own prose. Mathematical line parity, origin-time provenance, and double-blind intent contracts govern every transformation:

```
  Raw Audio / STT Transcripts
              │
              ▼
   [ Step 0: Pre-Flight Audit ]   ───> audit_decision_ledger.py (DEC-001 through DEC-020)
              │
              ▼
   [ 1. Fact-Checker Gates ]      ───> audit_semantic_grounding.py & verify_parity.py
              │                   ───> verify_intent_parity.py (Double-blind agency guards)
              ▼
   [ 2. Macro Character Gate ]    ───> harness/macro_auditor.py (Character voice profiles)
              │
              ▼
   [ 3. Developmental Critic ]    ───> critique_prose.py (Deep-POV, filter words & Swain MRUs)
              │
              ▼
   [ 4. Schema 2.0 Manifest ]     ───> generate_web_manifest.py & verify_manifest.py
              │
              ▼
   [ 5. Dual Edition EPUB ]       ───> novel/generate_epub.py (Illustrated & Text-Only)
              │
              ▼
   [ 6. Dual-Track Scorecard ]    ───> Track A (100% Tabletop) vs. Track B (Cinematic Cut)
```

---

## ⚖️ The Dual-Track Publishing Standard

Rather than forcing an awkward compromise between verbatim gaming logs and rapid commercial fiction, the engine compiles two parallel cuts:

1. **Track A: The Tabletop Cut (1:1 Ground-Truth Standard)**
   - 100% Monotonic line-by-line coverage (`sN-raw-indexed.md`).
   - Every spoken dialogue quote strictly anchored via `<!-- Lxxxx -->`. Zero unanchored quotes.
   - Comprehensive ledger accounting: `<!-- LEDGER: rendered=[...] skipped=[...] -->`.
   - Zero-Regex Dialogue Law: downstream tools never guess speakers from prose.

2. **Track B: The Cinematic Cut (Authorial Velocity Standard)**
   - Pacing-optimized set-pieces using coarse multi-turn spans (`<!-- Lxxxx-Lyyyy -->`).
   - Bound by double-blind **Intent Contracts** (`sN-intent-contract.json`) declaring character friction points, unilateral physical force, and Try-Fail cycles (*"Yes, but..."* / *"No, and..."*).
   - Reports explicit **Creative Liberty Index** and itemized narrative departures.

---

## 🌿 Branch Topology & Workflow

To maintain a clean separation between the generic publishing framework and specific story manuscripts:

* **`main` (The Campaign-Agnostic Engine Framework):**
  * Core linters, verification gates, and build tools (`sessions/_scripts/`).
  * The `pipeline-steward` skill, decision codex (`DEC-001` through `DEC-020`), and agent guidelines.
  * Universal templates (`sessions/config/s6-intent-contract-template.json`).
* **`<campaign-branch>` (e.g. `uneraseable`):**
  * Active workspace for a specific campaign (*The Margin: The Stolen Weave*).
  * Raw audio transcripts, indexed turns, modular scene blocks, and compiled EPUBs.
* **`archive/<campaign>` (e.g. `archive/vumbua`):**
  * Frozen historical archives of earlier campaigns or experimental indices.

> [!IMPORTANT]
> **The Commit-Anchor Invariant for Post-Mortems:** Any architectural post-mortem citing an alternative implementation, PR escape, or historical failure must record **both the branch name and the immutable commit SHA** (e.g. `devin/1790479715-s5-fidelity-cuts` at `54c9d3a`).

---

## 📁 Repository Structure

* `docs/`: Master architectural codex (`pipeline_architecture.md`) and failure registries.
* `campaign/`: Worldbuilding, factions, locations, NPC/PC dossiers, and session prep.
* `sessions/`: Transcripts, indexing ledgers, and modular scene blocks.
  * `config/`: Session speaker configs (`sN-session-config.json`) and intent contracts (`sN-intent-contract.json`).
  * `data/raw/`: Raw STT audio transcripts (`sN-raw.md`).
  * `data/index/`: Line-indexed raw transcripts and Schema 2.0 web manifests.
  * `data/clean/blocks/`: Track A modular scene blocks (`sN-scene-XX.md`).
  * `data/clean/blocks_authorial/`: Track B cinematic scene blocks (`sN-scene-XX-alt.md`).
  * `_scripts/`: Verification linters, manifest generators, and the publishing runner.
* `novel/`: Book configuration, styling, and EPUB compiler (`generate_epub.py`).
* `.agents/skills/`:
  * `pipeline-steward/`: Anti-amnesia interface, living decision ledger, and pre-flight audit.
  * `novel-critic/`: Adversarial prose telemetry, Deep-POV filter-word linters, and cadence scanners.
  * `session-audit/`: Line-by-line transcript parity and ledger verification.
  * `critique-pipeline/`: Automated eBook / Critique Reader feedback ingestion.

---

## 🚀 Running the Publishing Pipeline

To run the complete verification suite, compile manifests, build EPUBs, and output the dual-track scorecard:

```powershell
python sessions/_scripts/run_publishing_pipeline.py s5
```

To run pre-flight architectural checks across all 20 decision records:
```powershell
python .agents/skills/pipeline-steward/scripts/audit_decision_ledger.py
```

---

## 📄 License
MIT License. Built for tabletop storytellers, Game Masters, and authors everywhere.
