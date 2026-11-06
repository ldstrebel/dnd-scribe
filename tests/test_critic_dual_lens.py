"""
Unit tests for Dual-Lens Tabletop Coach & Closed-Loop Fuel Inquest (Edition 16).

Validates the 3 Core Principles:
1. Principle 1: Mundane actions stay mundane (no purple prose homework for skill checks).
2. Principle 2: Respect tactical reality under pressure (no false inquiry gaps).
3. Principle 3: Catch emotional handoffs (Don't take NPCs for granted).
"""

import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sessions._scripts.critique_tabletop import TabletopCoach


class TestCriticDualLens(unittest.TestCase):
    def setUp(self):
        self.coach = TabletopCoach("s8")

    def test_mundane_actions_never_penalized(self):
        """Principle 1: Basic physical checks are valid and do not require purple prose."""
        sample_prose = (
            "Pierre climbed the fire escape with athletic precision. "
            "Alfie picked the padlock with her rapier tip. "
            "Eusacles opened the heavy steel door and ran down the alley."
        )
        actions = self.coach.audit_mundane_actions(sample_prose)
        self.assertGreaterEqual(len(actions), 3, "Expected at least 3 mundane physical actions detected")
        for a in actions:
            self.assertEqual(a["status"], "VALID_MUNDANE_ACTION")
            self.assertIn("Mundane physical actions do not require purple prose", a["reason"])

    def test_tactical_urgency_respected(self):
        """Principle 2: Operative urgency under ticking clocks is sound roleplay, not an inquiry gap."""
        sample_prose = (
            "Automated emergency klaxons sounded as hydraulic blast shutters began dropping. "
            "The locker was clean, requisitioned two hours ago. They raced upstairs immediately."
        )
        findings = self.coach.audit_tactical_urgency(sample_prose)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["status"], "TACTICAL_URGENCY_RESPECTED")

    def test_npc_emotional_handoff_detection_and_coaching(self):
        """Principle 3: Detects weighty NPC gifts and coaches unreciprocated meta deflection."""
        mock_turns = [
            {
                "line": 100,
                "speaker": "theodore",
                "text": "Take the ancestral boon, son. When the timeline tries to shear you away, remember that the land remembers who stood upon it."
            },
            {
                "line": 101,
                "speaker": "john hagey",
                "text": "Wait, was my armor toggled off this whole time?! My heavy plate and shield weren't on!"
            }
        ]
        handoffs = self.coach.audit_emotional_handoffs(mock_turns)
        self.assertEqual(len(handoffs), 1)
        h = handoffs[0]
        self.assertEqual(h["npc"], "Teddy (Theodore)")
        self.assertTrue(h["meta_deflection"])
        self.assertFalse(h["emotional_grounding"])
        self.assertIn("Don't take NPCs for granted", h["coaching_directive"])

    def test_npc_emotional_handoff_with_grounded_reaction(self):
        """Principle 3: When a player character reacts in-character, handoff is praised."""
        mock_turns = [
            {
                "line": 200,
                "speaker": "thanatos",
                "text": "The watch ticks with peaceful death. Carry it well, my son."
            },
            {
                "line": 201,
                "speaker": "john hagey",
                "text": "I will, father. Thank you. I won't let the timeline fall."
            }
        ]
        handoffs = self.coach.audit_emotional_handoffs(mock_turns)
        self.assertEqual(len(handoffs), 1)
        h = handoffs[0]
        self.assertFalse(h["meta_deflection"])
        self.assertTrue(h["emotional_grounding"])
        self.assertIn("reciprocated with grounded character reaction", h["coaching_directive"])

    def test_anti_cheerleader_scorecard_integrity(self):
        """Rejects sycophantic 'Hurt: None observed' cop-outs and enforces realistic scores."""
        report = self.coach.run_fuel_audit()
        self.assertIsNotNone(report["tomatometer"])
        self.assertIsNotNone(report["popcornmeter"])

        for p in report["participants"]:
            self.assertNotIn("none observed", p["hurt"].lower(),
                             f"{p['character']} must have actionable critique, not 'None observed'")
            self.assertTrue(len(p["directive"]) > 10, f"{p['character']} missing actionable directive")

    def test_session8_real_pipeline_audit(self):
        """Session 8 audit detects Teddy's ancestral boon handoff in clean story."""
        report = self.coach.run_fuel_audit()
        p_audit = report["principles_audit"]
        self.assertTrue(p_audit["principle_1_mundane_actions"]["passed"])
        self.assertTrue(p_audit["principle_2_tactical_urgency"]["passed"])

        # Check that Teddy handoff was detected
        handoffs = p_audit["principle_3_emotional_handoffs"]["handoffs"]
        teddy_handoff = [h for h in handoffs if "Teddy" in h.get("npc", "")]
        self.assertGreaterEqual(len(teddy_handoff), 1, "Expected Teddy ancestral boon handoff detected in S8")
        self.assertIn("Don't take the NPCs for granted", teddy_handoff[0]["coaching_directive"])


if __name__ == "__main__":
    unittest.main()
