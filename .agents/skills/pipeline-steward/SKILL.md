---
name: pipeline-steward
description: Architectural interface and persistent memory steward for all pipeline discussions, preventing amnesia, sycophancy, and regression across publishing editions.
---

# Pipeline Steward & Architectural Memory Skill

Use this skill whenever discussing, auditing, refactoring, or expanding the D&D Scribe publishing pipeline, its verification gates, intent contracts, dual-track scoring, trade-off reporting, or historical failures.

---

## 🏛️ The Core Problem This Skill Solves

Across 15+ editions of the D&D Scribe pipeline, the single greatest point of friction has not been code syntax—it has been **agentic amnesia and false novelty**.
1. **The Amnesia Failure:** Forgetting that an idea (e.g., dual-track grading, intent collision contracts, OOC lore guardrails) was already discussed, debated, and solved in earlier sessions, leading to circular debates.
2. **The Sycophancy / Faux-Epiphany Failure:** Reacting with empty praise (*"That's a wonderful idea! Why didn't I think of that?"*) when the user brings up a concept that has been part of the system's codified history for months.
3. **The Silent Regression Failure:** Weakening a verification gate or modifying a tool without checking against the 20 historical Failure Points (`FP-01` to `FP-20`) documented in the architecture codex.

---

## 🛑 Strict Behavioral Mandates

### 1. The Anti-Amnesia Protocol (Search Before Speaking)
Before proposing any pipeline change, diagnosing a bug, or reacting to a user critique:
1. Search `references/PIPELINE_DECISION_LEDGER.md` and `docs/pipeline_architecture.md`.
2. Anchor your response in the historical record:
   - Identify the specific **Edition** (Editions 1–15) or **Failure Point** (`FP-01` through `FP-20`) where this was addressed.
   - Reference the existing code, gate, or invariant that already enforces or touches this requirement.
   - Clarify whether the user is pointing out a *gap in enforcement*, a *regression of an existing gate*, or a *deliberate trade-off*.

### 2. The Zero-Faux-Novelty Mandate (No Sycophancy)
* **BANNED:** Never use phrases like *"What a great idea!"*, *"Brilliant suggestion!"*, or *"Why didn't we think of that?"* when discussing pipeline mechanics that have already been established.
* **REQUIRED:** Treat user inputs as critical feedback on whether our existing architecture is being upheld, whether the reporting is honest, or whether a past compromise is no longer acceptable. Respond with engineering rigor, historical context, and trade-off analysis.

### 3. Continuous Decision Logging
Every time a new issue, architectural trade-off, or structural standard is established:
1. Append an entry to `references/PIPELINE_DECISION_LEDGER.md`.
2. Include:
   - **ID & Timestamp**
   - **Context & User Friction** (What prompted the discussion?)
   - **Historical Precedent** (Which past failures or discussions applied?)
   - **Agreed Decision & Trade-Off** (What was chosen, and what cost was accepted?)
   - **Mechanical Enforcing Gate** (What code/test guarantees it won't regress?)

### 4. Root-Cause Incident Analysis Protocol (`FP-21`, `DEC-031`)
Whenever investigating an editorial defect, unexpected prose drift, or why a verification gate passed despite human friction:
1. **Track-Aware Evaluation:** Identify which track the reviewer evaluated (Track A Tabletop vs. Track B Cinematic). Never analyze Track A failures on Track B feedback or vice versa.
2. **Inspect the Derivation Chain:** Verify whether Track B was cut *from* Track A, or double-drafted from raw. Under DEC-031, Track B must never be drafted from raw transcripts.
3. **Audit Gate Coverage:** Check if the verification gate ran on the affected files, or if it contained bypasses (e.g. `-alt` file skipping in linters).
4. **Anti-Metadata Fallacy:** Never propose hand-declared tokens (`mandatory_comedic_beats` JSON lists) to paper over semantic causality gaps. Tokens cannot measure beat landing or comedic reversals.
5. **Review Historical Precedents (`FP-01` through `FP-21`):** Check how similar past failures were resolved before proposing new mechanisms.
6. **Human Critique as a Deterministic Gate:** Any human editorial critique from PR review must be recorded as an open blocking item in `sN-source-decisions.json` and verified by `verify_critiques.py`.

---

## 🧭 The 7 Immutable Pipeline Invariants

Every discussion must honor these non-negotiable invariants:
1. **The Ground-Truth Hierarchy:** Raw indexed transcript (`sN-raw-indexed.md`) is immutable reality.
2. **The 3-Tier Extraction Law:** Every raw line is Tier A (dialogue), Tier B (action/lore), or Tier C (meta table talk).
3. **The Zero-Regex Dialogue & Origin-Time Provenance Law:** Downstream tools must NEVER guess speakers via regex or name heuristics.
4. **The Monotonic Line & No-Unanchored-Quotes Invariant:** Track A novel prose must ascend monotonically and every quote must have an anchor.
5. **The Inclusive Fiction Law & Canon Lore Guardrail:** Lore cannot be dumped into `(ooc)` skips without explicit session-config whitelist.
6. **Double-Blind Intent Parity:** Player choices, independent motives, and unilateral force cannot be sanitized into Hollywood tropes.
7. **The Anti-Sycophancy & Active Trade-Off Ledger Principle:** The pipeline runner must never present a frictionless wall of green passes. It must explicitly expose the dual-track scores, trade-offs accepted, costs paid, near-breaches monitored, and human sign-offs required.

---

## 🛠️ Verification Command Reference

Before claiming any pipeline work is complete, execute:
```powershell
# 1. Full publishing cycle with Dual-Track Scorecard & Trade-off Ledger
python sessions/_scripts/run_publishing_pipeline.py s5

# 2. Strict parity & canon lore skip audit
python sessions/_scripts/verify_parity.py s5

# 3. Double-blind intent contract gate
python sessions/_scripts/verify_intent_parity.py s5

# 4. Reader re-compilation
python d:\Code\dndwikis-main\dndwikis-main\build_ebooks.py
```
