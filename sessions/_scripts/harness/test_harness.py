"""Automated Unit Tests for the Vumbua Editorial Harness."""

import sys
import unittest
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sessions._scripts.harness.leak_detector import LeakDetector
from sessions._scripts.harness.echo_detector import EchoDetector
from sessions._scripts.harness.style_analyzer import StyleAnalyzer
from sessions._scripts.harness.lore_guardian import LoreGuardian
from sessions._scripts.harness.context_bridge import ContextBridge
from sessions._scripts.verify_alternate_scene import verify_alternate_scene





class TestEditorialHarness(unittest.TestCase):
    def setUp(self):
        self.leak_detector = LeakDetector()
        self.echo_detector = EchoDetector(proximity_window_words=50)
        self.style_analyzer = StyleAnalyzer()
        self.lore_guardian = LoreGuardian()

    def test_leak_detector_catches_player_name(self):
        bad_text = 'Ignatius walked forward. Luke told everyone to roll for initiative.'
        res = self.leak_detector.scan_text(bad_text)
        self.assertFalse(res["passed"])
        types = [v["type"] for v in res["violations"]]
        self.assertIn("PLAYER_NAME_LEAK", types)

    def test_leak_detector_catches_mechanics(self):
        bad_text = 'Iggy checked his character sheet and spent an armor slot.'
        res = self.leak_detector.scan_text(bad_text)
        self.assertFalse(res["passed"])
        types = [v["type"] for v in res["violations"]]
        self.assertIn("MECHANICS_LEAK", types)

    def test_leak_detector_catches_embedded_italic_dialogue(self):
        bad_text = '*I really think we should go back,* Pip said with a shudder.'
        res = self.leak_detector.scan_text(bad_text)
        self.assertFalse(res["passed"])
        types = [v["type"] for v in res["violations"]]
        self.assertIn("EMBEDDED_ITALIC_DIALOGUE", types)

    def test_lore_guardian_catches_phonetic_drift(self):
        bad_text = 'Ignatius turned toward Vanball and asked for advice.'
        res = self.lore_guardian.scan_text(bad_text)
        self.assertFalse(res["passed"])
        err_types = [e["type"] for e in res["errors"]]
        self.assertIn("PHONETIC_DRIFT", err_types)

    def test_lore_guardian_catches_tense_slip(self):
        bad_text = 'Britt turns toward the forest and watches the leaves fall.'
        res = self.lore_guardian.scan_text(bad_text)
        warn_types = [w["type"] for w in res["warnings"]]
        self.assertIn("TENSE_SLIPPAGE", warn_types)

    def test_echo_detector_catches_proximity_echo(self):
        repetitive_text = (
            "Through the shattered archway, Ignatius stepped with caution. "
            "The ancient stones were covered in dark green moss. "
            "Through the shattered archway, he could see the distant harbor."
        )
        res = self.echo_detector.scan_text(repetitive_text)
        self.assertGreater(res["echoes_found"], 0)

    def test_style_analyzer_metrics(self):
        sample_prose = (
            'The copper boiler hummed beneath the iron deck, vibrating through the soles of Lomi’s boots. '
            '"Are we ready to engage the main conduits?" Ignatius asked, wiping soot from his jaw. '
            '"Not quite yet," Lomi replied, adjusting his woolen cap. The smell of ozone and sulfur hung thick in the air.'
        )
        res = self.style_analyzer.generate_style_report(sample_prose)
        self.assertGreater(res["pacing"]["sentence_count"], 0)
        self.assertGreater(res["dialogue_ratio"]["dialogue_pct"], 0)
        self.assertGreater(res["sensory_palette"]["covered_registers"], 0)

    def test_context_bridge_format(self):
        bridge = ContextBridge()
        state = {
            "location_and_environment": "Apex Arena, basalt canyon, heavy morning rain",
            "characters_present": [
                {"name": "Ignatius", "status": "exhausted, crown glowing"},
                {"name": "Lomi", "status": "riding Ignatius's shoulders"}
            ],
            "key_items_or_props": ["Spirit Tortoise vial", "copper slates"],
            "immediate_preceding_action": "Ignatius crossed the rapids while Lomi held on tightly.",
            "emotional_tone_or_tension": "Elated relief after surviving the trials"
        }
        formatted = bridge.format_bridge_prompt(state)
        self.assertIn("Apex Arena", formatted)
        self.assertIn("Ignatius", formatted)
        self.assertIn("Spirit Tortoise vial", formatted)

    def test_alternate_scene_valid_passes(self):
        sample_arch = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n'
            'Pierre balanced cucumber on his eyelids. <!-- L0883 -->\n'
            '"I make the best pancakes," Mike said. <!-- L0903 -->\n'
            '"Zeus, not Seuss," Dravin corrected. <!-- L0968 -->'
        )
        sample_valid = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n'
            'Pierre protested from behind cucumber slices. "It can wait!" <!-- L0881-L0891 -->\n'
            'Mike brought hot pancakes to the porch with coffee. "Saturday pancakes!" <!-- L0900-L0942 -->\n'
            'Dravin adjusted his spectacles. "Zeus, not Seuss." <!-- L0954-L0973 -->'
        )
        report = verify_alternate_scene(sample_valid, sample_arch)
        self.assertTrue(report["passed"])
        self.assertTrue(report["gate1_entity_coverage"]["passed"])
        self.assertTrue(report["gate2_leaks_and_props"]["passed"])
        self.assertTrue(report["gate3_span_provenance"]["passed"])

    def test_alternate_scene_missing_entity_or_relic_fails(self):
        sample_arch = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n'
            'Pierre balanced cucumber on his eyelids. <!-- L0883 -->\n'
            '"I make the best pancakes," Mike said. <!-- L0903 -->\n'
            '"Zeus, not Seuss," Dravin corrected. <!-- L0968 -->'
        )
        # Dropped Mike and pancakes completely
        sample_missing = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n'
            'Pierre walked into the room. <!-- L0881-L0891 -->\n'
            'Dravin adjusted his spectacles. "Zeus, not Seuss." <!-- L0954-L0973 -->'
        )
        report = verify_alternate_scene(sample_missing, sample_arch)
        self.assertFalse(report["passed"])
        self.assertIn("Mike", report["gate1_entity_coverage"]["missing_entities"])
        self.assertIn("cucumber", report["gate1_entity_coverage"]["missing_relics"])

    def test_alternate_scene_leak_or_foreign_prop_fails(self):
        sample_arch = '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\nPierre said hello. <!-- L0883 -->'
        sample_leaked = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n'
            'Luke Foreman told everyone that Pierre got into a green Ford truck. <!-- L0881-L0891 -->'
        )
        report = verify_alternate_scene(sample_leaked, sample_arch)
        self.assertFalse(report["passed"])
        self.assertFalse(report["gate2_leaks_and_props"]["passed"])
        err_types = [e["type"] for e in report["gate2_leaks_and_props"]["errors"]]
        self.assertIn("PLAYER_NAME_LEAK", err_types)
        self.assertIn("FOREIGN_PROP_LEAK", err_types)

    def test_alternate_scene_inverted_spans_fails(self):
        sample_arch = '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\nPierre nodded. <!-- L0883 -->'
        sample_bad_spans = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n'
            'Pierre stepped forward. <!-- L0950-L0880 -->'
        )
        report = verify_alternate_scene(sample_bad_spans, sample_arch)
        self.assertFalse(report["passed"])
        self.assertFalse(report["gate3_span_provenance"]["passed"])
        err_types = [e["type"] for e in report["gate3_span_provenance"]["errors"]]
        self.assertIn("INVALID_SPAN_BOUNDS", err_types)


if __name__ == "__main__":
    unittest.main()

