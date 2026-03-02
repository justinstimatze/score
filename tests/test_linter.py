"""
Unit tests for arc_linter.py

Strategy: test each check function with synthetic PlayStrip objects.
No live plays_strips.json required — check functions are pure given strips.
Integration tests at the bottom exercise parse_strip and lead_days directly.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from arc_linter import (
    Arc,
    PlayStrip,
    check_arc_fit,
    check_activation_void,
    check_branch_merge_blocks,
    check_contraindicated,
    check_detection_accumulation,
    check_frame_requirement,
    check_group_dynamics,
    check_lead_time,
    check_parallel_tracks,
    check_participation_tiers,
    check_permission_sequenced,
    check_pre_arc,
    check_recovery_blocks,
    check_requires_consistency,
    check_reversibility,
    check_rhythm,
    check_thresholds,
    check_unknown_plays,
    check_world_mark_timing,
    is_branch_block,
    is_play_element,
    lead_days,
    load_arc,
    lint_arc,
    parse_strip,
)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def make_play(
    pid: str,
    beat: str = "/",
    arc_codes: list[str] | None = None,
    detection: str = "m",
    reversibility: str = "a",
    legacy: str = "p",
    lead_time: str = "0",
    frame_req: str = "n",
    permission_mode: str = "S",
    permission_grant: str = "",
    contraindicated_after: list[str] | None = None,
    requires: list[str] | None = None,
    autonomy: str = "A",
    # v2 fields
    group_role: str = "s",
    social_modifier: str = "neut",
    participation_tier: str = "U",
    parallel_capable: bool = False,
    activation_rate: float = 1.0,
    witness_mechanisms: list[str] | None = None,
) -> PlayStrip:
    p = PlayStrip(id=pid)
    p.beat = beat
    p.arc_codes = arc_codes if arc_codes is not None else ["b"]
    p.detection = detection
    p.reversibility = reversibility
    p.legacy = legacy
    p.lead_time = lead_time
    p.frame_req = frame_req
    p.permission_mode = permission_mode
    p.permission_grant = permission_grant
    p.contraindicated_after = contraindicated_after or []
    p.requires = requires or []
    p.autonomy = autonomy
    p.group_role = group_role
    p.social_modifier = social_modifier
    p.participation_tier = participation_tier
    p.parallel_capable = parallel_capable
    p.activation_rate = activation_rate
    p.witness_mechanisms = witness_mechanisms or []
    return p


def positions(n: int) -> list[int]:
    return list(range(n))


def codes(issues, field="code"):
    return [getattr(i, field) for i in issues]


def severities(issues):
    return [i.severity for i in issues]


# ── LEAD_DAYS ─────────────────────────────────────────────────────────────────

class TestLeadDays(unittest.TestCase):
    def test_zero_codes(self):
        self.assertEqual(lead_days("0"), 0)
        self.assertEqual(lead_days("sd"), 0)

    def test_day_codes(self):
        self.assertEqual(lead_days("1d"), 1)
        self.assertEqual(lead_days("3d"), 3)

    def test_week_codes(self):
        self.assertEqual(lead_days("1w"), 7)
        self.assertEqual(lead_days("2w"), 14)
        self.assertEqual(lead_days("4w"), 28)
        self.assertEqual(lead_days("8w"), 56)

    def test_unknown_defaults_zero(self):
        self.assertEqual(lead_days("??"), 0)
        self.assertEqual(lead_days(""), 0)


# ── PARSE_STRIP ───────────────────────────────────────────────────────────────

FULL_STRIP = """\
@my_play F·A·3d·2
#curiosity_exploration·pattern_recognition [be] /
C·n·m·a·p·m·a
prm:Q→slv
syn:false_breakthrough·knowledge_frontier_seed
!ctr:the_vetting_letter
req:cnf·loc
"""

MINIMAL_STRIP = "@bare_play M·CA·1w·3"


class TestParseStrip(unittest.TestCase):
    def test_full_strip_id(self):
        p = parse_strip(FULL_STRIP)
        self.assertIsNotNone(p)
        self.assertEqual(p.id, "my_play")

    def test_full_strip_l1_fields(self):
        p = parse_strip(FULL_STRIP)
        self.assertEqual(p.cost, "F")
        self.assertEqual(p.autonomy, "A")
        self.assertEqual(p.lead_time, "3d")
        self.assertEqual(p.intensity, "2")

    def test_full_strip_mechanisms(self):
        p = parse_strip(FULL_STRIP)
        self.assertIn("curiosity_exploration", p.mechanisms)
        self.assertIn("pattern_recognition", p.mechanisms)

    def test_full_strip_arc_codes(self):
        p = parse_strip(FULL_STRIP)
        self.assertIn("b", p.arc_codes)
        self.assertIn("e", p.arc_codes)

    def test_full_strip_beat(self):
        p = parse_strip(FULL_STRIP)
        self.assertEqual(p.beat, "/")

    def test_full_strip_permission_mode_and_grant(self):
        p = parse_strip(FULL_STRIP)
        self.assertEqual(p.permission_mode, "Q")
        self.assertEqual(p.permission_grant, "slv")

    def test_full_strip_synergizes(self):
        p = parse_strip(FULL_STRIP)
        self.assertIn("false_breakthrough", p.synergizes)
        self.assertIn("knowledge_frontier_seed", p.synergizes)

    def test_full_strip_contraindicated(self):
        p = parse_strip(FULL_STRIP)
        self.assertIn("the_vetting_letter", p.contraindicated_after)

    def test_full_strip_requires(self):
        p = parse_strip(FULL_STRIP)
        self.assertIn("cnf", p.requires)
        self.assertIn("loc", p.requires)

    def test_minimal_strip(self):
        p = parse_strip(MINIMAL_STRIP)
        self.assertIsNotNone(p)
        self.assertEqual(p.id, "bare_play")
        self.assertEqual(p.cost, "M")
        self.assertEqual(p.lead_time, "1w")

    def test_empty_strip_returns_none(self):
        self.assertIsNone(parse_strip(""))
        self.assertIsNone(parse_strip("   "))

    def test_bad_l1_returns_none(self):
        self.assertIsNone(parse_strip("not a valid strip"))

    def test_lead_days_property(self):
        p = parse_strip(FULL_STRIP)
        self.assertEqual(p.lead_days, 3)

    def test_liminal_beat_parsed(self):
        strip = "@threshold_play F·A·sd·1\n#identity_shift [pt] ~\nC·n·l·r·p·l·r"
        p = parse_strip(strip)
        self.assertEqual(p.beat, "~")


# ── CHECK: UNKNOWN PLAYS ──────────────────────────────────────────────────────

class TestCheckUnknownPlays(unittest.TestCase):
    def setUp(self):
        self.library = {"known_play": make_play("known_play")}

    def test_known_play_no_issues(self):
        issues = check_unknown_plays(["known_play"], self.library)
        self.assertEqual(issues, [])

    def test_unknown_play_is_error(self):
        issues = check_unknown_plays(["nonexistent"], self.library)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "ERROR")
        self.assertEqual(issues[0].code, "UNKNOWN")

    def test_mixed_known_unknown(self):
        issues = check_unknown_plays(["known_play", "ghost"], self.library)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].play_id, "ghost")

    def test_all_unknown(self):
        issues = check_unknown_plays(["a", "b", "c"], self.library)
        self.assertEqual(len(issues), 3)


# ── CHECK: CONTRAINDICATED ────────────────────────────────────────────────────

class TestCheckContraindicated(unittest.TestCase):
    def test_no_contraindication(self):
        plays = [make_play("a"), make_play("b")]
        self.assertEqual(check_contraindicated(plays, positions(2)), [])

    def test_contraindicated_after_prior(self):
        a = make_play("a")
        b = make_play("b", contraindicated_after=["a"])
        issues = check_contraindicated([a, b], positions(2))
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "ERROR")
        self.assertEqual(issues[0].code, "CONTRAINDICATED")

    def test_contraindication_only_fires_if_prior_present(self):
        # b is contraindicated after 'x', but 'x' is not in the arc
        b = make_play("b", contraindicated_after=["x"])
        issues = check_contraindicated([b], positions(1))
        self.assertEqual(issues, [])

    def test_contraindication_direction(self):
        # a.contraindicated_after = [b] means: don't place a after b
        b = make_play("b")
        a = make_play("a", contraindicated_after=["b"])
        # order: a then b — 'b' has NOT preceded 'a', so no issue
        issues = check_contraindicated([a, b], positions(2))
        self.assertEqual(issues, [])
        # order: b then a — 'b' preceded 'a', so ERROR
        issues = check_contraindicated([b, a], positions(2))
        self.assertEqual(len(issues), 1)


# ── CHECK: FRAME REQUIREMENT ──────────────────────────────────────────────────

class TestCheckFrameRequirement(unittest.TestCase):
    def test_naive_plays_always_pass(self):
        plays = [make_play("a", frame_req="n"), make_play("b", frame_req="n")]
        self.assertEqual(check_frame_requirement(plays, positions(2)), [])

    def test_any_frame_always_pass(self):
        plays = [make_play("a", frame_req="*")]
        self.assertEqual(check_frame_requirement(plays, positions(1)), [])

    def test_primed_play_too_early_is_warn(self):
        # frame is still naive, play needs primed
        plays = [make_play("a", frame_req="q", beat="/", arc_codes=["p"])]
        issues = check_frame_requirement(plays, positions(1))
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "WARN")
        self.assertEqual(issues[0].code, "FRAME_REQ")

    def test_primed_play_after_ramp_passes(self):
        # first play is a ramp in build — primes frame
        ramp = make_play("ramp", beat="/", arc_codes=["b"], frame_req="n")
        primed = make_play("primed", beat="/", arc_codes=["b"], frame_req="q")
        issues = check_frame_requirement([ramp, primed], positions(2))
        self.assertEqual(issues, [])

    def test_meta_play_before_meta_frame_is_error(self):
        plays = [make_play("a", frame_req="m")]
        issues = check_frame_requirement(plays, positions(1))
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "ERROR")


# ── CHECK: PERMISSION SEQUENCED ───────────────────────────────────────────────

class TestCheckPermissionSequenced(unittest.TestCase):
    def test_standard_permission_no_issues(self):
        plays = [make_play("a", permission_mode="S")]
        self.assertEqual(check_permission_sequenced(plays, positions(1)), [])

    def test_prm_q_at_position_0_is_warn(self):
        plays = [make_play("a", permission_mode="Q")]
        issues = check_permission_sequenced(plays, positions(1))
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "WARN")
        self.assertEqual(issues[0].code, "PERMISSION")

    def test_prm_q_at_position_1_is_warn(self):
        plays = [make_play("a"), make_play("b", permission_mode="Q")]
        issues = check_permission_sequenced(plays, positions(2))
        self.assertEqual(len(issues), 1)

    def test_prm_q_at_position_2_passes(self):
        plays = [make_play("a"), make_play("b"), make_play("c", permission_mode="Q")]
        issues = check_permission_sequenced(plays, positions(3))
        self.assertEqual(issues, [])

    def test_prm_q_with_unmet_grant_is_warn(self):
        plays = [
            make_play("a"),
            make_play("b"),
            make_play("c", permission_mode="Q", permission_grant="slv"),
        ]
        issues = check_permission_sequenced(plays, positions(3))
        grant_issues = [i for i in issues if "slv" in i.message]
        self.assertTrue(len(grant_issues) >= 1)

    def test_prm_q_with_prior_grant_passes(self):
        plays = [
            make_play("a", permission_grant="slv"),
            make_play("b"),
            make_play("c", permission_mode="Q", permission_grant="slv"),
        ]
        issues = check_permission_sequenced(plays, positions(3))
        # Should have no grant-missing warning
        grant_issues = [i for i in issues if "slv" in i.message]
        self.assertEqual(grant_issues, [])


# ── CHECK: LEAD TIME ──────────────────────────────────────────────────────────

class TestCheckLeadTime(unittest.TestCase):
    def test_no_days_skips_check(self):
        plays = [make_play("a", lead_time="3d")]
        issues = check_lead_time(plays, positions(1), [None])
        self.assertEqual(issues, [])

    def test_sufficient_lead_time_passes(self):
        plays = [make_play("a", lead_time="3d")]
        issues = check_lead_time(plays, positions(1), [5])
        self.assertEqual(issues, [])

    def test_insufficient_lead_time_is_error(self):
        plays = [make_play("a", lead_time="3d")]
        issues = check_lead_time(plays, positions(1), [0])
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "ERROR")
        self.assertEqual(issues[0].code, "LEAD_TIME")

    def test_exact_lead_time_passes(self):
        plays = [make_play("a", lead_time="3d")]
        issues = check_lead_time(plays, positions(1), [3])
        self.assertEqual(issues, [])

    def test_one_day_short_is_error(self):
        plays = [make_play("a", lead_time="1w")]
        issues = check_lead_time(plays, positions(1), [6])
        self.assertEqual(len(issues), 1)

    def test_zero_lead_time_always_passes(self):
        plays = [make_play("a", lead_time="0")]
        issues = check_lead_time(plays, positions(1), [0])
        self.assertEqual(issues, [])

    def test_none_day_skipped(self):
        plays = [make_play("a", lead_time="3d"), make_play("b", lead_time="3d")]
        issues = check_lead_time(plays, positions(2), [None, 0])
        # Only 'b' should be flagged
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].play_id, "b")


# ── CHECK: RHYTHM ─────────────────────────────────────────────────────────────

class TestCheckRhythm(unittest.TestCase):
    def _spikes(self, n):
        return [make_play(f"s{i}", beat="^") for i in range(n)]

    def test_four_consecutive_spikes_ok(self):
        plays = self._spikes(4)
        issues = check_rhythm(plays, positions(4))
        rhythm_issues = [i for i in issues if i.code == "RHYTHM" and i.position >= 0]
        self.assertEqual(rhythm_issues, [])

    def test_five_consecutive_spikes_is_warn(self):
        plays = self._spikes(5)
        issues = check_rhythm(plays, positions(5))
        warn = [i for i in issues if i.code == "RHYTHM" and i.severity == "WARN" and i.position >= 0]
        self.assertEqual(len(warn), 1)

    def test_no_hold_in_long_arc_is_warn(self):
        plays = [make_play(f"r{i}", beat="/") for i in range(7)]
        issues = check_rhythm(plays, positions(7))
        arc_warns = [i for i in issues if i.code == "RHYTHM" and i.position == -1
                     and "dwell" in i.message]
        self.assertEqual(len(arc_warns), 1)

    def test_hold_present_suppresses_no_hold_warn(self):
        plays = [make_play(f"r{i}", beat="/") for i in range(6)] + [make_play("h", beat="_")]
        issues = check_rhythm(plays, positions(7))
        arc_warns = [i for i in issues if "dwell" in i.message]
        self.assertEqual(arc_warns, [])

    def test_short_arc_no_hold_warn_not_triggered(self):
        # Arc of 6 scored plays — threshold is >6
        plays = [make_play(f"r{i}", beat="/") for i in range(6)]
        issues = check_rhythm(plays, positions(6))
        arc_warns = [i for i in issues if "dwell" in i.message]
        self.assertEqual(arc_warns, [])

    def test_low_cathartic_density_warn(self):
        # 7 ramp plays + 1 spike = 1 spike in 8 plays
        plays = [make_play(f"r{i}", beat="/") for i in range(7)] + [make_play("s", beat="^")]
        issues = check_rhythm(plays, positions(8))
        density_warns = [i for i in issues if "cathartic" in i.message]
        self.assertEqual(len(density_warns), 1)

    def test_two_spikes_no_cathartic_warn(self):
        plays = [make_play(f"r{i}", beat="/") for i in range(6)] + \
                [make_play("s1", beat="^"), make_play("s2", beat="^")]
        issues = check_rhythm(plays, positions(8))
        density_warns = [i for i in issues if "cathartic" in i.message]
        self.assertEqual(density_warns, [])

    def test_spike_after_rest_is_warn(self):
        plays = [make_play("a", beat="-"), make_play("b", beat="^")]
        issues = check_rhythm(plays, positions(2))
        re_escalation = [i for i in issues if "re-escalation" in i.message]
        self.assertEqual(len(re_escalation), 1)

    def test_liminal_does_not_count_in_scored_beats(self):
        # 6 ramps + 1 liminal = 6 scored beats — at threshold (not >6), no warn
        plays = [make_play(f"r{i}", beat="/") for i in range(6)] + [make_play("lim", beat="~")]
        issues = check_rhythm(plays, positions(7))
        arc_warns = [i for i in issues if "dwell" in i.message]
        self.assertEqual(arc_warns, [])

    def test_liminal_does_not_reset_spike_run(self):
        # 4 spikes + liminal + 1 more spike = 5 spike run (liminal doesn't reset)
        plays = [make_play(f"s{i}", beat="^") for i in range(4)] + \
                [make_play("lim", beat="~")] + [make_play("s5", beat="^")]
        issues = check_rhythm(plays, positions(6))
        fatigue = [i for i in issues if "fatigue" in i.message]
        self.assertEqual(len(fatigue), 1)


# ── CHECK: DETECTION ACCUMULATION ────────────────────────────────────────────

class TestCheckDetectionAccumulation(unittest.TestCase):
    def test_low_detection_no_warn(self):
        plays = [make_play(f"p{i}", detection="l") for i in range(6)]
        issues = check_detection_accumulation(plays, positions(6))
        self.assertEqual(issues, [])

    def test_four_immediate_detection_is_warn(self):
        # risk=4 each × 4 = 16 ≥ 10
        plays = [make_play(f"p{i}", detection="i") for i in range(4)]
        issues = check_detection_accumulation(plays, positions(4))
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "WARN")

    def test_window_below_threshold_passes(self):
        # risk=2 each (medium) × 4 = 8 < 10
        plays = [make_play(f"p{i}", detection="m") for i in range(4)]
        issues = check_detection_accumulation(plays, positions(4))
        self.assertEqual(issues, [])

    def test_window_slides_correctly(self):
        # positions 0-3: low risk; positions 4-7: immediate risk
        low = [make_play(f"l{i}", detection="l") for i in range(4)]
        high = [make_play(f"h{i}", detection="i") for i in range(4)]
        plays = low + high
        issues = check_detection_accumulation(plays, positions(8))
        # Only the high-risk window should fire
        self.assertTrue(len(issues) >= 1)
        # The flagged position should be in the high-detection window
        flagged_positions = [i.position for i in issues]
        self.assertTrue(all(p >= 4 for p in flagged_positions))


# ── CHECK: REVERSIBILITY ──────────────────────────────────────────────────────

class TestCheckReversibility(unittest.TestCase):
    def test_irreversible_late_is_ok(self):
        plays = [make_play(f"p{i}") for i in range(8)] + \
                [make_play("irrev", reversibility="x")]
        issues = check_reversibility(plays, positions(9))
        self.assertEqual(issues, [])

    def test_irreversible_in_first_quarter_is_warn(self):
        plays = [make_play("irrev", reversibility="x")] + \
                [make_play(f"p{i}") for i in range(7)]
        issues = check_reversibility(plays, positions(8))
        rev_warns = [i for i in issues if i.code == "REVERSIBILITY"]
        self.assertEqual(len(rev_warns), 1)
        self.assertEqual(rev_warns[0].severity, "WARN")

    def test_reversible_in_first_quarter_is_ok(self):
        plays = [make_play("rev", reversibility="a")] + \
                [make_play(f"p{i}") for i in range(7)]
        issues = check_reversibility(plays, positions(8))
        self.assertEqual(issues, [])


# ── CHECK: ARC FIT ────────────────────────────────────────────────────────────

class TestCheckArcFit(unittest.TestCase):
    def test_no_phases_skips_check(self):
        plays = [make_play("a", arc_codes=["b"])]
        issues = check_arc_fit(plays, positions(1), [None])
        self.assertEqual(issues, [])

    def test_matching_phase_passes(self):
        plays = [make_play("a", arc_codes=["b"])]
        issues = check_arc_fit(plays, positions(1), ["b"])
        self.assertEqual(issues, [])

    def test_mismatched_phase_is_warn(self):
        plays = [make_play("a", arc_codes=["e"])]
        issues = check_arc_fit(plays, positions(1), ["b"])
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "WARN")
        self.assertEqual(issues[0].code, "ARC_FIT")

    def test_wildcard_arc_code_always_passes(self):
        plays = [make_play("a", arc_codes=["*"])]
        issues = check_arc_fit(plays, positions(1), ["b"])
        self.assertEqual(issues, [])

    def test_multi_arc_code_passes_if_any_match(self):
        plays = [make_play("a", arc_codes=["b", "e"])]
        issues = check_arc_fit(plays, positions(1), ["e"])
        self.assertEqual(issues, [])


# ── CHECK: WORLD MARK TIMING ─────────────────────────────────────────────────

class TestCheckWorldMarkTiming(unittest.TestCase):
    def test_world_mark_early_no_warn(self):
        # Position 0 of 10 — early, fine
        plays = [make_play("a", legacy="w", lead_time="0")] + \
                [make_play(f"p{i}") for i in range(9)]
        issues = check_world_mark_timing(plays, positions(10))
        self.assertEqual(issues, [])

    def test_world_mark_late_short_lead_is_warn(self):
        # Position 7 of 10 (70% through) with 0d lead time
        plays = [make_play(f"p{i}") for i in range(7)] + \
                [make_play("wm", legacy="w", lead_time="0")] + \
                [make_play(f"q{i}") for i in range(2)]
        issues = check_world_mark_timing(plays, positions(10))
        warns = [i for i in issues if i.code == "LEGACY_SCOPE"]
        self.assertEqual(len(warns), 1)

    def test_world_mark_late_long_lead_passes(self):
        # 2w lead time — sufficient
        plays = [make_play(f"p{i}") for i in range(7)] + \
                [make_play("wm", legacy="w", lead_time="2w")] + \
                [make_play(f"q{i}") for i in range(2)]
        issues = check_world_mark_timing(plays, positions(10))
        warns = [i for i in issues if i.code == "LEGACY_SCOPE"]
        self.assertEqual(warns, [])


# ── CHECK: REQUIRES CONSISTENCY ───────────────────────────────────────────────

class TestCheckRequiresConsistency(unittest.TestCase):
    def test_single_confederate_no_info(self):
        plays = [make_play("a", autonomy="CA")]
        issues = check_requires_consistency(plays, positions(1))
        confederate_info = [i for i in issues if "confederate" in i.message]
        self.assertEqual(confederate_info, [])

    def test_two_confederate_plays_is_info(self):
        plays = [make_play("a", autonomy="CA"), make_play("b", autonomy="CA")]
        issues = check_requires_consistency(plays, positions(2))
        confederate_info = [i for i in issues if "confederate" in i.message]
        self.assertEqual(len(confederate_info), 1)
        self.assertEqual(confederate_info[0].severity, "INFO")

    def test_two_location_plays_is_info(self):
        plays = [
            make_play("a", requires=["loc"]),
            make_play("b", requires=["loc"]),
        ]
        issues = check_requires_consistency(plays, positions(2))
        loc_info = [i for i in issues if "location" in i.message]
        self.assertEqual(len(loc_info), 1)

    def test_single_location_no_info(self):
        plays = [make_play("a", requires=["loc"])]
        issues = check_requires_consistency(plays, positions(1))
        loc_info = [i for i in issues if "location" in i.message]
        self.assertEqual(loc_info, [])


# ── INTEGRATION: KNOWN-GOOD ARCS ─────────────────────────────────────────────

class TestIntegrationKnownArcs(unittest.TestCase):
    """
    Integration tests against the live strips file.
    Skipped if plays_strips.json is not present.
    """

    @classmethod
    def setUpClass(cls):
        strips_file = Path(__file__).parent.parent / "plays_strips.json"
        cls.has_library = strips_file.exists()

    def _lint(self, play_ids, days=None, phases=None):
        from arc_linter import _lint_flat
        return _lint_flat(play_ids, days, phases)

    def _skip_if_no_library(self):
        if not self.has_library:
            self.skipTest("plays_strips.json not present")

    def test_all_latitude_plays_exist(self):
        self._skip_if_no_library()
        latitude_plays = [
            "the_vetting_letter", "stripping_ceremony", "welcome_flood",
            "incremental_oath", "layered_secret_system", "lexical_deepening",
            "environmental_narrative_space", "the_us_signal", "graduation_ritual",
        ]
        issues, _ = self._lint(latitude_plays)
        unknown = [i for i in issues if i.code == "UNKNOWN"]
        self.assertEqual(unknown, [], f"Unknown plays: {[i.play_id for i in unknown]}")

    def test_latitude_arc_has_no_hold_warn(self):
        self._skip_if_no_library()
        latitude_plays = [
            "the_vetting_letter", "stripping_ceremony", "welcome_flood",
            "incremental_oath", "layered_secret_system", "lexical_deepening",
            "environmental_narrative_space", "the_us_signal", "graduation_ritual",
        ]
        issues, _ = self._lint(latitude_plays)
        no_hold = [i for i in issues if "dwell" in i.message]
        self.assertEqual(len(no_hold), 1, "Latitude arc should warn: no hold beats")

    def test_latitude_arc_has_low_cathartic_density_warn(self):
        self._skip_if_no_library()
        latitude_plays = [
            "the_vetting_letter", "stripping_ceremony", "welcome_flood",
            "incremental_oath", "layered_secret_system", "lexical_deepening",
            "environmental_narrative_space", "the_us_signal", "graduation_ritual",
        ]
        issues, _ = self._lint(latitude_plays)
        density = [i for i in issues if "cathartic" in i.message]
        self.assertEqual(len(density), 1, "Latitude arc should warn: low cathartic density")

    def test_lead_time_error_on_day_zero(self):
        self._skip_if_no_library()
        # the_vetting_letter has 3d lead time — day 0 should error
        issues, _ = self._lint(["the_vetting_letter"], days=[0])
        lead_errors = [i for i in issues if i.code == "LEAD_TIME" and i.severity == "ERROR"]
        self.assertEqual(len(lead_errors), 1)

    def test_lead_time_passes_with_sufficient_days(self):
        self._skip_if_no_library()
        issues, _ = self._lint(["the_vetting_letter"], days=[14])
        lead_errors = [i for i in issues if i.code == "LEAD_TIME" and i.severity == "ERROR"]
        self.assertEqual(lead_errors, [])

    def test_single_known_play_no_unknown_error(self):
        self._skip_if_no_library()
        issues, plays = self._lint(["welcome_flood"])
        unknown = [i for i in issues if i.code == "UNKNOWN"]
        self.assertEqual(unknown, [])
        self.assertEqual(len(plays), 1)
        self.assertEqual(plays[0].id, "welcome_flood")


# ── PARSE_STRIP V2 ────────────────────────────────────────────────────────────

STRIP_WITH_GRP = """\
@one_on_one_private_scene F·C·sd·3
#status_elevation·dyadic_interaction [e] ^
C·n·h·a·ps·s·d
prm:Q→selected
grp:ac·dist·U·0·0.15
wit:SV·SP"""

STRIP_WITH_GRP_ENSEMBLE = """\
@communitas_beat F·A·0·2
#collective_effervescence·belonging [bec] ~
B·*·l·+·s·n·t
prm:S
grp:e·amp·U·0·1.0"""


class TestParseStripV2(unittest.TestCase):
    def test_grp_line_parsed(self):
        strip = parse_strip(STRIP_WITH_GRP)
        self.assertIsNotNone(strip)
        self.assertEqual(strip.group_role, "ac")
        self.assertEqual(strip.social_modifier, "dist")
        self.assertEqual(strip.participation_tier, "U")
        self.assertFalse(strip.parallel_capable)
        self.assertAlmostEqual(strip.activation_rate, 0.15)

    def test_wit_line_parsed(self):
        strip = parse_strip(STRIP_WITH_GRP)
        self.assertIsNotNone(strip)
        self.assertEqual(strip.witness_mechanisms, ["SV", "SP"])

    def test_grp_ensemble(self):
        strip = parse_strip(STRIP_WITH_GRP_ENSEMBLE)
        self.assertIsNotNone(strip)
        self.assertEqual(strip.group_role, "e")
        self.assertEqual(strip.social_modifier, "amp")
        self.assertAlmostEqual(strip.activation_rate, 1.0)

    def test_solo_default_when_no_grp(self):
        strip = parse_strip("""\
@basic F·A·0·2
#curiosity_exploration [b] /
C·n·m·a·p·m·a
prm:S""")
        self.assertIsNotNone(strip)
        self.assertEqual(strip.group_role, "s")
        self.assertEqual(strip.activation_rate, 1.0)
        self.assertFalse(strip.parallel_capable)
        self.assertEqual(strip.witness_mechanisms, [])


# ── LOAD_ARC_V2 ───────────────────────────────────────────────────────────────

class TestLoadArc(unittest.TestCase):
    def test_flat_list_of_strings(self):
        arc = load_arc(["play1", "play2"])
        self.assertEqual(len(arc.plays), 2)
        self.assertEqual(arc.plays[0], {"id": "play1"})

    def test_flat_list_of_dicts(self):
        arc = load_arc([{"id": "play1", "day": 0, "phase": "p"}])
        self.assertEqual(arc.plays[0]["id"], "play1")

    def test_v2_dict_format(self):
        data = {
            "arc_type": "investigation",
            "audience_scale": "mass",
            "pre_arc": {"plays": [{"id": "pre_play", "day": -14}]},
            "parallel_tracks": [{"track_id": "ambient", "plays": []}],
            "thresholds": [{"id": "t1", "condition": "operator_signal:GO"}],
            "plays": [{"id": "main_play", "day": 0, "phase": "b"}],
        }
        arc = load_arc(data)
        self.assertEqual(arc.arc_type, "investigation")
        self.assertEqual(arc.audience_scale, "mass")
        self.assertEqual(len(arc.pre_arc_plays), 1)
        self.assertEqual(arc.pre_arc_plays[0]["id"], "pre_play")
        self.assertEqual(len(arc.parallel_tracks), 1)
        self.assertEqual(len(arc.thresholds), 1)
        self.assertEqual(arc.plays[0]["id"], "main_play")

    def test_is_branch_block(self):
        self.assertTrue(is_branch_block({"id": "b1", "branch_point": {}}))
        self.assertFalse(is_branch_block({"id": "p1"}))
        # branch_point without id still discriminates as a branch block (id is optional)
        self.assertTrue(is_branch_block({"branch_point": {}}))

    def test_is_play_element(self):
        self.assertTrue(is_play_element({"id": "p1", "day": 0}))
        self.assertFalse(is_play_element({"id": "b1", "branch_point": {}}))


# ── CHECK_PRE_ARC ─────────────────────────────────────────────────────────────

class TestPreArcChecks(unittest.TestCase):
    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_pre_arc_unknown_play_errors(self):
        issues, grants = check_pre_arc(
            [{"id": "nonexistent", "day": -14}], {}
        )
        self.assertTrue(any(i.code == "UNKNOWN" for i in issues))

    def test_pre_arc_lead_time_fail(self):
        lib = self._lib(make_play("seed", lead_time="4w"))  # 28d lead needed
        # day=-7 → 7d available, insufficient
        issues, _ = check_pre_arc([{"id": "seed", "day": -7}], lib)
        lead_errs = [i for i in issues if i.code == "LEAD_TIME"]
        self.assertTrue(len(lead_errs) > 0)

    def test_pre_arc_lead_time_ok(self):
        lib = self._lib(make_play("seed", lead_time="1w"))  # 7d lead needed
        # day=-28 → 28d available
        issues, _ = check_pre_arc([{"id": "seed", "day": -28}], lib)
        lead_errs = [i for i in issues if i.code == "LEAD_TIME"]
        self.assertEqual(lead_errs, [])

    def test_pre_arc_grants_accumulated(self):
        lib = self._lib(make_play("grant_play", permission_grant="asr"))
        _, grants = check_pre_arc([{"id": "grant_play", "day": -14}], lib)
        self.assertIn("asr", grants)

    def test_pre_arc_grants_passed_to_main(self):
        # pre_arc produces "asr"; main arc play needs "asr" at position 0 — should NOT warn
        pre_play = make_play("pre_seeder", permission_grant="asr")
        main_play = make_play("needs_asr", permission_mode="Q", permission_grant="asr")
        issues = check_permission_sequenced([main_play], [0], initial_grants={"asr"})
        grant_warns = [i for i in issues if "asr" in i.message and "not yet produced" in i.message]
        self.assertEqual(grant_warns, [])

    def test_permission_no_initial_grants_still_warns(self):
        play = make_play("needs_asr", permission_mode="Q", permission_grant="asr")
        issues = check_permission_sequenced([play], [0])
        grant_warns = [i for i in issues if "asr" in i.message and "not yet produced" in i.message]
        self.assertTrue(len(grant_warns) > 0)


# ── CHECK_PARALLEL_TRACKS ─────────────────────────────────────────────────────

class TestParallelTrackChecks(unittest.TestCase):
    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_no_end_day_warns(self):
        lib = self._lib(make_play("ambient_ad", lead_time="0"))
        tracks = [{"track_id": "pressure", "plays": [
            {"id": "ambient_ad", "start_day": 0}  # no end_day
        ]}]
        issues, _ = check_parallel_tracks(tracks, [], lib)
        self.assertTrue(any(i.code == "PARALLEL_END_CONDITION" for i in issues))

    def test_with_end_day_no_warn(self):
        lib = self._lib(make_play("ambient_ad", lead_time="0"))
        tracks = [{"track_id": "pressure", "plays": [
            {"id": "ambient_ad", "start_day": 0, "end_day": 14}
        ]}]
        issues, _ = check_parallel_tracks(tracks, [], lib)
        end_warns = [i for i in issues if i.code == "PARALLEL_END_CONDITION"]
        self.assertEqual(end_warns, [])

    def test_insufficient_lead_time_errors(self):
        lib = self._lib(make_play("slow_burn", lead_time="4w"))  # needs 28d
        tracks = [{"track_id": "seeding", "plays": [
            {"id": "slow_burn", "start_day": 7, "end_day": 35}  # only 7d
        ]}]
        issues, _ = check_parallel_tracks(tracks, [], lib)
        self.assertTrue(any(i.code == "PARALLEL_LEAD_TIME" for i in issues))

    def test_unknown_parallel_play_errors(self):
        tracks = [{"track_id": "x", "plays": [
            {"id": "ghost_play", "start_day": 0, "end_day": 7}
        ]}]
        issues, _ = check_parallel_tracks(tracks, [], {})
        self.assertTrue(any(i.code == "UNKNOWN" for i in issues))

    def test_day_risk_map_populated(self):
        lib = self._lib(make_play("hi_det", detection="i"))
        tracks = [{"track_id": "t", "plays": [
            {"id": "hi_det", "start_day": 0, "end_day": 3}
        ]}]
        _, day_risk = check_parallel_tracks(tracks, [], lib)
        self.assertTrue(len(day_risk) > 0)
        self.assertTrue(any(v > 0 for v in day_risk.values()))

    def test_overlap_with_high_detection_main_play(self):
        lib = self._lib(
            make_play("parallel_play", detection="s"),
            make_play("main_hot", detection="i"),
        )
        main_plays = [{"id": "main_hot", "day": 5}]
        tracks = [{"track_id": "t", "plays": [
            {"id": "parallel_play", "start_day": 3, "end_day": 7}
        ]}]
        issues, _ = check_parallel_tracks(tracks, main_plays, lib)
        self.assertTrue(any(i.code == "PARALLEL_OVERLAP_WITH_MAIN" for i in issues))


# ── CHECK_DETECTION_DAY_INDEXED ───────────────────────────────────────────────

class TestDetectionDayIndexed(unittest.TestCase):
    def test_positional_mode_still_works(self):
        plays = [make_play(f"p{i}", detection="i") for i in range(5)]
        issues = check_detection_accumulation(plays, list(range(5)))
        self.assertTrue(any(i.code == "DETECTION" for i in issues))

    def test_day_indexed_fires_on_dense_window(self):
        plays = [
            make_play("a", detection="i"),
            make_play("b", detection="i"),
            make_play("c", detection="s"),
        ]
        days = [0, 1, 2]  # all within 7-day window, risk = 4+4+3=11 > 10
        issues = check_detection_accumulation(plays, [0, 1, 2], days=days)
        self.assertTrue(any(i.code == "DETECTION" for i in issues))

    def test_day_indexed_no_fire_when_spread(self):
        plays = [
            make_play("a", detection="i"),
            make_play("b", detection="i"),
        ]
        days = [0, 30]  # far apart, separate 7-day windows
        issues = check_detection_accumulation(plays, [0, 1], days=days)
        det = [i for i in issues if i.code == "DETECTION"]
        self.assertEqual(det, [])

    def test_extra_day_risks_contribute(self):
        plays = [make_play("a", detection="m")]  # risk 2
        days = [0]
        extra = {0: 9.0}  # push total to 11
        issues = check_detection_accumulation(plays, [0], days=days, extra_day_risks=extra)
        self.assertTrue(any(i.code == "DETECTION" for i in issues))


# ── CHECK_BRANCH_MERGE ────────────────────────────────────────────────────────

class TestBranchMergeChecks(unittest.TestCase):
    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def _block(self, **kwargs):
        base = {
            "id": "test_branch",
            "day": 10,
            "phase": "e",
            "branch_point": {"selection": "activation_rate:0.15", "visible_to_group": True},
            "branches": {
                "activated": {
                    "participants": "role:investigator",
                    "plays": [{"id": "act_play", "phase": "e"}],
                    "grants": ["selected"],
                },
                "witness": {
                    "participants": "all_others",
                    "plays": [{"id": "wit_play", "phase": "e"}],
                },
            },
            "merge_point": {"play": "merge_play", "context_visible": True},
        }
        base.update(kwargs)
        return base

    def test_merge_designed_error_on_missing_key(self):
        block = self._block()
        del block["merge_point"]
        lib = self._lib(make_play("act_play"), make_play("wit_play"))
        issues = check_branch_merge_blocks([block], lib)
        self.assertTrue(any(i.code == "MERGE_DESIGNED" for i in issues))

    def test_null_merge_point_is_valid(self):
        block = self._block()
        block["merge_point"] = None
        lib = self._lib(make_play("act_play"), make_play("wit_play"))
        issues = check_branch_merge_blocks([block], lib)
        merge_errors = [i for i in issues if i.code == "MERGE_DESIGNED"]
        self.assertEqual(merge_errors, [])

    def test_witness_void_fires_without_witness_branch(self):
        block = self._block()
        del block["branches"]["witness"]
        lib = self._lib(make_play("act_play"))
        issues = check_branch_merge_blocks([block], lib)
        self.assertTrue(any(i.code == "WITNESS_VOID" for i in issues))

    def test_no_witness_void_when_witness_present(self):
        block = self._block()
        lib = self._lib(make_play("act_play"), make_play("wit_play"), make_play("merge_play"))
        issues = check_branch_merge_blocks([block], lib)
        void_warns = [i for i in issues if i.code == "WITNESS_VOID"]
        self.assertEqual(void_warns, [])

    def test_merge_beat_warns_on_hold(self):
        block = self._block()
        lib = self._lib(
            make_play("act_play"),
            make_play("wit_play"),
            make_play("merge_play", beat="_"),  # hold at merge point
        )
        issues = check_branch_merge_blocks([block], lib)
        self.assertTrue(any(i.code == "MERGE_BEAT" for i in issues))

    def test_merge_beat_ok_on_spike(self):
        block = self._block()
        lib = self._lib(
            make_play("act_play"),
            make_play("wit_play"),
            make_play("merge_play", beat="^"),  # spike at merge point
        )
        issues = check_branch_merge_blocks([block], lib)
        beat_warns = [i for i in issues if i.code == "MERGE_BEAT"]
        self.assertEqual(beat_warns, [])

    def test_cascade_fatigue_on_triple_activation(self):
        selector = "role:investigator"
        blocks = []
        for i in range(3):
            blocks.append({
                "id": f"branch_{i}", "day": i * 5, "phase": "e",
                "branch_point": {"selection": "activation_rate:0.2"},
                "branches": {
                    "activated": {"participants": selector, "plays": []},
                    "witness": {"participants": "all_others", "plays": []},
                },
                "merge_point": None,
            })
        issues = check_branch_merge_blocks(blocks, {})
        self.assertTrue(any(i.code == "CASCADE_FATIGUE" for i in issues))

    def test_cascade_fatigue_ok_on_two(self):
        selector = "role:investigator"
        blocks = [
            {
                "id": f"branch_{i}", "day": i * 5, "phase": "e",
                "branch_point": {"selection": "activation_rate:0.2"},
                "branches": {
                    "activated": {"participants": selector, "plays": []},
                    "witness": {"participants": "all_others", "plays": []},
                },
                "merge_point": None,
            }
            for i in range(2)
        ]
        issues = check_branch_merge_blocks(blocks, {})
        fatigue = [i for i in issues if i.code == "CASCADE_FATIGUE"]
        self.assertEqual(fatigue, [])

    def test_permanent_divergence_info_emitted(self):
        block = self._block()
        block["merge_point"] = None
        lib = self._lib(make_play("act_play"), make_play("wit_play"))
        issues = check_branch_merge_blocks([block], lib)
        self.assertTrue(any(i.code == "PERMANENT_DIVERGENCE_COVERAGE" for i in issues))


# ── CHECK_GROUP_DYNAMICS ──────────────────────────────────────────────────────

class TestGroupDynamicsChecks(unittest.TestCase):
    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_climax_coverage_warns_on_solo_climax(self):
        arc_plays = [{"id": "climax_play", "day": 20, "phase": "c"}]
        lib = self._lib(make_play("climax_play", group_role="s", arc_codes=["c"]))
        issues = check_group_dynamics(arc_plays, lib)
        self.assertTrue(any(i.code == "CLIMAX_COVERAGE" for i in issues))

    def test_climax_coverage_ok_on_ensemble_climax(self):
        arc_plays = [{"id": "climax_play", "day": 20, "phase": "c"}]
        lib = self._lib(make_play("climax_play", group_role="e", arc_codes=["c"]))
        issues = check_group_dynamics(arc_plays, lib)
        coverage_issues = [i for i in issues if i.code == "CLIMAX_COVERAGE"]
        self.assertEqual(coverage_issues, [])

    def test_witness_density_warns(self):
        arc_plays = [{"id": "act_play", "day": 10, "phase": "e",
                      "assignment": {"activated": ["marcus"], "witnesses": []}}]
        lib = self._lib(make_play("act_play", group_role="ac", arc_codes=["e"]))
        issues = check_group_dynamics(arc_plays, lib)
        self.assertTrue(any(i.code == "WITNESS_DENSITY" for i in issues))

    def test_witness_density_ok_with_witnesses(self):
        arc_plays = [{"id": "act_play", "day": 10, "phase": "e",
                      "assignment": {"activated": ["marcus"], "witnesses": ["nadia", "dev"]}}]
        lib = self._lib(make_play("act_play", group_role="ac", arc_codes=["e"]))
        issues = check_group_dynamics(arc_plays, lib)
        density_issues = [i for i in issues if i.code == "WITNESS_DENSITY"]
        self.assertEqual(density_issues, [])

    def test_activation_fatigue_fires_on_consecutive(self):
        arc_plays = [
            {"id": "play1", "day": 5, "phase": "e",
             "assignment": {"activated": ["marcus"], "witnesses": ["nadia"]}},
            {"id": "play2", "day": 6, "phase": "e",
             "assignment": {"activated": ["marcus"], "witnesses": ["nadia"]}},
        ]
        lib = self._lib(
            make_play("play1", group_role="ac"),
            make_play("play2", group_role="ac"),
        )
        issues = check_group_dynamics(arc_plays, lib)
        self.assertTrue(any(i.code == "ACTIVATION_FATIGUE" for i in issues))

    def test_dist_play_at_climax_warns(self):
        arc_plays = [{"id": "dist_climax", "day": 20, "phase": "c"}]
        lib = self._lib(make_play("dist_climax", social_modifier="dist", arc_codes=["c"]))
        issues = check_group_dynamics(arc_plays, lib)
        self.assertTrue(any(i.code == "DIST_PLAY_CONTEXT" for i in issues))

    def test_dist_play_at_build_ok(self):
        arc_plays = [{"id": "dist_build", "day": 5, "phase": "b"}]
        lib = self._lib(make_play("dist_build", social_modifier="dist", arc_codes=["b"]))
        issues = check_group_dynamics(arc_plays, lib)
        dist_issues = [i for i in issues if i.code == "DIST_PLAY_CONTEXT"]
        self.assertEqual(dist_issues, [])


# ── CHECK_PARTICIPATION_TIERS ─────────────────────────────────────────────────

class TestParticipationTierChecks(unittest.TestCase):
    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_tier_floor_fires_on_mass_without_P(self):
        arc_plays = [{"id": "p1"}, {"id": "p2"}]
        lib = self._lib(
            make_play("p1", participation_tier="U"),
            make_play("p2", participation_tier="E"),
        )
        issues = check_participation_tiers(arc_plays, lib, "mass")
        self.assertTrue(any(i.code == "TIER_FLOOR" for i in issues))

    def test_tier_ceiling_fires_on_mass_without_U(self):
        arc_plays = [{"id": "p1"}, {"id": "p2"}]
        lib = self._lib(
            make_play("p1", participation_tier="P"),
            make_play("p2", participation_tier="A"),
        )
        issues = check_participation_tiers(arc_plays, lib, "mass")
        self.assertTrue(any(i.code == "TIER_CEILING" for i in issues))

    def test_no_tier_checks_for_intimate(self):
        arc_plays = [{"id": "p1"}]
        lib = self._lib(make_play("p1", participation_tier="U"))
        issues = check_participation_tiers(arc_plays, lib, "intimate")
        tier_issues = [i for i in issues if i.code in ("TIER_FLOOR", "TIER_CEILING")]
        self.assertEqual(tier_issues, [])

    def test_mass_arc_with_both_tiers_no_issues(self):
        arc_plays = [{"id": "p1"}, {"id": "p2"}]
        lib = self._lib(
            make_play("p1", participation_tier="P"),
            make_play("p2", participation_tier="U"),
        )
        issues = check_participation_tiers(arc_plays, lib, "mass")
        tier_issues = [i for i in issues if i.code in ("TIER_FLOOR", "TIER_CEILING")]
        self.assertEqual(tier_issues, [])

    def test_collective_solve_calibration_fires_on_ensemble_collective(self):
        arc_plays = [{"id": "communal"}]
        play = make_play("communal", group_role="e")
        play.mechanisms = ["collective_effervescence"]  # trigger mechanism
        lib = {"communal": play}
        issues = check_participation_tiers(arc_plays, lib, "intimate")
        self.assertTrue(any(i.code == "COLLECTIVE_SOLVE_CALIBRATION" for i in issues))


# ── CHECK_ACTIVATION_VOID ─────────────────────────────────────────────────────

class TestActivationVoidCheck(unittest.TestCase):
    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_void_fires_when_no_witness_design(self):
        arc_plays = [{"id": "act_play"}]
        lib = self._lib(make_play("act_play", group_role="ac", activation_rate=0.15))
        issues = check_activation_void(arc_plays, lib)
        self.assertTrue(any(i.code == "ACTIVATION_VOID" for i in issues))

    def test_no_void_when_witness_mechanisms_present(self):
        arc_plays = [{"id": "act_play"}]
        play = make_play("act_play", group_role="ac", activation_rate=0.15,
                         witness_mechanisms=["SP", "SV"])
        lib = {"act_play": play}
        issues = check_activation_void(arc_plays, lib)
        void = [i for i in issues if i.code == "ACTIVATION_VOID"]
        self.assertEqual(void, [])

    def test_no_void_when_in_witness_branch(self):
        # act_play appears in a branch's witness plays → no void
        arc_plays = [
            {
                "id": "branch1",
                "branch_point": {},
                "branches": {
                    "activated": {"participants": "all", "plays": [{"id": "act_play"}]},
                    "witness": {"participants": "all_others", "plays": [{"id": "act_play"}]},
                },
                "merge_point": None,
            }
        ]
        lib = self._lib(make_play("act_play", group_role="ac", activation_rate=0.15))
        issues = check_activation_void(arc_plays, lib)
        void = [i for i in issues if i.code == "ACTIVATION_VOID"]
        self.assertEqual(void, [])

    def test_no_void_when_rate_is_one(self):
        arc_plays = [{"id": "act_play"}]
        lib = self._lib(make_play("act_play", group_role="ac", activation_rate=1.0))
        issues = check_activation_void(arc_plays, lib)
        self.assertEqual(issues, [])


# ── CHECK_THRESHOLDS ──────────────────────────────────────────────────────────

class TestThresholdChecks(unittest.TestCase):
    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_invalid_condition_warns(self):
        thresholds = [{"id": "t1", "condition": "freeform gobbledygook"}]
        issues = check_thresholds(thresholds, [], {})
        self.assertTrue(any(i.code == "THRESHOLD_CONDITION_INVALID" for i in issues))

    def test_valid_play_count_condition(self):
        thresholds = [{"id": "t1", "condition": "play_count:phone_activation >= 777",
                       "triggers": {"play": "escalate", "phase": "e"}}]
        lib = self._lib(make_play("escalate", arc_codes=["e"]))
        issues = check_thresholds(thresholds, [], lib)
        invalid = [i for i in issues if i.code == "THRESHOLD_CONDITION_INVALID"]
        self.assertEqual(invalid, [])

    def test_valid_operator_signal_condition(self):
        thresholds = [{"id": "t1", "condition": "operator_signal:GO_NOW",
                       "triggers": {"play": "reveal", "phase": "c"}}]
        lib = self._lib(make_play("reveal", arc_codes=["c"]))
        issues = check_thresholds(thresholds, [], lib)
        invalid = [i for i in issues if i.code == "THRESHOLD_CONDITION_INVALID"]
        self.assertEqual(invalid, [])

    def test_missing_condition_errors(self):
        thresholds = [{"id": "t1", "triggers": {"play": "escalate"}}]  # no condition
        issues = check_thresholds(thresholds, [], {})
        self.assertTrue(any(i.code == "THRESHOLD_CONDITION_INVALID" for i in issues))

    def test_threshold_climax_timing_warns_when_all_climax_is_threshold(self):
        thresholds = [{"id": "t1", "condition": "operator_signal:GO",
                       "triggers": {"play": "climax_play", "phase": "c"}}]
        arc_plays = [{"id": "climax_play", "phase": "c"}]
        lib = self._lib(make_play("climax_play", arc_codes=["c"]))
        issues = check_thresholds(thresholds, arc_plays, lib)
        self.assertTrue(any(i.code == "THRESHOLD_CLIMAX_TIMING" for i in issues))


# ── CHECK_RECOVERY_BLOCKS ─────────────────────────────────────────────────────

class TestRecoveryBlockChecks(unittest.TestCase):
    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_recovery_lead_time_warns(self):
        arc_plays = [{"id": "parent", "phase": "e",
                      "recovery": {"cold": ["slow_recovery"]}}]
        lib = self._lib(
            make_play("parent", arc_codes=["e"]),
            make_play("slow_recovery", lead_time="1w", arc_codes=["e"]),  # 7d lead
        )
        issues = check_recovery_blocks(arc_plays, lib)
        self.assertTrue(any(i.code == "RECOVERY_LEAD_TIME" for i in issues))

    def test_recovery_immediate_lead_ok(self):
        arc_plays = [{"id": "parent", "phase": "e",
                      "recovery": {"cold": ["instant_rec"]}}]
        lib = self._lib(
            make_play("parent", arc_codes=["e"]),
            make_play("instant_rec", lead_time="0", arc_codes=["e"]),
        )
        issues = check_recovery_blocks(arc_plays, lib)
        lead_warns = [i for i in issues if i.code == "RECOVERY_LEAD_TIME"]
        self.assertEqual(lead_warns, [])

    def test_recovery_contraindicated_errors(self):
        arc_plays = [{"id": "parent", "phase": "e",
                      "recovery": {"cold": ["bad_rec"]}}]
        lib = self._lib(
            make_play("parent", arc_codes=["e"]),
            make_play("bad_rec", contraindicated_after=["parent"], arc_codes=["e"]),
        )
        issues = check_recovery_blocks(arc_plays, lib)
        self.assertTrue(any(i.code == "RECOVERY_CONTRAINDICATED" for i in issues))

    def test_operator_pause_sentinel_not_checked(self):
        arc_plays = [{"id": "parent", "phase": "e",
                      "recovery": {"distressed": ["OPERATOR_PAUSE"]}}]
        lib = self._lib(make_play("parent", arc_codes=["e"]))
        issues = check_recovery_blocks(arc_plays, lib)
        # OPERATOR_PAUSE should not produce UNKNOWN or other errors
        op_issues = [i for i in issues if "OPERATOR_PAUSE" in str(i)]
        self.assertEqual(op_issues, [])

    def test_all_four_modes_supported(self):
        arc_plays = [{"id": "parent", "phase": "e",
                      "recovery": {
                          "cold": ["rec1"], "confused": ["rec2"],
                          "distressed": ["rec3"], "over_engaged": ["rec4"],
                      }}]
        lib = self._lib(
            make_play("parent", arc_codes=["e"]),
            make_play("rec1", arc_codes=["e"]),
            make_play("rec2", arc_codes=["e"]),
            make_play("rec3", arc_codes=["e"]),
            make_play("rec4", arc_codes=["e"]),
        )
        issues = check_recovery_blocks(arc_plays, lib)
        mode_errors = [i for i in issues if i.code == "RECOVERY_PHASE"
                       and "unknown mode" in i.message]
        self.assertEqual(mode_errors, [])

    def test_unknown_recovery_mode_warns(self):
        arc_plays = [{"id": "parent", "phase": "e",
                      "recovery": {"weird_mode": ["rec1"]}}]
        lib = self._lib(make_play("parent"), make_play("rec1"))
        issues = check_recovery_blocks(arc_plays, lib)
        self.assertTrue(any("unknown mode" in i.message for i in issues))


# ── LINT_ARC_V2 INTEGRATION ───────────────────────────────────────────────────

class TestLintArcIntegration(unittest.TestCase):
    """Smoke tests for lint_arc end-to-end with synthetic arcs.
    These require plays_strips.json — skipped if not present."""

    def setUp(self):
        from pathlib import Path
        strips_file = Path(__file__).parent.parent / "plays_strips.json"
        if not strips_file.exists():
            self.skipTest("plays_strips.json not found — skipping v2 integration tests")

    def _v2_arc(self, **kwargs):
        data = {"arc_type": "investigation", "plays": [], **kwargs}
        return load_arc(data)

    def test_empty_arc_no_errors(self):
        arc = self._v2_arc()
        issues, plays = lint_arc(arc)
        errors = [i for i in issues if i.severity == "ERROR"]
        self.assertEqual(errors, [])

    def test_flat_list_through_v2_path(self):
        arc = load_arc(["knowledge_frontier_seed", "false_breakthrough"])
        issues, plays = lint_arc(arc)
        self.assertIsInstance(issues, list)
        self.assertIsInstance(plays, list)

    def test_v2_dict_with_pre_arc_smoke(self):
        data = {
            "arc_type": "investigation",
            "pre_arc": {"plays": [{"id": "knowledge_frontier_seed", "day": -14}]},
            "plays": [{"id": "false_breakthrough", "day": 0, "phase": "b"}],
        }
        arc = load_arc(data)
        issues, plays = lint_arc(arc)
        self.assertIsInstance(issues, list)


# ── GROUP_MODE TESTS ──────────────────────────────────────────────────────────

class TestGroupModeClimaxCoverage(unittest.TestCase):
    """group_mode:parallel on arc play elements suppresses CLIMAX_COVERAGE WARN
    for solo plays at climax in group arcs."""

    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_solo_climax_without_group_mode_warns(self):
        solo = make_play("reveal_play", beat="^", group_role="s")
        arc_plays = [{"id": "reveal_play", "phase": "c"}]
        issues = check_group_dynamics(arc_plays, self._lib(solo))
        codes = [i.code for i in issues]
        self.assertIn("CLIMAX_COVERAGE", codes)

    def test_parallel_group_mode_suppresses_climax_coverage_warn(self):
        solo = make_play("reveal_play", beat="^", group_role="s")
        arc_plays = [{"id": "reveal_play", "phase": "c", "group_mode": "parallel"}]
        issues = check_group_dynamics(arc_plays, self._lib(solo))
        codes = [i.code for i in issues]
        self.assertNotIn("CLIMAX_COVERAGE", codes)

    def test_ensemble_group_mode_suppresses_climax_coverage_warn(self):
        solo = make_play("reveal_play", beat="^", group_role="s")
        arc_plays = [{"id": "reveal_play", "phase": "c", "group_mode": "ensemble"}]
        issues = check_group_dynamics(arc_plays, self._lib(solo))
        codes = [i.code for i in issues]
        self.assertNotIn("CLIMAX_COVERAGE", codes)

    def test_group_mode_does_not_affect_non_climax_plays(self):
        solo = make_play("ramp_play", beat="/", group_role="s")
        arc_plays = [{"id": "ramp_play", "phase": "b", "group_mode": "parallel"}]
        issues = check_group_dynamics(arc_plays, self._lib(solo))
        codes = [i.code for i in issues]
        self.assertNotIn("CLIMAX_COVERAGE", codes)


# ── REGRESSION TESTS FOR CODE REVIEW FIXES ───────────────────────────────────

class TestThresholdRegexRegressions(unittest.TestCase):
    """Regression tests for threshold condition regex fix.
    engagement_rate must accept values >= 1.0, not just < 1.0."""

    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_engagement_rate_one_point_zero_is_valid(self):
        # Regression: regex `0?\.\\d+` rejected 1.0; fixed to `\\d+(\\.\\d+)?`
        thresholds = [{"id": "t1", "condition": "engagement_rate:play_x >= 1.0"}]
        lib = self._lib(make_play("play_x"))
        issues = check_thresholds(thresholds, [], lib)
        invalid = [i for i in issues if i.code == "THRESHOLD_CONDITION_INVALID"]
        self.assertEqual(invalid, [], "engagement_rate >= 1.0 should be valid")

    def test_engagement_rate_zero_point_five_is_valid(self):
        thresholds = [{"id": "t1", "condition": "engagement_rate:play_x >= 0.5"}]
        lib = self._lib(make_play("play_x"))
        issues = check_thresholds(thresholds, [], lib)
        invalid = [i for i in issues if i.code == "THRESHOLD_CONDITION_INVALID"]
        self.assertEqual(invalid, [])

    def test_engagement_rate_integer_is_valid(self):
        thresholds = [{"id": "t1", "condition": "engagement_rate:play_x >= 2"}]
        lib = self._lib(make_play("play_x"))
        issues = check_thresholds(thresholds, [], lib)
        invalid = [i for i in issues if i.code == "THRESHOLD_CONDITION_INVALID"]
        self.assertEqual(invalid, [])

    def test_engagement_rate_bad_format_warns(self):
        thresholds = [{"id": "t1", "condition": "engagement_rate:play_x > 0.5"}]
        lib = self._lib(make_play("play_x"))
        issues = check_thresholds(thresholds, [], lib)
        invalid = [i for i in issues if i.code == "THRESHOLD_CONDITION_INVALID"]
        self.assertEqual(len(invalid), 1)


class TestParallelTrackDayOrderRegression(unittest.TestCase):
    """Regression: start_day > end_day should produce an ERROR."""

    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_start_day_after_end_day_errors(self):
        # Regression: previously silently ignored, now errors
        tracks = [{"track_id": "ambient", "plays": [
            {"id": "play_x", "start_day": 10, "end_day": 5}
        ]}]
        lib = self._lib(make_play("play_x"))
        issues, _ = check_parallel_tracks(tracks, [], lib)
        errors = [i for i in issues if i.code == "PARALLEL_END_CONDITION" and i.severity == "ERROR"]
        self.assertEqual(len(errors), 1)
        self.assertIn("start_day", errors[0].message)

    def test_valid_day_range_no_error(self):
        tracks = [{"track_id": "ambient", "plays": [
            {"id": "play_x", "start_day": 0, "end_day": 10}
        ]}]
        lib = self._lib(make_play("play_x"))
        issues, _ = check_parallel_tracks(tracks, [], lib)
        order_errors = [i for i in issues
                        if i.code == "PARALLEL_END_CONDITION" and "start_day" in i.message]
        self.assertEqual(order_errors, [])

    def test_same_start_and_end_day_ok(self):
        tracks = [{"track_id": "ambient", "plays": [
            {"id": "play_x", "start_day": 5, "end_day": 5}
        ]}]
        lib = self._lib(make_play("play_x"))
        issues, _ = check_parallel_tracks(tracks, [], lib)
        order_errors = [i for i in issues
                        if i.code == "PARALLEL_END_CONDITION" and "start_day" in i.message]
        self.assertEqual(order_errors, [])


class TestActivationFatigueWindowRegression(unittest.TestCase):
    """Regression: ACTIVATION_FATIGUE should fire even with non-activated play between."""

    def _lib(self, *plays):
        return {p.id: p for p in plays}

    def test_consecutive_activations_still_fires(self):
        # Original behavior preserved: back-to-back activations warn
        arc_plays = [
            {"id": "p1", "phase": "e",
             "assignment": {"activated": ["alice"], "witnesses": ["bob"]}},
            {"id": "p2", "phase": "e",
             "assignment": {"activated": ["alice"], "witnesses": ["bob"]}},
        ]
        lib = self._lib(
            make_play("p1", group_role="ac"),
            make_play("p2", group_role="ac"),
        )
        issues = check_group_dynamics(arc_plays, lib)
        self.assertTrue(any(i.code == "ACTIVATION_FATIGUE" for i in issues))

    def test_activation_with_ensemble_between_fires(self):
        # Regression: previously reset prev_activated on non-activated plays;
        # now persists through ensemble plays until a rest beat.
        arc_plays = [
            {"id": "p1", "phase": "e",
             "assignment": {"activated": ["alice"], "witnesses": ["bob"]}},
            {"id": "ensemble_beat", "phase": "e"},  # no assignment
            {"id": "p3", "phase": "e",
             "assignment": {"activated": ["alice"], "witnesses": ["bob"]}},
        ]
        lib = self._lib(
            make_play("p1", group_role="ac"),
            make_play("ensemble_beat", group_role="e", beat="/"),
            make_play("p3", group_role="ac"),
        )
        issues = check_group_dynamics(arc_plays, lib)
        self.assertTrue(any(i.code == "ACTIVATION_FATIGUE" for i in issues))

    def test_rest_beat_clears_fatigue_window(self):
        # A rest beat ('-') should clear prev_activated
        arc_plays = [
            {"id": "p1", "phase": "e",
             "assignment": {"activated": ["alice"], "witnesses": ["bob"]}},
            {"id": "rest_beat", "phase": "e"},  # rest beat, no assignment
            {"id": "p3", "phase": "e",
             "assignment": {"activated": ["alice"], "witnesses": ["bob"]}},
        ]
        lib = self._lib(
            make_play("p1", group_role="ac"),
            make_play("rest_beat", group_role="e", beat="-"),
            make_play("p3", group_role="ac"),
        )
        issues = check_group_dynamics(arc_plays, lib)
        fatigue = [i for i in issues if i.code == "ACTIVATION_FATIGUE"]
        self.assertEqual(fatigue, [], "Rest beat should clear fatigue window")

    def test_different_participants_no_fatigue(self):
        # alice then bob — no overlap, no warning
        arc_plays = [
            {"id": "p1", "phase": "e",
             "assignment": {"activated": ["alice"], "witnesses": ["bob"]}},
            {"id": "p2", "phase": "e",
             "assignment": {"activated": ["bob"], "witnesses": ["alice"]}},
        ]
        lib = self._lib(
            make_play("p1", group_role="ac"),
            make_play("p2", group_role="ac"),
        )
        issues = check_group_dynamics(arc_plays, lib)
        fatigue = [i for i in issues if i.code == "ACTIVATION_FATIGUE"]
        self.assertEqual(fatigue, [])


if __name__ == "__main__":
    unittest.main()
