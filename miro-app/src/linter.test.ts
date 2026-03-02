// linter.test.ts — unit tests for lintArc() and loadStrips()

import { describe, expect, it } from "vitest";
import { lintArc, loadStrips } from "./linter.js";
import type { StripMap } from "./types.js";

// ── FIXTURES ──────────────────────────────────────────────────────────────────

// Minimal strip notation for test plays (uses a subset of real notation)
const STRIP_DATA = [
  {
    id: "ramp_a",
    strip: "@ramp_a F·A·0·1\n#curiosity_exploration [b·e] /\nC·n·l·a·e·n·e\nprm:S",
  },
  {
    id: "spike_b",
    strip: "@spike_b F·A·0·3\n#ordeal_completion [e·t] ^\nC·n·m·i·s·m·m\nprm:S",
  },
  {
    id: "hold_c",
    strip: "@hold_c F·A·0·1\n#belonging [b·e] -\nC·n·l·a·e·n·e\nprm:S",
  },
  {
    id: "liminal_d",
    strip: "@liminal_d F·C·sd·2\n#liminality_induction [b] ~\nC·n·l·i·e·n·e\nprm:S",
  },
  {
    id: "contra_first",
    strip: "@contra_first F·A·0·1\n#belonging [b] /\nC·n·l·a·e·n·e\nprm:S\n!ctr:ramp_a",
  },
  {
    id: "unknown_play",
    strip: "",  // intentionally empty — loadStrips will skip it
  },
];

let stripsMap: StripMap;

// ── SETUP ─────────────────────────────────────────────────────────────────────

stripsMap = loadStrips(STRIP_DATA.filter((s) => s.strip));

// ── TESTS ─────────────────────────────────────────────────────────────────────

describe("loadStrips", () => {
  it("parses all provided strips", () => {
    expect(Object.keys(stripsMap).length).toBeGreaterThanOrEqual(4);
  });

  it("parses beat correctly", () => {
    expect(stripsMap["ramp_a"]?.beat).toBe("/");
    expect(stripsMap["spike_b"]?.beat).toBe("^");
    expect(stripsMap["hold_c"]?.beat).toBe("-");
    expect(stripsMap["liminal_d"]?.beat).toBe("~");
  });

  it("parses mechanisms", () => {
    expect(stripsMap["ramp_a"]?.mechanisms).toContain("curiosity_exploration");
  });

  it("parses contraindicated_after", () => {
    expect(stripsMap["contra_first"]?.contraindicated_after).toContain("ramp_a");
  });
});

describe("lintArc — UNKNOWN check", () => {
  it("flags plays not in library", () => {
    const result = lintArc({ plays: [{ id: "nonexistent_play" }] }, stripsMap);
    expect(result.errors.length).toBeGreaterThan(0);
    expect(result.errors[0]?.message).toMatch(/not found in library/i);
  });

  it("passes for known plays", () => {
    const result = lintArc({ plays: [{ id: "ramp_a" }] }, stripsMap);
    const unknownErrors = result.errors.filter((e) => e.message.match(/not in library/i));
    expect(unknownErrors.length).toBe(0);
  });
});

describe("lintArc — CONTRAINDICATED check", () => {
  it("flags play that appears after its contraindicated predecessor", () => {
    const result = lintArc({ plays: [{ id: "ramp_a" }, { id: "contra_first" }] }, stripsMap);
    const ctrErrors = result.errors.filter((e) => e.message.includes("CONTRAINDICATED"));
    expect(ctrErrors.length).toBeGreaterThan(0);
  });

  it("passes when contraindicated predecessor is absent", () => {
    const result = lintArc({ plays: [{ id: "contra_first" }] }, stripsMap);
    const ctrErrors = result.errors.filter((e) => e.message.includes("CONTRAINDICATED"));
    expect(ctrErrors.length).toBe(0);
  });
});

describe("lintArc — beat shape", () => {
  it("produces beat shape string", () => {
    const result = lintArc({ plays: [{ id: "ramp_a" }, { id: "spike_b" }, { id: "hold_c" }] }, stripsMap);
    expect(result.beatShape).toBe("/ ^ -");
  });

  it("excludes liminal beats from cathartic density count", () => {
    // A 7-play arc with only 1 non-liminal spike should warn about low cathartic density.
    // Liminal beats should not count toward the arc length for this check.
    const plays = [
      { id: "ramp_a" }, { id: "hold_c" }, { id: "ramp_a" }, { id: "hold_c" },
      { id: "ramp_a" }, { id: "hold_c" }, { id: "spike_b" },
    ];
    const result = lintArc({ plays }, stripsMap);
    const densityWarn = result.warns.find((w) => w.message.includes("cathartic density"));
    expect(densityWarn).toBeDefined();
  });
});

describe("lintArc — empty arc", () => {
  it("returns no issues for empty arc", () => {
    const result = lintArc({ plays: [] }, stripsMap);
    expect(result.errors.length).toBe(0);
    expect(result.warns.length).toBe(0);
  });
});
