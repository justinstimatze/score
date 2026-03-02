#!/usr/bin/env python3
"""
arc_linter.py

Deterministic constraint validator for immersive experience arcs.
Accepts flat play lists and structured arc dicts (with pre_arc,
parallel_tracks, thresholds, branch/merge blocks, group dynamics).

Usage:
  python arc_linter.py play1 play2 play3 ...
  python arc_linter.py --file arc.json
  python arc_linter.py --file arc.json --phases "p,b,e,e,c"
  python arc_linter.py --file arc.json --days "0,0,3,7,14,21"

Arc file formats:
  flat list:   ["play1", "play2", ...]
  flat list:   [{"id": "play1", "day": 0, "phase": "p"}, ...]
  structured:  {"arc_type": "investigation", "plays": [...], "pre_arc": {...}, ...}

Exit code: 0 = clean, 1 = errors present, 2 = file not found
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

STRIPS_FILE = Path(__file__).parent / "plays_strips.json"

# ── LEAD TIME DECODE ─────────────────────────────────────────────────────────

LEAD_TIME_DAYS = {
    "0": 0, "sd": 0, "1d": 1, "3d": 3, "1w": 7,
    "2w": 14, "4w": 28, "8w": 56,
}

def lead_days(code: str) -> int:
    return LEAD_TIME_DAYS.get(code, 0)


# ── ARC PHASE ORDER ───────────────────────────────────────────────────────────

PHASE_ORDER = {"p": 0, "b": 1, "e": 2, "t": 3, "c": 4, "r": 4, "d": 5}

PHASE_NAMES = {
    "p": "pre/open", "b": "build", "e": "escalate",
    "t": "threshold", "c": "climax", "r": "revelation",
    "d": "denouement", "*": "any", "R": "reinforcement",
}

CLIMAX_PHASES = {"c", "r"}

# ── STRIP PARSER ──────────────────────────────────────────────────────────────

@dataclass
class PlayStrip:
    id: str
    cost: str = ""
    autonomy: str = ""
    lead_time: str = ""
    intensity: str = ""
    mechanisms: list[str] = field(default_factory=list)
    arc_codes: list[str] = field(default_factory=list)
    beat: str = ""
    agency_type: str = ""
    frame_req: str = ""
    agency_demand: str = ""
    landscape: str = ""
    legacy: str = ""
    detection: str = ""
    reversibility: str = ""
    permission_mode: str = "S"
    permission_grant: str = ""
    synergizes: list[str] = field(default_factory=list)
    contraindicated_after: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    # v2 group fields
    group_role: str = "s"          # s=solo e=ensemble ac=activated am=ambient lo=lottery
    social_modifier: str = "neut"  # amp dist req neut
    participation_tier: str = "U"  # P A E U
    parallel_capable: bool = False
    activation_rate: float = 1.0
    witness_mechanisms: list[str] = field(default_factory=list)

    @property
    def lead_days(self) -> int:
        return lead_days(self.lead_time)

    @property
    def persona_bound(self) -> bool:
        """N1: True if play efficacy depends on a specific operator identity (AUTONOMY includes pb)."""
        return "pb" in self.autonomy

    @property
    def intensity_int(self) -> int:
        try:
            return int(self.intensity)
        except (ValueError, TypeError):
            return 0

    @property
    def arc_fits_any(self) -> bool:
        return "*" in self.arc_codes

    def arc_fits_phase(self, phase_code: str) -> bool:
        return self.arc_fits_any or phase_code in self.arc_codes

    @property
    def is_ensemble(self) -> bool:
        return self.group_role == "e"

    @property
    def is_lottery(self) -> bool:
        return self.group_role == "lo"

    @property
    def is_activated(self) -> bool:
        return self.group_role == "ac"


def parse_strip(raw: str) -> PlayStrip | None:
    lines = [l.strip() for l in raw.strip().split("\n") if l.strip()]
    if not lines:
        return None

    # L1: @id C·U·LT·I
    m = re.match(r"@(\S+)\s+(.+)", lines[0])
    if not m:
        return None
    pid = m.group(1)
    l1_parts = m.group(2).split("·")
    cost = l1_parts[0] if len(l1_parts) > 0 else ""
    autonomy = l1_parts[1] if len(l1_parts) > 1 else ""
    lead_time = l1_parts[2] if len(l1_parts) > 2 else ""
    intensity = l1_parts[3] if len(l1_parts) > 3 else ""

    play = PlayStrip(id=pid, cost=cost, autonomy=autonomy,
                     lead_time=lead_time, intensity=intensity)

    if len(lines) < 2:
        return play

    # L2: #M·M [arc] bf
    l2 = lines[1]
    arc_m = re.search(r"\[([^\]]+)\]", l2)
    if arc_m:
        arc_str = arc_m.group(1)
        play.arc_codes = list(arc_str)
        after = l2[arc_m.end():].strip()
        play.beat = after[0] if after else ""
        mech_part = l2[:arc_m.start()].lstrip("#").strip()
        play.mechanisms = [x.strip() for x in mech_part.split("·") if x.strip()]

    if len(lines) < 3:
        return play

    # L3: AT·FR·AD·LA·LG·DE·RV
    l3_parts = lines[2].split("·")
    if len(l3_parts) >= 7:
        play.agency_type = l3_parts[0]
        play.frame_req   = l3_parts[1]
        play.agency_demand = l3_parts[2]
        play.landscape   = l3_parts[3]
        play.legacy      = l3_parts[4]
        play.detection   = l3_parts[5]
        play.reversibility = l3_parts[6]

    # L4+ labeled fields
    for line in lines[3:]:
        if line.startswith("prm:"):
            prm = line[4:]
            if "→" in prm:
                mode, grant = prm.split("→", 1)
                play.permission_mode = mode.strip()
                play.permission_grant = grant.strip()
            else:
                play.permission_mode = prm.strip()
        elif line.startswith("syn:"):
            play.synergizes = [x.strip() for x in line[4:].split("·") if x.strip()]
        elif line.startswith("!ctr:"):
            play.contraindicated_after = [x.strip() for x in line[5:].split("·") if x.strip()]
        elif line.startswith("req:"):
            play.requires = [x.strip() for x in line[4:].split("·") if x.strip()]
        elif line.startswith("grp:"):
            # grp:GROUP_ROLE·SOCIAL_MODIFIER·TIER·PC·AR
            parts = line[4:].split("·")
            if len(parts) >= 1:
                play.group_role = parts[0]
            if len(parts) >= 2:
                play.social_modifier = parts[1]
            if len(parts) >= 3:
                play.participation_tier = parts[2]
            if len(parts) >= 4:
                play.parallel_capable = parts[3] == "1"
            if len(parts) >= 5:
                try:
                    play.activation_rate = float(parts[4])
                except ValueError:
                    pass
        elif line.startswith("wit:"):
            play.witness_mechanisms = [x.strip() for x in line[4:].split("·") if x.strip()]

    return play


def load_strips() -> dict[str, PlayStrip]:
    data = json.loads(STRIPS_FILE.read_text())
    result = {}
    for entry in data:
        strip = parse_strip(entry["strip"])
        if strip:
            result[strip.id] = strip
    return result


# ── ARC V2 STRUCTURE ──────────────────────────────────────────────────────────

def is_branch_block(element: dict) -> bool:
    """Discriminate branch/merge blocks from play elements."""
    return isinstance(element, dict) and "branch_point" in element

def is_play_element(element: dict) -> bool:
    return isinstance(element, dict) and "id" in element and "branch_point" not in element


@dataclass
class Arc:
    arc_type: str = "investigation"
    audience_scale: str = "intimate"  # intimate | mass
    group: dict = field(default_factory=dict)
    pre_arc_plays: list[dict] = field(default_factory=list)
    pre_arc_note: str = ""
    parallel_tracks: list[dict] = field(default_factory=list)
    thresholds: list[dict] = field(default_factory=list)
    plays: list[dict] = field(default_factory=list)
    early_exit: str = ""   # N2: play ID to deliver if arc must close before designed climax


def load_arc(data: list | dict) -> Arc:
    """Convert any arc format to Arc."""
    arc = Arc()
    if isinstance(data, list):
        arc.plays = [
            {"id": item} if isinstance(item, str) else item
            for item in data
        ]
        return arc

    arc.arc_type = data.get("arc_type", "investigation")
    arc.audience_scale = data.get("audience_scale", "intimate")
    arc.group = data.get("group", {})

    pre_arc = data.get("pre_arc", {})
    if pre_arc:
        arc.pre_arc_plays = pre_arc.get("plays", [])
        arc.pre_arc_note = pre_arc.get("note", "")

    arc.parallel_tracks = data.get("parallel_tracks", [])
    arc.thresholds = data.get("thresholds", [])
    arc.plays = data.get("plays", [])
    arc.early_exit = data.get("early_exit", "")
    return arc


def _extract_main_sequence(arc_plays: list[dict]) -> list[dict]:
    """
    Flatten arc plays for sequential checks.
    Branch/merge blocks contribute their merge_point play at their position.
    """
    result = []
    for element in arc_plays:
        if is_branch_block(element):
            mp = element.get("merge_point")
            if mp and isinstance(mp, dict) and mp.get("play"):
                result.append({
                    "id": mp["play"],
                    "day": element.get("day"),
                    "phase": element.get("phase"),
                })
        elif is_play_element(element):
            result.append(element)
    return result


# ── ISSUE TYPES ───────────────────────────────────────────────────────────────

@dataclass
class Issue:
    severity: str    # ERROR | WARN | INFO
    position: int    # 0-indexed play position (-1 = arc-level)
    play_id: str
    code: str
    message: str

    def __str__(self):
        pos = f"[{self.position + 1}]" if self.position >= 0 else "[arc]"
        return f"  {pos} {self.play_id} — {self.message}"


# ── V1 CHECKS (unchanged signature, backward compatible) ─────────────────────

def check_unknown_plays(
    play_ids: list[str], library: dict[str, PlayStrip]
) -> list[Issue]:
    issues = []
    for i, pid in enumerate(play_ids):
        if pid not in library:
            issues.append(Issue("ERROR", i, pid, "UNKNOWN",
                                f"play '{pid}' not found in library"))
    return issues


def check_contraindicated(
    plays: list[PlayStrip], positions: list[int]
) -> list[Issue]:
    issues = []
    for i, play in enumerate(plays):
        for j in range(i):
            prior = plays[j]
            if prior.id in play.contraindicated_after:
                issues.append(Issue("ERROR", positions[i], play.id, "CONTRAINDICATED",
                    f"CONTRAINDICATED_AFTER {prior.id!r} (at position {positions[j]+1})"))
    return issues


def check_frame_requirement(plays: list[PlayStrip], positions: list[int]) -> list[Issue]:
    issues = []
    frame = "n"

    for i, play in enumerate(plays):
        fr = play.frame_req
        if fr in ("*", ""):
            pass
        elif fr == "n":
            pass
        elif fr == "q":
            if frame == "n":
                issues.append(Issue("WARN", positions[i], play.id, "FRAME_REQ",
                    f"FRAME_REQUIREMENT=primed but frame is still naive — needs prior build/ramp"))
        elif fr == "m":
            if frame != "m":
                issues.append(Issue("ERROR", positions[i], play.id, "FRAME_REQ",
                    f"FRAME_REQUIREMENT=meta but frame not yet meta — only valid post-reveal"))
        elif fr in ("nq", "nm", "qm"):
            pass

        if play.beat in ("/", "-") and any(c in play.arc_codes for c in ["b", "e", "t"]):
            if frame == "n":
                frame = "q"
        if play.beat == ">" and any(c in play.arc_codes for c in ["c", "r", "d"]):
            frame = "m"

    return issues


def check_permission_sequenced(
    plays: list[PlayStrip],
    positions: list[int],
    initial_grants: set[str] | None = None,
) -> list[Issue]:
    """
    prm:Q plays require prior arc investment (at least 2 preceding plays).
    prm:Q→grant plays require a prior play that produced that grant.
    initial_grants: grants accumulated before this sequence (e.g. from pre_arc plays).
    """
    issues = []
    accumulated_grants: set[str] = set(initial_grants or [])

    for i, play in enumerate(plays):
        mode = play.permission_mode
        grant_needed = play.permission_grant

        if mode == "Q":
            if i < 2:
                issues.append(Issue("WARN", positions[i], play.id, "PERMISSION",
                    f"prm:Q (sequenced) — appears too early (position {i+1}); "
                    f"needs prior arc investment"))
            if grant_needed and grant_needed not in accumulated_grants:
                issues.append(Issue("WARN", positions[i], play.id, "PERMISSION",
                    f"prm:Q→{grant_needed} requires prior grant '{grant_needed}' — "
                    f"not yet produced by preceding plays"))

        if play.permission_grant:
            accumulated_grants.add(play.permission_grant)

    return issues


def check_lead_time(
    plays: list[PlayStrip],
    positions: list[int],
    days: list[int | None],
) -> list[Issue]:
    if not any(d is not None for d in days):
        return []
    issues = []
    for i, play in enumerate(plays):
        day = days[i]
        if day is None:
            continue
        required = play.lead_days
        # Pre-arc plays have negative days; use abs value
        effective_day = abs(day) if day < 0 else day
        if required > effective_day:
            issues.append(Issue("ERROR", positions[i], play.id, "LEAD_TIME",
                f"LEAD_TIME requires {required}d setup but scheduled on day {day} — "
                f"only {effective_day}d available"))
    return issues


def check_rhythm(plays: list[PlayStrip], positions: list[int]) -> list[Issue]:
    issues = []
    beats = [p.beat for p in plays]
    n = len(beats)
    scored_beats = [b for b in beats if b != "~"]
    n_scored = len(scored_beats)

    run = 0
    for i, b in enumerate(beats):
        if b == "^":
            run += 1
            if run >= 5:
                issues.append(Issue("WARN", positions[i], plays[i].id, "RHYTHM",
                    f"5th consecutive spike — participant fatigue risk; insert ramp or hold"))
        elif b != "~":
            run = 0

    if n_scored > 6 and "-" not in scored_beats:
        issues.append(Issue("WARN", -1, "arc", "RHYTHM",
            "No hold beat anywhere in arc — no dwell space for participant processing; "
            "add at least one hold"))

    if n >= 4:
        last_four = beats[-4:]
        if "d" in [c for p in plays[-4:] for c in p.arc_codes] and "-" not in last_four:
            issues.append(Issue("INFO", -1, "arc", "RHYTHM",
                "Denouement plays present but no rest beat preceding them — "
                "consider a rest or transition to close the arc"))

    if n_scored > 8 and ">" not in scored_beats:
        issues.append(Issue("INFO", -1, "arc", "RHYTHM",
            f"No transition beat in {n_scored}-play arc — arcs this long usually need at least "
            f"one structural gear change"))

    spike_count = scored_beats.count("^")
    if n_scored > 6 and spike_count < 2:
        issues.append(Issue("WARN", -1, "arc", "RHYTHM",
            f"Only {spike_count} spike beat(s) in {n_scored}-play arc — low cathartic density; "
            f"consider adding at least one high-intensity beat"))

    for i in range(1, n):
        if beats[i-1] == "_" and beats[i] == "^":
            issues.append(Issue("WARN", positions[i], plays[i].id, "RHYTHM",
                "Spike immediately follows rest — abrupt re-escalation; "
                "consider a ramp between them"))

    return issues


def check_detection_accumulation(
    plays: list[PlayStrip],
    positions: list[int],
    days: list[int | None] | None = None,
    extra_day_risks: dict[int, float] | None = None,
) -> list[Issue]:
    """
    Flag windows where detection risk accumulates.
    Detection codes: i=immediate s=short m=medium l=long n=never_solo
    Risk weights: i=4 s=3 m=2 l=1 n=0

    When days are provided, use a 7-calendar-day sliding window (day-indexed).
    When days are not provided, use a 4-play positional sliding window.
    extra_day_risks: additional risk contributions from parallel tracks, keyed by day.
    """
    WEIGHTS = {"i": 4, "s": 3, "m": 2, "l": 1, "n": 0, "S": 1, "D": 1, "t": 0, "?": 1}
    issues = []
    risk = [WEIGHTS.get(p.detection, 1) for p in plays]

    has_days = days and any(d is not None for d in days)

    if has_days:
        # Build day-indexed risk map
        day_risk: dict[int, float] = {}
        for i, play in enumerate(plays):
            day = days[i]
            if day is None:
                continue
            day_risk[day] = day_risk.get(day, 0) + risk[i]

        # Add parallel track risks
        if extra_day_risks:
            for day, r in extra_day_risks.items():
                day_risk[day] = day_risk.get(day, 0) + r

        if not day_risk:
            return issues

        # 7-day sliding window on calendar days
        all_days = sorted(day_risk.keys())
        DAY_WINDOW = 7
        THRESHOLD = 10
        for i, start_day in enumerate(all_days):
            window_days = [d for d in all_days if start_day <= d < start_day + DAY_WINDOW]
            window_risk = sum(day_risk[d] for d in window_days)
            if window_risk >= THRESHOLD:
                # Find the main-arc play closest to end of window
                end_day = window_days[-1]
                play_idx = None
                for j, play in enumerate(plays):
                    if days[j] is not None and days[j] == end_day:
                        play_idx = j
                        break
                if play_idx is None:
                    play_idx = len(plays) - 1
                issues.append(Issue("WARN", positions[play_idx], plays[play_idx].id,
                    "DETECTION",
                    f"High detection accumulation in day window {start_day}–{start_day+DAY_WINDOW-1} "
                    f"(risk={window_risk:.0f}/{THRESHOLD}) — "
                    f"consider spreading high-detection plays or inserting a low-detection hold"))
                # Skip forward past this window to avoid duplicate flags
                break  # flag first violation only; operator can re-lint after adjusting

    else:
        # Positional 4-play sliding window (no day fields provided)
        WINDOW = 4
        THRESHOLD = 10
        for i in range(len(risk) - WINDOW + 1):
            window_risk = sum(risk[i:i+WINDOW])
            if window_risk >= THRESHOLD:
                issues.append(Issue("WARN", positions[i + WINDOW - 1],
                    plays[i + WINDOW - 1].id, "DETECTION",
                    f"High detection accumulation in plays {positions[i]+1}–{positions[i+WINDOW-1]+1} "
                    f"(risk={window_risk}/{THRESHOLD}) — "
                    f"consider spreading high-detection plays or inserting a low-detection hold"))

    return issues


def check_reversibility(plays: list[PlayStrip], positions: list[int]) -> list[Issue]:
    issues = []
    n = len(plays)
    quarter = max(2, n // 4)

    for i, play in enumerate(plays):
        if play.reversibility == "x":
            if i < quarter:
                issues.append(Issue("WARN", positions[i], play.id, "REVERSIBILITY",
                    f"Irreversible play in first quarter of arc (position {i+1}/{n}) — "
                    f"participant trajectory not yet established"))

    return issues


def check_arc_fit(
    plays: list[PlayStrip],
    positions: list[int],
    declared_phases: list[str | None],
) -> list[Issue]:
    if not any(p is not None for p in declared_phases):
        return []
    issues = []
    for i, play in enumerate(plays):
        phase = declared_phases[i]
        if phase is None:
            continue
        if not play.arc_fits_phase(phase):
            fits = "·".join(PHASE_NAMES.get(c, c) for c in play.arc_codes) or "none"
            issues.append(Issue("WARN", positions[i], play.id, "ARC_FIT",
                f"Declared phase={phase!r} but play fits [{fits}]"))
    return issues


def check_world_mark_timing(plays: list[PlayStrip], positions: list[int]) -> list[Issue]:
    issues = []
    n = len(plays)
    for i, play in enumerate(plays):
        if "w" in play.legacy and i > n * 0.6 and play.lead_days < 14:
            issues.append(Issue("WARN", positions[i], play.id, "LEGACY_SCOPE",
                f"world_mark play appearing in last 40% of arc with <2w lead time — "
                f"may not have time to establish before arc close"))
    return issues


def check_landscape_balance(
    plays: list[PlayStrip],
    positions: list[int],
    arc_type: str,
) -> list[Issue]:
    """
    L1: Warn if arc operates entirely on the identity plane with no action-plane plays.
    An arc with nothing for the participant to do, produce, or complete is at risk of
    ideology vacancy regardless of correct beat shape.
    Suppressed for grief/memorial arc types (purely identity-plane arcs can be valid there).
    """
    SUPPRESS_FOR = {"grief", "memorial"}
    if arc_type in SUPPRESS_FOR:
        return []
    if not plays:
        return []
    # LANDSCAPE field: 'a'=action, 'i'=identity, '+'=both
    action_plays = [p for p in plays if p.landscape in ("a", "+")]
    if not action_plays:
        identity_count = sum(1 for p in plays if p.landscape == "i")
        if identity_count > 0:
            return [Issue("WARN", -1, "arc", "LANDSCAPE",
                "No action-plane plays in arc (all LANDSCAPE:identity) — "
                "arc has nothing for the participant to do, produce, or complete; "
                "ideology vacancy risk even if beat shape is correct. "
                "Initiation arcs are highest risk. Add at least one LANDSCAPE:action play.")]
    return []


def check_early_exit(arc: "Arc", library: dict[str, "PlayStrip"]) -> list[Issue]:
    """
    L2: Initiation arcs require an early_exit play — the play ID to deliver if the
    operator must close the arc before the designed climax.
    Latitude's failure was partly that there was no exit before graduation_ritual at day 120.
    """
    if arc.arc_type != "initiation":
        return []
    if arc.early_exit:
        # Validate the referenced play exists
        if arc.early_exit not in library:
            return [Issue("WARN", -1, "arc", "EARLY_EXIT",
                f"early_exit play '{arc.early_exit}' not found in library")]
        return []
    return [Issue("WARN", -1, "arc", "EARLY_EXIT",
        "Initiation arc has no early_exit play defined — "
        "arc has no graceful short-circuit if operator needs to close before climax. "
        "Add early_exit: <play_id> (a hold or denouement beat) to the arc JSON.")]


def check_participation_rate(
    arc_plays: list[dict],
    library: dict[str, "PlayStrip"],
    threshold: float = 0.7,
) -> list[Issue]:
    """
    L3: For ensemble spike beats with expected_participation set, warn if participation
    is below threshold — the arc's cathartic beat may be unavailable to a significant
    portion of the group.
    For lottery spike beats, emit INFO noting the experiential bifurcation (low
    expected_participation is by design for lottery beats).
    expected_participation is a float 0.0-1.0 on the arc play element, not in the library.
    """
    issues: list[Issue] = []
    for i, element in enumerate(arc_plays):
        if not is_play_element(element):
            continue
        pid = element.get("id", "")
        ep = element.get("expected_participation")
        if ep is None:
            continue
        strip = library.get(pid)
        if not strip:
            continue
        effective_role = element.get("group_mode", strip.group_role)
        if strip.beat == "^" and effective_role == "e" and ep < threshold:
            pct = int(ep * 100)
            issues.append(Issue("WARN", i, pid, "LOW_COVERAGE_RISK",
                f"Spike beat '{pid}' (ensemble) has expected_participation={ep:.0%} — "
                f"cathartic beat may be unavailable to {100-pct}% of group; "
                f"consider lottery mechanic, parallel spike, or lower-barrier alternative"))
        elif strip.beat == "^" and effective_role == "lo":
            pct = int(ep * 100)
            issues.append(Issue("INFO", i, pid, "LOTTERY_BIFURCATION",
                f"Spike beat '{pid}' (lottery) has expected_participation={ep:.0%} — "
                f"arc bifurcates: ~{pct}% of participants receive the full spike path, "
                f"~{100-pct}% experience the arc without it; design both paths intentionally"))
    return issues


def check_requires_consistency(plays: list[PlayStrip], positions: list[int]) -> list[Issue]:
    issues = []
    needs_confederate = [p for p in plays if "cnf" in p.requires or p.autonomy in ("C", "CA", "CR")]
    needs_location = [p for p in plays if "loc" in p.requires]

    if len(needs_confederate) > 1:
        issues.append(Issue("INFO", -1, "arc", "REQUIRES",
            f"{len(needs_confederate)} plays require a confederate — "
            f"confirm same person is available for full arc duration"))

    if len(needs_location) > 1:
        issues.append(Issue("INFO", -1, "arc", "REQUIRES",
            f"{len(needs_location)} plays require specific location access — "
            f"confirm logistics are coordinated"))

    return issues


# ── V2 CHECKS ─────────────────────────────────────────────────────────────────

def check_pre_arc(
    pre_arc_plays: list[dict],
    library: dict[str, PlayStrip],
) -> tuple[list[Issue], set[str]]:
    """
    Lint pre-arc infrastructure plays.
    Returns (issues, grants_accumulated).
    Checks: LEAD_TIME only. No FRAME_REQ, no beat sequence.
    Detection accumulation tracked separately (day-indexed from negative days).
    """
    issues: list[Issue] = []
    grants: set[str] = set()

    resolved: list[PlayStrip] = []
    days: list[int | None] = []

    for entry in pre_arc_plays:
        pid = entry.get("id", "")
        day = entry.get("day")
        if pid not in library:
            issues.append(Issue("ERROR", -1, pid, "UNKNOWN",
                f"pre_arc play '{pid}' not found in library"))
            continue
        strip = library[pid]
        resolved.append(strip)
        days.append(day)
        if strip.permission_grant:
            grants.add(strip.permission_grant)

    positions = list(range(len(resolved)))
    issues.extend(check_lead_time(resolved, positions, days))

    # Detection accumulation for pre-arc window
    if resolved:
        issues.extend(check_detection_accumulation(resolved, positions, days))

    return issues, grants


def check_parallel_tracks(
    parallel_tracks: list[dict],
    main_plays: list[dict],
    library: dict[str, PlayStrip],
) -> tuple[list[Issue], dict[int, float]]:
    """
    Lint parallel/ambient track plays.
    Returns (issues, day_risk_map) where day_risk_map can be merged with main-arc detection.
    """
    DETECTION_WEIGHTS = {"i": 4, "s": 3, "m": 2, "l": 1, "n": 0, "S": 1, "D": 1, "t": 0, "?": 1}
    issues: list[Issue] = []
    day_risk: dict[int, float] = {}

    # Build main-arc day → high-detection plays map
    high_det_days: set[int] = set()
    for entry in main_plays:
        if is_branch_block(entry):
            continue
        pid = entry.get("id", "")
        day = entry.get("day")
        if day is not None and pid in library:
            strip = library[pid]
            if strip.detection in ("i", "s"):
                high_det_days.add(day)

    for track in parallel_tracks:
        track_id = track.get("track_id", "?")
        for entry in track.get("plays", []):
            pid = entry.get("id", "")
            start_day = entry.get("start_day")
            end_day = entry.get("end_day")

            if pid not in library:
                issues.append(Issue("ERROR", -1, pid, "UNKNOWN",
                    f"parallel track '{track_id}' play '{pid}' not found in library"))
                continue

            strip = library[pid]

            # PARALLEL_END_CONDITION: missing end_day
            if end_day is None:
                issues.append(Issue("WARN", -1, pid, "PARALLEL_END_CONDITION",
                    f"parallel track '{track_id}': '{pid}' has no end_day — "
                    f"ambient plays must have a designed endpoint"))

            # PARALLEL_DAY_ORDER: start_day must not exceed end_day
            if start_day is not None and end_day is not None and start_day > end_day:
                issues.append(Issue("ERROR", -1, pid, "PARALLEL_END_CONDITION",
                    f"parallel track '{track_id}': '{pid}' has start_day ({start_day}) > "
                    f"end_day ({end_day}) — invalid day range"))
                continue

            # PARALLEL_LEAD_TIME
            if start_day is not None:
                required = strip.lead_days
                effective_day = abs(start_day) if start_day < 0 else start_day
                if required > effective_day:
                    issues.append(Issue("ERROR", -1, pid, "PARALLEL_LEAD_TIME",
                        f"parallel track '{track_id}': '{pid}' needs {required}d lead "
                        f"but scheduled on day {start_day}"))

            # PARALLEL_OVERLAP_WITH_MAIN (high-detection collision)
            if start_day is not None and end_day is not None:
                overlap_days = high_det_days & set(range(start_day, end_day + 1))
                if overlap_days:
                    issues.append(Issue("INFO", -1, pid, "PARALLEL_OVERLAP_WITH_MAIN",
                        f"parallel track '{track_id}': '{pid}' overlaps with "
                        f"high-detection main-arc play(s) on day(s) {sorted(overlap_days)} — "
                        f"review combined detection accumulation"))

            # Accumulate detection risk for each day the play is active
            if start_day is not None and end_day is not None:
                w = DETECTION_WEIGHTS.get(strip.detection, 1)
                for d in range(start_day, end_day + 1):
                    day_risk[d] = day_risk.get(d, 0) + w / max(1, end_day - start_day + 1)

    return issues, day_risk


def check_branch_merge_blocks(
    arc_plays: list[dict],
    library: dict[str, PlayStrip],
) -> list[Issue]:
    """
    Lint branch/merge structural elements.
    Checks: MERGE_DESIGNED, WITNESS_VOID, MERGE_BEAT, CASCADE_FATIGUE,
            PERMANENT_DIVERGENCE_COVERAGE.
    Also lints branch plays within each branch (LEAD_TIME, CONTRAINDICATED).
    """
    issues: list[Issue] = []
    activation_counts: dict[str, int] = {}  # selector → count (for CASCADE_FATIGUE)

    for i, element in enumerate(arc_plays):
        if not is_branch_block(element):
            continue

        block_id = element.get("id", f"branch_{i}")
        block_day = element.get("day")

        # MERGE_DESIGNED: merge_point key must be present (null is explicit, missing is error)
        if "merge_point" not in element:
            issues.append(Issue("ERROR", i, block_id, "MERGE_DESIGNED",
                f"branch/merge block '{block_id}' has no merge_point key — "
                f"set merge_point to a play id or null for permanent divergence"))

        branches = element.get("branches", {})

        # WITNESS_VOID: if any branch is 'activated', there should be a 'witness' branch
        has_activated = "activated" in branches
        has_witness = "witness" in branches
        if has_activated and not has_witness:
            issues.append(Issue("WARN", i, block_id, "WITNESS_VOID",
                f"branch/merge block '{block_id}' has an 'activated' branch but no 'witness' branch — "
                f"non-activated participants' simultaneous experience is undesigned"))

        # Lint plays within each branch
        for branch_name, branch_data in branches.items():
            if not isinstance(branch_data, dict):
                continue
            branch_plays = branch_data.get("plays", [])
            branch_play_ids = [p.get("id", "") for p in branch_plays if isinstance(p, dict)]
            branch_strips = [library[pid] for pid in branch_play_ids if pid in library]
            branch_positions = list(range(len(branch_strips)))

            # LEAD_TIME within branch
            branch_days = [block_day] * len(branch_strips)
            issues.extend(check_lead_time(branch_strips, branch_positions, branch_days))

            # CONTRAINDICATED within branch
            issues.extend(check_contraindicated(branch_strips, branch_positions))

        # MERGE_BEAT: merge_point play should be a spike or transition, not hold/rest
        merge_point = element.get("merge_point")
        if merge_point and isinstance(merge_point, dict):
            mp_play_id = merge_point.get("play")
            if mp_play_id and mp_play_id in library:
                mp_strip = library[mp_play_id]
                if mp_strip.beat in ("_", "-"):
                    issues.append(Issue("WARN", i, block_id, "MERGE_BEAT",
                        f"branch/merge block '{block_id}': merge_point play '{mp_play_id}' "
                        f"has beat '{mp_strip.beat}' — reintegration of asymmetric-context "
                        f"participants should be a spike or transition, not a hold/rest"))

        # PERMANENT_DIVERGENCE_COVERAGE: merge_point: null
        if "merge_point" in element and element["merge_point"] is None:
            # Find arc's last main-arc play day
            last_day = None
            for el in arc_plays:
                if is_play_element(el) and el.get("day") is not None:
                    last_day = el["day"]
            # Find divergent branch's last play day
            all_branch_plays_flat = []
            for bd in branches.values():
                if isinstance(bd, dict):
                    all_branch_plays_flat.extend(bd.get("plays", []))
            divergent_last_day = block_day  # fallback
            if all_branch_plays_flat:
                for bp in all_branch_plays_flat:
                    if isinstance(bp, dict) and bp.get("day") is not None:
                        divergent_last_day = bp["day"]
            if last_day is not None and divergent_last_day is not None:
                gap = last_day - divergent_last_day
                if gap > 7:
                    issues.append(Issue("WARN", i, block_id, "PERMANENT_DIVERGENCE_COVERAGE",
                        f"branch/merge block '{block_id}' has merge_point: null (permanent divergence) "
                        f"but divergent branch ends {gap}d before arc's last play (day {last_day}) — "
                        f"confirm the divergent participant's arc is fully designed to arc end"))
            else:
                issues.append(Issue("INFO", i, block_id, "PERMANENT_DIVERGENCE_COVERAGE",
                    f"branch/merge block '{block_id}' has merge_point: null (permanent divergence) — "
                    f"confirm the divergent participant's arc is fully designed through the arc's end"))

        # CASCADE_FATIGUE: track activation selectors
        activated_branch = branches.get("activated", {})
        if isinstance(activated_branch, dict):
            selector = activated_branch.get("participants", "unknown")
            activation_counts[selector] = activation_counts.get(selector, 0) + 1
            if activation_counts[selector] > 2:
                issues.append(Issue("WARN", i, block_id, "CASCADE_FATIGUE",
                    f"branch/merge block '{block_id}': selector '{selector}' has been "
                    f"activated {activation_counts[selector]} times — "
                    f"CASCADE_FATIGUE risk; insert a hold beat before activating again"))

    return issues


def check_group_dynamics(
    arc_plays: list[dict],
    library: dict[str, PlayStrip],
    arc: Arc | None = None,
) -> list[Issue]:
    """
    Lint group dynamics constraints.
    Checks: CLIMAX_COVERAGE, ACTIVATION_FATIGUE, WITNESS_DENSITY, DIST_PLAY_CONTEXT.
    Note: GROUP_FLOOR requires multi-profile scoring — see arc_matchmaker.py.
    """
    issues: list[Issue] = []
    profiles = set()
    if arc and arc.group.get("profiles"):
        profiles = set(p.split("/")[-1].replace(".json", "")
                       for p in arc.group.get("profiles", []))

    prev_activated: set[str] = set()

    for i, element in enumerate(arc_plays):
        if is_branch_block(element):
            prev_activated = set()
            continue
        if not is_play_element(element):
            continue

        pid = element.get("id", "")
        phase = element.get("phase", "")
        assignment = element.get("assignment") or {}
        activated_set = set(assignment.get("activated", []))
        witnesses_set = set(assignment.get("witnesses", []))

        strip = library.get(pid)
        if not strip:
            continue

        # CLIMAX_COVERAGE: climax/revelation plays must be ensemble or cover all profiles
        # group_mode on the arc element overrides the strip's GROUP_ROLE for this check:
        #   "parallel" — solo mechanics, runs simultaneously to every participant (covers all)
        #   "ensemble" — treat as ensemble regardless of strip GROUP_ROLE
        group_mode = element.get("group_mode", "")
        effective_role = strip.group_role
        if group_mode == "parallel":
            effective_role = "parallel"   # bypasses all CLIMAX_COVERAGE warnings
        elif group_mode == "ensemble":
            effective_role = "e"

        if phase in CLIMAX_PHASES:
            if effective_role not in ("e", "am", "parallel"):
                # Not ensemble or parallel. Flag non-ensemble climax plays as suspect.
                if profiles and activated_set and not profiles <= (activated_set | witnesses_set):
                    # Known group, activated set doesn't cover all
                    issues.append(Issue("ERROR", i, pid, "CLIMAX_COVERAGE",
                        f"Climax/revelation play '{pid}' (phase={phase}) is not ensemble "
                        f"and assignment doesn't cover all profiles — the reveal must land for everyone"))
                elif effective_role == "ac" and not activated_set:
                    # Activated play at climax with no explicit assignment
                    issues.append(Issue("WARN", i, pid, "CLIMAX_COVERAGE",
                        f"Climax/revelation play '{pid}' (phase={phase}) has GROUP_ROLE:activated "
                        f"with no explicit assignment — may not reach all participants"))
                elif effective_role == "s":
                    # Solo play at climax: each participant experiences independently
                    issues.append(Issue("WARN", i, pid, "CLIMAX_COVERAGE",
                        f"Climax/revelation play '{pid}' (phase={phase}) has GROUP_ROLE:solo — "
                        f"participants experience the climax independently; "
                        f"consider GROUP_ROLE:ensemble or group_mode:parallel"))

        # ACTIVATION_FATIGUE: same participant activated without an intervening rest
        # prev_activated persists through ensemble/hold plays; only a rest beat clears it
        if activated_set and activated_set & prev_activated:
            overlap = activated_set & prev_activated
            issues.append(Issue("WARN", i, pid, "ACTIVATION_FATIGUE",
                f"Participant(s) {sorted(overlap)} are activated again without an intervening "
                f"rest beat — insert a '_' rest beat between activations"))
        if activated_set:
            prev_activated = activated_set
        elif strip.beat == "_":
            prev_activated = set()

        # WITNESS_DENSITY: activated play with 1 activated, 0 witnesses
        if strip.group_role == "ac":
            if assignment and len(activated_set) > 0 and len(witnesses_set) == 0:
                issues.append(Issue("WARN", i, pid, "WITNESS_DENSITY",
                    f"Activated play '{pid}' has activated={len(activated_set)}, witnesses=0 — "
                    f"defeats the social architecture; consider adding a witness assignment"))

        # DIST_PLAY_CONTEXT: diluting play at climax
        if strip.social_modifier == "dist" and phase in CLIMAX_PHASES:
            issues.append(Issue("WARN", i, pid, "DIST_PLAY_CONTEXT",
                f"Play '{pid}' has SOCIAL_MODIFIER:dist but is at climax/revelation phase — "
                f"dilutes intensity at the wrong moment"))

    return issues


def check_participation_tiers(
    arc_plays: list[dict],
    library: dict[str, PlayStrip],
    audience_scale: str,
) -> list[Issue]:
    """
    TIER_FLOOR / TIER_CEILING / COLLECTIVE_SOLVE_CALIBRATION.
    Only fires when audience_scale == 'mass'.
    COLLECTIVE_SOLVE_CALIBRATION fires on plays with ensemble mechanics
    regardless of audience scale.
    """
    issues: list[Issue] = []

    play_ids = [el.get("id", "") for el in arc_plays if is_play_element(el)]
    strips = [library[pid] for pid in play_ids if pid in library]

    if audience_scale == "mass":
        tiers = {s.participation_tier for s in strips}
        if "P" not in tiers:
            issues.append(Issue("WARN", -1, "arc", "TIER_FLOOR",
                "Mass-audience arc has no Passive-tier (P) plays — "
                "passive participants have no entry point"))
        if "U" not in tiers:
            issues.append(Issue("WARN", -1, "arc", "TIER_CEILING",
                "Mass-audience arc has no Ultra-activated (U) plays — "
                "no participant gets the peak experience"))

    # COLLECTIVE_SOLVE_CALIBRATION: fires on ensemble plays with community-oriented mechanisms
    # Check mechanism list for collective-solve related mechanisms rather than hardcoded play ID
    COLLECTIVE_MECHS = {
        "collective_effervescence", "social_proof", "in_group_identity",
        "social_accountability", "community_solve_bait",
    }
    for s in strips:
        play_mechs = set(s.mechanisms)
        if s.group_role in ("e", "am") and play_mechs & COLLECTIVE_MECHS:
            issues.append(Issue("INFO", -1, s.id, "COLLECTIVE_SOLVE_CALIBRATION",
                f"Play '{s.id}' uses collective/community mechanisms — "
                f"collective intelligence routinely outpaces individual puzzle difficulty "
                f"estimates by 10x (The Beast lesson); calibrate solve complexity accordingly"))

    return issues


def check_activation_void(
    arc_plays: list[dict],
    library: dict[str, PlayStrip],
) -> list[Issue]:
    """
    ACTIVATION_VOID: activated play with activation_rate < 1.0 but no witness design.
    Witness design means: (a) a corresponding witness branch in a branch/merge block,
    or (b) WITNESS_MECHANISMS on the play itself.
    """
    issues: list[Issue] = []

    # Build set of play IDs that appear in witness branches
    witness_designed: set[str] = set()
    for element in arc_plays:
        if is_branch_block(element):
            witness_branch = element.get("branches", {}).get("witness", {})
            if isinstance(witness_branch, dict):
                for bp in witness_branch.get("plays", []):
                    if isinstance(bp, dict) and "id" in bp:
                        witness_designed.add(bp["id"])

    for element in arc_plays:
        if not is_play_element(element):
            continue
        pid = element.get("id", "")
        strip = library.get(pid)
        if not strip:
            continue
        if strip.group_role == "ac" and strip.activation_rate < 1.0:
            has_witness = pid in witness_designed or bool(strip.witness_mechanisms)
            if not has_witness:
                issues.append(Issue("WARN", -1, pid, "ACTIVATION_VOID",
                    f"Play '{pid}' is GROUP_ROLE:activated with ACTIVATION_RATE={strip.activation_rate} "
                    f"but has no witness branch or WITNESS_MECHANISMS — "
                    f"non-activated participants' experience is undesigned"))

    return issues


_THRESHOLD_CONDITION_PATTERNS = [
    re.compile(r"^play_count:\w+ >= \d+$"),
    re.compile(r"^engagement_rate:\w+ >= \d+(\.\d+)?$"),
    re.compile(r"^community_solve_bait:\w+ == (true|false)$"),
    re.compile(r"^operator_signal:\w+$"),
]

def check_thresholds(
    thresholds: list[dict],
    arc_plays: list[dict],
    library: dict[str, PlayStrip],
) -> list[Issue]:
    """
    Validate threshold mechanics.
    Checks: THRESHOLD_CONDITION_INVALID, THRESHOLD_CLIMAX_TIMING.
    """
    issues: list[Issue] = []

    # Collect climax play IDs (regardless of whether they have day fields)
    climax_play_ids_in_arc: set[str] = {
        el.get("id", "") for el in arc_plays
        if is_play_element(el) and el.get("phase") in CLIMAX_PHASES
    }

    threshold_ids: set[str] = set()
    for thresh in thresholds:
        tid = thresh.get("id", "?")
        condition = thresh.get("condition", "")
        triggers = thresh.get("triggers", {})

        if tid in threshold_ids:
            issues.append(Issue("ERROR", -1, tid, "THRESHOLD_CONDITION_INVALID",
                f"Duplicate threshold id '{tid}'"))
        threshold_ids.add(tid)

        # THRESHOLD_CONDITION_INVALID
        if not condition:
            issues.append(Issue("ERROR", -1, tid, "THRESHOLD_CONDITION_INVALID",
                f"Threshold '{tid}' has no condition"))
        elif not any(p.match(condition) for p in _THRESHOLD_CONDITION_PATTERNS):
            issues.append(Issue("WARN", -1, tid, "THRESHOLD_CONDITION_INVALID",
                f"Threshold '{tid}' condition '{condition}' doesn't match known patterns — "
                f"expected: play_count:X >= N, engagement_rate:X >= 0.N, "
                f"community_solve_bait:X == true/false, or operator_signal:ID"))

        # Lint threshold-triggered play against its declared phase
        triggered_play = triggers.get("play") if isinstance(triggers, dict) else None
        triggered_phase = triggers.get("phase") if isinstance(triggers, dict) else None
        if triggered_play and triggered_play in library and triggered_phase:
            strip = library[triggered_play]
            if not strip.arc_fits_phase(triggered_phase):
                fits = "·".join(PHASE_NAMES.get(c, c) for c in strip.arc_codes) or "none"
                issues.append(Issue("WARN", -1, triggered_play, "ARC_FIT",
                    f"Threshold-triggered play '{triggered_play}' declared phase={triggered_phase!r} "
                    f"but play fits [{fits}]"))

    # THRESHOLD_CLIMAX_TIMING: if all climax plays are threshold-triggered
    threshold_triggered_plays = {
        t.get("triggers", {}).get("play")
        for t in thresholds
        if isinstance(t.get("triggers"), dict)
    }
    if climax_play_ids_in_arc and climax_play_ids_in_arc <= threshold_triggered_plays:
        issues.append(Issue("WARN", -1, "arc", "THRESHOLD_CLIMAX_TIMING",
            "All climax plays are threshold-triggered — arc climax timing is fully "
            "community-paced with no day-based fallback; confirm operator has a manual "
            "operator_signal trigger ready"))

    return issues


def check_recovery_blocks(
    arc_plays: list[dict],
    library: dict[str, PlayStrip],
) -> list[Issue]:
    """
    Lint inline recovery blocks on plays.
    Checks: RECOVERY_LEAD_TIME, RECOVERY_CONTRAINDICATED, RECOVERY_PHASE.
    All four failure modes supported: cold, confused, distressed, over_engaged.
    """
    issues: list[Issue] = []
    VALID_MODES = {"cold", "confused", "distressed", "over_engaged"}

    for i, element in enumerate(arc_plays):
        if not is_play_element(element):
            continue
        pid = element.get("id", "")
        parent_phase = element.get("phase")
        recovery = element.get("recovery")
        if not recovery or not isinstance(recovery, dict):
            continue

        parent_strip = library.get(pid)

        for mode, rec_play_ids in recovery.items():
            if mode not in VALID_MODES:
                issues.append(Issue("WARN", i, pid, "RECOVERY_PHASE",
                    f"Recovery block on '{pid}' has unknown mode '{mode}' — "
                    f"valid modes: {', '.join(sorted(VALID_MODES))}"))
                continue

            if not isinstance(rec_play_ids, list):
                continue

            for rec_pid in rec_play_ids:
                if rec_pid == "OPERATOR_PAUSE":
                    continue
                if rec_pid not in library:
                    issues.append(Issue("WARN", i, pid, "UNKNOWN",
                        f"Recovery play '{rec_pid}' (mode={mode}) not found in library"))
                    continue

                rec_strip = library[rec_pid]

                # RECOVERY_LEAD_TIME: recovery plays can't be staged on-demand if lead > 0
                if rec_strip.lead_days > 0:
                    issues.append(Issue("WARN", i, pid, "RECOVERY_LEAD_TIME",
                        f"Recovery play '{rec_pid}' (mode={mode}) has LEAD_TIME={rec_strip.lead_time} — "
                        f"cannot be staged on-demand after failure; pre-stage before the arc"))

                # RECOVERY_CONTRAINDICATED: recovery play is CONTRAINDICATED_AFTER parent
                if parent_strip and parent_strip.id in rec_strip.contraindicated_after:
                    issues.append(Issue("ERROR", i, pid, "RECOVERY_CONTRAINDICATED",
                        f"Recovery play '{rec_pid}' (mode={mode}) is CONTRAINDICATED_AFTER "
                        f"its parent play '{pid}'"))

                # RECOVERY_PHASE: recovery play must fit parent's phase
                if parent_phase and not rec_strip.arc_fits_phase(parent_phase):
                    fits = "·".join(PHASE_NAMES.get(c, c) for c in rec_strip.arc_codes) or "none"
                    issues.append(Issue("WARN", i, pid, "RECOVERY_PHASE",
                        f"Recovery play '{rec_pid}' (mode={mode}) fits [{fits}] "
                        f"but parent play is at phase={parent_phase!r}"))

    return issues


# ── ARC SHAPE DISPLAY ─────────────────────────────────────────────────────────

BEAT_NAMES = {"^": "spike", "/": "ramp", "-": "hold", "_": "rest", ">": "transition", "~": "liminal"}
DETECTION_LABELS = {"i": "▓▓▓", "s": "▓▓░", "m": "▓░░", "l": "░░░", "n": "   "}


def arc_summary(plays: list[PlayStrip]) -> str:
    lines = []

    beat_str = " ".join(p.beat or "?" for p in plays)
    lines.append(f"  Beats:      {beat_str}")

    arc_str = " ".join(("".join(p.arc_codes[:2]) or "?") for p in plays)
    lines.append(f"  Arc codes:  {arc_str}")

    det_str = " ".join(DETECTION_LABELS.get(p.detection, " ? ") for p in plays)
    lines.append(f"  Detection:  {det_str}   (▓=high ░=low)")

    int_str = " ".join(p.intensity or "?" for p in plays)
    lines.append(f"  Intensity:  {int_str}")

    beats = [p.beat for p in plays]
    counts = {name: beats.count(sym) for sym, name in BEAT_NAMES.items()}
    count_str = "  ".join(f"{name}:{n}" for name, n in counts.items() if n > 0)
    lines.append(f"  Beat mix:   {count_str}")

    _legacy_labels = {"e": "ephemeral", "p": "personal", "s": "social", "w": "world_mark"}
    legacy_types: dict[str, int] = {}
    for p in plays:
        for c in p.legacy:
            legacy_types[c] = legacy_types.get(c, 0) + 1
    legacy_str = "  ".join(
        f"{_legacy_labels.get(k, k)}:{v}"
        for k, v in sorted(legacy_types.items())
    )
    lines.append(f"  Legacy mix: {legacy_str}")

    return "\n".join(lines)


# ── MAIN LINTERS ──────────────────────────────────────────────────────────────

def _lint_flat(
    play_ids: list[str],
    days: list[int | None] | None = None,
    phases: list[str | None] | None = None,
) -> tuple[list[Issue], list[PlayStrip]]:
    library = load_strips()
    days = days or [None] * len(play_ids)
    phases = phases or [None] * len(play_ids)
    positions = list(range(len(play_ids)))

    unknown_issues = check_unknown_plays(play_ids, library)
    known_ids = [pid for pid in play_ids if pid in library]
    known_positions = [i for i, pid in enumerate(play_ids) if pid in library]
    plays = [library[pid] for pid in known_ids]
    known_days = [days[i] for i in known_positions]
    known_phases = [phases[i] for i in known_positions]

    all_issues: list[Issue] = []
    all_issues.extend(unknown_issues)
    all_issues.extend(check_contraindicated(plays, known_positions))
    all_issues.extend(check_frame_requirement(plays, known_positions))
    all_issues.extend(check_permission_sequenced(plays, known_positions))
    all_issues.extend(check_lead_time(plays, known_positions, known_days))
    all_issues.extend(check_rhythm(plays, known_positions))
    all_issues.extend(check_detection_accumulation(plays, known_positions, known_days))
    all_issues.extend(check_reversibility(plays, known_positions))
    all_issues.extend(check_arc_fit(plays, known_positions, known_phases))
    all_issues.extend(check_world_mark_timing(plays, known_positions))
    all_issues.extend(check_requires_consistency(plays, known_positions))

    return all_issues, plays


def lint_arc(arc: Arc) -> tuple[list[Issue], list[PlayStrip]]:
    """Structured arc linter — accepts Arc with pre_arc, parallel_tracks,
    thresholds, branch/merge blocks, and group dynamics."""
    library = load_strips()
    all_issues: list[Issue] = []

    # 1. Pre-arc checks (LEAD_TIME + grant accumulation)
    if arc.pre_arc_plays:
        pre_issues, pre_grants = check_pre_arc(arc.pre_arc_plays, library)
        all_issues.extend(pre_issues)
    else:
        pre_grants = set()

    # 2. Parallel tracks (PARALLEL_END_CONDITION, LEAD_TIME, OVERLAP + day risk map)
    if arc.parallel_tracks:
        para_issues, parallel_day_risks = check_parallel_tracks(
            arc.parallel_tracks, arc.plays, library
        )
        all_issues.extend(para_issues)
    else:
        parallel_day_risks = {}

    # 3. Extract main sequence for sequential checks
    main_seq = _extract_main_sequence(arc.plays)
    play_ids = [el.get("id", "") for el in main_seq]
    days = [el.get("day") for el in main_seq]
    phases = [el.get("phase") for el in main_seq]
    positions = list(range(len(play_ids)))

    unknown_issues = check_unknown_plays(play_ids, library)
    all_issues.extend(unknown_issues)

    known_ids = [pid for pid in play_ids if pid in library]
    known_positions = [i for i, pid in enumerate(play_ids) if pid in library]
    plays = [library[pid] for pid in known_ids]
    known_days = [days[i] for i in known_positions]
    known_phases = [phases[i] for i in known_positions]

    all_issues.extend(check_contraindicated(plays, known_positions))
    all_issues.extend(check_frame_requirement(plays, known_positions))
    all_issues.extend(check_permission_sequenced(plays, known_positions, pre_grants))
    all_issues.extend(check_lead_time(plays, known_positions, known_days))
    all_issues.extend(check_rhythm(plays, known_positions))
    all_issues.extend(check_detection_accumulation(
        plays, known_positions, known_days, parallel_day_risks
    ))
    all_issues.extend(check_reversibility(plays, known_positions))
    all_issues.extend(check_arc_fit(plays, known_positions, known_phases))
    all_issues.extend(check_world_mark_timing(plays, known_positions))
    all_issues.extend(check_requires_consistency(plays, known_positions))
    all_issues.extend(check_landscape_balance(plays, known_positions, arc.arc_type))
    all_issues.extend(check_early_exit(arc, library))
    all_issues.extend(check_participation_rate(arc.plays, library))

    # 4. V2 structural checks
    all_issues.extend(check_branch_merge_blocks(arc.plays, library))
    all_issues.extend(check_group_dynamics(arc.plays, library, arc))
    all_issues.extend(check_participation_tiers(arc.plays, library, arc.audience_scale))
    all_issues.extend(check_activation_void(arc.plays, library))
    if arc.thresholds:
        all_issues.extend(check_thresholds(arc.thresholds, arc.plays, library))
    all_issues.extend(check_recovery_blocks(arc.plays, library))

    return all_issues, plays


# ── REPORT FORMATTING ─────────────────────────────────────────────────────────

def _format_flat_report(
    play_ids: list[str],
    issues: list[Issue],
    plays: list[PlayStrip],
    days: list[int | None] | None = None,
) -> str:
    errors = [i for i in issues if i.severity == "ERROR"]
    warns  = [i for i in issues if i.severity == "WARN"]
    infos  = [i for i in issues if i.severity == "INFO"]

    lines = []
    lines.append(f"ARC LINT REPORT — {len(play_ids)} plays")
    lines.append("═" * 60)
    lines.append("")

    if days and any(d is not None for d in days):
        day_str = "  ".join(f"{pid}:d{d}" if d is not None else pid
                            for pid, d in zip(play_ids, days))
        lines.append(f"Schedule:  {day_str}")
        lines.append("")

    lines.append("Plays:")
    for i, pid in enumerate(play_ids):
        strip = next((p for p in plays if p.id == pid), None)
        if strip:
            day_tag = f"  d{days[i]}" if days and days[i] is not None else ""
            lines.append(f"  [{i+1:>2}] {pid:<40} "
                         f"{strip.beat} {BEAT_NAMES.get(strip.beat,'')+day_tag}")
        else:
            lines.append(f"  [{i+1:>2}] {pid}  [NOT FOUND]")
    lines.append("")

    if errors:
        lines.append(f"ERRORS ({len(errors)}):")
        for issue in errors:
            lines.append(str(issue))
        lines.append("")

    if warns:
        lines.append(f"WARNINGS ({len(warns)}):")
        for issue in warns:
            lines.append(str(issue))
        lines.append("")

    if infos:
        lines.append(f"INFO ({len(infos)}):")
        for issue in infos:
            lines.append(str(issue))
        lines.append("")

    if not issues:
        lines.append("✓  No issues found.")
        lines.append("")

    if plays:
        lines.append("ARC SHAPE:")
        lines.append(arc_summary(plays))
        lines.append("")

    status = "PASS" if not errors else "FAIL"
    lines.append(f"{'─'*60}")
    lines.append(f"Status: {status}  |  {len(errors)} errors  {len(warns)} warnings  {len(infos)} info")

    return "\n".join(lines)


def format_report(
    arc: Arc,
    issues: list[Issue],
    plays: list[PlayStrip],
) -> str:
    errors = [i for i in issues if i.severity == "ERROR"]
    warns  = [i for i in issues if i.severity == "WARN"]
    infos  = [i for i in issues if i.severity == "INFO"]

    lines = []
    main_count = sum(1 for el in arc.plays if is_play_element(el))
    branch_count = sum(1 for el in arc.plays if is_branch_block(el))
    pre_count = len(arc.pre_arc_plays)
    track_count = len(arc.parallel_tracks)

    lines.append(f"ARC LINT REPORT — {arc.arc_type} / {arc.audience_scale}")
    lines.append("═" * 60)
    lines.append(f"  Main plays:       {main_count}")
    if branch_count:
        lines.append(f"  Branch/merge:     {branch_count} block(s)")
    if pre_count:
        lines.append(f"  Pre-arc plays:    {pre_count}")
    if track_count:
        lines.append(f"  Parallel tracks:  {track_count}")
    if arc.thresholds:
        lines.append(f"  Thresholds:       {len(arc.thresholds)}")
    if arc.early_exit:
        lines.append(f"  Early exit:       {arc.early_exit}")
    if arc.group.get("profiles"):
        names = [p.split("/")[-1].replace(".json","") for p in arc.group["profiles"]]
        lines.append(f"  Group:            {', '.join(names)}")
    lines.append("")

    if errors:
        lines.append(f"ERRORS ({len(errors)}):")
        for issue in errors:
            lines.append(str(issue))
        lines.append("")

    if warns:
        lines.append(f"WARNINGS ({len(warns)}):")
        for issue in warns:
            lines.append(str(issue))
        lines.append("")

    if infos:
        lines.append(f"INFO ({len(infos)}):")
        for issue in infos:
            lines.append(str(issue))
        lines.append("")

    if not issues:
        lines.append("✓  No issues found.")
        lines.append("")

    if plays:
        lines.append("MAIN SEQUENCE SHAPE:")
        lines.append(arc_summary(plays))
        lines.append("")

    status = "PASS" if not errors else "FAIL"
    lines.append(f"{'─'*60}")
    lines.append(f"Status: {status}  |  {len(errors)} errors  {len(warns)} warnings  {len(infos)} info")

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Arc linter for immersive experience plays")
    parser.add_argument("plays", nargs="*", help="Play IDs in arc order")
    parser.add_argument("--file", "-f", help="JSON file with arc definition (flat list or structured dict)")
    parser.add_argument("--days", help="Comma-separated day numbers (e.g. 0,0,3,7,14)")
    parser.add_argument("--phases", help="Comma-separated arc phases (e.g. p,p,b,e,c)")
    parser.add_argument("--json", action="store_true", help="Output issues as JSON")
    args = parser.parse_args()

    if args.file:
        data = json.loads(Path(args.file).read_text())

        if isinstance(data, dict):
            arc = load_arc(data)
            issues, plays = lint_arc(arc)

            if args.json:
                out = [{"severity": i.severity, "position": i.position + 1,
                        "play": i.play_id, "code": i.code, "message": i.message}
                       for i in issues]
                print(json.dumps(out, indent=2))
            else:
                print(format_report(arc, issues, plays))

            errors = [i for i in issues if i.severity == "ERROR"]
            sys.exit(1 if errors else 0)

        else:
            # flat list format
            play_ids: list[str] = []
            days: list[int | None] = []
            phases: list[str | None] = []

            if data and isinstance(data[0], dict):
                # Filter out branch/merge blocks (use structured dict format for those)
                flat = [d for d in data if isinstance(d, dict) and "branch_point" not in d]
                play_ids = [d["id"] for d in flat]
                days = [d.get("day") for d in flat]
                phases = [d.get("phase") for d in flat]
            else:
                play_ids = [str(d) for d in data]

            if args.days:
                raw_days = args.days.split(",")
                days = [int(d.strip()) if d.strip() != "" else None for d in raw_days]
            if args.phases:
                raw_phases = args.phases.split(",")
                phases = [p.strip() if p.strip() else None for p in raw_phases]

            while len(days) < len(play_ids):
                days.append(None)
            while len(phases) < len(play_ids):
                phases.append(None)

            issues, plays = _lint_flat(play_ids, days, phases)

            if args.json:
                out = [{"severity": i.severity, "position": i.position + 1,
                        "play": i.play_id, "code": i.code, "message": i.message}
                       for i in issues]
                print(json.dumps(out, indent=2))
            else:
                print(_format_flat_report(play_ids, issues, plays,
                                          days if any(d is not None for d in days) else None))

            errors = [i for i in issues if i.severity == "ERROR"]
            sys.exit(1 if errors else 0)

    elif args.plays:
        play_ids = args.plays
        days_raw = []
        phases_raw = []
        if args.days:
            days_raw = [int(d.strip()) if d.strip() else None for d in args.days.split(",")]
        if args.phases:
            phases_raw = [p.strip() if p.strip() else None for p in args.phases.split(",")]
        while len(days_raw) < len(play_ids):
            days_raw.append(None)
        while len(phases_raw) < len(play_ids):
            phases_raw.append(None)

        issues, plays = _lint_flat(play_ids, days_raw, phases_raw)

        if args.json:
            out = [{"severity": i.severity, "position": i.position + 1,
                    "play": i.play_id, "code": i.code, "message": i.message}
                   for i in issues]
            print(json.dumps(out, indent=2))
        else:
            print(_format_flat_report(play_ids, issues, plays,
                                      days_raw if any(d is not None for d in days_raw) else None))

        errors = [i for i in issues if i.severity == "ERROR"]
        sys.exit(1 if errors else 0)

    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
