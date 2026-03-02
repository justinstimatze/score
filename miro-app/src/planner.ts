// planner.ts — TypeScript port of arc_planner.py
// Runs entirely client-side; no backend required.

import type {
  ArcElement,
  EngagementBucket,
  FailureModes,
  MechIndex,
  PlanEntry,
  PlanEntryError,
  PlanItem,
  PlanResult,
  Profile,
  StripMap,
  StripPlay,
} from "./types.js";

// ── MECHANISM SETS ───────────────────────────────────────────────────────────

const O_MECHS = new Set([
  "curiosity_exploration",
  "information_gap",
  "apophenia_induction",
  "anticipatory_attention",
  "participant_as_detective",
  "narrative_without_exposition",
  "object_archaeology",
  "environmental_semiotics",
  "knowledge_frontier",
  "curiosity_gap",
  "exploration_license",
]);

const C_MECHS = new Set([
  "pattern_completion",
  "need_for_closure",
  "commitment_consistency",
  "reward_escalation",
  "sequential_discovery",
  "pattern_recognition",
]);

const N_MECHS = new Set([
  "hypervigilance",
  "paranoia_escalation",
  "disorientation",
  "significance_quest",
  "hot_cold_empathy_gap",
  "threat_appraisal",
  "uncanny_recognition",
  "fear_of_missing",
]);

const DISORIENTATION_MECHS = new Set([
  "hypervigilance",
  "paranoia_escalation",
  "disorientation",
  "uncanny_recognition",
  "reality_rupture",
  "liminal_destabilization",
  "dissonance_induction",
  "threat_appraisal",
]);

const COGNITIVE_SCAFFOLD_MECHS = new Set([
  "curiosity_exploration",
  "information_gap",
  "participant_as_detective",
  "knowledge_frontier",
  "narrative_without_exposition",
  "pattern_recognition",
  "object_archaeology",
  "environmental_semiotics",
  "curiosity_gap",
  "apophenia_induction",
  "sequential_discovery",
  "need_for_cognition",
]);

const IDENTITY_MECHS: Record<string, Set<string>> = {
  interesting: new Set([
    "aesthetic_response",
    "creative_expression",
    "somatic_awareness",
    "embodied_cognition",
    "flow_state",
    "sensory_seeking",
  ]),
  creative: new Set([
    "creative_expression",
    "making_agency",
    "authorship_invitation",
    "craft_engagement",
    "creative_agency",
  ]),
  good: new Set([
    "prosocial_alignment",
    "moral_clarity",
    "care_expression",
    "ethical_weight",
    "moral_elevation",
  ]),
  brave: new Set([
    "ordeal_completion",
    "threshold_crossing",
    "discomfort_endurance",
    "physical_intensity",
    "courage_demand",
  ]),
  dependable: new Set([
    "commitment_consistency",
    "reliability_signal",
    "follow_through",
    "duty_activation",
  ]),
  perceptive: new Set([
    "pattern_recognition",
    "participant_as_detective",
    "knowledge_frontier",
    "curiosity_exploration",
    "information_gap",
    "curiosity_gap",
    "apophenia_induction",
  ]),
  influential: new Set([
    "significance_quest",
    "status_signal",
    "legacy_mark",
    "achievement_motivation",
    "social_proof",
  ]),
};

const SOCIAL_MECHS = new Set([
  "social_proof",
  "belonging",
  "direct_interaction",
  "dyadic_interaction",
  "status_selection",
]);

// ── SENSITIVITY × INTENSITY TABLE ────────────────────────────────────────────

const SENS_INT_FIT: Record<string, number> = {
  "low,1": 0.1,
  "low,2": 0.05,
  "low,3": -0.05,
  "low,4": -0.15,
  "medium,1": 0.0,
  "medium,2": 0.1,
  "medium,3": 0.08,
  "medium,4": -0.1,
  "high,1": -0.05,
  "high,2": 0.05,
  "high,3": 0.1,
  "high,4": 0.05,
};

// ── RECOVERY PLAYS ───────────────────────────────────────────────────────────

const RECOVERY_PLAYS: Record<string, string[]> = {
  cold: ["wrong_read_recovery", "breadcrumb_without_demand", "open_door_signal", "anomalous_receipt"],
  confused: ["elegant_failure", "misfire_as_story", "seam_acknowledgment"],
  distressed: ["seam_acknowledgment", "graceful_release", "OPERATOR_PAUSE"],
  over_engaged: ["optional_path", "open_door_signal", "OPERATOR_PAUSE"],
};

// ── MECHANISM SCORING ────────────────────────────────────────────────────────

function mechScore(
  playId: string,
  profile: Profile,
  mechIndex: MechIndex,
  mechOverride: string[] | null = null,
): number {
  const profileMechs = profile.mechanisms ?? {};
  const totalWeight = Object.values(profileMechs).reduce((a, b) => a + b, 0);
  if (!totalWeight) return 0.5;

  const playMechSet = new Set(mechOverride ?? (mechIndex[playId] ?? []));
  if (!playMechSet.size) return 0.5;

  let matched = 0;
  for (const [pmName, pmWeight] of Object.entries(profileMechs)) {
    if (playMechSet.has(pmName)) {
      matched += pmWeight;
    } else {
      const pmRoot = pmName.split("_")[0]!;
      for (const pm of playMechSet) {
        if (pm.includes(pmRoot) || pm.split("_")[0] === pmRoot) {
          matched += pmWeight * 0.4;
          break;
        }
      }
    }
  }
  return Math.min(matched / totalWeight, 1.0);
}

function getPlayMechs(playId: string, mechIndex: MechIndex): string[] {
  return mechIndex[playId] ?? [];
}

// ── ENGAGEMENT PROBABILITY ────────────────────────────────────────────────────

export function engagementProb(
  strip: StripPlay,
  profile: Profile,
  priorSpikes: number,
  mechIndex: MechIndex,
  scaffoldCount = 0,
  role = "activated",
): number {
  if (strip.beat === "~") return 100;

  const playMechSet = new Set(getPlayMechs(strip.id, mechIndex));

  if (role === "witness") {
    const overrideMechs = strip.witness_mechanisms.length ? strip.witness_mechanisms : null;
    const match = overrideMechs
      ? mechScore(strip.id, profile, mechIndex, overrideMechs)
      : 0.55;
    const base = 55.0 + (match - 0.5) * 30;
    return Math.round(Math.max(20, Math.min(85, base)));
  }

  let base = 60.0;
  const match = mechScore(strip.id, profile, mechIndex);
  base += (match - 0.5) * 40;

  const sensitivity = profile.sensitivity ?? "medium";
  base += (SENS_INT_FIT[`${sensitivity},${strip.intensity_int}`] ?? 0) * 100;

  const bf = profile.big_five ?? {};
  const O = bf.O ?? 0;
  const C = bf.C ?? 0;
  const N = bf.N ?? 0;
  const E = bf.E ?? 0;

  if ([...playMechSet].some((m) => O_MECHS.has(m))) base += O * 4;
  if (strip.beat === "/") base += C * 3;
  if (strip.detection === "h" || [...playMechSet].some((m) => N_MECHS.has(m))) base -= N * 4;
  if ([...playMechSet].some((m) => SOCIAL_MECHS.has(m))) base += E * 4;

  if (strip.beat === "^" && priorSpikes >= 2) base -= 5;

  // I3: register fit penalty
  const register = profile.p5_register ?? "";
  if (register === "rewired") {
    if ([...playMechSet].some((m) => DISORIENTATION_MECHS.has(m)) && scaffoldCount < 2) {
      base -= 15;
    }
  }

  // Identity invite bonus
  const identity = profile.identity_invite ?? "";
  if (identity === "seeker_pattern_finder") {
    if ([...playMechSet].some((m) => O_MECHS.has(m) || C_MECHS.has(m))) base += 7;
  } else if (identity === "protagonist") {
    if (strip.beat === "^") base += 5;
  }

  return Math.round(Math.max(20, Math.min(95, base)));
}

// ── FAILURE PROBABILITIES ─────────────────────────────────────────────────────

export function failureProbs(strip: StripPlay, profile: Profile, engProb: number): FailureModes {
  const failTotal = 100 - engProb;
  if (failTotal <= 0) return { cold: 0, confused: 0, distressed: 0, over_engaged: 0 };

  const bf = profile.big_five ?? {};
  const N = bf.N ?? 0;
  const C = bf.C ?? 0;

  const w = { cold: 40, confused: 30, distressed: 10, over_engaged: 20 };
  if (strip.detection === "h") {
    w.confused += 20;
    w.cold -= 10;
  }
  if (strip.reversibility === "i") {
    w.distressed += 15;
    w.cold -= 5;
  }
  if (strip.intensity_int >= 4) {
    w.distressed += 20;
    w.cold -= 10;
  }
  w.distressed += N * 10;
  w.over_engaged += C * 8;

  const totalW = Object.values(w).reduce((a, b) => a + Math.max(0, b), 0);
  if (!totalW) return { cold: 0, confused: 0, distressed: 0, over_engaged: 0 };

  const result = { cold: 0, confused: 0, distressed: 0, over_engaged: 0 };
  let remaining = failTotal;
  const sorted = Object.entries(w).sort((a, b) => b[1] - a[1]) as Array<
    [keyof FailureModes, number]
  >;
  sorted.forEach(([mode, weight], i) => {
    if (i === sorted.length - 1) {
      result[mode] = remaining;
    } else {
      const share = Math.round((Math.max(0, weight) / totalW) * failTotal);
      result[mode] = share;
      remaining -= share;
    }
  });
  return result;
}

// ── ENGAGEMENT BUCKET ─────────────────────────────────────────────────────────

export function engBucket(eng: number): EngagementBucket {
  if (eng >= 70) return "strong";
  if (eng >= 50) return "moderate";
  return "weak";
}

// ── PROFILE WARNINGS ─────────────────────────────────────────────────────────

function checkRegisterFit(
  playId: string,
  profile: Profile,
  priorScaffoldCount: number,
  mechIndex: MechIndex,
): string | null {
  if ((profile.p5_register ?? "") !== "rewired") return null;
  const mechs = new Set(getPlayMechs(playId, mechIndex));
  const hits = [...mechs].filter((m) => DISORIENTATION_MECHS.has(m));
  if (!hits.length) return null;
  if (priorScaffoldCount >= 2) return null;
  return `REGISTER_FIT: 'rewired' participant — disorientation-register play (${hits.join(", ")}) before sufficient scaffolding (${priorScaffoldCount}/2 scaffold plays seen)`;
}

function checkIdentityAntifit(
  playId: string,
  profile: Profile,
  mechIndex: MechIndex,
): string | null {
  const rejected = profile.identity_negative_space ?? [];
  if (!rejected.length) return null;
  const mechs = new Set(getPlayMechs(playId, mechIndex));
  for (const dim of rejected) {
    const dimMechs = IDENTITY_MECHS[dim.toLowerCase()] ?? new Set<string>();
    const hits = [...mechs].filter((m) => dimMechs.has(m));
    if (hits.length >= 2) {
      return `IDENTITY_ANTIFIT: play engages via '${dim}' identity dimension (${hits.join(", ")}) which participant has rejected`;
    }
  }
  return null;
}

function checkHardConstraints(
  playId: string,
  profile: Profile,
  mechIndex: MechIndex,
): string | null {
  const constraints = profile.hard_constraints ?? [];
  if (!constraints.length) return null;
  const mechs = getPlayMechs(playId, mechIndex);
  // Use token-based matching to avoid false positives (e.g. "knife" matching "pocketknife").
  // A constraint keyword must match an entire underscore-delimited token in the play ID or
  // any mechanism name — not a substring of one.
  const pidTokens = new Set(playId.toLowerCase().split("_"));
  const mechTokens = new Set(mechs.flatMap((m) => m.toLowerCase().split("_")));
  for (const c of constraints) {
    const kw = c.toLowerCase().trim();
    if (kw && (pidTokens.has(kw) || mechTokens.has(kw))) {
      return `HARD_CONSTRAINT: play matches sponsor E2 exclusion '${c}'. Review before including.`;
    }
  }
  return null;
}

// ── MAIN ENTRY ────────────────────────────────────────────────────────────────

export function planArc(
  arcData: { arc_type?: string; plays?: ArcElement[] } | ArcElement[],
  profile: Profile,
  stripsMap: StripMap,
  mechIndex: MechIndex,
): PlanResult {
  const plays: ArcElement[] = Array.isArray(arcData) ? arcData : (arcData.plays ?? []);
  const arcType = Array.isArray(arcData) ? "investigation" : (arcData.arc_type ?? "investigation");

  const plan: PlanItem[] = [];
  let priorSpikes = 0;
  let scaffoldCount = 0;
  let warningCount = 0;

  for (let i = 0; i < plays.length; i++) {
    const el = plays[i]!;
    if (!el.id || el.branch_point) continue;
    const pid = el.id;
    const strip = stripsMap[pid];

    if (!strip) {
      plan.push({ id: pid, error: "not found in library" } satisfies PlanEntryError);
      continue;
    }

    const eng = engagementProb(strip, profile, priorSpikes, mechIndex, scaffoldCount);
    const failures = failureProbs(strip, profile, eng);
    const topFailure = Object.entries(failures).sort((a, b) => b[1] - a[1])[0]!;
    const topRecovery = RECOVERY_PLAYS[topFailure[0]]?.[0] ?? null;

    const warnings: string[] = [];
    const rw = checkRegisterFit(pid, profile, scaffoldCount, mechIndex);
    if (rw) {
      warnings.push(rw);
      warningCount++;
    }
    const aw = checkIdentityAntifit(pid, profile, mechIndex);
    if (aw) {
      warnings.push(aw);
      warningCount++;
    }
    const hw = checkHardConstraints(pid, profile, mechIndex);
    if (hw) {
      warnings.push(hw);
      warningCount++;
    }

    const expectedParticipation = el.expected_participation ?? null;
    const effectiveRole = el.group_mode ?? strip.group_role;
    let effectiveEng: number | null = null;
    let lotteryUnfiredEng: number | null = null;

    if (expectedParticipation != null) {
      if (effectiveRole === "e") {
        effectiveEng = Math.round(eng * expectedParticipation);
      } else if (effectiveRole === "lo") {
        effectiveEng = eng;
        lotteryUnfiredEng = 0;
      }
    }

    let coverageTag = "";
    if (lotteryUnfiredEng != null) {
      const pct = Math.round((expectedParticipation ?? 0.1) * 100);
      coverageTag = ` (lottery: ${engBucket(eng)} if selected [${pct}%] / arc continues if not)`;
    } else if (effectiveEng != null) {
      const pct = Math.round((expectedParticipation ?? 1.0) * 100);
      coverageTag = ` (eff=${engBucket(effectiveEng)} @${pct}%)`;
    }

    const pbTag = strip.persona_bound ? " [pb]" : "";

    plan.push({
      id: pid,
      position: i + 1,
      beat: strip.beat,
      engagement_pct: eng,
      engagement_bucket: engBucket(eng),
      coverage_tag: coverageTag,
      persona_bound_tag: pbTag,
      effective_engagement_pct: effectiveEng,
      lottery_unfired_engagement_pct: lotteryUnfiredEng,
      expected_participation: expectedParticipation,
      failure_modes: failures,
      top_failure_mode: topFailure[0],
      top_failure_pct: topFailure[1],
      top_recovery: topRecovery,
      warnings,
    } satisfies PlanEntry);

    if (strip.beat === "^") priorSpikes++;
    if (new Set(getPlayMechs(pid, mechIndex)).size > 0) {
      if ([...new Set(getPlayMechs(pid, mechIndex))].some((m) => COGNITIVE_SCAFFOLD_MECHS.has(m))) {
        scaffoldCount++;
      }
    }
  }

  return { plan, warning_count: warningCount, arc_type: arcType };
}

// ── FIT REPORT ────────────────────────────────────────────────────────────────

export function fitReport(
  profile: Profile,
  stripsMap: StripMap,
  mechIndex: MechIndex,
  showWeak = false,
): Array<{ id: string; bucket: EngagementBucket; eng: number; matching: string[]; gaps: string[] }> {
  const results = [];
  for (const [pid, strip] of Object.entries(stripsMap)) {
    if (strip.beat === "~") continue;
    const eng = engagementProb(strip, profile, 0, mechIndex);
    const bucket = engBucket(eng);
    if (!showWeak && bucket === "weak") continue;

    const profileMechKeys = Object.keys(profile.mechanisms ?? {});
    const playMechSet = new Set(getPlayMechs(pid, mechIndex));
    const matching = profileMechKeys.filter((m) => playMechSet.has(m));
    const gaps = profileMechKeys.filter((m) => !playMechSet.has(m)).slice(0, 3);

    results.push({ id: pid, bucket, eng, matching, gaps });
  }
  results.sort((a, b) => b.eng - a.eng);
  return results;
}
