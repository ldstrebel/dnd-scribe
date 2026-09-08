# 💬 Feedback & Editorial Forum UI Component Specification

This specification defines the data contract and layout guidelines for rendering the **Feedback & Forum** component at the bottom of chapters, the bottom of the Table of Contents scroll drawer, or on D&D Wiki campaign hub pages.

---

## 🏗️ Architectural Purpose

1. **Meta-Editorial Transparency:** Shares honest AI adversarial critique, active narrative trade-offs, and nearest story risks directly with readers, players, and GMs.
2. **Pinned Bot Review:** The very first post in the forum is automatically rendered as the **Initial Bot Review** (ruthless and helpful analysis).
3. **Community & Player Critique Stream:** Below the bot review, readers and table players can submit comments or anchor-specific feedback.
4. **Iterative Changelog Stream:** As PR reviews are merged and the pipeline re-runs, updated iteration notes are appended to the forum thread.

---

## 📦 JSON Schema Ingestion (`sX-manifest-v2.json`)

Downstream reader apps consume the `editorialForum` object from `sessions/data/index/sX-manifest-v2.json`:

```json
{
  "editorialForum": {
    "forumTitle": "Session 1 Editorial Meta-Review & Discussion Forum",
    "summary": "Forensic telemetry, active trade-offs, and historical PR change records.",
    "initialBotReview": {
      "author": "Adversarial Prose Critic (Bot)",
      "badge": "Autonomous Editorial Lead",
      "grade": "A-",
      "verdict": "VERIFIED PRODUCTION-READY (ACTIVE TRADE-OFFS MONITORED)",
      "technicalCompliance": {
        "earthLeaks": 0,
        "dialogueStutters": 0,
        "stagnantTalkingHeads": 0,
        "transcriptParity": "100%"
      },
      "ruthlessAnalysis": "Fast-paced dimensional transit and brisk ink-beast combat...",
      "tradeOffs": [
        {
          "dimension": "Narrative Velocity vs. Tangential Banter",
          "chosenStance": "Heavy Compression (~0.20-0.28 ratio)",
          "counterStance": "Expanded Slice-of-Life & Table Humor",
          "tradeOffCost": "Sacrifices casual OOC table banter in favor of cinematic plot momentum."
        }
      ],
      "nearestRisks": [
        {
          "title": "Emotional Velocity Friction",
          "risk": "High-speed combat transitions in Act I risk rushing party bonding.",
          "mitigation": "Ensure quiet sanctuary intermissions in upcoming chapters."
        }
      ]
    },
    "changelog": [
      {
        "iteration": "PR #001 (uneraseable-s1-strebs-482131)",
        "timestamp": "2026-09-08T03:34:42.131Z",
        "reviewer": "Strebs",
        "summary": "Restored Pierre Paris-Versailles reference; logged Dravin Chill Touch table fidelity to Retcon Watchlist; resolved Fates NPC ordinal color styling."
      }
    ],
    "retconWatchlist": [
      {
        "id": "RETCON-S01-01",
        "anchor": "b060 (L1150)",
        "subject": "Dravin Chill Touch magical awakening",
        "note": "Player cast Chill Touch at table; character framed as unwitting academic discovering necrotic magic."
      }
    ]
  }
}
```

---

## 🎨 Recommended UI Layout & Component Slots

### 1. Pinned Bot Editorial Card (Post #1)
- **Header:** `[🤖 Adversarial Prose Critic (Bot)]` `[Grade: A-]`
- **Ruthless Analysis:** Callout box summarizing narrative pacing, dialogue-to-action ratio, and character spotlight skew.
- **Collapsible Drawer: ⚖️ Active Editorial Trade-Offs:** Accordion table displaying what was gained and what was sacrificed.
- **Collapsible Drawer: ⚠️ Top 3 Nearest Risks:** Highlights watchpoints for the GM and readers.

### 2. PR Iteration & Changelog Stream (Post #2+)
- Displays chronologically sorted cards for every merged critique PR:
  - *Reviewer handle & timestamp*
  - *Summary of prose, tagging, or continuity corrections applied*

### 3. Community Feedback & Review Form
- Interactive comment box allowing readers to:
  - Highlight specific block IDs (`uneraseable_s01_b060`)
  - Tag feedback category (`rewrite`, `continuity`, `audio_cue`, `character_voice`)
  - Submit exportable critique payloads directly as GitHub PRs.
