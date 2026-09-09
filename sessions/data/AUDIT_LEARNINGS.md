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

---

### 🛑 FP-07: Dialogue Bluff Flattening
- **The Breakdown:** Reducing a 40-turn extended comedic social encounter (such as Pierre's first-day intern bluff) to a single dry statement loses the table's unique humor and character voice.
- **Upstream Guardrail for Writers:**
  - Retain character mispronunciations, geographical confusions, and the antagonist NPC's vanity/pride.
  - Maintain the balance between tension and tabletop wit.

---

## ⚖️ Guidelines for Downstream Creative Dramatic Freedom

To ensure downstream writers have the freedom to write gripping, elevated prose without triggering false audit alarms:

1. **Sensory & Atmospheric Description is Free:** Writers are fully empowered to add sensory texture (*"amber lantern light," "pine knots," "air-conditioned atrium," "smell of ozone"*).
2. **Mechanics-to-Narrative Translation is Encouraged:** Translating a `Nat 20 Divine Sense` into *"A natural twenty flared in his blood, revealing the consecrated refuge shrouded by the Mist"* is 100% compliant.
3. **Dialogue Compression is Supported:** Converting 15 turns of rules discussion into a single polished in-character line is welcomed, provided the core claim and speaker attribution are preserved.
4. **World-State Entities Must Be Grounded:** Never introduce new vehicles, high-tech security systems, or foreign NPCs without grounding in the raw transcript.