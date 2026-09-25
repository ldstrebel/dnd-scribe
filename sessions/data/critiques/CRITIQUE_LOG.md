# 📋 Critique & PR Feedback Ingestion Log

This log tracks all community, player, and editor critique payloads ingested from the GitHub Pages eBook & Critique Reader, detailing the reviewed session, reviewer, anchors addressed, action taken, and detailed rationale/justification.

---

## Ingested PR Feedback Records

### 🧾 PR Record #006: `editorial-s5-candidate-audit`
- **Branch:** `main` (Audits `c5e088c` & `1b5a5b6`)
- **Session:** `s5` (*The Forgotten Trail & The Mad Doctor's Lecture*)
- **Reviewer:** `Adversarial Editorial Critic / Upstream QA`
- **Audit File:** [`sessions/data/index/s5-editorial-audit.md`](file:///d:/Code/dnd-scribe/sessions/data/index/s5-editorial-audit.md)
- **Response File:** [`sessions/data/critiques/s5-editorial-response.md`](file:///d:/Code/dnd-scribe/sessions/data/critiques/s5-editorial-response.md)
- **Status:** `[RESOLVED & APPLIED with FORMAL PUSHBACK LEDGER]`
- **Verification Gates:** `verify_manifest.py [PASS]`, `verify_parity.py [PASS]`, `macro_auditor.py [PASS]`, `critique_prose.py [PASS]`, `novel/generate_epub.py [PASS]`

#### 📝 Item-by-Item Review & Justification Ledger

| Block / Issue | Speaker | Category | Reviewer Note | Action Taken | Justification & Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `All Blocks` | All | Architecture / Pacing | *"All 220 blocks are lumped under single scene 'Prologue'!"* | **`[APPLIED]`** | Partitioned into Chapter 29 (Scenes 1–3), Chapter 30 (Scenes 4–6), and Chapter 31 (Scenes 7–10). Upgraded `generate_web_manifest.py` line parsing. |
| `b008` | Pierre | Attribution / Marker Drag | *"Manifest has speakerId='dravin', but prose says 'pierre'"* | **`[APPLIED]`** | Separated Pierre's crepe response (`<!-- L0121 -->`) from Dravin's spore description (`<!-- L0120 -->`). Corrected to `pierre`. |
| `b060` | Eusacles | Attribution / Turn Fusion | *"Manifest has speakerId='alfie', but prose says 'eusacles'"* | **`[APPLIED]`** | Separated Alfie's dialogue (`<!-- L0429 -->`) from Eusacles' question (`<!-- L0435 -->`). Corrected to `eusacles`. |
| `b071` | Eusacles | Attribution / Fused Turn | *"Manifest has speakerId='dravin', but prose says 'eusacles'"* | **`[APPLIED]`** | Disentangled Dravin's survival declaration (`<!-- L0550 --> <!-- L0558 -->`) from Eusacles' Lost Roads complaint (`<!-- L0566 --> <!-- L0567 -->`). Eliminated dialogue stutter. |
| `b104` | Pierre | Attribution / Turn Inversion | *"Manifest has speakerId='dravin', but prose says 'pierre'"* | **`[APPLIED]`** | Pierre's "French diplomacy" quip mapped to L0753; Dravin's pickpocket intent mapped to L0735/L0739. Corrected to `pierre`. |
| `b108` | Pierre | Attribution / Inverted Turns | *"Manifest has speakerId='attendant', but prose says 'pierre'"* | **`[APPLIED]`** | Disentangled Pierre's sandpaper accusation (`<!-- L0768 -->`) from Rick Ready (`<!-- L0762 -->`, `<!-- L0771 -->`). Corrected to `pierre`. |
| `b156` | Alfie | Attribution / Missing Marker | *"Manifest has speakerId='attendant', but prose says 'alfie'"* | **`[APPLIED]`** | Attached explicit anchor `<!-- L1022 -->` (Sophie: *"Al's looking for hats for university caps"*). Corrected to `alfie`. |
| `Scene 3` | Dravin | Narrative / Character Interiority | *"Zero interiority regarding what it means for an aging Stanford academic to learn his mother is a chthonic deity..."* | **`[PUSHBACK - DEFERRED]`** | **Adaptation Boundary Law:** William Webb deliberately chose not to stage an existential crisis at the table. Retroactively fabricating 1,500 words of angst risks severe continuity breaks with Session 6. Transferred to `s5-context-briefing.md` and `s6-context-briefing.md` for player/GM exploration. |
| `Scenes 4–7` | Alfie | Narrative / Screen Time | *"Alfie suffers from 'luggage syndrome'—sits silently without lines or agency for dozens of paragraphs."* | **`[PUSHBACK - GROUND TRUTH]`** | **Ground-Truth Hierarchy:** Sophie was quiet and Alfie was riding on Dravin's shoulder during highway transit. Fabricating unplayed rogue actions overwrites the player's actual table choices. Alfie's active actions (gift basket looting, warning about statues) remain fully staged. |

---

### 🧾 PR Record #005: `uneraseable-s3-strebs-855517`
- **Branch:** `critique/uneraseable-s3-strebs-855517`
- **Session:** `s3` (*The Raleigh Museum & The Aegean Inscription*)
- **Reviewer:** `Strebs`
- **Payload File:** [`sessions/data/critiques/uneraseable-s3-strebs-855517.json`](file:///d:/Code/dnd-scribe/sessions/data/critiques/uneraseable-s3-strebs-855517.json)
- **Export Timestamp:** `2026-09-16T01:57:35.517Z`
- **Status:** `[RESOLVED & APPLIED]`
- **Verification Gates:** `verify_manifest.py [PASS]`, `verify_parity.py [PASS]`, `generate_web_manifest.py [PASS]`, `novel/generate_epub.py [PASS]`

#### 📝 Item-by-Item Review & Justification Ledger

| Block ID | Speaker | Category | Reviewer Note | Action Taken | Justification & Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `uneraseable_s03_b088` (now `b092`) | Pierre -> Museum Attendant (`attendant`) | Tone / Speaker Attribution | *"why is this all showing up as Pierre?"* | **`[APPLIED]`** | Spoken line by senior museum curator (*"It is the premier history institution in the country, young man, not chewing gum!"*, L1633) was previously colored as Pierre. Attributed to Museum Attendant (`attendant`) with distinct NPC coloring and voice routing. |

---

### 🧾 PR Record #004: `uneraseable-s4-strebs-752800`
- **Branch:** `critique/uneraseable-s4-strebs-752800`
- **Session:** `s4` (*The Medusa Protocol & Echoes Across the Lost Roads*)
- **Reviewer:** `Strebs`
- **Payload File:** [`sessions/data/critiques/uneraseable-s4-strebs-752800.json`](file:///d:/Code/dnd-scribe/sessions/data/critiques/uneraseable-s4-strebs-752800.json)
- **Export Timestamp:** `2026-09-25T01:29:12.800Z`
- **Status:** `[RESOLVED & APPLIED]`
- **Verification Gates:** `verify_manifest.py [PASS]`, `verify_parity.py [PASS]`, `verify_alternate_scene.py [PASS]`, `generate_web_manifest.py [PASS]`, `novel/generate_epub.py [PASS]`

#### 📝 Item-by-Item Review & Justification Ledger

| Block ID | Speaker | Category | Reviewer Note | Action Taken | Justification & Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `uneraseable_s04_b047_alt6` | Alfie | General / OOC Table Dialogue | *"Out of character dialog included"* | **`[APPLIED]`** | Removed 3rd-person table description (*"Alfie is absolutely shook to his wooden core"*) from quoted spoken dialogue and converted it into narrator prose describing Alfie's physical trembling after touching the tablet (L0390). |
| `uneraseable_s04_b070_alt3` | Pierre | General / Meta Dialogue Leak | *"Another meta caught as a dialogue"* | **`[APPLIED]`** | Converted Luke S's 3rd-person player theory (*"Pierre believes that all Gorgons are essentially French..."*) into active narrator prose (L0459), preserving only the in-world spoken shout (*"Fresh bread!"*). |
| `uneraseable_s04_b110_alt4` | Pierre -> Alfie / Pierre | Formatting / Speaker Color & Tagging | *"Color of dialogue wrong"* | **`[APPLIED]`** | Separated the fused paragraph in Scene 6 into dedicated paragraphs: Alfie's *Mage Hand* terracotta pot drop (L0730–L0755) as Alfie's action/dialogue, and Pierre's attendant rescue quip (L0757–L0769) as Pierre's dialogue. |
| `uneraseable_s04_b141_alt4` | Pierre -> Alfie / Pierre | Formatting / Multi-Speaker Paragraph | *"Dialogue mixed. This is Alfie with the hat"* | **`[APPLIED]`** | Decomposed the triple-speaker paragraph in Scene 8 into 3 separate paragraphs: (1) gallery quiet & Nincy statue (L0969–L0970), (2) Alfie finding the souvenir trucker hat (L0984–L0988), and (3) Pierre asking about the dragon display (L0990). |

---

### 🧾 PR Record #003: `uneraseable-s3-claire-ick-321600`

- **Branch:** `critique/uneraseable-s3-claire-ick-321600`
- **Session:** `s3` (*The Raleigh Museum & The Aegean Inscription*)
- **Reviewer:** `Claire Ick`
- **Payload File:** [`sessions/data/critiques/uneraseable-s3-claire-ick-321600.json`](file:///d:/Code/dnd-scribe/sessions/data/critiques/uneraseable-s3-claire-ick-321600.json)
- **Export Timestamp:** `2026-09-16T00:58:41.600Z`
- **Status:** `[RESOLVED & APPLIED]`
- **Verification Gates:** `verify_manifest.py [PASS]`, `verify_parity.py [PASS]`, `critique_prose.py [PASS]`, `generate_web_manifest.py [PASS]`, `novel/generate_epub.py [PASS]`

#### 📝 Item-by-Item Review & Justification Ledger

| Block ID | Speaker | Category | Reviewer Note | Action Taken | Justification & Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `uneraseable_s03_b026` | Prof. Edward Dravin | General / Dialogue & Character Fidelity | *"where did all the back and forth with Nincy (not Nancy) go?"* | **`[APPLIED - RESTORED]`** | **NPC Name & Dialogue Restoration:** Raw transcript L0725–L0750 confirmed the receptionist explicitly stated her name was *Nincy* (*"Nincy with an I... N-I-N-C-Y... Some people with my accent, they don't hear"*). Fully dramatized the flirty banter with Dravin (*"You are quite the exhibit, Nincy"*), Pierre's academic wingman hype, Alfie's pull-string "shipwrecked Marvel action figure" routine (L0781–L0790), Pierre's botched pickpocket attempt on her lanyard badge (L0834–L0837), Dravin chucking the doll across the lobby, Pierre's panic (*"I told you that doll was haunted!"*), Nincy calling security, and Pierre's quip (*"He wants to be with you, Nincy!"*) preceding the *Sleep* $\rightarrow$ *Sheep* Wordcraft transmigration. Registered `nincy` in `generate_web_manifest.py`. |
| `uneraseable_s03_b040` | Narrator | Pacing / Chapter Architecture | *"there are way too many chapters... give them time to breathe"* | **`[APPLIED - CONSOLIDATED]`** | **Chapter Restructuring:** Consolidated 10 fragmented micro-chapters (where 100-line blocks each carried a separate `## CHAPTER` header, resulting in single-sentence chapters) into **3 substantial, breathing novel chapters** for Session 3: **Chapter 23: The Maintenance Shed Threshold** (Scenes 1–3), **Chapter 24: The Heist at the Front Desk** (Scenes 4–5), and **Chapter 25: The Research Annex & The Closing Bell** (Scenes 6–10). Scene transitions within chapters demarcated via `<hr class="ornament"/>` (`---`). Reduced Book 1 total chapters from 32 to 25. |

---

### 🧾 PR Record #002: `uneraseable-s3-strebs-140519`
- **Branch:** `critique/uneraseable-s3-strebs-140519`
- **Session:** `s3` (*The Raleigh Museum & The Aegean Inscription*)
- **Reviewer:** `Strebs`
- **Payload File:** [`sessions/data/critiques/uneraseable-s3-strebs-140519.json`](file:///d:/Code/dnd-scribe/sessions/data/critiques/uneraseable-s3-strebs-140519.json)
- **Export Timestamp:** `2026-09-09T00:02:20.519Z`
- **Status:** `[RESOLVED & APPLIED]`
- **Verification Gates:** `audit_semantic_grounding.py [PASS]`, `verify_parity.py [PASS]`, `generate_web_manifest.py [PASS]`, `novel/generate_epub.py [PASS]`

#### 📝 Item-by-Item Review & Justification Ledger

| Block ID | Speaker | Category | Reviewer Note | Action Taken | Justification & Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `uneraseable_s03_b036` | Narrator | General / Style | *"Repetitive start of lines and again tiny paragraphs"* | **`[APPLIED]`** | Eliminated repetitive sentence openers (*"Pierre examined... Pierre examined..."*) and expanded the scene into a rich tactical discussion between Pierre and Alfie. Restored the full tabletop deduction: realizing they only need physical touch (not hauling a 500-lb slab), inspecting the chipped corners of the tablet, and designing the forged limestone keystone plan. |
| `uneraseable_s03_b045` | Pierre | Continuity / Pacing | *"Needs descriptive pacing to paint the scene better"* | **`[APPLIED]`** | Expanded Pierre's first-day intern social bluff from a single dry line into a fully realized comedic exchange: Pierre's Parisian deadpan, confusing South vs North Carolina, pretending his staff email is inactive, asking if Massachusetts is a chewing gum brand, and feeding the curator's ego to get the cart positioned directly next to the exhibit plinth. |
| `uneraseable_s03_b053` | Narrator | General / Plot Anchor | *"Is this actually where we ended?"* | **`[APPLIED - CALIBRATED]`** | Clarified and tightly aligned the scene termination with the exact tabletop cliffhanger at `L1656`: the 6:00 PM closing chimes, Nancy live-streaming on multiple phones to social media (*"a little excitement in the Greek wing tonight"*), the staging cart positioned beside the pedestal, and the armed security guard's gloved hand hovering over the large red master button to bring down the reinforced protective claw. |

---

### 🧾 PR Record #001: `uneraseable-s1-strebs-482131`
- **Branch:** `critique/uneraseable-s1-strebs-482131`
- **Session:** `s1` (*The Bus from Vegas & The Library of the Fates*)
- **Reviewer:** `Strebs`
- **Payload File:** [`sessions/data/critiques/uneraseable-s1-strebs-482131.json`](file:///d:/Code/dnd-scribe/sessions/data/critiques/uneraseable-s1-strebs-482131.json)
- **Export Timestamp:** `2026-09-08T03:34:42.131Z`
- **Status:** `[RESOLVED & MERGED]`
- **Verification Gates:** `verify_manifest.py [PASS]`, `verify_parity.py [PASS]`, `novel/generate_epub.py [PASS]`

#### 📝 Item-by-Item Review & Justification Ledger

| Block ID | Speaker | Category | Reviewer Note | Action Taken | Justification & Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `uneraseable_s01_b015` | Pierre -> Narrator | Rewrite / Flow | *"Clear this. Breaks flow"* | **`[APPLIED]`** | Spoken dialogue right at the explosive moment of planar displacement punctures the terror and velocity of the transition. Replaced with visceral sensory breath-catching at `L0968` without altering plot points. |
| `uneraseable_s01_b024` | Narrator -> Fates | Audio Cue / Tag | *"Should be red for NPCs?"* | **`[APPLIED]`** | Dialogue from the second Fate was misattributed to `narrator` because regex lacked ordinal aliases (`"the second"`). Added ordinal aliases in `generate_web_manifest.py` so the web reader and ElevenLabs TTS correctly assign NPC purple styling and NPC voice routing. |
| `uneraseable_s01_b043` | Narrator -> Fates | Audio Cue / Tag | *"Red too?"* | **`[APPLIED]`** | Dialogue from the eldest Fate was misattributed to `narrator` (`"the eldest"`). Tagged as `speakerId: "fates"` to maintain proper NPC voice and UI badge consistency. |
| `uneraseable_s01_b060` | Dravin | Mechanistic Retcon | *"This may need a retcon later. I think he doesn't know spells yet and player is learning and worshipping character"* | **`[WATCHLIST / DEFERRED RETCON]`** | **Preserved table event:** The player explicitly declared *"Chill Touch!"* at the table during this turn. Preserved Dravin invoking the spell while framing it in prose as an unbidden, surprising instinct he is struggling to understand. Added to campaign **Retcon Watchlist** below for future continuity audit. |
| `uneraseable_s01_b080` | Dravin -> Narrator | Combat Transition | *"Transition here is super abrupt. Have the think about how we help add some questions between actors in DND combat to keep the scene moving and clearly communicated"* | **`[APPLIED]`** | Added connective prose tissue: Alfie tumbles clear and calls a flank alert; Dravin steps into the breach to cover the retreat before the bell toll fails. |
| `uneraseable_s01_b131` | Pierre | Geography / Accent | *"Paris (worth keeping in mind French accent may result in transcript error this was Pair-ey, hard French sound)"* | **`[APPLIED - CORRECTED]`** | The reviewer clarified that the player intended *"Versailles to Paris"* (or *"Paris to Versailles"*), which automated speech-to-text had garbled into an obscure landmark due to French phonemes (*"Pair-ey"*). Corrected directly to *"Like Versailles to Paris."* avoiding over-assumptive provincial rewrites. |

---

## 👁️ Active Retcon & Lore Watchlist

| Watch Item ID | Session & Anchor | Subject | Tabletop Fact | Potential Retcon / Ambiguity | Follow-up Trigger |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `RETCON-S01-01` | `s1` (`b060`, `L1150`) | Dravin *Chill Touch* knowledge | Player cast *Chill Touch* in combat. | Player was experimenting with D&D mechanics; character may canonically be an unwitting scholar with zero formal magical training prior to The Margin. | Check Session 4+ character dialogue regarding when Dravin first understood he was a necromancer. |
| `RETCON-S03-01` | `s3` (`b026`, `L0725`) | Nincy vs. Nancy STT Drift | Character explicitly introduces herself as "Nincy with an I". | Speech-to-text transcribed her name as "Nancy" due to Southern vowel merger; upstream aliases and character dossiers updated so TTS and manifests bind to `nincy`. | Completed in PR Record #003. |