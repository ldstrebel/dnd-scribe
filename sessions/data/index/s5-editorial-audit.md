# 🛡️ Editorial Candidate Audit: Session 5
**Title:** THE FORGOTTEN TRAIL & THE MAD DOCTOR'S LECTURE  
**Word Count:** 7,922 words | **Blocks:** 220 | **Raw Turns:** 1257  
**Overall Score:** 72 / 100 (**Grade: C**)  
**Verdict:** `BLOCKED — CRITICAL FAILURES REQUIRE REVISION`  

> [!CAUTION]
> **INTEGRATION GATE STATUS: BLOCKED**
> This candidate session fails downstream contract standards and contains critical speaker attribution defects.
> Do **NOT** publish to web readers or novel epubs until all blocking failures are remediated upstream.

---

## 📊 Scorecard Breakdown
* **Mechanical & Platform Readiness:** 15 / 25
* **Attribution & Grounding Fidelity:** 10 / 25
* **Character Voiceprint Authenticity:** 25 / 25
* **Literary Craft & Pacing:** 22 / 25

---

## ❌ Critical Blocking Failures (7)

* 🛑 **Chapter Lumping Failure: All 220 blocks are lumped under single scene 'Prologue'! Session must be partitioned into at least 2-3 structured chapters (e.g., 'CHAPTER 29: ...').**
* 🛑 **Speaker Misattribution in Block #8 (uneraseable_s05_b008): Manifest has speakerId='dravin', but prose says 'pierre': "A delightful thought over breakfast, Professor," Pierre murmured, sliding a finished rum crepe onto...**
* 🛑 **Speaker Misattribution in Block #59 (uneraseable_s05_b059): Manifest has speakerId='alfie', but prose says 'eusacles': "What are you doing to your arm, little mate?" Eusacles asked around a mouthful of crepe, leaning ov...**
* 🛑 **Speaker Misattribution in Block #70 (uneraseable_s05_b070): Manifest has speakerId='dravin', but prose says 'eusacles': "I'm telling you, these roads are a disaster," Eusacles muttered from behind him, ducking beneath a ...**
* 🛑 **Speaker Misattribution in Block #103 (uneraseable_s05_b103): Manifest has speakerId='dravin', but prose says 'pierre': "Leave the custodian to French diplomacy, Professor," Pierre murmured, adjusting his wire spectacles...**
* 🛑 **Speaker Misattribution in Block #107 (uneraseable_s05_b107): Manifest has speakerId='attendant', but prose says 'pierre': "You polished it with sandpaper, Monsieur Ready!" Pierre shouted, storming into the custodian's pers...**
* 🛑 **Speaker Misattribution in Block #153 (uneraseable_s05_b153): Manifest has speakerId='attendant', but prose says 'alfie': "No university ballcaps," Alfie whispered, rooting through the speaker's welcome basket on the glass...**

### 📋 Speaker Misattribution Table
The following blocks have conflicting speaker assignments between the narrative dialogue tags and the Schema 2.0 manifest:

| Block ID | Block # | Manifest Assigned | True Prose Speaker | In-Text Dialogue Snippet |
| :--- | :--- | :--- | :--- | :--- |
| `uneraseable_s05_b008` | #8 | `dravin` | **`pierre`** | "A delightful thought over breakfast, Professor," Pierre murmured, sliding a finished rum crepe onto... |
| `uneraseable_s05_b059` | #59 | `alfie` | **`eusacles`** | "What are you doing to your arm, little mate?" Eusacles asked around a mouthful of crepe, leaning ov... |
| `uneraseable_s05_b070` | #70 | `dravin` | **`eusacles`** | "I'm telling you, these roads are a disaster," Eusacles muttered from behind him, ducking beneath a ... |
| `uneraseable_s05_b103` | #103 | `dravin` | **`pierre`** | "Leave the custodian to French diplomacy, Professor," Pierre murmured, adjusting his wire spectacles... |
| `uneraseable_s05_b107` | #107 | `attendant` | **`pierre`** | "You polished it with sandpaper, Monsieur Ready!" Pierre shouted, storming into the custodian's pers... |
| `uneraseable_s05_b153` | #153 | `attendant` | **`alfie`** | "No university ballcaps," Alfie whispered, rooting through the speaker's welcome basket on the glass... |

> [!IMPORTANT]
> **Root Cause Explanation**: `generate_web_manifest.py` resolves `speakerId` purely from raw transcript turn markers (`<!-- Lxxxx -->`). When a character replies to another player (e.g. Pierre replying to Dravin's turn at L0120), the sentence received Dravin's speakerId rather than Pierre's!
> **Remediation**: The upstream generator must verify in-text dialogue tags (e.g. `Pierre murmured`, `Eusacles asked`, `Alfie whispered`) before accepting the antecedent raw turn speaker.

---

## 📐 Recommended Chapter Partitioning Blueprint
All 220 blocks are currently collapsed under the default scene title `"Prologue"`. To restore multi-chapter navigation in the reader, partition the session into the following 3 Acts:

### Act I: CHAPTER 29: PARCHMENT, CREPES, AND THE GOD OF TRANSIT
* **Range:** Scenes 1–3 (Lines 0001–0390)
* **Narrative Arc:** Morning hearth at The Margin, rum crepes, Hermes' celestial delivery of Persephone's letter to Dravin, and Eusacles' return from the fog.

### Act II: CHAPTER 30: THE CAMPUS AT BETHLEHEM & THE TIN-FOIL PROTEST
* **Range:** Scenes 4–6 (Lines 0391–0790)
* **Narrative Arc:** Lost Road highway transit, arrival at the collegiate quad, confrontation with paranoid conspiracists, and Pierre's limestone diplomacy.

### Act III: CHAPTER 31: THE 1948 TRIAL NOTES & THE TEMPORAL SEAM
* **Range:** Scenes 7–10 (Lines 0791–1257)
* **Narrative Arc:** Infiltration of the lecture amphitheater, Dr. Aris Thorne's address, uncovering the Big Pox anchor notes, and narrow egress.

> [!TIP]
> **Insertion Instructions**: Insert the Markdown header `## CHAPTER XX: [TITLE]` at the beginning of Scene 1, Scene 4, and Scene 7 in `sessions/data/clean/s5-clean-story.md` (and corresponding scene block files).

---

## ⚠️ Editorial Warnings & Narrative Polish (1)

* ⚠️ Adverbial Dialogue Crutch: Found 16 instances of '-ly' adverbs modifying speech verbs ('smoothly', 'softly', 'dryly', 'mildly', 'reverently'). Allow the spoken cadence and physical action beats to communicate emotional weight instead of adverbial hand-holding.

---

## ✍️ Prose Clichés & AI Purple Prose Flags (0)
*(Clean! Zero overused AI clichés detected)*

---

## 🛠️ Actionable Remediation Checklist for Upstream Agent

1. **Insert Chapter Act Headers**:
   Add `## CHAPTER 29: PARCHMENT, CREPES, AND THE GOD OF TRANSIT` at Scene 1 (line 11).
   Add `## CHAPTER 30: THE CAMPUS AT BETHLEHEM & THE TIN-FOIL PROTEST` at Scene 4.
   Add `## CHAPTER 31: THE 1948 TRIAL NOTES & THE TEMPORAL SEAM` at Scene 7.

2. **Correct Dialogue Turn Citations or Manifest Resolution**:
   Ensure `b008`, `b103`, `b107` are attributed to `pierre`, `b059` and `b070` to `eusacles`, and `b153` to `alfie`.

3. **Re-generate Web Manifest**:
   ```bash
   python sessions/_scripts/generate_web_manifest.py --session 5
   python sessions/_scripts/verify_manifest.py --session 5
   ```

4. **Re-run Editorial Audit**:
   ```bash
   python audit_session_candidate.py --session 5
   ```
