# 🔬 Post-Mortem & Pipeline Architecture Learnings: PR #33
**Incident Reference:** Feedback PR #33 (`critique/uneraseable-s5-strebs-106695`)  
**Session Analyzed:** Session 5 (*The Forgotten Trail & The Mad Doctor's Lecture*)  
**Reviewer:** `Strebs`  
**Date:** September 26, 2026  

---

## 1. Executive Summary

Feedback PR #33 exposed a critical class of narrative defects that passed all automated technical gates (`verify_manifest.py`, `verify_parity.py`, `critique_prose.py`). While our pipeline successfully verified line monotonicity, zero-regex speaker provenance, and absence of Earth-word leaks, it failed to detect **Character Intent Distortion**, **Hollywood Troping**, and **Causal Inversion**.

Specifically:
- Pierre was rewritten as a deliberate, calculating spy operator rather than an arrogant, aesthetically outraged French snob whose tantrums are opportunistically exploited by Dravin.
- Dravin was rewritten as a polite, considerate academic who "glanced down seeking consent" from Alfie, completely sanitizing the raw table action where Dravin ruthlessly snatched Alfie around the waist and slammed him into the relic tablet while the doll shouted in horror.
- The climactic temporal breach was causally inverted (the arrival of the Reductors, Dravin's apology, and the triggering of the vision were scrambled).
- Campus faculty were mislabeled with stale entities from earlier sessions (`attendant`).
- Raw markdown syntax (`***STALE.***`) escaped into published prose.

This post-mortem diagnoses the root causes of these escapes and establishes permanent pipeline upgrades to prevent recurrence across future sessions.

---

## 2. Root Cause Analysis

### A. The "Hollywood Competency" Bias (Pierre & The Custodian Heist)
* **The Symptom:** In blocks #107 and #109, Pierre murmurs *"Leave the custodian to French diplomacy, Professor"* with a *"predatory glint"*, executing a synchronized distraction so Dravin can steal keys.
* **The Table Reality:** Pierre (played by Luke S) had zero interest in helping Dravin steal keys. Pierre was genuinely, unreservedly furious that an American university had placed an 18th-century Hellenic classical bust next to an olive-drab plastic trash bin with pigeon droppings. Luke S was roleplaying a snobby Parisian architecture purist having a genuine fit. Dravin simply noticed Pierre about to make a scene and seized the moment to pickpocket Rick Ready.
* **Why the Pipeline Failed:**  
  The adapter failed to read and respect the actual ground truth right in front of it in the transcript. Luke S's words and focus were unambiguous: he was examining the stone, complaining about the pigeon filth, and yelling about the trash can. Instead of novelizing what the player actually said and did, the authoring process projected a synthetic Hollywood heist trope onto the scene, assuming conspiratorial teamwork where none existed. The failure was not a misunderstanding of Pierre's grand psychology—it was a failure to read the transcript and keep the player's true intent pure.

---

### B. "Polite Consent" Sanitization (Dravin & Alfie's Relic Breach)
* **The Symptom:** In block #209, Dravin *"glanced down at Alfie. Alfie looked back up, his carved wooden jaw tightening beneath his canvas ballcap"*, suggesting a mutual, heroic agreement to enter the temporal vision.
* **The Table Reality:** Dravin never asked. William Webb simply declared that Dravin seized Alfie by the torso and smashed him down onto the artifact binder to force a timeline reading. Sophie Foreman Noone roleplayed Alfie kicking and shouting *"Not again! Why me, not again!"* in sheer terror as he was compressed against the iron binding.
* **Why the Pipeline Failed:**  
  The prose generator instinctively softened interpersonal violence between party members, seeking to make the protagonist "likeable" and "ethical." By inserting mutual consent where none existed at the table, the adapter completely neutered the dramatic tension and stripped Alfie of her tragic vulnerability.

---

### C. Staging Gaps & Missing Connective Bridges
* **The Symptom:** Pacing felt rushed during campus navigation (Block #72, #132, #157). Dravin suddenly appears at the podium; Pierre vanishes and reappears sitting next to the introduction host.
* **The Table Reality:** At the table, multiple micro-actions occurred:
  1. Pierre and Rick Ready argued over whether janitors schedule sculpture curriculum.
  2. Dravin observed campus security chasing a demonstrator and used the distraction to slip into the faculty wing.
  3. Dravin bluff-scolded Pierre in his "dean voice," banishing Pierre back into the lecture hall where Pierre sat down right next to the traumatized faculty host who thought he had finally gotten rid of him.
* **Why the Pipeline Failed:**  
  When tabletop transcripts contain rapid banter without explicit GM physical staging, the novelizer tended to cut straight to the next major mechanic rather than constructing the comedic and spatial bridge.

---

### D. Stale Entity Carryover (`attendant` vs. `faculty_host`)
* **The Symptom:** Block #140 attributed lines spoken by the university department host (introducing Dr. Thorne) to `attendant` (a North Carolina museum employee from Session 3!).
* **The Table Reality:** The speaker was the University University Faculty Host.
* **Why the Pipeline Failed:**  
  The session config generator reused existing character keys from the global campaign dossier. Because `attendant` was already an active NPC key, ambiguous table lines in the lecture hall were lazily assigned to `attendant` without validating that the scene had moved hundreds of miles to an academic amphitheater in Pennsylvania.

---

### E. Chronological Inversion at Combat Thresholds
* **The Symptom:** In block #229, Dravin whispers *"Sorry, Alfie"* after the Reductors have already breached the room, scooping him up as combat starts.
* **The Table Reality:** Dravin whispered *"Sorry, Alfie"* BEFORE slamming him into the binder. The slamming of the doll into the relic triggered the 1948 temporal vision, and the Reductors kicked down the doors *at the exact moment* the vision ended, catching the party reeling.
* **Why the Pipeline Failed:**  
  The authoring tool struggled to stage simultaneous actions (a vision occurring internally while enemies breach externally), flattening the events into a sequential list and reversing the causal trigger.

---

## 3. Pipeline Architecture Hardening: Upgrades & Prevention

To ensure these failures cannot escape again:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PIPELINE DEFENSE UPGRADES                          │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. Transcript-First Intent Grounding (Zero Hallucinated Motivations)   │
│    • Never invent artificial conspiratorial intent or project generic   │
│      narrative tropes onto a character.                                 │
│    • Ground every character action, emotional trigger, and focus beat   │
│      STRICTLY in what the player actually declared in the transcript.    │
│    • In Scene 6, Pierre was examining masonry and throwing a tantrum    │
│      about a trash can—the text literally stated this. We failed by not │
│      reading what was right in front of us and inventing fake intent.   │
├─────────────────────────────────────────────────────────────────────────┤
│ 2. The "Unflinching Staging" Law (Anti-Polite Sanitization)             │
│    • Mandate that player mechanical declarations (shoving, grabbing,    │
│      slamming without consent) are NEVER softened into mutual nodding.   │
├─────────────────────────────────────────────────────────────────────────┤
│ 3. Automated Markdown Syntax Linter in critique_prose.py                │
│    • Hard check for raw markdown leaks: `***`, `__`, `###` in prose.    │
├─────────────────────────────────────────────────────────────────────────┤
│ 4. Cross-Session Entity Isolation Check in verify_parity.py             │
│    • Verifies all speaker IDs in session config against scene location. │
│    • Flags local-setting entity leaks (e.g. Session 3 museum staff in   │
│      Session 5 Pennsylvania university).                                │
├─────────────────────────────────────────────────────────────────────────┤
│ 5. Simultaneous Event Chronology Staging Checklist                      │
│    • Standardized pattern for staging parallel psychic visions and      │
│      physical threshold ambushes.                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Action Items & Verification
- [x] Ingest PR #33 feedback payload into `sessions/data/critiques/uneraseable-s5-strebs-106695.json`.
- [x] Author comprehensive response ledger in `sessions/data/critiques/s5-pr-33-feedback-response.md`.
- [x] Post summary comment to GitHub PR #33 and close PR.
- [x] Delete remote review branch `critique/uneraseable-s5-strebs-106695`.
- [x] Update `sessions/data/critiques/CRITIQUE_LOG.md` with PR Record #006.
- [x] Apply all 20 prose and attribution corrections across `s5-scene-*.md` and rebuild manifests.
