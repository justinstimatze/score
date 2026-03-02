#!/usr/bin/env python3
"""
arc_planner.py

Takes a linted arc and a participant profile, then annotates every play with:
  - Engagement probability
  - Most-likely failure mode and probability
  - Recovery plays for each failure mode
  - Bail point classification
  - Operator hold requirement

Accepts flat play lists and structured arc dicts (with pre_arc, parallel_tracks,
branch/merge blocks). For branch/merge blocks, merge_point plays are scored in
the main sequence; branch plays are annotated separately with their branch context.

Output: arc_plan.json — branching arc consumed by arc_simulator.py

Usage:
  python arc_planner.py --arc arc.json --profile profile.json
  python arc_planner.py --arc arc.json --profile profile.json --out plan.json
  python arc_planner.py --profile profile.json --fit-report              # design-time mode: all plays
  python arc_planner.py --profile profile.json --fit-report --show-weak  # include weak-fit plays
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

STRIPS_FILE  = Path(__file__).parent / "plays_strips.json"
MECH_INDEX_FILE = Path(__file__).parent / "plays_mechanisms.json"

_MECH_INDEX: dict[str, list[str]] = {}

def _load_mech_index() -> dict[str, list[str]]:
    global _MECH_INDEX
    if not _MECH_INDEX and MECH_INDEX_FILE.exists():
        _MECH_INDEX = json.loads(MECH_INDEX_FILE.read_text())
    return _MECH_INDEX

# ── STRIP PARSING ─────────────────────────────────────────────────────────────

@dataclass
class Strip:
    id: str
    cost: str = "F"
    autonomy: str = "A"
    lead: str = "0"
    intensity: int = 2
    mechanisms: list[str] = field(default_factory=list)
    arc_fit: str = "*"
    beat: str = "/"
    agency_type: str = ""      # AT field
    frame_req: str = ""        # FR field
    detection: str = "m"       # DE field (pos 5 of L3)
    reversibility: str = "a"   # RV field (pos 6 of L3)
    legacy: str = "p"
    requires_confederate: bool = False
    prm: str = ""
    permission_grant: str = ""
    requires: str = ""
    raw: str = ""
    # v2 group fields
    group_role: str = "s"          # s=solo e=ensemble ac=activated am=ambient lo=lottery
    social_modifier: str = "neut"  # amp dist req neut
    participation_tier: str = "U"  # P A E U
    parallel_capable: bool = False
    activation_rate: float = 1.0
    witness_mechanisms: list[str] = field(default_factory=list)

    @property
    def persona_bound(self) -> bool:
        """N1: True if play efficacy depends on a specific operator identity."""
        return "pb" in self.autonomy

    @property
    def is_lottery(self) -> bool:
        """True if this beat fires for a subset of participants via selection (not ensemble)."""
        return self.group_role == "lo"

_STRIPS: dict[str, Strip] = {}

def _parse_strips(path: Path) -> dict[str, Strip]:
    raw_list = json.loads(path.read_text())
    strips = {}
    for entry in raw_list:
        pid = entry["id"]
        text = entry.get("strip", "")
        s = _parse_one(pid, text)
        s.raw = text
        strips[pid] = s
    return strips

def _parse_one(pid: str, text: str) -> Strip:
    s = Strip(id=pid)
    lines = text.strip().splitlines()
    if not lines:
        return s

    # Line 1: @id COST·AUTONOMY·LEAD·INTENSITY
    m = re.match(r"@\S+\s+(\S+)·(\S+)·(\S+)·(\S+)", lines[0])
    if m:
        s.cost = m.group(1)
        s.autonomy = m.group(2)
        s.lead = m.group(3)
        try:
            s.intensity = int(m.group(4))
        except ValueError:
            s.intensity = 2

    # Line 2: #mech1·mech2... [arc_fit] beat
    if len(lines) > 1:
        m2 = re.match(r"#(\S+)\s+\[([^\]]+)\]\s+(\S+)", lines[1])
        if m2:
            s.mechanisms = m2.group(1).split("·")
            s.arc_fit = m2.group(2)
            s.beat = m2.group(3)

    # Line 3: AT·FR·AD·LA·LG·DE·RV (7 fields)
    if len(lines) > 2:
        parts = lines[2].split("·")
        if len(parts) >= 7:
            s.agency_type    = parts[0]   # AT
            s.frame_req      = parts[1]   # FR
            # parts[2] = AD (agency_demand, not stored)
            # parts[3] = LA (landscape, not stored)
            s.legacy         = parts[4]   # LG
            s.detection      = parts[5]   # DE
            s.reversibility  = parts[6]   # RV

    # Labeled lines (L4+) — must run before requires_confederate check
    for line in lines:
        if line.startswith("prm:"):
            s.prm = line[4:].strip()
            if "→" in s.prm:
                s.permission_grant = s.prm.split("→", 1)[1]
        elif line.startswith("req:"):
            s.requires = line[4:].strip()
        elif line.startswith("grp:"):
            # grp:GROUP_ROLE·SOCIAL_MODIFIER·TIER·PC·AR
            parts = line[4:].split("·")
            if len(parts) >= 1:
                s.group_role = parts[0]
            if len(parts) >= 2:
                s.social_modifier = parts[1]
            if len(parts) >= 3:
                s.participation_tier = parts[2]
            if len(parts) >= 4:
                s.parallel_capable = parts[3] == "1"
            if len(parts) >= 5:
                try:
                    s.activation_rate = float(parts[4])
                except ValueError:
                    pass
        elif line.startswith("wit:"):
            s.witness_mechanisms = [x.strip() for x in line[4:].split("·") if x.strip()]

    # Confederate requirement — evaluated after labeled lines so s.requires is populated
    s.requires_confederate = (
        "C" in s.autonomy or
        "cnf" in s.requires or
        "req:cnf" in text
    )

    return s


def _load_strips() -> dict[str, Strip]:
    global _STRIPS
    if not _STRIPS:
        _STRIPS = _parse_strips(STRIPS_FILE)
    return _STRIPS


# ── ARC FORMAT NORMALIZATION ──────────────────────────────────────────────────

def _is_branch_block(element: dict) -> bool:
    return isinstance(element, dict) and "branch_point" in element


def _extract_plays_for_planning(arc) -> list[dict]:
    """
    Extract a flat play list from any arc format for sequential planning.
    Branch/merge blocks contribute their merge_point play at their position.
    Branch plays are planned separately in branch annotations.
    """
    if isinstance(arc, list):
        return [{"id": item} if isinstance(item, str) else item for item in arc]

    if isinstance(arc, dict) and "plays" in arc:
        result = []
        for element in arc["plays"]:
            if _is_branch_block(element):
                mp = element.get("merge_point")
                if mp and isinstance(mp, dict) and mp.get("play"):
                    result.append({
                        "id": mp["play"],
                        "day": element.get("day"),
                        "phase": element.get("phase"),
                        "_from_branch": element.get("id"),
                    })
            elif isinstance(element, dict) and "id" in element:
                result.append(element)
        return result

    return []


def _extract_branch_blocks(arc) -> list[dict]:
    """Return all branch/merge blocks from any arc format."""
    if isinstance(arc, dict) and "plays" in arc:
        return [el for el in arc["plays"] if _is_branch_block(el)]
    return []


# ── MECHANISM MATCHING ────────────────────────────────────────────────────────

_O_MECHS = {
    "curiosity_exploration", "information_gap", "apophenia_induction",
    "anticipatory_attention", "participant_as_detective", "narrative_without_exposition",
    "object_archaeology", "environmental_semiotics", "knowledge_frontier",
    "curiosity_gap", "exploration_license",
}
_C_MECHS = {
    "pattern_completion", "need_for_closure", "commitment_consistency",
    "reward_escalation", "sequential_discovery", "pattern_recognition",
}
_N_MECHS = {
    "hypervigilance", "paranoia_escalation", "disorientation", "significance_quest",
    "hot_cold_empathy_gap", "threat_appraisal", "uncanny_recognition",
    "fear_of_missing",
}

# ── REGISTER & IDENTITY SETS (I3, I4, P4) ─────────────────────────────────────

# Plays heavy in these mechanisms are disorienting — require cognitive scaffolding
# first for "rewired" participants (P5 register).
_DISORIENTATION_MECHS = {
    "hypervigilance", "paranoia_escalation", "disorientation", "uncanny_recognition",
    "reality_rupture", "liminal_destabilization", "dissonance_induction",
    "threat_appraisal",
}

# Plays heavy in these mechanisms provide cognitive scaffolding — count toward
# the minimum-scaffold threshold before disorientation plays.
_COGNITIVE_SCAFFOLD_MECHS = {
    "curiosity_exploration", "information_gap", "participant_as_detective",
    "knowledge_frontier", "narrative_without_exposition", "pattern_recognition",
    "object_archaeology", "environmental_semiotics", "curiosity_gap",
    "apophenia_induction", "sequential_discovery", "need_for_cognition",
}

# Maps P7 identity rejection options → mechanism sets that primarily serve that dimension.
# A play triggers an identity anti-fit warning if ≥ 2 of its mechanisms appear here.
_IDENTITY_MECHS: dict[str, set] = {
    "interesting":  {"aesthetic_response", "creative_expression", "somatic_awareness",
                     "embodied_cognition", "flow_state", "sensory_seeking"},
    "creative":     {"creative_expression", "making_agency", "authorship_invitation",
                     "craft_engagement", "creative_agency"},
    "good":         {"prosocial_alignment", "moral_clarity", "care_expression",
                     "ethical_weight", "moral_elevation"},
    "brave":        {"ordeal_completion", "threshold_crossing", "discomfort_endurance",
                     "physical_intensity", "courage_demand"},
    "dependable":   {"commitment_consistency", "reliability_signal", "follow_through",
                     "duty_activation"},
    "perceptive":   {"pattern_recognition", "participant_as_detective", "knowledge_frontier",
                     "curiosity_exploration", "information_gap", "curiosity_gap",
                     "apophenia_induction"},
    "influential":  {"significance_quest", "status_signal", "legacy_mark",
                     "achievement_motivation", "social_proof"},
}

def _play_mechs(play_id: str) -> list[str]:
    return _load_mech_index().get(play_id, [])


def _check_register_fit(
    play_id: str,
    profile: dict,
    prior_scaffold_count: int,
) -> str | None:
    """
    I3: P5 register ordering constraint.
    Returns a warning string if this play violates the register ordering rule,
    None otherwise.
    """
    register = profile.get("p5_register", "")
    if register != "rewired":
        return None
    play_mech_set = set(_play_mechs(play_id))
    disorientation_hits = play_mech_set & _DISORIENTATION_MECHS
    if not disorientation_hits:
        return None
    if prior_scaffold_count >= 2:
        return None
    return (
        f"REGISTER_FIT: 'rewired' participant — disorientation-register play "
        f"({', '.join(sorted(disorientation_hits))}) before sufficient cognitive scaffolding "
        f"({prior_scaffold_count}/2 scaffold plays seen). Risk: shutdown rather than engagement."
    )


def _check_identity_antifit(play_id: str, profile: dict) -> str | None:
    """
    P4: Identity anti-filter.
    Returns a warning string if this play primarily serves a rejected identity dimension,
    None otherwise. Fires when ≥ 2 play mechanisms overlap with a rejected identity's set.
    """
    rejected = profile.get("identity_negative_space", [])
    if not rejected:
        return None
    play_mech_set = set(_play_mechs(play_id))
    if not play_mech_set:
        return None
    for dim in rejected:
        dim_mechs = _IDENTITY_MECHS.get(dim.lower(), set())
        hits = play_mech_set & dim_mechs
        if len(hits) >= 2:
            return (
                f"IDENTITY_ANTIFIT: play engages primarily via '{dim}' identity dimension "
                f"({', '.join(sorted(hits))}) which participant has rejected. "
                f"Low fit regardless of mechanism score."
            )
    return None


def _check_hard_constraints(play_id: str, profile: dict) -> str | None:
    """
    I4: E2 hard constraint passthrough.
    Returns a warning string if this play matches any hard_constraints keyword,
    None otherwise. Match is approximate: substring against mechanism names and play ID.
    """
    constraints = profile.get("hard_constraints", [])
    if not constraints:
        return None
    play_mech_set = set(_play_mechs(play_id))
    play_mech_str = " ".join(play_mech_set).lower()
    play_id_lower = play_id.lower()
    for constraint in constraints:
        kw = constraint.lower().strip()
        if not kw:
            continue
        if kw in play_id_lower or kw in play_mech_str:
            return (
                f"HARD_CONSTRAINT: play matches sponsor E2 exclusion '{constraint}'. "
                f"Review before including in arc."
            )
    return None


def _play_warnings(
    play_id: str,
    profile: dict,
    prior_scaffold_count: int,
) -> list[str]:
    """Collect all profile-level warnings for a play."""
    warnings = []
    w = _check_register_fit(play_id, profile, prior_scaffold_count)
    if w:
        warnings.append(w)
    w = _check_identity_antifit(play_id, profile)
    if w:
        warnings.append(w)
    w = _check_hard_constraints(play_id, profile)
    if w:
        warnings.append(w)
    return warnings


def _mech_score(play_id: str, profile: dict, mech_override: list[str] | None = None) -> float:
    """
    Score 0-1: weighted fraction of profile mechanisms that appear in this play.
    mech_override: if provided, score against these mechanisms instead of the indexed ones.
    Used for witness scoring (against WITNESS_MECHANISMS field).
    """
    profile_mechs = profile.get("mechanisms", {})
    if not profile_mechs:
        return 0.5

    total_weight = sum(profile_mechs.values())
    if total_weight == 0:
        return 0.5

    if mech_override is not None:
        play_mech_set = set(mech_override)
    else:
        play_mech_set = set(_play_mechs(play_id))

    if not play_mech_set:
        return 0.5

    matched = 0.0
    for pm_name, pm_weight in profile_mechs.items():
        if pm_name in play_mech_set:
            matched += pm_weight
        else:
            pm_root = pm_name.split("_")[0]
            for play_mech in play_mech_set:
                if pm_root in play_mech or play_mech.split("_")[0] == pm_root:
                    matched += pm_weight * 0.4
                    break

    return min(matched / total_weight, 1.0)


# ── ENGAGEMENT PROBABILITY ────────────────────────────────────────────────────

SENSITIVITY_INTENSITY_FIT = {
    ("low",    1): 0.10, ("low",    2): 0.05, ("low",    3): -0.05, ("low",    4): -0.15,
    ("medium", 1): 0.00, ("medium", 2): 0.10, ("medium", 3):  0.08, ("medium", 4): -0.10,
    ("high",   1): -0.05, ("high",  2): 0.05, ("high",   3):  0.10, ("high",   4):  0.05,
}

def _engagement_prob(
    strip: Strip,
    profile: dict,
    prior_spikes: int,
    role: str = "activated",
) -> float:
    """
    Return estimated engagement probability 0-100 (integer).
    role: 'activated' scores against main mechanisms; 'witness' scores against
          witness_mechanisms if present, otherwise uses a flat 0.55 base.
    """
    if strip.beat == "~":
        return 100

    # Witness scoring: use witness_mechanisms if available
    if role == "witness":
        if strip.witness_mechanisms:
            match = _mech_score(strip.id, profile, mech_override=strip.witness_mechanisms)
        else:
            match = 0.55  # default witness engagement — less than activated, more than 0.5
        base = 55.0
        base += (match - 0.5) * 30  # narrower range for witness scoring
        base = max(20.0, min(85.0, base))
        return round(base)

    base = 60.0

    match = _mech_score(strip.id, profile)
    base += (match - 0.5) * 40

    sensitivity = profile.get("sensitivity", "medium")
    base += SENSITIVITY_INTENSITY_FIT.get((sensitivity, strip.intensity), 0) * 100

    bf = profile.get("big_five", {})
    O = bf.get("O", 0)
    C = bf.get("C", 0)
    N = bf.get("N", 0)
    E = bf.get("E", 0)

    play_mech_set = set(_play_mechs(strip.id))

    if play_mech_set & _O_MECHS:
        base += O * 4
    if strip.beat == "/":
        base += C * 3
    if strip.detection == "h" or play_mech_set & _N_MECHS:
        base -= N * 4
    if any(m in play_mech_set for m in ("social_proof", "belonging", "direct_interaction",
                                         "dyadic_interaction", "status_selection")):
        base += E * 4

    if strip.beat == "^" and prior_spikes >= 2:
        base -= 5

    # I3: P5 register ordering penalty — "rewired" participant + disorientation play
    # before sufficient cognitive scaffolding
    register = profile.get("p5_register", "")
    prior_scaffold = profile.get("_prior_scaffold_count", 0)  # set by plan_arc
    if register == "rewired":
        play_mech_set_local = set(_play_mechs(strip.id))
        if play_mech_set_local & _DISORIENTATION_MECHS and prior_scaffold < 2:
            base -= 15

    identity = profile.get("identity_invite", "")
    if identity == "seeker_pattern_finder":
        if play_mech_set & (_O_MECHS | _C_MECHS):
            base += 7
    elif identity == "protagonist":
        if strip.beat == "^":
            base += 5

    base = max(20.0, min(95.0, base))
    return round(base)


# ── FAILURE MODE PROBABILITIES ────────────────────────────────────────────────

def _failure_probs(strip: Strip, profile: dict, eng_prob: int) -> dict[str, int]:
    fail_total = 100 - eng_prob
    if fail_total <= 0:
        return {"cold": 0, "confused": 0, "distressed": 0, "over_engaged": 0}

    bf = profile.get("big_five", {})
    N = bf.get("N", 0)
    C = bf.get("C", 0)

    w = {"cold": 40, "confused": 30, "distressed": 10, "over_engaged": 20}

    if strip.detection == "h":
        w["confused"] += 20
        w["cold"] -= 10
    if strip.reversibility == "i":
        w["distressed"] += 15
        w["cold"] -= 5
    if strip.intensity >= 4:
        w["distressed"] += 20
        w["cold"] -= 10

    w["distressed"] += N * 10
    w["over_engaged"] += C * 8

    total_w = sum(max(0, v) for v in w.values())
    if total_w == 0:
        return {k: 0 for k in w}

    result = {}
    remaining = fail_total
    items = sorted(w.items(), key=lambda x: -x[1])
    for i, (mode, weight) in enumerate(items):
        if i == len(items) - 1:
            result[mode] = remaining
        else:
            share = round((max(0, weight) / total_w) * fail_total)
            result[mode] = share
            remaining -= share

    return result


# ── RECOVERY PLAY SELECTION ───────────────────────────────────────────────────

RECOVERY_PLAYS: dict[str, list[str]] = {
    "cold": [
        "wrong_read_recovery",
        "breadcrumb_without_demand",
        "open_door_signal",
        "anomalous_receipt",
    ],
    "confused": [
        "elegant_failure",
        "misfire_as_story",
        "seam_acknowledgment",
    ],
    "distressed": [
        "seam_acknowledgment",
        "graceful_release",
        "OPERATOR_PAUSE",
    ],
    "over_engaged": [
        "optional_path",
        "open_door_signal",
        "OPERATOR_PAUSE",
    ],
}

def _recovery_plays(
    failure_probs: dict[str, int],
    strip: Strip,
    strips: dict[str, Strip],
    inline_recovery: dict[str, list[str]] | None = None,
) -> dict[str, list[str]]:
    """
    For each meaningful failure mode, return ranked recovery plays.
    inline_recovery: per-play recovery overrides from arc JSON (§8 inline blocks).
    """
    result = {}
    for mode, prob in failure_probs.items():
        if prob < 3:
            continue
        # Prefer inline recovery block if provided
        if inline_recovery and mode in inline_recovery:
            candidates = [p for p in inline_recovery[mode]
                         if p == "OPERATOR_PAUSE" or p in strips]
        else:
            candidates = [p for p in RECOVERY_PLAYS.get(mode, [])
                         if p == "OPERATOR_PAUSE" or p in strips]
        if candidates:
            result[mode] = candidates
    return result


# ── BAIL POINT CLASSIFICATION ─────────────────────────────────────────────────

def _bail_classification(
    strip: Strip,
    phase_index: int,
    total_plays: int,
    arc_seq: list[dict],
    i: int,
) -> dict:
    if strip.id in ("exit_honored", "open_door_signal", "graceful_release"):
        return {
            "is_bail_point": True, "bail_type": "explicit",
            "bail_note": "Built-in exit beat — participant can stop here cleanly."
        }
    if strip.beat == "-" and i < total_plays - 1:
        return {
            "is_bail_point": True, "bail_type": "natural",
            "bail_note": "Rest beat — low-intensity interstitial; participant can be released without disruption."
        }
    if strip.beat == ">":
        return {
            "is_bail_point": True, "bail_type": "natural",
            "bail_note": "Transition beat — clean pivot point if participant is not engaging."
        }
    if i < total_plays - 1:
        next_id = arc_seq[i + 1].get("id", "")
        strips = _load_strips()
        if next_id in strips:
            nxt = strips[next_id]
            if nxt.reversibility == "i" or nxt.detection == "h":
                return {
                    "is_bail_point": False, "bail_type": "operator_hold",
                    "bail_note": f"Operator must confirm participant engagement before releasing '{next_id}'."
                }
    return {"is_bail_point": False, "bail_type": None, "bail_note": ""}


# ── PLANNER ───────────────────────────────────────────────────────────────────

def plan_arc(arc, profile: dict) -> dict:
    """
    Plan an arc for a single profile.
    arc: flat list, v2 dict, or any format accepted by _extract_plays_for_planning().
    """
    strips = _load_strips()
    arc_seq = _extract_plays_for_planning(arc)
    branch_blocks = _extract_branch_blocks(arc)
    total = len(arc_seq)
    planned_plays = []
    prior_spikes = 0
    prior_scaffold_count = 0  # I3: tracks cognitive scaffolding plays seen so far

    for i, entry in enumerate(arc_seq):
        pid = entry.get("id", "") if isinstance(entry, dict) else str(entry)
        day = entry.get("day", i) if isinstance(entry, dict) else i
        phase = entry.get("phase", "?") if isinstance(entry, dict) else "?"
        from_branch = entry.get("_from_branch") if isinstance(entry, dict) else None

        if pid not in strips:
            planned_plays.append({
                "id": pid, "day": day, "phase": phase,
                "error": f"Play '{pid}' not found in strip library.",
            })
            continue

        strip = strips[pid]

        # Inject scaffold count into profile for _engagement_prob to read (I3)
        profile["_prior_scaffold_count"] = prior_scaffold_count

        # Check if this participant is a witness at this play (for activated plays)
        # For now, plan as activated (full engagement); witness scoring is arc-level
        eng = _engagement_prob(strip, profile, prior_spikes, role="activated")
        fp = _failure_probs(strip, profile, eng)

        # Pull inline recovery block from arc entry if present
        inline_recovery = entry.get("recovery") if isinstance(entry, dict) else None
        recoveries = _recovery_plays(fp, strip, strips, inline_recovery)
        bail = _bail_classification(strip, i, total, arc_seq, i)
        warnings = _play_warnings(pid, profile, prior_scaffold_count)

        if strip.beat == "^":
            prior_spikes += 1
        else:
            prior_spikes = 0

        # Advance scaffold count after scoring this play
        play_mech_set = set(_play_mechs(pid))
        if play_mech_set & _COGNITIVE_SCAFFOLD_MECHS:
            prior_scaffold_count += 1

        # G1: expected_participation from arc element → effective engagement for ensemble/lottery plays
        expected_participation = (
            entry.get("expected_participation") if isinstance(entry, dict) else None
        )
        effective_eng = None
        lottery_unfired_eng = None
        if expected_participation is not None:
            if strip.group_role == "e":
                effective_eng = round(eng * expected_participation)
            elif strip.group_role == "lo":
                # Lottery beats bifurcate: fired path gets full engagement, unfired path drops the beat
                effective_eng = eng  # fired path — full engagement
                lottery_unfired_eng = 0  # unfired path — beat absent

        play_plan = {
            "id": pid,
            "day": day,
            "phase": phase,
            "beat": strip.beat,
            "beat_name": {"/": "ramp", "^": "spike", "_": "hold", "-": "rest",
                          ">": "transition", "~": "liminal"}.get(strip.beat, strip.beat),
            "intensity": strip.intensity,
            "detection": strip.detection,
            "reversibility": strip.reversibility,
            "requires_confederate": strip.requires_confederate,
            "grants": strip.permission_grant,
            "group_role": strip.group_role,
            "social_modifier": strip.social_modifier,
            "activation_rate": strip.activation_rate,
            "persona_bound": strip.persona_bound,   # N1
            "engagement_pct": eng,
            "failure_modes": fp,
            "recovery_plays": recoveries,
            "bail": bail,
            "warnings": warnings,
        }
        if expected_participation is not None:
            play_plan["expected_participation"] = expected_participation
        if effective_eng is not None:
            play_plan["effective_engagement_pct"] = effective_eng
        if lottery_unfired_eng is not None:
            play_plan["lottery_unfired_engagement_pct"] = lottery_unfired_eng
        if from_branch:
            play_plan["merge_point_for"] = from_branch
        planned_plays.append(play_plan)

    # Plan branch plays (annotated, not in main sequence)
    branch_plans = []
    for block in branch_blocks:
        block_plan = {
            "id": block.get("id"),
            "day": block.get("day"),
            "phase": block.get("phase"),
            "branches": {},
        }
        branches = block.get("branches", {})
        for branch_name, branch_data in branches.items():
            if not isinstance(branch_data, dict):
                continue
            role = "witness" if branch_name == "witness" else "activated"
            branch_plays = []
            branch_prior_spikes = 0
            for bp in branch_data.get("plays", []):
                bpid = bp.get("id", "")
                bphase = bp.get("phase", "?")
                if bpid not in strips:
                    branch_plays.append({"id": bpid, "error": "not found"})
                    continue
                bstrip = strips[bpid]
                beng = _engagement_prob(bstrip, profile, branch_prior_spikes, role=role)
                bfp = _failure_probs(bstrip, profile, beng)
                brecoveries = _recovery_plays(bfp, bstrip, strips)
                if bstrip.beat == "^":
                    branch_prior_spikes += 1
                else:
                    branch_prior_spikes = 0
                branch_plays.append({
                    "id": bpid,
                    "phase": bphase,
                    "role": role,
                    "beat": bstrip.beat,
                    "engagement_pct": beng,
                    "failure_modes": bfp,
                    "recovery_plays": brecoveries,
                })
            block_plan["branches"][branch_name] = {
                "participants": branch_data.get("participants", ""),
                "plays": branch_plays,
                "grants": branch_data.get("grants", []),
            }
        branch_plans.append(block_plan)

    profile.pop("_prior_scaffold_count", None)  # remove temp field injected for scoring

    bail_days = [p["day"] for p in planned_plays if p.get("bail", {}).get("is_bail_point")]
    operator_holds = [p["day"] for p in planned_plays if p.get("bail", {}).get("bail_type") == "operator_hold"]
    avg_eng = round(sum(p.get("engagement_pct", 0) for p in planned_plays) / max(len(planned_plays), 1))
    weakest = min((p for p in planned_plays if "engagement_pct" in p),
                  key=lambda x: x["engagement_pct"], default=None)

    all_warnings = [
        (p["id"], w) for p in planned_plays
        for w in p.get("warnings", [])
    ]

    result = {
        "participant": profile.get("name", "unknown"),
        "total_plays": total,
        "avg_engagement_pct": avg_eng,
        "weakest_play": weakest["id"] if weakest else None,
        "weakest_play_pct": weakest["engagement_pct"] if weakest else None,
        "bail_days": bail_days,
        "operator_hold_days": operator_holds,
        "warning_count": len(all_warnings),
        "plays": planned_plays,
    }
    if branch_plans:
        result["branch_plans"] = branch_plans
    return result


# ── CLI ───────────────────────────────────────────────────────────────────────

def _eng_bucket(pct: int | None) -> str:
    """P1: Convert raw engagement % to ordinal bucket label."""
    if pct is None:
        return "unknown"
    if pct >= 70:
        return "strong"
    if pct >= 50:
        return "moderate"
    return "weak"


def _print_plan(plan: dict) -> None:
    print(f"\nARC PLAN — {plan['participant']}")
    print("═" * 70)
    weakest_pct = plan['weakest_play_pct']
    avg_pct = plan['avg_engagement_pct']
    print(f"Plays: {plan['total_plays']}   "
          f"Avg engagement: {_eng_bucket(avg_pct)}")
    print(f"Weakest play: {plan['weakest_play']} ({_eng_bucket(weakest_pct)})")
    print(f"Bail points: days {plan['bail_days']}")
    print(f"Operator holds before: days {plan['operator_hold_days']}")
    if plan.get("warning_count", 0):
        print(f"Profile warnings: {plan['warning_count']} (see ⚠ below)")
    print()

    for p in plan["plays"]:
        if "error" in p:
            print(f"  [d{p['day']:>2}] {p['id']:<40} ERROR: {p['error']}")
            continue

        beat_sym = {"ramp": "/", "spike": "^", "hold": "_", "rest": "-",
                    "transition": ">", "liminal": "~"}.get(p["beat_name"], p["beat"])
        eng = p["engagement_pct"]
        bar_len = eng // 5
        bar = "█" * bar_len + "░" * (20 - bar_len)
        bucket = _eng_bucket(eng)

        bail_info = p.get("bail", {})
        bail_tag = ""
        if bail_info.get("bail_type") == "explicit":
            bail_tag = " [EXIT]"
        elif bail_info.get("bail_type") == "natural":
            bail_tag = " [bail]"
        elif bail_info.get("bail_type") == "operator_hold":
            bail_tag = " [HOLD→next]"

        grp = p.get("group_role", "s")
        grp_tag = f" [{grp}]" if grp != "s" else ""
        pb_tag = " [pb]" if p.get("persona_bound") else ""
        cov_tag = ""
        if p.get("lottery_unfired_engagement_pct") is not None:
            ep = p.get("expected_participation", 0.1)
            cov_tag = (f" (lottery: {_eng_bucket(p['effective_engagement_pct'])} if selected "
                       f"[{ep:.0%}] / arc continues if not)")
        elif p.get("effective_engagement_pct") is not None:
            eff = p["effective_engagement_pct"]
            ep = p.get("expected_participation", 1.0)
            cov_tag = f" (eff={_eng_bucket(eff)} @{ep:.0%})"

        print(f"  [d{p['day']:>2}] {beat_sym} {p['id']:<36} {bar} {bucket}{bail_tag}{grp_tag}{pb_tag}{cov_tag}")

        fp = p.get("failure_modes", {})
        top_fails = sorted(fp.items(), key=lambda x: -x[1])[:2]
        for mode, prob in top_fails:
            if prob > 3:
                recoveries = p.get("recovery_plays", {}).get(mode, [])
                rec_str = " → " + ", ".join(recoveries[:2]) if recoveries else ""
                print(f"         if {mode} ({prob}%){rec_str}")

        if bail_info.get("bail_note"):
            print(f"         ↳ {bail_info['bail_note']}")

        for warn in p.get("warnings", []):
            print(f"         ⚠  {warn}")

        print()

    if plan.get("branch_plans"):
        print("BRANCH PLANS:")
        for block in plan["branch_plans"]:
            print(f"  [{block['id']}]")
            for bname, bdata in block.get("branches", {}).items():
                plays = bdata.get("plays", [])
                avg = round(sum(p.get("engagement_pct", 0) for p in plays if "engagement_pct" in p)
                            / max(1, len(plays)))
                print(f"    {bname}: {len(plays)} plays, avg {avg}%")


def _fit_score_play(strip: Strip, profile: dict) -> tuple[int, list[str], list[str]]:
    """
    Compute engagement % for a single play against a profile, plus matching and gap mechanisms.
    Returns (engagement_pct, matching_mechs, gap_mechs).
    """
    match = _mech_score(strip.id, profile)
    base = 60.0
    base += (match - 0.5) * 40

    sensitivity = profile.get("sensitivity", "medium")
    base += SENSITIVITY_INTENSITY_FIT.get((sensitivity, strip.intensity), 0) * 100

    bf = profile.get("big_five", {})
    O = bf.get("O", 0)
    C = bf.get("C", 0)
    N = bf.get("N", 0)
    E = bf.get("E", 0)

    play_mech_set = set(_play_mechs(strip.id))

    if play_mech_set & _O_MECHS:
        base += O * 4
    if strip.beat == "/":
        base += C * 3
    if strip.detection == "h" or play_mech_set & _N_MECHS:
        base -= N * 4
    if any(m in play_mech_set for m in ("social_proof", "belonging", "direct_interaction",
                                         "dyadic_interaction", "status_selection")):
        base += E * 4

    base = max(20.0, min(95.0, base))
    eng = round(base)

    # Matching mechanisms: profile mechs that appear in this play, sorted by weight desc
    profile_mechs = profile.get("mechanisms", {})
    matching = sorted(
        [pm for pm in profile_mechs if pm in play_mech_set],
        key=lambda m: -profile_mechs.get(m, 0)
    )
    # Gap mechanisms: top profile mechs NOT in this play
    gap = sorted(
        [pm for pm in profile_mechs if pm not in play_mech_set],
        key=lambda m: -profile_mechs.get(m, 0)
    )

    return eng, matching, gap


def fit_report(profile: dict) -> dict:
    """
    Score every play in the library against a profile.
    Returns dict with bucketed play lists: strong / moderate / weak.
    """
    strips = _parse_strips(STRIPS_FILE)
    _load_mech_index()

    results = []
    for play_id, strip in strips.items():
        eng, matching, gap = _fit_score_play(strip, profile)
        results.append({
            "id": play_id,
            "arc_fit": strip.arc_fit,
            "beat": strip.beat,
            "engagement_pct": eng,
            "matching_mechs": matching[:5],
            "gap_mechs": gap[:5],
        })

    results.sort(key=lambda x: -x["engagement_pct"])

    strong   = [r for r in results if r["engagement_pct"] >= 70]
    moderate = [r for r in results if 50 <= r["engagement_pct"] < 70]
    weak     = [r for r in results if r["engagement_pct"] < 50]

    profile_mechs = profile.get("mechanisms", {})
    top_profile = sorted(profile_mechs.keys(), key=lambda m: -profile_mechs.get(m, 0))[:8]

    return {
        "participant": profile.get("name", "unknown"),
        "top_profile_mechanisms": top_profile,
        "strong": strong,
        "moderate": moderate,
        "weak": weak,
    }


def _print_fit_report(report: dict, show_weak: bool = False, max_per_bucket: int = 30) -> None:
    name = report["participant"]
    top = " · ".join(report["top_profile_mechanisms"])
    strong   = report["strong"]
    moderate = report["moderate"]
    weak     = report["weak"]

    print(f"\nFIT REPORT — {name}")
    print("═" * 70)
    print(f"Profile top mechanisms: {top}")
    print(f"Library: {len(strong)+len(moderate)+len(weak)} plays  |  "
          f"strong: {len(strong)}  moderate: {len(moderate)}  weak: {len(weak)}")
    print()

    def _bucket_lines(plays: list[dict], label: str, show_all: bool) -> None:
        shown = plays if show_all else plays[:max_per_bucket]
        for p in shown:
            match_str = " · ".join(p["matching_mechs"][:3]) or "(none)"
            print(f"  {p['id']:<40} {p['arc_fit']:<20} {label}  {p['engagement_pct']}%")
            print(f"    matches: {match_str}")
            if label == "weak" and p["gap_mechs"]:
                gap_str = " · ".join(p["gap_mechs"][:3])
                print(f"    gaps:    {gap_str}")
        if not show_all and len(plays) > max_per_bucket:
            print(f"  ... and {len(plays) - max_per_bucket} more")
        print()

    print(f"STRONG (≥70%)  [{len(strong)} plays]")
    print("─" * 70)
    _bucket_lines(strong, "strong", show_all=False)

    print(f"MODERATE (50-70%)  [{len(moderate)} plays]")
    print("─" * 70)
    _bucket_lines(moderate, "moderate", show_all=False)

    if show_weak:
        print(f"WEAK (<50%)  [{len(weak)} plays]")
        print("─" * 70)
        _bucket_lines(weak, "weak", show_all=False)
    else:
        print(f"WEAK (<50%)  [{len(weak)} plays — omitted; use --show-weak to display]")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Arc planner: annotate arc with engagement, bail points, and recovery branches.")
    parser.add_argument("--arc", help="Arc JSON file (v1 list or v2 dict) — required unless --fit-report")
    parser.add_argument("--profile", required=True, help="Participant profile JSON file")
    parser.add_argument("--out", help="Output plan JSON file (default: stdout + print)")
    parser.add_argument("--fit-report", action="store_true",
                        help="Show mechanism fit report for all plays against the profile (design-time mode)")
    parser.add_argument("--show-weak", action="store_true",
                        help="Include weak-fit plays in fit report output")
    args = parser.parse_args()

    profile_path = Path(args.profile)
    if not profile_path.exists():
        print(f"ERROR: profile file not found: {profile_path}", file=sys.stderr)
        sys.exit(2)
    profile = json.loads(profile_path.read_text())

    if args.fit_report:
        report = fit_report(profile)
        _print_fit_report(report, show_weak=args.show_weak)
        if args.out:
            Path(args.out).write_text(json.dumps(report, indent=2))
            print(f"\nFit report written to: {args.out}")
        return

    if not args.arc:
        print("ERROR: --arc is required unless --fit-report is specified", file=sys.stderr)
        sys.exit(2)

    arc_path = Path(args.arc)
    if not arc_path.exists():
        print(f"ERROR: arc file not found: {arc_path}", file=sys.stderr)
        sys.exit(2)

    arc = json.loads(arc_path.read_text())
    plan = plan_arc(arc, profile)
    _print_plan(plan)

    if args.out:
        Path(args.out).write_text(json.dumps(plan, indent=2))
        print(f"\nPlan written to: {args.out}")
    else:
        print("\n(Use --out plan.json to save for simulator)")


if __name__ == "__main__":
    main()
