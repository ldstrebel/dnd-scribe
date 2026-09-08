# 📜 The Margin: Community Critique & Editorial Decision Log

This log tracks every community review pull request, editor feedback payload, editorial decision, justification, and upstream skill calibration for the novelization pipeline.

---

## Summary of Ingested Reviews

| PR / Ingestion ID | Session | Reviewer | Items | Status | Key Actions / Justifications |
|---|---|---|---|---|---|
| `uneraseable-s1-strebs-482131` | S1 | Strebs | 6 | **RESOLVED** | Fixed "Paris" phonetic transcription, smoothed *Toll the Dead*, pruned filler, logged *Chill Touch* to Retcon Watchlist. |
| `uneraseable-s3-strebs-601985` | S3 | Strebs | 1 | **RESOLVED** | Full Session 3 grounding overhaul: eradicated truck hallucination; restored maintenance shed threshold, Ally (Maiden of Persephone), and Raleigh museum broom closet infiltration. |
| `uneraseable-s1-strebs-426204` | S1 | Strebs | 4 | **RESOLVED** | Justified Eusacles roulette dialogue; fixed Alfie Cockney voice tag; clarified lawnmower grass combat revival; smoothed Pierre ride transition. |

---

## Detailed PR Records

### 🔹 PR Record #001: `uneraseable-s1-strebs-482131`
- **Session:** Session 1 (*The Bus from Vegas & The Library of the Fates*)
- **Reviewer:** Strebs
- **Items Processed:**
  1. **Block `b015` ("Wow..." Pierre void breath):** Removed filler to tighten narrative pacing.
  2. **Blocks `b024` & `b043` (Fates NPC dialogue styling):** Fixed dialogue classifier to properly attribute Fate sisters as NPCs (`#a855f7`).
  3. **Block `b060` (*Chill Touch* cast):** 
     - *Feedback:* "This may need a retcon later. I think he doesn't know spells yet and player is learning and worshipping character."
     - *Decision & Justification:* Retained raw transcript canon (*Chill Touch* cast at Tabletop L740). Logged to Active Retcon Watchlist below to evaluate when player later defines magical progression.
  4. **Block `b080` (*Toll the Dead* combat transition):** Added sensory combat choreography between actors to maintain scene momentum.
  5. **Block `b131` ("Versailles to Brittany"):** 
     - *Feedback:* "Paris (worth keeping in mind French accent may result in transcript error this was Pair-ey, hard French sound)."
     - *Decision:* Corrected to "Versailles to Paris" and added phonetic accent disambiguation heuristics to `dnd-character-dossiers`.

---

### 🔹 PR Record #002: `uneraseable-s3-strebs-601985`
- **Session:** Session 3 (*The Museum Heist in North Carolina*)
- **Reviewer:** Strebs
- **Items Processed:**
  1. **Block `uneraseable_s03_b001` (Opening & Infiltration Route):**
     - *Feedback:* *"Ai took a lot of liberty on this session. Need to justify"*
     - *Root Cause Analysis:* Upstream drafting agent hallucinated a green Ford farm truck driving on an asphalt highway into Raleigh, completely bypassing the canonical Tabletop events.
     - *Investigation & Tabletop Transcript Grounding:* In `s3-raw-indexed.md` (lines 327–1200), the party stepped through the Margin's **maintenance shed door** directly into the shifting **Lost Roads** (Pierre Nat 20 Survival check), encountered **Ally, Maiden of Persephone** (who revealed Theodore's past quest and warned about temporal dilation), and emerged through an interdimensional threshold directly inside the **dusty storage annex / broom closet of the North Carolina Museum of History in Raleigh**.
     - *Action & Rewrite:* Complete overhaul across 10 scenes (Ch. 23–32) matching 100% transcript grounding:
       - **Ch. 23:** Shed threshold into the Lost Roads (Pierre's Nat 20, ancient Greek tools).
       - **Ch. 24:** Encounter with Ally (Maiden of Persephone), Theodore lore, Zeus/Seuss banter, pancake jokes, threshold into the Raleigh museum broom closet.
       - **Ch. 25:** Reconnaissance in the Aegean wing & locating the fractured limestone stele under glass.
       - **Ch. 26:** The six o'clock closing bell & stealth positioning.
       - **Ch. 27:** Alfie's Wordcraft (*Sleep* $\rightarrow$ *Sheep*), spectral sheep spawning and scattering guards.
       - **Ch. 28:** Grabbing the conservation lab coat & lanyard badge.
       - **Ch. 29:** Pierre bluffing security as the first-day Sorbonne intern.
       - **Ch. 30:** Alfie bypassing magnetic contact sensors & lifting the glass case.
       - **Ch. 31:** Aligning the fragment, golden/violet resonance, mending the stele.
       - **Ch. 32:** Sirens blaring, sprint through the service corridor, tumbling through the threshold back to The Margin.
     - *Result:* Parity 100% verified, 0 hallucinations, Schema 2.0 Web Manifest generated.

---

### 🔹 PR Record #003: `uneraseable-s1-strebs-426204`
- **Session:** Session 1 (*The Bus from Vegas & The Library of the Fates*)
- **Reviewer:** Strebs
- **Items Processed:**
  1. **Block `uneraseable_s01_b132` (Two Hundred Kilometers / Roulette):**
     - *Feedback:* *"I'm pretty sure this is Pierre"*
     - *Decision & Justification:* **Retained speaker as Eusacles.** In Tabletop canon (raw lines 1930–1956), Dravin states "About two hundred kilometers." Pierre (French student) remarks "Like Versailles to Paris." Eusacles (the demigod gambler from Las Vegas) immediately responds in frustration: *"That is so far from Vegas! Not even a little bit close! All I wanted to do was play roulette!"* Attributing this to Pierre would break character identity, as Eusacles is the Vegas gambler.
  2. **Block `uneraseable_s01_b134` (Alfie's Dialogue Color):**
     - *Feedback:* *"Another missed dialogue color"*
     - *Action:* Added `"cockney voice"` to `SPEAKER_ALIASES["alfie"]` in `generate_web_manifest.py`. Tagged as `#10b981`.
  3. **Block `uneraseable_s01_b139` (Lawnmower Combat Revival):**
     - *Feedback:* *"I don't know what's happening here but it makes no sense"*
     - *Action:* Clarified blocking: Alfie had fainted from magical exhaustion, Dravin gave him a sternum rub, and upon springing awake in combat mode, Alfie swung his needle rapier wildly at crabgrass before realizing no enemy was present.
  4. **Block `uneraseable_s01_b146` (Pierre Ride Transition):**
     - *Feedback:* *"The jumping back and forth without any transition text is hard to follow"*
     - *Action:* Added smooth bridging text showing Pierre noticing the panting doll in the grass and gently extending an open palm to offer him a shoulder ride.

---

## 🎯 Active Retcon & Continuity Watchlist

| Item ID | Topic | Potential Retcon / Ambiguity | Monitoring Strategy |
|---|---|---|---|
| `RTC-001` | Dravin Spellcasting (S1 Ch. 7) | Player cast *Chill Touch* early before formal wizard progression was clarified. | Keep table-accurate; if Session 4+ reveals backstory constraint, apply targeted in-universe explanation. |
| `RTC-002` | Eusacles Vegas Distance (S1 Ch. 10) | Eusacles lamenting distance from Vegas. | Preserved gambler motivation; verify alignment with S2/S3 Vegas casino lore. |
| `RTC-003` | Lost Roads Travel Mechanics (S3 Ch. 23-24) | Interdimensional traversal via thresholds vs. physical road transit. | Grounded in Margin maintenance shed & threshold doors. |
