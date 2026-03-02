#!/usr/bin/env python3
"""
arc_matchmaker.py

Pre-arc planning tool: given a pool of profiles and a candidate arc,
suggests optimal group compositions and flags interpersonal dynamics.

Matchmaking runs BEFORE arc design — complementing arc_linter.py (which runs
AFTER). The matchmaker reads planner engagement matrices to find:
  - Complementary tension: near-opposite engagement on key plays
  - Mutual amplification: aligned high engagement on ensemble plays
  - Chronic underservice: a profile > 20% below group mean
  - Cascade risk: multiple profiles with same dominant failure mode on same plays

Usage:
  python arc_matchmaker.py --arc arc.json --profiles p1.json p2.json p3.json p4.json
  python arc_matchmaker.py --arc arc.json --profiles p1.json p2.json --out match.json
  python arc_matchmaker.py --arc arc.json --profiles-dir profiles/
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import NamedTuple

from arc_planner import plan_arc, _load_strips


# ── DATA STRUCTURES ───────────────────────────────────────────────────────────

class ProfileEngagement(NamedTuple):
    profile_id: str
    name: str
    play_scores: dict[str, int]   # play_id → engagement_pct
    play_failures: dict[str, dict[str, int]]  # play_id → failure_modes dict
    avg: float


class MatchFlag(NamedTuple):
    kind: str       # complementary_tension | mutual_amplification | chronic_underservice | cascade_risk
    severity: str   # INFO | WARN
    profiles: list[str]
    play_id: str | None
    message: str

    def __str__(self):
        ps = ", ".join(self.profiles)
        play = f" [{self.play_id}]" if self.play_id else ""
        return f"  [{self.severity}] {self.kind}{play}: {ps}\n         {self.message}"


# ── ENGAGEMENT MATRIX ─────────────────────────────────────────────────────────

def build_engagement_matrix(arc, profiles: list[dict]) -> list[ProfileEngagement]:
    """Run planner for each profile and build engagement matrix."""
    matrix = []
    for profile in profiles:
        plan = plan_arc(arc, profile)
        play_scores = {}
        play_failures = {}
        for play in plan.get("plays", []):
            pid = play.get("id", "")
            if "engagement_pct" in play:
                play_scores[pid] = play["engagement_pct"]
                play_failures[pid] = play.get("failure_modes", {})
        avg = plan.get("avg_engagement_pct", 0)
        pid_str = profile.get("id", profile.get("name", "?").lower().replace(" ", "_"))
        matrix.append(ProfileEngagement(
            profile_id=pid_str,
            name=profile.get("name", pid_str),
            play_scores=play_scores,
            play_failures=play_failures,
            avg=avg,
        ))
    return matrix


# ── MATCHMAKING FLAGS ─────────────────────────────────────────────────────────

COMPLEMENTARY_TENSION_THRESHOLD = 25   # pct gap to flag as complementary tension
MUTUAL_AMP_THRESHOLD = 70              # both profiles above this on same play
UNDERSERVICE_THRESHOLD = 20            # pct below group mean
CASCADE_THRESHOLD = 0.40               # dominant failure mode weight


def check_complementary_tension(
    matrix: list[ProfileEngagement],
    arc,
) -> list[MatchFlag]:
    """Flag pairs with near-opposite engagement on key plays (useful for designed ensemble)."""
    flags = []
    strips = _load_strips()
    all_play_ids = list({pid for pe in matrix for pid in pe.play_scores})

    for pa, pb in combinations(matrix, 2):
        shared = set(pa.play_scores) & set(pb.play_scores)
        for play_id in shared:
            a_score = pa.play_scores[play_id]
            b_score = pb.play_scores[play_id]
            gap = abs(a_score - b_score)
            if gap >= COMPLEMENTARY_TENSION_THRESHOLD:
                strip = strips.get(play_id)
                is_ensemble = strip and strip.group_role in ("e", "ac")
                if is_ensemble:
                    flags.append(MatchFlag(
                        kind="complementary_tension",
                        severity="INFO",
                        profiles=[pa.profile_id, pb.profile_id],
                        play_id=play_id,
                        message=(f"{pa.name} ({a_score}%) vs {pb.name} ({b_score}%) — "
                                 f"{gap}pt gap on ensemble play. "
                                 f"Their divergent response IS the scene.")
                    ))
    return flags


def check_mutual_amplification(
    matrix: list[ProfileEngagement],
    arc,
) -> list[MatchFlag]:
    """Flag plays where multiple profiles all score high (good communitas moments)."""
    flags = []
    strips = _load_strips()
    all_play_ids = list({pid for pe in matrix for pid in pe.play_scores})

    for play_id in all_play_ids:
        scores = [(pe.profile_id, pe.name, pe.play_scores[play_id])
                  for pe in matrix if play_id in pe.play_scores]
        if len(scores) < 2:
            continue
        high_scorers = [(pid, name, s) for pid, name, s in scores if s >= MUTUAL_AMP_THRESHOLD]
        if len(high_scorers) >= 2:
            strip = strips.get(play_id)
            is_ensemble = strip and strip.group_role in ("e", "am")
            if is_ensemble:
                names = ", ".join(f"{name} ({s}%)" for _, name, s in high_scorers)
                flags.append(MatchFlag(
                    kind="mutual_amplification",
                    severity="INFO",
                    profiles=[pid for pid, _, _ in high_scorers],
                    play_id=play_id,
                    message=f"Aligned high engagement on ensemble play: {names} — strong communitas potential."
                ))
    return flags


def check_chronic_underservice(
    matrix: list[ProfileEngagement],
) -> list[MatchFlag]:
    """Flag profiles whose arc-level average is > 20% below group mean (GROUP_FLOOR)."""
    flags = []
    if not matrix:
        return flags

    group_mean = sum(pe.avg for pe in matrix) / len(matrix)

    for pe in matrix:
        gap = group_mean - pe.avg
        if gap > UNDERSERVICE_THRESHOLD:
            flags.append(MatchFlag(
                kind="chronic_underservice",
                severity="WARN",
                profiles=[pe.profile_id],
                play_id=None,
                message=(f"{pe.name} avg {pe.avg:.0f}% vs group mean {group_mean:.0f}% "
                         f"({gap:.0f}pt below) — this participant is chronically underserved. "
                         f"Reconsider arc plays or reconfigure group.")
            ))
    return flags


def check_cascade_risk(
    matrix: list[ProfileEngagement],
) -> list[MatchFlag]:
    """
    Flag plays where 2+ profiles share the same dominant failure mode
    with high probability — if one cold-fails, others likely do too.
    """
    flags = []
    all_play_ids = list({pid for pe in matrix for pid in pe.play_failures})

    for play_id in all_play_ids:
        failure_profiles: dict[str, list[str]] = {}  # failure_mode → profile names
        for pe in matrix:
            if play_id not in pe.play_failures:
                continue
            fp = pe.play_failures[play_id]
            if not fp:
                continue
            dominant_mode = max(fp, key=fp.get)
            dominant_weight = fp[dominant_mode] / max(sum(fp.values()), 1)
            if dominant_weight >= CASCADE_THRESHOLD:
                failure_profiles.setdefault(dominant_mode, []).append(pe.name)

        for mode, names in failure_profiles.items():
            if len(names) >= 2:
                flags.append(MatchFlag(
                    kind="cascade_risk",
                    severity="WARN",
                    profiles=[pe.profile_id for pe in matrix
                              if pe.name in names],
                    play_id=play_id,
                    message=(f"{', '.join(names)} all likely to fail as '{mode}' — "
                             f"if one disengages, others follow. "
                             f"Add a recovery beat or redesign play for this group.")
                ))
    return flags


# ── PAIRWISE COMPATIBILITY ────────────────────────────────────────────────────

def pairwise_compatibility(
    pa: ProfileEngagement,
    pb: ProfileEngagement,
    strips: dict,
) -> dict:
    """Score compatibility between two profiles for ensemble plays."""
    shared = set(pa.play_scores) & set(pb.play_scores)
    ensemble_plays = [pid for pid in shared
                      if strips.get(pid) and strips[pid].group_role in ("e", "ac", "am")]

    if not ensemble_plays:
        return {"score": 0.5, "note": "No ensemble plays to score"}

    diffs = [abs(pa.play_scores[pid] - pb.play_scores[pid]) for pid in ensemble_plays]
    avg_diff = sum(diffs) / len(diffs)

    # Lower diff = higher alignment (good for communitas)
    # Higher diff = better tension (good for designed conflict)
    alignment = 1.0 - (avg_diff / 100.0)

    return {
        "profiles": [pa.profile_id, pb.profile_id],
        "ensemble_play_count": len(ensemble_plays),
        "avg_engagement_gap": round(avg_diff, 1),
        "alignment_score": round(alignment, 2),
        "note": ("High alignment — good communitas potential" if alignment > 0.75
                 else "High tension — good for designed conflict ensemble" if alignment < 0.4
                 else "Mixed — versatile grouping"),
    }


# ── MAIN MATCHMAKER ───────────────────────────────────────────────────────────

def match(arc, profiles: list[dict]) -> dict:
    """Run full matchmaking analysis."""
    matrix = build_engagement_matrix(arc, profiles)
    strips = _load_strips()

    flags = []
    flags.extend(check_complementary_tension(matrix, arc))
    flags.extend(check_mutual_amplification(matrix, arc))
    flags.extend(check_chronic_underservice(matrix))
    flags.extend(check_cascade_risk(matrix))

    # Pairwise compatibility table
    pairs = []
    for pa, pb in combinations(matrix, 2):
        pairs.append(pairwise_compatibility(pa, pb, strips))

    # Group summary
    group_mean = sum(pe.avg for pe in matrix) / len(matrix) if matrix else 0
    summary = {
        "group_size": len(matrix),
        "group_mean_engagement": round(group_mean, 1),
        "profiles": [
            {"id": pe.profile_id, "name": pe.name, "avg_engagement": round(pe.avg, 1)}
            for pe in matrix
        ],
    }

    return {
        "summary": summary,
        "flags": [
            {
                "kind": f.kind,
                "severity": f.severity,
                "profiles": f.profiles,
                "play": f.play_id,
                "message": f.message,
            }
            for f in flags
        ],
        "pairwise": pairs,
    }


def print_match_report(result: dict) -> None:
    summary = result["summary"]
    print(f"\nMATCHMAKING REPORT — {summary['group_size']} profiles")
    print("═" * 60)
    print(f"Group mean engagement: {summary['group_mean_engagement']}%")
    for p in summary["profiles"]:
        print(f"  {p['name']:<30} {p['avg_engagement']}%")
    print()

    flags = result["flags"]
    warns = [f for f in flags if f["severity"] == "WARN"]
    infos = [f for f in flags if f["severity"] == "INFO"]

    if warns:
        print(f"WARNINGS ({len(warns)}):")
        for f in warns:
            play = f" [{f['play']}]" if f["play"] else ""
            print(f"  [{f['kind']}{play}]")
            print(f"    Profiles: {', '.join(f['profiles'])}")
            print(f"    {f['message']}")
            print()

    if infos:
        print(f"INFO ({len(infos)}):")
        for f in infos:
            play = f" [{f['play']}]" if f["play"] else ""
            print(f"  [{f['kind']}{play}]")
            print(f"    Profiles: {', '.join(f['profiles'])}")
            print(f"    {f['message']}")
            print()

    if result["pairwise"]:
        print("PAIRWISE COMPATIBILITY:")
        for pair in result["pairwise"]:
            pa, pb = pair["profiles"]
            print(f"  {pa} × {pb}: gap={pair['avg_engagement_gap']}pt "
                  f"alignment={pair['alignment_score']} — {pair['note']}")
        print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Arc matchmaker: suggest group compositions from a profile pool")
    parser.add_argument("--arc", required=True, help="Arc JSON file")
    parser.add_argument("--profiles", nargs="+", help="Profile JSON files")
    parser.add_argument("--profiles-dir", help="Directory containing profile JSON files")
    parser.add_argument("--out", help="Output match JSON file")
    args = parser.parse_args()

    arc_path = Path(args.arc)
    if not arc_path.exists():
        print(f"ERROR: arc file not found: {arc_path}", file=sys.stderr)
        sys.exit(2)

    profile_paths = []
    if args.profiles:
        profile_paths.extend(Path(p) for p in args.profiles)
    if args.profiles_dir:
        profile_paths.extend(sorted(Path(args.profiles_dir).glob("*.json")))

    if not profile_paths:
        print("ERROR: provide --profiles or --profiles-dir", file=sys.stderr)
        sys.exit(2)

    arc = json.loads(arc_path.read_text())
    profiles = []
    for pp in profile_paths:
        if not pp.exists():
            print(f"WARN: profile not found: {pp}", file=sys.stderr)
            continue
        p = json.loads(pp.read_text())
        if "id" not in p:
            p["id"] = pp.stem
        profiles.append(p)

    if len(profiles) < 2:
        print("ERROR: need at least 2 profiles for matchmaking", file=sys.stderr)
        sys.exit(2)

    result = match(arc, profiles)
    print_match_report(result)

    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2))
        print(f"Match report written to: {args.out}")


if __name__ == "__main__":
    main()
