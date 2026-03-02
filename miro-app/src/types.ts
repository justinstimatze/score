// Canonical type definitions for the arc linter + planner.

export type Severity = "ERROR" | "WARN" | "INFO";
export type EngagementBucket = "strong" | "moderate" | "weak";
export type Sensitivity = "low" | "medium" | "high";

// ── STRIP / LIBRARY ──────────────────────────────────────────────────────────

export interface StripPlay {
  id: string;
  cost: string;
  autonomy: string;
  lead_time: string;
  intensity: string;
  intensity_int: number;
  lead_days: number;
  mechanisms: string[];
  arc_codes: string[];
  beat: string;
  agency_type: string;
  frame_req: string;
  agency_demand: string;
  landscape: string;
  legacy: string;
  detection: string;
  reversibility: string;
  permission_mode: string;
  permission_grant: string;
  synergizes: string[];
  contraindicated_after: string[];
  requires: string[];
  group_role: string;
  social_modifier: string;
  participation_tier: string;
  parallel_capable: boolean;
  activation_rate: number;
  witness_mechanisms: string[];
  persona_bound: boolean;
  // Computed helpers — stored as arrow-function properties for convenient call-site syntax
  is_ensemble: () => boolean;
  is_lottery: () => boolean;
  arc_fits_any: () => boolean;
  arc_fits_phase: (phase: string) => boolean;
}

export type StripMap = Record<string, StripPlay>;
export type MechIndex = Record<string, string[]>;
export type PlayInfo = Record<string, { invite?: string; desc?: string }>;

// ── ARC ──────────────────────────────────────────────────────────────────────

export interface ArcElement {
  id?: string;
  phase?: string;
  day?: number;
  group_mode?: string;
  expected_participation?: number;
  early_exit?: string;
  // Branch-block fields (legacy notation)
  branch_point?: boolean;
  merge_point?: { play?: string };
}

export interface ArcData {
  arc_type: string;
  audience_scale: string;
  group: Record<string, unknown>;
  pre_arc_plays: ArcElement[];
  parallel_tracks: unknown[];
  thresholds: unknown[];
  plays: ArcElement[];
  early_exit: string;
}

// ── LINTER ───────────────────────────────────────────────────────────────────

export interface Issue {
  severity: Severity;
  position: number;
  play_id: string;
  code: string;
  message: string;
}

export interface LintResult {
  issues: Issue[];
  errors: Issue[];
  warns: Issue[];
  infos: Issue[];
  beatShape: string;
  beatMix: string;
  legacyMix: string;
  arc: ArcData;
}

// ── PLANNER ──────────────────────────────────────────────────────────────────

export interface BigFive {
  O?: number;
  C?: number;
  N?: number;
  E?: number;
  A?: number;
}

export interface Profile {
  name?: string;
  mechanisms: Record<string, number>;
  big_five?: BigFive;
  sensitivity?: Sensitivity;
  p5_register?: string;
  identity_invite?: string;
  identity_negative_space?: string[];
  hard_constraints?: string[];
  /** Internal planner state — injected during planArc, not part of user schema. */
  _prior_scaffold_count?: number;
}

export interface FailureModes {
  cold: number;
  confused: number;
  distressed: number;
  over_engaged: number;
}

export interface PlanEntry {
  id: string;
  position: number;
  beat: string;
  engagement_pct: number;
  engagement_bucket: EngagementBucket;
  coverage_tag: string;
  persona_bound_tag: string;
  effective_engagement_pct: number | null;
  lottery_unfired_engagement_pct: number | null;
  expected_participation: number | null;
  failure_modes: FailureModes;
  top_failure_mode: string;
  top_failure_pct: number;
  top_recovery: string | null;
  warnings: string[];
}

export interface PlanEntryError {
  id: string;
  error: string;
}

export type PlanItem = PlanEntry | PlanEntryError;

export interface PlanResult {
  plan: PlanItem[];
  warning_count: number;
  arc_type: string;
  profile_name?: string;
}

// ── APP STATE ────────────────────────────────────────────────────────────────

export interface ArcMeta {
  arcType: string;
  audienceScale: string;
  earlyExit: string;
}

export interface CardMeta {
  phase?: string;
  day?: number;
  group_mode?: string;
  expected_participation?: number;
  early_exit?: string;
}
