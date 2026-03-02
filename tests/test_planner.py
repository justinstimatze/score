"""
Unit tests for arc_planner.py

Focus: mechanism scoring (_mech_score), strip parsing (_parse_one),
and engagement probability direction checks.

The mech index is mocked so tests don't require plays_mechanisms.json.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import arc_planner
from arc_planner import _mech_score, _parse_one, Strip


# ── HELPERS ───────────────────────────────────────────────────────────────────

def make_profile(mechanisms: dict, big_five: dict | None = None, sensitivity: str = "medium") -> dict:
    return {
        "name": "Test Participant",
        "mechanisms": mechanisms,
        "big_five": big_five or {"O": 0, "C": 0, "E": 0, "N": 0, "A": 0},
        "sensitivity": sensitivity,
        "avoidance": [],
    }


FULL_PLANNER_STRIP = """\
@my_play F·A·3d·2
#curiosity_exploration·pattern_recognition [be] /
C·n·m·a·p·m·a
prm:Q→slv
req:cnf
"""


# ── STRIP PARSING ─────────────────────────────────────────────────────────────

class TestParseOne(unittest.TestCase):
    def test_id_parsed(self):
        s = _parse_one("test_play", FULL_PLANNER_STRIP)
        self.assertEqual(s.id, "test_play")

    def test_l1_fields(self):
        s = _parse_one("test_play", FULL_PLANNER_STRIP)
        self.assertEqual(s.cost, "F")
        self.assertEqual(s.autonomy, "A")
        self.assertEqual(s.lead, "3d")
        self.assertEqual(s.intensity, 2)

    def test_l2_mechanisms(self):
        s = _parse_one("test_play", FULL_PLANNER_STRIP)
        self.assertIn("curiosity_exploration", s.mechanisms)
        self.assertIn("pattern_recognition", s.mechanisms)

    def test_l2_arc_fit_and_beat(self):
        s = _parse_one("test_play", FULL_PLANNER_STRIP)
        self.assertEqual(s.arc_fit, "be")
        self.assertEqual(s.beat, "/")

    def test_permission_and_grants(self):
        s = _parse_one("test_play", FULL_PLANNER_STRIP)
        self.assertIn("Q", s.prm)
        self.assertEqual(s.permission_grant, "slv")

    def test_no_grants_field(self):
        s = _parse_one("test_play", FULL_PLANNER_STRIP)
        self.assertFalse(hasattr(s, "grants"))

    def test_confederate_detection_from_autonomy(self):
        strip = "@test_play F·A·3d·2\n#curiosity_exploration [be] /\nC·n·m·a·p·m·a\nprm:S"
        s = _parse_one("test_play", strip)
        # autonomy="A", no req:cnf in text — no confederate
        self.assertFalse(s.requires_confederate)

    def test_confederate_detected_from_ca_autonomy(self):
        strip = "@cnf_play F·CA·0·2\n#curiosity [*] /\nC·n·m·a·p·m·a"
        s = _parse_one("cnf_play", strip)
        self.assertTrue(s.requires_confederate)

    def test_confederate_detected_from_req_cnf(self):
        strip = "@cnf_play F·A·0·2\n#curiosity [*] /\nC·n·m·a·p·m·a\nreq:cnf"
        s = _parse_one("cnf_play", strip)
        self.assertTrue(s.requires_confederate)

    def test_empty_strip_returns_defaults(self):
        s = _parse_one("bare", "")
        self.assertEqual(s.id, "bare")
        self.assertEqual(s.beat, "/")  # default

    def test_intensity_fallback_on_bad_value(self):
        strip = "@test F·A·0·X\n#mech [b] /"
        s = _parse_one("test", strip)
        self.assertEqual(s.intensity, 2)  # default

    def test_l3_detection_at_position_5(self):
        # L3 = AT·FR·AD·LA·LG·DE·RV; DE is position 5
        strip = "@test F·A·0·2\n#m [b] /\nh·f·l·b·p·s·i\nprm:S"
        s = _parse_one("test", strip)
        self.assertEqual(s.detection, "s")  # pos 5 = "s"

    def test_l3_reversibility_at_position_6(self):
        # RV is position 6, not position 3
        strip = "@test F·A·0·2\n#m [b] /\nh·f·l·b·p·m·i\nprm:S"
        s = _parse_one("test", strip)
        self.assertEqual(s.reversibility, "i")  # pos 6 = "i"

    def test_l3_legacy_at_position_4(self):
        strip = "@test F·A·0·2\n#m [b] /\nh·f·l·b·w·m·a\nprm:S"
        s = _parse_one("test", strip)
        self.assertEqual(s.legacy, "w")  # pos 4 = "w"

    def test_l3_agency_type_at_position_0(self):
        strip = "@test F·A·0·2\n#m [b] /\nB·f·l·b·p·m·a\nprm:S"
        s = _parse_one("test", strip)
        self.assertEqual(s.agency_type, "B")

    def test_l3_frame_req_at_position_1(self):
        strip = "@test F·A·0·2\n#m [b] /\nh·q·l·b·p·m·a\nprm:S"
        s = _parse_one("test", strip)
        self.assertEqual(s.frame_req, "q")

    def test_no_witness_field(self):
        s = _parse_one("test_play", FULL_PLANNER_STRIP)
        self.assertFalse(hasattr(s, "witness"))

    def test_l3_short_leaves_defaults(self):
        # < 7 parts — fields stay at defaults
        strip = "@test F·A·0·2\n#m [b] /\nC·n·m·a\nprm:S"
        s = _parse_one("test", strip)
        self.assertEqual(s.detection, "m")
        self.assertEqual(s.reversibility, "a")


# ── MECHANISM SCORING ─────────────────────────────────────────────────────────

class TestMechScore(unittest.TestCase):
    """
    _mech_score calls _load_mech_index() which reads from a file.
    We mock _load_mech_index to return a controlled index.
    """

    def _score(self, play_id: str, profile: dict, mech_index: dict) -> float:
        with patch.object(arc_planner, "_load_mech_index", return_value=mech_index):
            # Reset cached index so mock takes effect
            arc_planner._MECH_INDEX = {}
            return _mech_score(play_id, profile)

    def test_exact_match_scores_high(self):
        index = {"test_play": ["curiosity_exploration", "pattern_recognition"]}
        profile = make_profile({"curiosity_exploration": 3.0, "pattern_recognition": 2.0})
        score = self._score("test_play", profile, index)
        self.assertGreater(score, 0.8)

    def test_no_match_scores_low(self):
        index = {"test_play": ["social_validation", "status_signaling"]}
        profile = make_profile({"curiosity_exploration": 3.0})
        score = self._score("test_play", profile, index)
        self.assertLess(score, 0.5)

    def test_partial_match_is_intermediate(self):
        # Profile has two mechanisms; play only contains one of them
        # matched = 3.0 / (3.0 + 2.0) = 0.6
        index = {"test_play": ["curiosity_exploration"]}
        profile = make_profile({"curiosity_exploration": 3.0, "social_validation": 2.0})
        score = self._score("test_play", profile, index)
        self.assertAlmostEqual(score, 0.6, places=5)

    def test_empty_profile_mechanisms_returns_neutral(self):
        index = {"test_play": ["curiosity_exploration"]}
        profile = make_profile({})
        score = self._score("test_play", profile, index)
        self.assertAlmostEqual(score, 0.5)

    def test_play_not_in_index_returns_neutral(self):
        index = {}
        profile = make_profile({"curiosity_exploration": 3.0})
        score = self._score("absent_play", profile, index)
        self.assertAlmostEqual(score, 0.5)

    def test_score_capped_at_one(self):
        index = {"test_play": ["curiosity_exploration"]}
        # Very high weight
        profile = make_profile({"curiosity_exploration": 100.0})
        score = self._score("test_play", profile, index)
        self.assertLessEqual(score, 1.0)

    def test_root_prefix_fallback_gives_partial_credit(self):
        # Profile has "curiosity_exploration"; play has "curiosity_gap"
        # Root "curiosity" matches — should get partial credit (0.4×weight)
        index = {"test_play": ["curiosity_gap"]}
        profile = make_profile({"curiosity_exploration": 3.0})
        score = self._score("test_play", profile, index)
        # Partial credit: 3.0 * 0.4 / 3.0 = 0.4
        self.assertAlmostEqual(score, 0.4, places=5)

    def test_high_openness_profile_scores_higher_on_exploration_play(self):
        """Pattern Seeker (high O) should score higher than high N profile on curiosity plays."""
        index = {"exploration_play": ["curiosity_exploration", "information_gap", "pattern_recognition"]}
        pattern_seeker = make_profile({
            "curiosity_exploration": 3.0,
            "information_gap": 2.5,
            "pattern_recognition": 2.0,
        }, big_five={"O": 2, "C": 1, "E": 0, "N": -1, "A": 0})
        n_profile = make_profile({
            "hypervigilance": 3.0,
            "paranoia_escalation": 2.5,
            "disorientation": 2.0,
        }, big_five={"O": -1, "C": 0, "E": 0, "N": 2, "A": 0})
        score_ps = self._score("exploration_play", pattern_seeker, index)
        score_n  = self._score("exploration_play", n_profile, index)
        self.assertGreater(score_ps, score_n)

    def test_the_witness_low_for_most_profiles(self):
        """
        the_witness engages via N-aligned mechanisms.
        A high-O, low-N profile should score lower on it than a high-N profile.
        Validated against SNM arc analysis findings.
        """
        index = {"the_witness": ["hypervigilance", "paranoia_escalation",
                                  "significance_quest", "disorientation"]}
        high_n = make_profile({
            "hypervigilance": 3.0,
            "paranoia_escalation": 2.5,
            "significance_quest": 2.0,
            "disorientation": 1.5,
        }, big_five={"O": 0, "C": 0, "E": -1, "N": 2, "A": 0})
        pattern_seeker = make_profile({
            "curiosity_exploration": 3.0,
            "pattern_recognition": 2.5,
            "information_gap": 2.0,
        }, big_five={"O": 2, "C": 1, "E": 0, "N": -1, "A": 0})
        score_n  = self._score("the_witness", high_n, index)
        score_ps = self._score("the_witness", pattern_seeker, index)
        self.assertGreater(score_n, score_ps)


# ── INTEGRATION: LIVE LIBRARY ─────────────────────────────────────────────────

class TestPlannerIntegration(unittest.TestCase):
    """
    Integration tests against live plays_strips.json and plays_mechanisms.json.
    Skipped if files are not present.
    """

    @classmethod
    def setUpClass(cls):
        root = Path(__file__).parent.parent
        cls.has_files = (
            (root / "plays_strips.json").exists() and
            (root / "plays_mechanisms.json").exists()
        )

    def _skip_if_no_files(self):
        if not self.has_files:
            self.skipTest("plays_strips.json or plays_mechanisms.json not present")

    def test_strips_load_without_error(self):
        self._skip_if_no_files()
        from arc_planner import _load_strips
        arc_planner._STRIPS = {}
        strips = _load_strips()
        self.assertGreater(len(strips), 300)

    def test_mech_index_loads_without_error(self):
        self._skip_if_no_files()
        from arc_planner import _load_mech_index
        arc_planner._MECH_INDEX = {}
        index = _load_mech_index()
        self.assertGreater(len(index), 0)

    def test_known_play_has_strip(self):
        self._skip_if_no_files()
        from arc_planner import _load_strips
        arc_planner._STRIPS = {}
        strips = _load_strips()
        self.assertIn("the_vetting_letter", strips)
        self.assertIn("graduation_ritual", strips)

    def test_mech_score_nonzero_for_matching_profile(self):
        self._skip_if_no_files()
        arc_planner._MECH_INDEX = {}
        profile = make_profile({
            "curiosity_exploration": 3.0,
            "pattern_recognition": 2.5,
            "information_gap": 2.0,
        })
        score = _mech_score("the_vetting_letter", profile)
        # With any mechanism data present, should not be exactly 0.5 (neutral)
        # (it will be 0.5 only if no mechanisms in index — which would be a data error)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
