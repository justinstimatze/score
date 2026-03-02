// linter.ts — TypeScript port of arc_linter.py
// Runs entirely client-side; no backend required.

import type { ArcData, ArcElement, Issue, LintResult, Severity, StripMap, StripPlay } from "./types.js";

// ── CONSTANTS ────────────────────────────────────────────────────────────────

const LEAD_TIME_DAYS: Record<string, number> = {
  "0": 0,
  sd: 0,
  "1d": 1,
  "3d": 3,
  "1w": 7,
  "2w": 14,
  "4w": 28,
  "8w": 56,
};

const PHASE_NAMES: Record<string, string> = {
  p: "pre/open",
  b: "build",
  e: "escalate",
  t: "threshold",
  c: "climax",
  r: "revelation",
  d: "denouement",
  "*": "any",
};

const CLIMAX_PHASES = new Set(["c", "r"]);

const DETECTION_WEIGHTS: Record<string, number> = {
  i: 4,
  s: 3,
  m: 2,
  l: 1,
  n: 0,
  S: 1,
  D: 1,
  t: 0,
  "?": 1,
};

function leadDays(code: string): number {
  return LEAD_TIME_DAYS[code] ?? 0;
}

// ── STRIP PARSER ─────────────────────────────────────────────────────────────

export function parseStrip(raw: string): StripPlay | null {
  const lines = raw
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
  if (!lines.length) return null;

  const m1 = lines[0]!.match(/^@(\S+)\s+(.+)/);
  if (!m1) return null;

  const pid = m1[1]!;
  const l1parts = m1[2]!.split("·");

  // Build the play object. Arrow-function properties close over `play` for
  // convenient call-site syntax; this is safe because they are never invoked
  // during construction.
  // biome-ignore lint/style/useConst: play is mutated after construction
  let play: StripPlay;

  play = {
    id: pid,
    cost: l1parts[0] ?? "",
    autonomy: l1parts[1] ?? "",
    lead_time: l1parts[2] ?? "",
    intensity: l1parts[3] ?? "",
    intensity_int: 0,
    lead_days: 0,
    mechanisms: [],
    arc_codes: [],
    beat: "",
    agency_type: "",
    frame_req: "",
    agency_demand: "",
    landscape: "",
    legacy: "",
    detection: "",
    reversibility: "",
    permission_mode: "S",
    permission_grant: "",
    synergizes: [],
    contraindicated_after: [],
    requires: [],
    group_role: "s",
    social_modifier: "neut",
    participation_tier: "U",
    parallel_capable: false,
    activation_rate: 1.0,
    witness_mechanisms: [],
    persona_bound: false,
    // eslint-disable-next-line no-use-before-define
    is_ensemble: () => play.group_role === "e",
    is_lottery: () => play.group_role === "lo",
    arc_fits_any: () => play.arc_codes.includes("*"),
    arc_fits_phase: (ph: string) => play.arc_fits_any() || play.arc_codes.includes(ph),
  };

  play.lead_days = leadDays(play.lead_time);
  play.intensity_int = parseInt(play.intensity, 10) || 0;
  play.persona_bound = play.autonomy.includes("pb");

  if (lines.length < 2) return play;

  // L2: #M·M [arc] bf
  const arcMatch = lines[1]!.match(/\[([^\]]+)\]/);
  if (arcMatch?.index !== undefined) {
    play.arc_codes = arcMatch[1]!.split("");
    const after = lines[1]!.slice(arcMatch.index + arcMatch[0]!.length).trim();
    play.beat = after[0] ?? "";
    const mechPart = lines[1]!.slice(0, arcMatch.index).replace(/^#/, "").trim();
    play.mechanisms = mechPart
      .split("·")
      .map((x) => x.trim())
      .filter(Boolean);
  }

  if (lines.length < 3) return play;

  // L3: AT·FR·AD·LA·LG·DE·RV
  const l3 = lines[2]!.split("·");
  if (l3.length >= 7) {
    play.agency_type = l3[0]!;
    play.frame_req = l3[1]!;
    play.agency_demand = l3[2]!;
    play.landscape = l3[3]!;
    play.legacy = l3[4]!;
    play.detection = l3[5]!;
    play.reversibility = l3[6]!;
  }

  // L4+: labeled fields
  for (const line of lines.slice(3)) {
    if (line.startsWith("prm:")) {
      const prm = line.slice(4);
      if (prm.includes("→")) {
        const [mode, grant] = prm.split("→", 2) as [string, string];
        play.permission_mode = mode.trim();
        play.permission_grant = grant.trim();
      } else {
        play.permission_mode = prm.trim();
      }
    } else if (line.startsWith("syn:")) {
      play.synergizes = line
        .slice(4)
        .split("·")
        .map((x) => x.trim())
        .filter(Boolean);
    } else if (line.startsWith("!ctr:")) {
      play.contraindicated_after = line
        .slice(5)
        .split("·")
        .map((x) => x.trim())
        .filter(Boolean);
    } else if (line.startsWith("req:")) {
      play.requires = line
        .slice(4)
        .split("·")
        .map((x) => x.trim())
        .filter(Boolean);
    } else if (line.startsWith("grp:")) {
      const parts = line.slice(4).split("·");
      if (parts[0]) play.group_role = parts[0];
      if (parts[1]) play.social_modifier = parts[1];
      if (parts[2]) play.participation_tier = parts[2];
      if (parts[3] !== undefined) play.parallel_capable = parts[3] === "1";
      if (parts[4]) play.activation_rate = parseFloat(parts[4]) || 1.0;
    } else if (line.startsWith("wit:")) {
      play.witness_mechanisms = line
        .slice(4)
        .split("·")
        .map((x) => x.trim())
        .filter(Boolean);
    }
  }

  return play;
}

export function loadStrips(data: Array<{ id: string; strip: string }>): StripMap {
  const map: StripMap = {};
  for (const entry of data) {
    const s = parseStrip(entry.strip);
    if (s) map[s.id] = s;
  }
  return map;
}

// ── ARC LOADING ──────────────────────────────────────────────────────────────

function isBranchBlock(el: ArcElement): boolean {
  return "branch_point" in el && el.branch_point === true;
}

function isPlayElement(el: ArcElement): boolean {
  return "id" in el && !("branch_point" in el);
}

export function loadArc(data: unknown): ArcData {
  if (Array.isArray(data)) {
    return {
      arc_type: "investigation",
      audience_scale: "intimate",
      group: {},
      pre_arc_plays: [],
      parallel_tracks: [],
      thresholds: [],
      plays: data.map((x: unknown) =>
        typeof x === "string" ? { id: x } : (x as ArcElement),
      ),
      early_exit: "",
    };
  }
  const d = data as Record<string, unknown>;
  return {
    arc_type: (d["arc_type"] as string | undefined) ?? "investigation",
    audience_scale: (d["audience_scale"] as string | undefined) ?? "intimate",
    group: (d["group"] as Record<string, unknown> | undefined) ?? {},
    pre_arc_plays:
      ((d["pre_arc"] as Record<string, unknown> | undefined)?.["plays"] as ArcElement[] | undefined) ?? [],
    parallel_tracks: (d["parallel_tracks"] as unknown[] | undefined) ?? [],
    thresholds: (d["thresholds"] as unknown[] | undefined) ?? [],
    plays: (d["plays"] as ArcElement[] | undefined) ?? [],
    early_exit: (d["early_exit"] as string | undefined) ?? "",
  };
}

function extractMainSequence(arcPlays: ArcElement[]): ArcElement[] {
  const result: ArcElement[] = [];
  for (const el of arcPlays) {
    if (isBranchBlock(el)) {
      const mp = el.merge_point;
      if (mp?.play) {
        result.push({ id: mp.play, day: el.day, phase: el.phase });
      }
    } else if (isPlayElement(el)) {
      result.push(el);
    }
  }
  return result;
}

// ── ISSUE FACTORY ────────────────────────────────────────────────────────────

function mkIssue(
  severity: Severity,
  position: number,
  play_id: string,
  code: string,
  message: string,
): Issue {
  return { severity, position, play_id, code, message };
}

// ── CHECKS ───────────────────────────────────────────────────────────────────

function checkUnknown(playIds: string[], library: StripMap): Issue[] {
  return playIds
    .map((pid, i) =>
      pid in library
        ? null
        : mkIssue("ERROR", i, pid, "UNKNOWN", `play '${pid}' not found in library`),
    )
    .filter((x): x is Issue => x !== null);
}

function checkContraindicated(plays: StripPlay[], positions: number[]): Issue[] {
  const issues: Issue[] = [];
  for (let i = 0; i < plays.length; i++) {
    for (let j = 0; j < i; j++) {
      if (plays[i]!.contraindicated_after.includes(plays[j]!.id)) {
        issues.push(
          mkIssue(
            "ERROR",
            positions[i]!,
            plays[i]!.id,
            "CONTRAINDICATED",
            `CONTRAINDICATED_AFTER '${plays[j]!.id}' (at position ${positions[j]! + 1})`,
          ),
        );
      }
    }
  }
  return issues;
}

function checkFrameRequirement(plays: StripPlay[], positions: number[]): Issue[] {
  const issues: Issue[] = [];
  let frame = "n";
  for (let i = 0; i < plays.length; i++) {
    const p = plays[i]!;
    const fr = p.frame_req;
    if (fr === "q" && frame === "n") {
      issues.push(
        mkIssue(
          "WARN",
          positions[i]!,
          p.id,
          "FRAME_REQ",
          "FRAME_REQUIREMENT=primed but frame is still naive — needs prior build/ramp",
        ),
      );
    } else if (fr === "m" && frame !== "m") {
      issues.push(
        mkIssue(
          "ERROR",
          positions[i]!,
          p.id,
          "FRAME_REQ",
          "FRAME_REQUIREMENT=meta but frame not yet meta — only valid post-reveal",
        ),
      );
    }
    if (["/", "-"].includes(p.beat) && p.arc_codes.some((c) => ["b", "e", "t"].includes(c))) {
      if (frame === "n") frame = "q";
    }
    if (p.beat === ">" && p.arc_codes.some((c) => ["c", "r", "d"].includes(c))) {
      frame = "m";
    }
  }
  return issues;
}

function checkPermissionSequenced(
  plays: StripPlay[],
  positions: number[],
  initialGrants = new Set<string>(),
): Issue[] {
  const issues: Issue[] = [];
  const grants = new Set(initialGrants);
  for (let i = 0; i < plays.length; i++) {
    const p = plays[i]!;
    const { permission_mode: mode, permission_grant: grantNeeded } = p;
    if (mode === "Q") {
      if (i < 2) {
        issues.push(
          mkIssue(
            "WARN",
            positions[i]!,
            p.id,
            "PERMISSION",
            `prm:Q (sequenced) — appears too early (position ${i + 1}); needs prior arc investment`,
          ),
        );
      }
      if (grantNeeded && !grants.has(grantNeeded)) {
        issues.push(
          mkIssue(
            "WARN",
            positions[i]!,
            p.id,
            "PERMISSION",
            `prm:Q→${grantNeeded} requires prior grant '${grantNeeded}' — not yet produced by preceding plays`,
          ),
        );
      }
    }
    if (p.permission_grant) grants.add(p.permission_grant);
  }
  return issues;
}

function checkLeadTime(
  plays: StripPlay[],
  positions: number[],
  days: Array<number | null>,
): Issue[] {
  if (!days.some((d) => d != null)) return [];
  const issues: Issue[] = [];
  for (let i = 0; i < plays.length; i++) {
    const day = days[i];
    if (day == null) continue;
    const required = plays[i]!.lead_days;
    const effectiveDay = day < 0 ? Math.abs(day) : day;
    if (required > effectiveDay) {
      issues.push(
        mkIssue(
          "ERROR",
          positions[i]!,
          plays[i]!.id,
          "LEAD_TIME",
          `LEAD_TIME requires ${required}d setup but scheduled on day ${day} — only ${effectiveDay}d available`,
        ),
      );
    }
  }
  return issues;
}

function checkRhythm(plays: StripPlay[], positions: number[]): Issue[] {
  const issues: Issue[] = [];
  const beats = plays.map((p) => p.beat);
  const scoredBeats = beats.filter((b) => b !== "~");
  const nScored = scoredBeats.length;

  let run = 0;
  for (let i = 0; i < beats.length; i++) {
    const b = beats[i]!;
    if (b === "^") {
      run++;
      if (run >= 5) {
        issues.push(
          mkIssue(
            "WARN",
            positions[i]!,
            plays[i]!.id,
            "RHYTHM",
            "5th consecutive spike — participant fatigue risk; insert ramp or hold",
          ),
        );
      }
    } else if (b !== "~") {
      run = 0;
    }
  }

  if (nScored > 6 && !scoredBeats.includes("-")) {
    issues.push(
      mkIssue(
        "WARN",
        -1,
        "arc",
        "RHYTHM",
        "No hold beat anywhere in arc — no dwell space for participant processing; add at least one hold",
      ),
    );
  }

  if (nScored > 8 && !scoredBeats.includes(">")) {
    issues.push(
      mkIssue(
        "INFO",
        -1,
        "arc",
        "RHYTHM",
        `No transition beat in ${nScored}-play arc — arcs this long usually need at least one structural gear change`,
      ),
    );
  }

  const spikeCount = scoredBeats.filter((b) => b === "^").length;
  if (nScored > 6 && spikeCount < 2) {
    issues.push(
      mkIssue(
        "WARN",
        -1,
        "arc",
        "RHYTHM",
        `Only ${spikeCount} spike beat(s) in ${nScored}-play arc — low cathartic density; consider adding at least one high-intensity beat`,
      ),
    );
  }

  for (let i = 1; i < beats.length; i++) {
    if (beats[i - 1] === "-" && beats[i] === "^") {
      issues.push(
        mkIssue(
          "WARN",
          positions[i]!,
          plays[i]!.id,
          "RHYTHM",
          "Spike immediately follows rest — abrupt re-escalation; consider a ramp between them",
        ),
      );
    }
  }

  if (beats.length >= 4) {
    const last4 = plays.slice(-4);
    if (last4.some((p) => p.arc_codes.includes("d")) && !beats.slice(-4).includes("_")) {
      issues.push(
        mkIssue(
          "INFO",
          -1,
          "arc",
          "RHYTHM",
          "Denouement plays present but no rest beat preceding them — consider a rest or transition to close the arc",
        ),
      );
    }
  }

  return issues;
}

function checkDetectionAccumulation(
  plays: StripPlay[],
  positions: number[],
  days: Array<number | null> | null = null,
): Issue[] {
  const issues: Issue[] = [];
  const risk = plays.map((p) => DETECTION_WEIGHTS[p.detection] ?? 1);
  const hasDays = days != null && days.some((d) => d != null);

  if (hasDays && days != null) {
    const dayRisk: Record<number, number> = {};
    for (let i = 0; i < plays.length; i++) {
      const day = days[i];
      if (day == null) continue;
      dayRisk[day] = (dayRisk[day] ?? 0) + (risk[i] ?? 0);
    }
    const allDays = Object.keys(dayRisk)
      .map(Number)
      .sort((a, b) => a - b);
    const THRESHOLD = 10;
    for (const startDay of allDays) {
      const windowDays = allDays.filter((d) => d >= startDay && d < startDay + 7);
      const windowRisk = windowDays.reduce((s, d) => s + (dayRisk[d] ?? 0), 0);
      if (windowRisk >= THRESHOLD) {
        const endDay = windowDays[windowDays.length - 1]!;
        let playIdx = plays.findIndex((_, j) => days[j] === endDay);
        if (playIdx === -1) playIdx = plays.length - 1;
        issues.push(
          mkIssue(
            "WARN",
            positions[playIdx]!,
            plays[playIdx]!.id,
            "DETECTION",
            `High detection accumulation in day window ${startDay}–${startDay + 6} (risk=${windowRisk}/${THRESHOLD}) — consider spreading high-detection plays or inserting a low-detection hold`,
          ),
        );
        break;
      }
    }
  } else {
    const WINDOW = 4;
    const THRESHOLD = 10;
    for (let i = 0; i <= risk.length - WINDOW; i++) {
      const windowRisk = risk.slice(i, i + WINDOW).reduce((a, b) => a + b, 0);
      if (windowRisk >= THRESHOLD) {
        issues.push(
          mkIssue(
            "WARN",
            positions[i + WINDOW - 1]!,
            plays[i + WINDOW - 1]!.id,
            "DETECTION",
            `High detection accumulation in plays ${positions[i]! + 1}–${positions[i + WINDOW - 1]! + 1} (risk=${windowRisk}/${THRESHOLD}) — consider spreading high-detection plays or inserting a low-detection hold`,
          ),
        );
        break;
      }
    }
  }
  return issues;
}

function checkReversibility(plays: StripPlay[], positions: number[]): Issue[] {
  const issues: Issue[] = [];
  const n = plays.length;
  const quarter = Math.max(2, Math.floor(n / 4));
  for (let i = 0; i < plays.length; i++) {
    if (plays[i]!.reversibility === "x" && i < quarter) {
      issues.push(
        mkIssue(
          "WARN",
          positions[i]!,
          plays[i]!.id,
          "REVERSIBILITY",
          `Irreversible play in first quarter of arc (position ${i + 1}/${n}) — participant trajectory not yet established`,
        ),
      );
    }
  }
  return issues;
}

function checkArcFit(
  plays: StripPlay[],
  positions: number[],
  declaredPhases: Array<string | null>,
): Issue[] {
  if (!declaredPhases.some((p) => p != null)) return [];
  const issues: Issue[] = [];
  for (let i = 0; i < plays.length; i++) {
    const phase = declaredPhases[i];
    if (phase == null) continue;
    if (!plays[i]!.arc_fits_phase(phase)) {
      const fits = plays[i]!.arc_codes.map((c) => PHASE_NAMES[c] ?? c).join("·") || "none";
      issues.push(
        mkIssue(
          "WARN",
          positions[i]!,
          plays[i]!.id,
          "ARC_FIT",
          `Declared phase='${phase}' but play fits [${fits}]`,
        ),
      );
    }
  }
  return issues;
}

function checkWorldMarkTiming(plays: StripPlay[], positions: number[]): Issue[] {
  const issues: Issue[] = [];
  const n = plays.length;
  for (let i = 0; i < plays.length; i++) {
    const p = plays[i]!;
    if (p.legacy.includes("w") && i > n * 0.6 && p.lead_days < 14) {
      issues.push(
        mkIssue(
          "WARN",
          positions[i]!,
          p.id,
          "LEGACY_SCOPE",
          "world_mark play appearing in last 40% of arc with <2w lead time — may not have time to establish before arc close",
        ),
      );
    }
  }
  return issues;
}

function checkLandscapeBalance(plays: StripPlay[], _positions: number[], arcType: string): Issue[] {
  const SUPPRESS_FOR = new Set(["grief", "memorial"]);
  if (SUPPRESS_FOR.has(arcType) || !plays.length) return [];
  const actionPlays = plays.filter((p) => p.landscape === "a" || p.landscape === "+");
  if (!actionPlays.length) {
    const identityCount = plays.filter((p) => p.landscape === "i").length;
    if (identityCount > 0) {
      return [
        mkIssue(
          "WARN",
          -1,
          "arc",
          "LANDSCAPE",
          "No action-plane plays in arc (all LANDSCAPE:identity) — arc has nothing for the participant to do, produce, or complete; ideology vacancy risk even if beat shape is correct. Initiation arcs are highest risk. Add at least one LANDSCAPE:action play.",
        ),
      ];
    }
  }
  return [];
}

function checkEarlyExit(arc: ArcData, library: StripMap): Issue[] {
  if (arc.arc_type !== "initiation") return [];
  if (arc.early_exit) {
    if (!(arc.early_exit in library)) {
      return [
        mkIssue(
          "WARN",
          -1,
          "arc",
          "EARLY_EXIT",
          `early_exit play '${arc.early_exit}' not found in library`,
        ),
      ];
    }
    return [];
  }
  return [
    mkIssue(
      "WARN",
      -1,
      "arc",
      "EARLY_EXIT",
      "Initiation arc has no early_exit play defined — arc has no graceful short-circuit if operator needs to close before climax. Add early_exit: <play_id> (a hold or denouement beat) to the arc JSON.",
    ),
  ];
}

function checkParticipationRate(
  arcPlays: ArcElement[],
  library: StripMap,
  threshold = 0.7,
): Issue[] {
  const issues: Issue[] = [];
  for (let i = 0; i < arcPlays.length; i++) {
    const el = arcPlays[i]!;
    if (!isPlayElement(el) || !el.id) continue;
    const pid = el.id;
    const ep = el.expected_participation;
    if (ep == null) continue;
    const strip = library[pid];
    if (!strip) continue;
    const effectiveRole = el.group_mode ?? strip.group_role;
    if (strip.beat === "^" && effectiveRole === "e" && ep < threshold) {
      const pct = Math.floor(ep * 100);
      issues.push(
        mkIssue(
          "WARN",
          i,
          pid,
          "LOW_COVERAGE_RISK",
          `Spike beat '${pid}' (ensemble) has expected_participation=${pct}% — cathartic beat may be unavailable to ${100 - pct}% of group; consider lottery mechanic, parallel spike, or lower-barrier alternative`,
        ),
      );
    } else if (strip.beat === "^" && effectiveRole === "lo") {
      const pct = Math.floor(ep * 100);
      issues.push(
        mkIssue(
          "INFO",
          i,
          pid,
          "LOTTERY_BIFURCATION",
          `Spike beat '${pid}' (lottery) has expected_participation=${pct}% — arc bifurcates: ~${pct}% of participants receive the full spike path, ~${100 - pct}% experience the arc without it; design both paths intentionally`,
        ),
      );
    }
  }
  return issues;
}

function checkRequiresConsistency(plays: StripPlay[], _positions: number[]): Issue[] {
  const issues: Issue[] = [];
  const needsConfederate = plays.filter(
    (p) =>
      p.requires.includes("cnf") ||
      p.autonomy.includes("C") ||
      p.autonomy.includes("CR") ||
      p.autonomy.includes("CA"),
  );
  const needsLocation = plays.filter((p) => p.requires.includes("loc"));
  if (needsConfederate.length > 1) {
    issues.push(
      mkIssue(
        "INFO",
        -1,
        "arc",
        "REQUIRES",
        `${needsConfederate.length} plays require a confederate — confirm same person is available for full arc duration`,
      ),
    );
  }
  if (needsLocation.length > 1) {
    issues.push(
      mkIssue(
        "INFO",
        -1,
        "arc",
        "REQUIRES",
        `${needsLocation.length} plays require specific location access — confirm logistics are coordinated`,
      ),
    );
  }
  return issues;
}

function checkGroupDynamics(arcPlays: ArcElement[], library: StripMap): Issue[] {
  const issues: Issue[] = [];
  for (let i = 0; i < arcPlays.length; i++) {
    const el = arcPlays[i]!;
    if (!isPlayElement(el) || !el.id) continue;
    const pid = el.id;
    const phase = el.phase ?? "";
    const strip = library[pid];
    if (!strip) continue;
    const groupMode = el.group_mode ?? "";
    let effectiveRole = strip.group_role;
    if (groupMode === "parallel") effectiveRole = "parallel";
    else if (groupMode === "e" || groupMode === "ensemble") effectiveRole = "e";
    else if (groupMode === "lo") effectiveRole = "lo";

    if (CLIMAX_PHASES.has(phase) && !["e", "am", "parallel"].includes(effectiveRole)) {
      issues.push(
        mkIssue(
          "WARN",
          i,
          pid,
          "CLIMAX_COVERAGE",
          `Climax/revelation play '${pid}' (phase=${phase}) has GROUP_ROLE:${effectiveRole} — participants experience the climax independently; consider GROUP_ROLE:ensemble or group_mode:parallel`,
        ),
      );
    }
  }
  return issues;
}

// ── BEAT SHAPE UTILS ─────────────────────────────────────────────────────────

export function beatShape(plays: StripPlay[]): string {
  return plays.map((p) => p.beat || "?").join(" ");
}

export function beatMix(plays: StripPlay[]): string {
  const counts: Record<string, number> = {};
  for (const p of plays) {
    const b = p.beat || "?";
    counts[b] = (counts[b] ?? 0) + 1;
  }
  const beatNames: Record<string, string> = {
    "/": "ramp",
    "^": "spike",
    "-": "hold",
    _: "rest",
    ">": "transition",
    "~": "liminal",
  };
  return Object.entries(counts)
    .map(([b, n]) => `${beatNames[b] ?? b}:${n}`)
    .join("  ");
}

// ── MAIN ENTRY ───────────────────────────────────────────────────────────────

export function lintArc(arcData: unknown, library: StripMap): LintResult {
  const arc = loadArc(arcData);
  const allIssues: Issue[] = [];

  const mainSeq = extractMainSequence(arc.plays);
  const playIds = mainSeq.map((el) => el.id).filter((id): id is string => Boolean(id));
  const days = mainSeq.map((el) => el.day ?? null);
  const declaredPhases = mainSeq.map((el) => el.phase ?? null);

  allIssues.push(...checkUnknown(playIds, library));

  const resolvedStrips = mainSeq
    .filter((el) => el.id && el.id in library)
    .map((el) => library[el.id!]!);
  const resolvedPositions = mainSeq
    .map((el, i) => ({ id: el.id, i }))
    .filter(({ id }) => id && id in library)
    .map(({ i }) => i);
  const resolvedDays = mainSeq
    .filter((el) => el.id && el.id in library)
    .map((el) => el.day ?? null);
  const resolvedPhases = mainSeq
    .filter((el) => el.id && el.id in library)
    .map((el) => el.phase ?? null);

  if (resolvedStrips.length) {
    allIssues.push(...checkContraindicated(resolvedStrips, resolvedPositions));
    allIssues.push(...checkFrameRequirement(resolvedStrips, resolvedPositions));
    allIssues.push(...checkPermissionSequenced(resolvedStrips, resolvedPositions));
    allIssues.push(...checkLeadTime(resolvedStrips, resolvedPositions, resolvedDays));
    allIssues.push(...checkRhythm(resolvedStrips, resolvedPositions));
    allIssues.push(
      ...checkDetectionAccumulation(resolvedStrips, resolvedPositions, resolvedDays),
    );
    allIssues.push(...checkReversibility(resolvedStrips, resolvedPositions));
    allIssues.push(...checkArcFit(resolvedStrips, resolvedPositions, resolvedPhases));
    allIssues.push(...checkWorldMarkTiming(resolvedStrips, resolvedPositions));
    allIssues.push(...checkLandscapeBalance(resolvedStrips, resolvedPositions, arc.arc_type));
    allIssues.push(...checkRequiresConsistency(resolvedStrips, resolvedPositions));
  }

  allIssues.push(...checkEarlyExit(arc, library));
  allIssues.push(...checkParticipationRate(arc.plays, library));
  allIssues.push(...checkGroupDynamics(arc.plays, library));

  const shape = beatShape(resolvedStrips);
  const mix = beatMix(resolvedStrips);

  const legacyCounts: Record<string, number> = {};
  for (const s of resolvedStrips) {
    for (const ch of (s.legacy ?? "").split("")) {
      if (ch && ch !== "·") legacyCounts[ch] = (legacyCounts[ch] ?? 0) + 1;
    }
  }
  const legacyNames: Record<string, string> = {
    p: "personal",
    s: "social",
    w: "world_mark",
    e: "ephemeral",
  };
  const legacyMix = Object.entries(legacyCounts)
    .map(([c, n]) => `${legacyNames[c] ?? c}:${n}`)
    .join("  ");

  const errors = allIssues.filter((x) => x.severity === "ERROR");
  const warns = allIssues.filter((x) => x.severity === "WARN");
  const infos = allIssues.filter((x) => x.severity === "INFO");

  return { issues: allIssues, errors, warns, infos, beatShape: shape, beatMix: mix, legacyMix, arc };
}
