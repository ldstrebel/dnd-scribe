"""Automated Unit Tests for the Vumbua Editorial Harness."""

import json
import os
import sys
import tempfile
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
from sessions._scripts.audit_semantic_grounding import (
    audit_skip_ledger,
    audit_transcript_boundary,
    check_boundary_prose,
    extract_content_words,
    load_lore_lexicon,
    load_skip_exemptions,
)





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
        guardian = LoreGuardian(phonetic_map={"vanball": "Vambal"})
        bad_text = 'Ignatius turned toward Vanball and asked for advice.'
        res = guardian.scan_text(bad_text)
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
        dummy_contract = {"rules": [], "authorial_liberties": [{"scene": "scene-05", "liberty": "pancake banter compression"}]}
        report = verify_alternate_scene(sample_valid, sample_arch, intent_contract=dummy_contract)
        self.assertTrue(report["passed"])
        self.assertTrue(report["gate1_entity_coverage"]["passed"])
        self.assertTrue(report["gate2_leaks_and_props"]["passed"])
        self.assertTrue(report["gate3_span_provenance"]["passed"])
        self.assertTrue(report["gate4_adaptation_divergence"]["passed"])

    def test_alternate_scene_zero_divergence_fails(self):
        sample_arch = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n'
            'Pierre balanced cucumber on his eyelids. <!-- L0883 -->\n'
            '"I make the best pancakes," Mike said. <!-- L0903 -->\n'
            '"Zeus, not Seuss," Dravin corrected. <!-- L0968 -->'
        )
        report = verify_alternate_scene(sample_arch, sample_arch)
        self.assertFalse(report["passed"])
        self.assertFalse(report["gate4_adaptation_divergence"]["passed"])
        err_types = [e["type"] for e in report["gate4_adaptation_divergence"]["errors"]]
        self.assertIn("ZERO_CINEMATIC_DIVERGENCE", err_types)

    def test_alternate_scene_unitemized_liberty_fails(self):
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
        empty_contract = {"rules": [], "authorial_liberties": []}
        report = verify_alternate_scene(sample_valid, sample_arch, intent_contract=empty_contract)
        self.assertFalse(report["passed"])
        self.assertFalse(report["gate4_adaptation_divergence"]["passed"])
        err_types = [e["type"] for e in report["gate4_adaptation_divergence"]["errors"]]
        self.assertIn("UNITEMIZED_AUTHORIAL_LIBERTY", err_types)

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

    def test_alternate_scene_unanchored_dialogue_quote_fails(self):
        sample_arch = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n\n'
            'Pierre balanced cucumber on his eyelids. <!-- L0883 -->\n\n'
            '"I make the best pancakes," Mike said. <!-- L0903 -->\n\n'
            '"Zeus, not Seuss," Dravin corrected. <!-- L0968 -->'
        )
        sample_unanchored_quote = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n\n'
            'Pierre protested from behind cucumber slices. "It can wait!" <!-- L0881-L0891 -->\n\n'
            '"Look, pal, I do not run the art department!" Mike snapped back, waving his arms.\n\n'
            'Dravin adjusted his spectacles. "Zeus, not Seuss." <!-- L0954-L0973 -->'
        )
        dummy_contract = {"rules": [], "authorial_liberties": [{"scene": "scene-05", "liberty": "pancake banter compression"}]}
        report = verify_alternate_scene(sample_unanchored_quote, sample_arch, intent_contract=dummy_contract)
        self.assertFalse(report["passed"])
        self.assertFalse(report["gate3_span_provenance"]["passed"])
        err_types = [e["type"] for e in report["gate3_span_provenance"]["errors"]]
        self.assertIn("UNANCHORED_DIALOGUE_QUOTE", err_types)

    def test_alternate_scene_inverted_dialogue_attribution_fails(self):
        sample_arch = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n\n'
            'Pierre balanced cucumber on his eyelids. <!-- L0883 -->\n\n'
            '"I make the best pancakes," Mike said. <!-- L0903 -->\n\n'
            '"Zeus, not Seuss," Dravin corrected. <!-- L0968 -->'
        )
        sample_inverted = (
            '<!-- RAW_RANGE: [881, 1010] | SCENE_ID: 5 -->\n\n'
            'Pierre protested from behind cucumber slices. "It can wait!" <!-- L0881-L0891:pierre -->\n\n'
            '"Look, pal, I do not run the art department!" Mike snapped back, waving his arms. <!-- L0900-L0942:pierre -->\n\n'
            'Dravin adjusted his spectacles. "Zeus, not Seuss." <!-- L0954-L0973:dravin -->'
        )
        dummy_contract = {"rules": [], "authorial_liberties": [{"scene": "scene-05", "liberty": "pancake banter compression"}]}
        report = verify_alternate_scene(sample_inverted, sample_arch, intent_contract=dummy_contract)
        self.assertFalse(report["passed"])
        self.assertFalse(report["gate3_span_provenance"]["passed"])
        err_types = [e["type"] for e in report["gate3_span_provenance"]["errors"]]
        self.assertIn("INVERTED_DIALOGUE_ATTRIBUTION", err_types)


class TestTranscriptBoundary(unittest.TestCase):
    """FP-17 enforcement: Track A must cut at the transcript boundary."""

    PCS = ["Pierre", "Dravin", "Eusacles", "Alfie"]
    CLEAN_BLOCK = (
        '<!-- RAW_RANGE: [1206, 1257] | SCENE_ID: 10 -->\n\n'
        '<!-- LEDGER: rendered=[1242, 1256] skipped=[1257(ooc)] -->\n\n'
        'Three cloaked figures strode into the auditorium, hooves cracking the tile. <!-- L1242 -->\n\n'
        '"Sorry, Alfie," Dravin whispered, scooping the doll and the binder into his arms. <!-- L1256 -->\n\n'
        'The trap had sprung.\n'
    )
    OVERREACH_BLOCK = CLEAN_BLOCK + (
        '\nPierre drew his bronze-tipped javelin from beneath his overcoat. Eusacles stepped in front of '
        'the stage stairs, rolling his heavy iron morningstar in one leather-gloved fist.\n'
    )

    def test_clean_cliffhanger_passes(self):
        report = check_boundary_prose(self.CLEAN_BLOCK, self.PCS, cutoff_line=1257)
        self.assertEqual(report["max_anchor"], 1256)
        self.assertEqual(report["beyond_cutoff"], [])
        self.assertEqual(report["tail_pc_actions"], [])
        self.assertFalse(report["flagged"])

    def test_post_cutoff_pc_action_is_flagged(self):
        report = check_boundary_prose(self.OVERREACH_BLOCK, self.PCS, cutoff_line=1257)
        self.assertTrue(report["flagged"])
        self.assertEqual(report["tail_pc_actions"], ["Eusacles", "Pierre"])

    def test_long_unanchored_tail_is_flagged_without_pc_names(self):
        tail = " ".join(["the klaxon screamed on"] * 15)
        report = check_boundary_prose(self.CLEAN_BLOCK + "\n" + tail + "\n", self.PCS, cutoff_line=1257)
        self.assertTrue(report["flagged"])
        self.assertEqual(report["tail_pc_actions"], [])

    def test_anchor_beyond_declared_cutoff_is_reported(self):
        block = self.CLEAN_BLOCK.replace("<!-- L1256 -->", "<!-- L1260 -->")
        report = check_boundary_prose(block, self.PCS, cutoff_line=1257)
        self.assertEqual(report["beyond_cutoff"], [1260])

    def _write_session(self, root, track_a, track_b=None, liberty=False):
        os.makedirs(os.path.join(root, "sessions", "config"))
        os.makedirs(os.path.join(root, "sessions", "data", "clean", "blocks"))
        os.makedirs(os.path.join(root, "sessions", "data", "clean", "blocks_authorial"))
        with open(os.path.join(root, "sessions", "config", "s9-session-config.json"), "w", encoding="utf-8") as f:
            json.dump({
                "players": {"A": "Pierre", "B": "Prof. Edward Dravin", "C": "Alfie", "D": "Eusacles"},
                "session_cutoff": {"line": 1257},
            }, f)
        liberties = [{"scene": "scene-10", "boundary": "post_cutoff", "liberty": "x", "impact": "y"}] if liberty else []
        with open(os.path.join(root, "sessions", "config", "s9-intent-contract.json"), "w", encoding="utf-8") as f:
            json.dump({"rules": [], "authorial_liberties": liberties}, f)
        with open(os.path.join(root, "sessions", "data", "clean", "blocks", "s9-scene-10.md"), "w", encoding="utf-8") as f:
            f.write(track_a)
        if track_b is not None:
            with open(os.path.join(root, "sessions", "data", "clean", "blocks_authorial", "s9-scene-10-alt.md"), "w", encoding="utf-8") as f:
                f.write(track_b)

    def test_session_audit_flags_track_a_and_unlicensed_track_b(self):
        with tempfile.TemporaryDirectory() as root:
            self._write_session(root, self.OVERREACH_BLOCK, self.OVERREACH_BLOCK, liberty=False)
            errors, _, _ = audit_transcript_boundary("s9", root)
        codes = [e.split("]")[0] for e in errors]
        self.assertIn("Scene 10: [POST_CUTOFF_STAGING", codes)
        self.assertIn("Scene 10: [UNLICENSED_POST_CUTOFF_STAGING", codes)

    def test_session_audit_passes_clean_track_a_and_licensed_track_b(self):
        with tempfile.TemporaryDirectory() as root:
            self._write_session(root, self.CLEAN_BLOCK, self.OVERREACH_BLOCK, liberty=True)
            errors, _, info = audit_transcript_boundary("s9", root)
        self.assertEqual(errors, [])
        self.assertTrue(any("licensed by itemized liberty" in line for line in info))
        self.assertTrue(any("L1257 (s9-session-config.json)" in line for line in info))


class TestSkipLedgerGate(unittest.TestCase):
    """DEC-024: substantive spoken turns cannot hide behind a naked (ooc) skip."""

    RAW = [
        "**Luke Foreman:** ok one sec",
        "**Sophie Foreman Noone:** So, a fragment isn't necessarily an item. Could just be a moment in time. Or is it always an item?",
        "**John Hagey:** the ancient lighthouse keeper poured molten bronze across the harbor chains before dawn broke over the ruined city",
        "**Luke Foreman:** roll initiative and that is where we will end our session today",
    ]
    LORE_RE = load_lore_lexicon("s9", "/nonexistent", {"session_lore_terms": ["fragment"], "npcs": [{"name": "Spectral Child"}]})

    def _audit(self, skipped, prose="", exemptions=None):
        words = set(extract_content_words(prose))
        return audit_skip_ledger(9, skipped, self.RAW, words, self.LORE_RE, exemptions or {})

    def _codes(self, errors):
        return [e.split("]")[0].split("[")[1] for e in errors]

    def test_substantive_naked_ooc_is_hard_error_for_any_speaker(self):
        errors, _ = self._audit([("3", "ooc")])
        self.assertEqual(self._codes(errors), ["UNJUSTIFIED_OOC_DROP"])

    def test_short_or_meta_ooc_passes(self):
        errors, _ = self._audit([("1", "ooc"), ("4", "ooc")])
        self.assertEqual(errors, [])

    def test_player_spoken_lore_term_is_detected(self):
        errors, _ = self._audit([("2", "ooc")])
        self.assertIn("TIER_B_LORE_DROP", self._codes(errors))
        self.assertIn("fragment", errors[0])

    def test_npc_name_matches_whole_phrase_only(self):
        self.assertIsNotNone(self.LORE_RE.search("the spectral child appears"))
        self.assertIsNone(self.LORE_RE.search("a child appears"))

    def test_structured_exemption_with_reason_passes(self):
        exemptions = load_skip_exemptions({"legitimate_ooc_lore_skips": [{"line": 3, "reason": "GM recap of prior session"}]})
        self.assertEqual(exemptions, {3: "GM recap of prior session"})
        errors, _ = self._audit([("3", "ooc")], exemptions=exemptions)
        self.assertEqual(errors, [])

    def test_legacy_integer_exemption_still_parses(self):
        exemptions = load_skip_exemptions({"legitimate_ooc_lore_skips": [2, {"line": 3, "reason": "x"}]})
        self.assertEqual(set(exemptions), {2, 3})
        errors, _ = self._audit([("2", "ooc")], exemptions=exemptions)
        self.assertEqual(errors, [])

    def test_hollow_compressed_fails(self):
        errors, _ = self._audit([("3", "compressed")], prose="Pierre adjusted his beret and ordered a baguette.")
        self.assertEqual(self._codes(errors), ["HOLLOW_COMPRESSED_SKIP"])

    def test_covered_compressed_passes(self):
        prose = "Before dawn the lighthouse keeper poured molten bronze over the harbor chains of the ruined city."
        errors, _ = self._audit([("3", "compressed")], prose=prose)
        self.assertEqual(errors, [])


from sessions._scripts.audit_arc_ledger import audit_arc_ledger
from sessions._scripts.audit_reader_context import audit_reader_context, load_declared_introductions


class TestWritersRoomGates(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(os.path.join(REPO_ROOT, "campaign", "CAMPAIGN_ARC_LEDGER.md")), "No campaign arc ledger on campaign-agnostic engine branch")
    def test_arc_ledger_audit_passes_real_campaign(self):
        passed, errors, warnings = audit_arc_ledger(str(REPO_ROOT))
        self.assertTrue(passed, f"Arc ledger audit failed with errors: {errors}")
        self.assertEqual(len(errors), 0)

    @unittest.skipIf(not os.path.exists(os.path.join(REPO_ROOT, "sessions", "data", "clean", "blocks")), "No clean blocks on campaign-agnostic engine branch")
    def test_reader_context_audit_passes_s5(self):
        passed, errors, warnings = audit_reader_context("s5", str(REPO_ROOT))
        self.assertTrue(passed, f"Reader context audit failed with errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_synthetic_arc_ledger_audit(self):
        with tempfile.TemporaryDirectory() as td:
            camp_dir = os.path.join(td, "campaign")
            raw_dir = os.path.join(td, "sessions", "data", "index")
            os.makedirs(camp_dir)
            os.makedirs(raw_dir)
            with open(os.path.join(raw_dir, "s1-raw-indexed.md"), "w", encoding="utf-8") as f:
                f.write("L0100: Player: We found the artifact.\n")
            with open(os.path.join(camp_dir, "CAMPAIGN_ARC_LEDGER.md"), "w", encoding="utf-8") as f:
                f.write("# Codex\n## 1. Cosmology\n- The relic was uncovered [ESTABLISHED: S1 L0100].\n")
            passed, errors, _ = audit_arc_ledger(td)
            self.assertTrue(passed)
            self.assertEqual(len(errors), 0)

    def test_synthetic_arc_ledger_milestone_table_bounds(self):
        with tempfile.TemporaryDirectory() as td:
            camp_dir = os.path.join(td, "campaign")
            idx_dir = os.path.join(td, "sessions", "data", "index")
            os.makedirs(camp_dir)
            os.makedirs(idx_dir)
            manifest_s1 = {
                "session_id": "s1",
                "total_raw_lines": 600,
                "scene_blocks": [
                    {"scene_id": 101, "ooc": True, "line_range": [1, 99]},
                    {"scene_id": 1, "ooc": False, "line_range": [100, 500]}
                ]
            }
            with open(os.path.join(idx_dir, "s1-manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest_s1, f)

            valid_ledger = (
                "# Codex\n## 4. Session Milestone Registry\n"
                "| Session | Setting | Relic | Milestone | Factions |\n"
                "| :--- | :--- | :--- | :--- | :--- |\n"
                "| **S1** | Bus | None | Event happens [ESTABLISHED: S1 L0200]. | Fates [ESTABLISHED: S1 L0300] |\n"
            )
            with open(os.path.join(camp_dir, "CAMPAIGN_ARC_LEDGER.md"), "w", encoding="utf-8") as f:
                f.write(valid_ledger)

            passed, errors, _ = audit_arc_ledger(td)
            self.assertTrue(passed, f"Valid milestone failed: {errors}")

            # Phantom line (> total_raw_lines 600)
            phantom_ledger = valid_ledger.replace("L0200", "L0800")
            with open(os.path.join(camp_dir, "CAMPAIGN_ARC_LEDGER.md"), "w", encoding="utf-8") as f:
                f.write(phantom_ledger)
            passed, errors, _ = audit_arc_ledger(td)
            self.assertFalse(passed)
            self.assertTrue(any("MILESTONE_CITES_PHANTOM_LINE" in e for e in errors))

            # Out of in-world bounds (OOC line 50, when in-world is 100-500)
            oob_ledger = valid_ledger.replace("L0200", "L0050")
            with open(os.path.join(camp_dir, "CAMPAIGN_ARC_LEDGER.md"), "w", encoding="utf-8") as f:
                f.write(oob_ledger)
            passed, errors, _ = audit_arc_ledger(td)
            self.assertFalse(passed)
            self.assertTrue(any("MILESTONE_OUT_OF_BOUNDS" in e for e in errors))

    def test_synthetic_reader_context_audit(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_dir = os.path.join(td, "sessions", "config")
            blocks_dir = os.path.join(td, "sessions", "data", "clean", "blocks")
            os.makedirs(cfg_dir)
            os.makedirs(blocks_dir)
            with open(os.path.join(cfg_dir, "s1-session-config.json"), "w", encoding="utf-8") as f:
                json.dump({"session_lore_terms": [{"term": "gadget", "introduced_scene": 1}]}, f)
            with open(os.path.join(blocks_dir, "s1-scene-01.md"), "w", encoding="utf-8") as f:
                f.write("He picked up the gadget from the desk. <!-- L0010 -->\n")
            passed, errors, _ = audit_reader_context("s1", td)
            self.assertTrue(passed)
            self.assertEqual(len(errors), 0)

    def test_declared_introductions_parser(self):
        cfg = {
            "session_lore_terms": [
                {"term": "fragment", "introduced_scene": 1},
                {"term": "briefcase", "introduced_scene": 9},
                "legacy_string_term"
            ],
            "npcs": [
                {"name": "Dr. Aris Thorne", "introduced_scene": 2},
                "Legacy NPC"
            ]
        }
        declared = load_declared_introductions(cfg)
        self.assertEqual(declared["fragment"], 1)
        self.assertEqual(declared["briefcase"], 9)
        self.assertEqual(declared["legacy_string_term"], 1)
        self.assertEqual(declared["dr. aris thorne"], 2)
        self.assertEqual(declared["legacy npc"], 1)


if __name__ == "__main__":
    unittest.main()

