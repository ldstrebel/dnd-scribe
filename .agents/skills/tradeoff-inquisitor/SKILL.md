---
name: tradeoff-inquisitor
description: Red-team adversarial inquisitor that interrogates documented editorial compromises, authorial liberties, and skipped lore to prevent ungrounded narrative drift.
---

# 🕵️ Adversarial Trade-Off Inquisitor

Use this skill to conduct periodic, red-team audits of D&D Scribe publishing compromises. Unlike the standard publishing pipeline (which verifies that permits exist and line arithmetic balances), the Inquisitor attacks the **justifications themselves**.

---

## 🏛️ Prime Directive: The Red Team Mindset

1. **Assume Every "Velocity" Cut is a Lazy Shortcut Until Proven Otherwise:**
   - When an authorial liberty claims a scene was condensed "to improve narrative velocity," interrogate whether it actually erased a player's independent tactical choice, a character-defining quirk, or an organic causal transition.
2. **Expose the True Price of Whitelisted Skips:**
   - When a skipped line is approved as "banter" or "table logistics," check whether it contained an unconfirmed player deduction or a subtle GM hint that matters in subsequent sessions.
3. **Guard Against Polite Hollywood Sanitization (`FP-01`, `FP-02`):**
   - Verify that physical conflict, non-consensual party actions (e.g., shoving, grabbing, binding), and chaotic independent impulses were not smoothed over into cooperative Hollywood heist teamwork.

---

## 🔬 The 4 Inquest Probes

Every audit report must evaluate the target session against these four lenses:

```
           Target Session Trade-Offs & Compromises
                              │
     ┌────────────────────────┼────────────────────────┐
     ▼                        ▼                        ▼
1. The Rationalization   2. Downstream Debt       3. The Sanitization
   Probe                    & Arc Collision          Probe
   "Did 'velocity' kill     "Did an S4 skip sever    "Did we smooth out
   authentic roleplay?"     an S5 consequence?"      friction into teamwork?"
```

1. **Probe 1: The Convenient Rationalization Test**
   - Extract each entry in `authorial_liberties`. Compare raw transcript turns against the cinematic cut (`blocks_authorial/`).
   - Flag any scene where cutting dialogue turns flattened the character voice or turned an eccentric reaction into generic action-hero behavior.
2. **Probe 2: The Downstream Debt & Arc Collision Test**
   - Cross-reference substantive skips (`legitimate_ooc_lore_skips`) and omitted decisions (`source-decisions.json`) against `campaign/CAMPAIGN_ARC_LEDGER.md` and subsequent sessions.
   - Flag any skipped clue that makes later knowledge appear out of nowhere.
3. **Probe 3: The Polite Consent & Agency Test**
   - Inspect scenes with physical interaction, panic, or moral disagreement.
   - Verify that characters react with visceral Swain MRUs (neuro-physiological shock, recoil, verbal resistance) rather than quiet acquiescence.
4. **Probe 4: The Popcorn vs. Tomato Divergence Test**
   - Review the dual Rotten Tomatoes score: Tomatometer (Literary Craft) vs. Popcornmeter (Table Energy).
   - Diagnose why literary purists or table purists balked at the cut.

---

## 🔄 The 3-Night Targeted Rotation Schedule

To keep audits focused, actionable, and reviewable in under 3 minutes (avoiding review fatigue):

| Night | Trigger Time | Focus Scope | Key Deliverable |
|---|---|---|---|
| **Sunday Night** | Mon 02:00 AM | **Agency & High-Stakes Friction** (Recent Session) | Attacks unilateral force, panic, and combat thresholds (e.g., S5 Scene 10). |
| **Tuesday Night** | Wed 02:00 AM | **Authorial Liberties & Compression** (Recent Session) | Attacks "velocity" justifications in transit/dialogue scenes (e.g., S5 Scenes 1, 4, 8). |
| **Friday Night** | Sat 02:00 AM | **Cross-Session Continuity & Downstream Debt** | Pairs Session $N$ with Session $N-1$ to audit lore retention and prop continuity. |

---

## 🚀 Execution & PR Creation

Run the automated inquisitor strike:
```powershell
# Targeted single-session audit
python sessions/_scripts/run_tradeoff_inquisitor.py --session s5

# Specific focus mode (agency, liberties, continuity)
python sessions/_scripts/run_tradeoff_inquisitor.py --session s5 --focus agency

# Push branch and generate GitHub PR link
python sessions/_scripts/run_tradeoff_inquisitor.py --session s5 --push
```
