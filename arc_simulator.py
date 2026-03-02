#!/usr/bin/env python3
"""
arc_simulator.py

Runs probabilistic simulation of an arc plan against a participant profile.
Consumes output of arc_planner.py. Produces a scenario report showing:
  - Predicted arc path (most likely)
  - Failure rate per play
  - Most common recovery plays triggered
  - Overall completion rate
  - Scenario variants (best case / worst case / median)

Usage:
  python arc_simulator.py --plan arc_plan.json --profile profile.json
  python arc_simulator.py --plan arc_plan.json --profile profile.json --runs 500 --seed 42
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── DATA STRUCTURES ───────────────────────────────────────────────────────────

@dataclass
class PlayOutcome:
    id: str
    day: int
    phase: str
    engaged: bool
    failure_mode: Optional[str]         # None if engaged
    recovery_played: Optional[str]      # None if engaged
    arc_continues: bool                  # False = arc ends here


@dataclass
class SimRun:
    outcomes: list[PlayOutcome] = field(default_factory=list)
    completed: bool = False             # Reached final play
    terminated_at: Optional[str] = None
    bail_taken: bool = False
    recovery_count: int = 0


# ── SIMULATION CORE ───────────────────────────────────────────────────────────

def _sample_failure_mode(failure_modes: dict, rng: random.Random) -> str:
    """Sample a failure mode from the probability distribution."""
    modes = [(mode, prob) for mode, prob in failure_modes.items() if prob > 0]
    if not modes:
        return "cold"

    total = sum(p for _, p in modes)
    r = rng.uniform(0, total)
    cumulative = 0
    for mode, prob in modes:
        cumulative += prob
        if r <= cumulative:
            return mode
    return modes[-1][0]


def _choose_recovery(recovery_plays: dict, failure_mode: str, rng: random.Random) -> Optional[str]:
    """Pick a recovery play for the given failure mode."""
    candidates = recovery_plays.get(failure_mode, [])
    if not candidates:
        return None
    # Prefer first candidate (highest-priority), with some randomness
    weights = [max(1, 10 - i * 3) for i in range(len(candidates))]
    return rng.choices(candidates, weights=weights, k=1)[0]


def _run_once(plan: dict, profile: dict, rng: random.Random) -> SimRun:
    """Simulate one run of the arc."""
    run = SimRun()
    plays = plan["plays"]
    accumulated_grants: set[str] = set()
    consecutive_failures = 0

    for i, play in enumerate(plays):
        if "error" in play:
            # Skip errored plays in simulation
            continue

        pid = play["id"]
        day = play.get("day", i)
        phase = play.get("phase", "?")
        beat = play.get("beat", "/")
        eng_pct = play.get("engagement_pct", 60)
        failure_modes = play.get("failure_modes", {})
        recovery_plays_map = play.get("recovery_plays", {})
        bail_info = play.get("bail", {})

        # Liminal beats always succeed — structural, not experiential
        if beat == "~" or eng_pct == 100:
            run.outcomes.append(PlayOutcome(
                id=pid, day=day, phase=phase,
                engaged=True, failure_mode=None, recovery_played=None,
                arc_continues=True,
            ))
            if play.get("grants"):
                accumulated_grants.add(play["grants"])
            continue

        # Adjust engagement based on arc state
        adj_eng = eng_pct

        # Accumulated engagement momentum: prior successes increase probability
        adj_eng += min(consecutive_failures * -5, 0)   # failures drag momentum

        # Check grants — if play requires grant that's been produced, bonus
        grants = play.get("grants", "")
        if grants and grants in accumulated_grants:
            adj_eng += 5  # already set up

        adj_eng = max(5, min(98, adj_eng))

        # Roll for engagement
        engaged = rng.randint(1, 100) <= adj_eng

        if engaged:
            consecutive_failures = 0
            # Accumulate grants from this play
            if grants:
                accumulated_grants.add(grants)

            outcome = PlayOutcome(
                id=pid, day=day, phase=phase,
                engaged=True, failure_mode=None, recovery_played=None,
                arc_continues=True,
            )
            run.outcomes.append(outcome)

        else:
            consecutive_failures += 1
            failure_mode = _sample_failure_mode(failure_modes, rng)
            recovery = _choose_recovery(recovery_plays_map, failure_mode, rng)
            if recovery == "OPERATOR_PAUSE":
                recovery = None

            # Determine if arc continues after failure
            arc_continues = True

            if failure_mode == "distressed":
                # Distress always pauses; high chance of termination
                if rng.random() < 0.4:
                    arc_continues = False
                    run.terminated_at = pid
                    run.bail_taken = True
            elif failure_mode == "cold" and consecutive_failures >= 2:
                # Two consecutive cold failures: check bail point
                if bail_info.get("is_bail_point") or bail_info.get("bail_type") == "natural":
                    if rng.random() < 0.6:
                        arc_continues = False
                        run.terminated_at = pid
                        run.bail_taken = True

            if recovery:
                run.recovery_count += 1

            outcome = PlayOutcome(
                id=pid, day=day, phase=phase,
                engaged=False, failure_mode=failure_mode, recovery_played=recovery,
                arc_continues=arc_continues,
            )
            run.outcomes.append(outcome)

            if not arc_continues:
                break

        # Explicit bail point: participant opts out (low probability if engaged)
        if engaged and bail_info.get("bail_type") == "explicit":
            if rng.random() < 0.05:  # 5% chance to exit even when engaged
                run.bail_taken = True
                run.terminated_at = pid
                break

    # Arc completed if last outcome is engagement and no termination
    if not run.terminated_at:
        engaged_outcomes = [o for o in run.outcomes if o.engaged]
        if engaged_outcomes and engaged_outcomes[-1].id == plays[-1]["id"]:
            run.completed = True
        elif len([o for o in run.outcomes if o.engaged]) >= len(plays) * 0.8:
            run.completed = True

    return run


# ── ANALYSIS ──────────────────────────────────────────────────────────────────

def _analyze(runs: list[SimRun], plan: dict) -> dict:
    n = len(runs)
    plays = [p["id"] for p in plan["plays"] if "error" not in p]
    # Exclude liminal beats from length for normalization purposes
    scored_plays = [p["id"] for p in plan["plays"]
                    if "error" not in p and p.get("beat") != "~" and p.get("engagement_pct", 60) < 100]
    n_scored = max(len(scored_plays), 1)

    # Completion rate
    completed = sum(1 for r in runs if r.completed)
    completion_rate = round(completed / n * 100)

    # Per-play engagement rate (normalized): geometric mean across scored plays
    # = completion_rate ^ (1/n_scored), i.e. the avg single-play engagement implied
    import math
    if completion_rate > 0 and n_scored > 1:
        per_play_rate = round((completion_rate / 100) ** (1.0 / n_scored) * 100)
    else:
        per_play_rate = completion_rate

    # Bail rate
    bailed = sum(1 for r in runs if r.bail_taken)
    bail_rate = round(bailed / n * 100)

    # Per-play: failure rate, most common failure mode, most common recovery
    play_stats: dict[str, dict] = {}
    for pid in plays:
        all_outcomes = [o for r in runs for o in r.outcomes if o.id == pid]
        if not all_outcomes:
            continue
        engaged = sum(1 for o in all_outcomes if o.engaged)
        failed = len(all_outcomes) - engaged
        failure_modes = Counter(o.failure_mode for o in all_outcomes if not o.engaged)
        recoveries = Counter(o.recovery_played for o in all_outcomes if o.recovery_played)

        play_stats[pid] = {
            "seen": len(all_outcomes),
            "engaged_pct": round(engaged / len(all_outcomes) * 100),
            "failed_pct": round(failed / len(all_outcomes) * 100),
            "top_failure": failure_modes.most_common(1)[0] if failure_modes else None,
            "top_recovery": recoveries.most_common(1)[0] if recoveries else None,
        }

    # Termination points
    terminations = Counter(r.terminated_at for r in runs if r.terminated_at)

    # Average recovery count
    avg_recoveries = sum(r.recovery_count for r in runs) / n

    # Scenario variants: categorize runs
    def _run_category(run: SimRun) -> str:
        if run.completed and run.recovery_count == 0:
            return "clean"
        elif run.completed:
            return "recovered"
        elif run.bail_taken:
            return "bail"
        else:
            return "stalled"

    categories = Counter(_run_category(r) for r in runs)

    return {
        "runs": n,
        "n_scored_plays": n_scored,
        "completion_rate": completion_rate,
        "per_play_rate": per_play_rate,
        "bail_rate": bail_rate,
        "avg_recovery_count": round(avg_recoveries, 1),
        "scenario_breakdown": dict(categories),
        "termination_points": dict(terminations.most_common(5)),
        "play_stats": play_stats,
    }


# ── REPORT ────────────────────────────────────────────────────────────────────

def _print_report(analysis: dict, plan: dict) -> None:
    participant = plan.get("participant", "unknown")
    n = analysis["runs"]

    print(f"\nARC SIMULATION — {participant}  ({n} runs)")
    print("═" * 70)
    n_sp = analysis.get("n_scored_plays", "?")
    print(f"Completion rate:  {analysis['completion_rate']}%  ({n_sp} scored plays)")
    print(f"Per-play rate:    {analysis['per_play_rate']}%  (length-normalized geometric mean)")
    print(f"Bail rate:        {analysis['bail_rate']}%")
    print(f"Avg recoveries:   {analysis['avg_recovery_count']} per run")
    print()

    cats = analysis["scenario_breakdown"]
    total = sum(cats.values())
    print("Scenario breakdown:")
    for cat in ["clean", "recovered", "bail", "stalled"]:
        pct = round(cats.get(cat, 0) / total * 100)
        bar = "█" * (pct // 3) + "░" * (33 - pct // 3)
        print(f"  {cat:<12} {bar} {pct}%")
    print()

    if analysis["termination_points"]:
        print("Most common bail / stall points:")
        for pid, count in analysis["termination_points"].items():
            pct = round(count / n * 100)
            print(f"  {pid:<40} {pct}%")
        print()

    print("Per-play engagement (simulated):")
    print(f"  {'Play':<40} {'Seen':>5} {'Eng%':>5} {'Top failure':>14} {'Top recovery':>30}")
    print("  " + "─" * 100)

    plays = [p["id"] for p in plan["plays"] if "error" not in p]
    for pid in plays:
        stat = analysis["play_stats"].get(pid)
        if not stat:
            print(f"  {pid:<40} {'—':>5}")
            continue

        eng = stat["engaged_pct"]
        bar_len = eng // 5
        bar = "█" * bar_len + "░" * (20 - bar_len)

        top_fail = ""
        if stat["top_failure"]:
            mode, cnt = stat["top_failure"]
            pct = round(cnt / stat["seen"] * 100)
            top_fail = f"{mode} ({pct}%)"

        top_rec = ""
        if stat["top_recovery"]:
            rec, cnt = stat["top_recovery"]
            top_rec = rec

        # Flag weak plays
        flag = " ⚠" if eng < 55 else "  "
        print(f"  {pid:<40} {stat['seen']:>5} {bar} {eng:>3}%{flag} {top_fail:>14}  {top_rec:<30}")

    print()
    print("⚠ = simulated engagement below 55% — consider strengthening or adding recovery branch")
    print()

    # Actionable callouts
    weak_plays = [(pid, s["engaged_pct"]) for pid, s in analysis["play_stats"].items() if s["engaged_pct"] < 55]
    if weak_plays:
        print("CALLOUTS:")
        for pid, pct in sorted(weak_plays, key=lambda x: x[1]):
            rec = analysis["play_stats"][pid].get("top_recovery")
            rec_name = rec[0] if rec else "none triggered"
            print(f"  {pid} — {pct}% engagement. Most common recovery: {rec_name}")
        print()


# ── SCENARIO DETAIL ───────────────────────────────────────────────────────────

def _print_sample_runs(runs: list[SimRun], plan: dict, count: int = 3) -> None:
    """Print a few representative run transcripts."""
    # Best run (most plays completed, fewest recoveries)
    def _run_score(r: SimRun) -> tuple:
        return (len([o for o in r.outcomes if o.engaged]), -r.recovery_count)

    sorted_runs = sorted(runs, key=_run_score, reverse=True)
    samples = [
        ("Best case",   sorted_runs[0]),
        ("Median",      sorted_runs[len(sorted_runs) // 2]),
        ("Worst case",  sorted_runs[-1]),
    ]

    print("─" * 70)
    print("SAMPLE SCENARIOS")
    print()

    for label, run in samples:
        completed_str = "COMPLETED" if run.completed else f"BAILED at {run.terminated_at}" if run.bail_taken else "STALLED"
        print(f"  [{label}] — {completed_str}  |  {run.recovery_count} recovery plays")
        for o in run.outcomes:
            status = "✓" if o.engaged else "✗"
            detail = ""
            if not o.engaged:
                detail = f"  → {o.failure_mode}"
                if o.recovery_played:
                    detail += f" / played: {o.recovery_played}"
            print(f"    {status} d{o.day:<3} {o.id:<40}{detail}")
        print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Arc simulator: run probabilistic scenarios through an arc plan.")
    parser.add_argument("--plan", required=True, help="Arc plan JSON (from arc_planner.py)")
    parser.add_argument("--profile", required=True, help="Participant profile JSON")
    parser.add_argument("--runs", type=int, default=200, help="Number of simulation runs (default: 200)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--scenarios", action="store_true", help="Print sample run transcripts")
    args = parser.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"ERROR: plan file not found: {plan_path}", file=sys.stderr)
        sys.exit(2)

    profile_path = Path(args.profile)
    if not profile_path.exists():
        print(f"ERROR: profile file not found: {profile_path}", file=sys.stderr)
        sys.exit(2)

    plan = json.loads(plan_path.read_text())
    profile = json.loads(profile_path.read_text())

    rng = random.Random(args.seed)
    runs = [_run_once(plan, profile, rng) for _ in range(args.runs)]

    analysis = _analyze(runs, plan)
    _print_report(analysis, plan)

    if args.scenarios:
        _print_sample_runs(runs, plan)


if __name__ == "__main__":
    main()
