// planner.test.ts — unit tests for planArc() and engagementProb()

import { describe, expect, it } from "vitest";
import { engagementProb, planArc } from "./planner.js";
import { loadStrips } from "./linter.js";
import type { MechIndex, Profile, StripMap } from "./types.js";

// ── FIXTURES ──────────────────────────────────────────────────────────────────

const STRIP_DATA = [
  {
    id: "curiosity_ramp",
    strip: "@curiosity_ramp F·A·0·2\n#curiosity_exploration·information_gap [b·e] /\nC·n·l·a·e·n·e\nprm:S",
  },
  {
    id: "social_spike",
    strip: "@social_spike F·A·0·3\n#belonging·social_synchrony [e·t] ^\nC·n·m·a·s·n·m\nprm:S",
  },
  {
    id: "ordeal_spike",
    strip: "@ordeal_spike F·A·sd·4\n#ordeal_completion·threshold_crossing [t·c] ^\nC·n·h·i·s·m·d\nprm:S",
  },
  {
    id: "liminal_beat",
    strip: "@liminal_beat F·C·sd·2\n#liminality_induction [b] ~\nC·n·l·i·e·n·e\nprm:S",
  },
];

let stripsMap: StripMap;
let mechIndex: MechIndex;

stripsMap = loadStrips(STRIP_DATA);
mechIndex = {
  curiosity_ramp: ["curiosity_exploration", "information_gap"],
  social_spike: ["belonging", "social_synchrony"],
  ordeal_spike: ["ordeal_completion", "threshold_crossing"],
  liminal_beat: ["liminality_induction"],
};

const PATTERN_SEEKER: Profile = {
  name: "Pattern Seeker",
  mechanisms: {
    curiosity_exploration: 0.9,
    information_gap: 0.8,
    knowledge_frontier: 0.7,
  },
  big_five: { O: 0.8, C: 0.5, N: 0.1, E: -0.2, A: 0.1 },
  sensitivity: "high",
  p5_register: "unsettled",
  identity_invite: "seeker_pattern_finder",
  identity_negative_space: [],
  hard_constraints: [],
};

const SOCIAL_BEING: Profile = {
  name: "Social Being",
  mechanisms: {
    belonging: 0.9,
    social_synchrony: 0.8,
    group_cohesion: 0.7,
  },
  big_five: { O: 0.3, C: 0.2, N: 0.1, E: 0.8, A: 0.7 },
  sensitivity: "medium",
  p5_register: "opened",
  identity_invite: undefined,
  identity_negative_space: [],
  hard_constraints: [],
};

// ── ENGAGEMENT PROBABILITY ────────────────────────────────────────────────────

describe("engagementProb", () => {
  it("returns 100 for liminal beats", () => {
    const strip = stripsMap["liminal_beat"]!;
    expect(engagementProb(strip, PATTERN_SEEKER, 0, mechIndex)).toBe(100);
  });

  it("scores higher for mechanism-matched plays", () => {
    const curiosityStrip = stripsMap["curiosity_ramp"]!;
    const socialStrip = stripsMap["social_spike"]!;
    const curiosityEng = engagementProb(curiosityStrip, PATTERN_SEEKER, 0, mechIndex);
    const socialEng = engagementProb(socialStrip, PATTERN_SEEKER, 0, mechIndex);
    // Pattern seeker has curiosity mechs, not social mechs — curiosity should score higher
    expect(curiosityEng).toBeGreaterThan(socialEng);
  });

  it("social being scores higher on social play than pattern seeker", () => {
    const socialStrip = stripsMap["social_spike"]!;
    const seekerEng = engagementProb(socialStrip, PATTERN_SEEKER, 0, mechIndex);
    const socialEng = engagementProb(socialStrip, SOCIAL_BEING, 0, mechIndex);
    expect(socialEng).toBeGreaterThan(seekerEng);
  });

  it("applies spike fatigue after 2 prior spikes", () => {
    const strip = stripsMap["curiosity_ramp"]!; // ramp, not spike — fatigue only applies to spikes
    const spikeStrip = stripsMap["social_spike"]!;
    const noFatigue = engagementProb(spikeStrip, SOCIAL_BEING, 0, mechIndex);
    const withFatigue = engagementProb(spikeStrip, SOCIAL_BEING, 2, mechIndex);
    expect(withFatigue).toBeLessThan(noFatigue);
    void strip; // used to avoid unused var warning
  });

  it("stays within 20–95% bounds", () => {
    const strips = Object.values(stripsMap).filter((s) => s.beat !== "~");
    for (const strip of strips) {
      const eng = engagementProb(strip, PATTERN_SEEKER, 0, mechIndex);
      expect(eng).toBeGreaterThanOrEqual(20);
      expect(eng).toBeLessThanOrEqual(95);
    }
  });
});

// ── PLAN ARC ──────────────────────────────────────────────────────────────────

describe("planArc", () => {
  it("returns a plan entry for each known play", () => {
    const result = planArc(
      { plays: [{ id: "curiosity_ramp" }, { id: "social_spike" }] },
      PATTERN_SEEKER,
      stripsMap,
      mechIndex,
    );
    expect(result.plan.length).toBe(2);
  });

  it("marks unknown plays as errors", () => {
    const result = planArc(
      { plays: [{ id: "nonexistent_play" }] },
      PATTERN_SEEKER,
      stripsMap,
      mechIndex,
    );
    expect(result.plan.length).toBe(1);
    expect("error" in result.plan[0]!).toBe(true);
  });

  it("does NOT mutate the profile object", () => {
    const profile = { ...PATTERN_SEEKER };
    const before = JSON.stringify(profile);
    planArc(
      { plays: [{ id: "curiosity_ramp" }, { id: "ordeal_spike" }, { id: "social_spike" }] },
      profile,
      stripsMap,
      mechIndex,
    );
    expect(JSON.stringify(profile)).toBe(before);
  });

  it("includes profile_name after caller sets it", () => {
    const result = planArc({ plays: [] }, PATTERN_SEEKER, stripsMap, mechIndex);
    result.profile_name = "Pattern Seeker";
    expect(result.profile_name).toBe("Pattern Seeker");
  });

  it("skips branch_point elements", () => {
    const result = planArc(
      { plays: [{ id: "curiosity_ramp" }, { id: "", branch_point: true }] },
      PATTERN_SEEKER,
      stripsMap,
      mechIndex,
    );
    // Only the real play should be in the plan
    expect(result.plan.length).toBe(1);
  });
});

// ── HARD CONSTRAINT MATCHING ──────────────────────────────────────────────────

describe("planArc — hard constraints (token-based)", () => {
  it("flags exact token matches", () => {
    const profile = { ...PATTERN_SEEKER, hard_constraints: ["ordeal"] };
    const result = planArc(
      { plays: [{ id: "ordeal_spike" }] },
      profile,
      stripsMap,
      mechIndex,
    );
    const entry = result.plan[0];
    if (!entry || "error" in entry) throw new Error("expected plan entry");
    expect(entry.warnings.some((w) => w.includes("HARD_CONSTRAINT"))).toBe(true);
  });

  it("does NOT flag substring-only matches (pocketknife != knife)", () => {
    // "ordeal" should not match a hypothetical play ID "colonial_ordeal_compound"
    // whose tokens are ["colonial", "ordeal", "compound"] — this WILL match since "ordeal" is a token.
    // Test the reverse: "eal" should NOT match "ordeal" (not a full token).
    const profile = { ...PATTERN_SEEKER, hard_constraints: ["eal"] };
    const result = planArc(
      { plays: [{ id: "ordeal_spike" }] },
      profile,
      stripsMap,
      mechIndex,
    );
    const entry = result.plan[0];
    if (!entry || "error" in entry) throw new Error("expected plan entry");
    expect(entry.warnings.some((w) => w.includes("HARD_CONSTRAINT"))).toBe(false);
  });
});
