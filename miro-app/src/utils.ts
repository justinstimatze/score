// utils.ts — shared HTML helpers, decode maps, and display utilities

export function esc(str: unknown): string {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function el<K extends keyof HTMLElementTagNameMap>(id: string): HTMLElementTagNameMap[K] {
  const node = document.getElementById(id) as HTMLElementTagNameMap[K] | null;
  if (!node) throw new Error(`Element #${id} not found`);
  return node;
}

const ACRONYMS = new Set(["ai", "id", "llc", "llm", "usps", "arg", "npc", "url", "qr", "mice", "osint", "tinag"]);

export function humanName(id: string): string {
  return id
    .replace(/_/g, " ")
    .replace(/\b\w+/g, (w) => (ACRONYMS.has(w) ? w.toUpperCase() : w[0]!.toUpperCase() + w.slice(1)));
}

export function intBars(n: number): string {
  const heights = [3, 6, 9, 12];
  const bars = heights
    .map((h, i) => {
      const y = 12 - h;
      const fill = i < n ? "var(--text-2)" : "var(--border)";
      return `<rect x="${i * 5}" y="${y}" width="3" height="${h}" rx="1" fill="${fill}"/>`;
    })
    .join("");
  return `<svg class="int-bars" viewBox="0 0 20 12" width="20" height="12" aria-hidden="true">${bars}</svg>`;
}

export function detRow(label: string, value: string, cls?: string): string {
  if (!value) return "";
  return `<div class="lib-det-row"><span class="lib-det-label">${esc(label)}</span><span class="lib-det-val${cls ? ` ${cls}` : ""}">${esc(value)}</span></div>`;
}

export const BEAT_LABEL: Record<string, string> = {
  "/": "ramp", "^": "spike", "-": "hold", _: "rest", ">": "transition", "~": "liminal",
};

export const BEAT_WORD: Record<string, string> = {
  "/": "Ramp", "^": "Spike", "-": "Hold", "_": "Rest", ">": "Transition", "~": "Liminal",
};

export const BEAT_COLOR_CLASS: Record<string, string> = {
  "/": "bt-ramp", "^": "bt-spike", "-": "bt-hold", "_": "bt-rest", ">": "bt-transition", "~": "bt-liminal",
};

export const BEAT_ORDER: Record<string, number> = {
  "/": 0, "^": 1, "-": 2, "_": 3, ">": 4, "~": 5,
};

export const PHASE_FULL: Record<string, string> = {
  p: "Pre-arc", b: "Build", e: "Escalation", t: "Threshold",
  c: "Climax", r: "Reveal", d: "Denouement", "*": "Any",
};

export const COST_LABEL: Record<string, string> = {
  F: "Free", L: "Low", M: "Medium", H: "High",
  G: "Goodwill", $: "Ongoing financial", "?": "Unknown",
};

export const AUTONOMY_LABEL: Record<string, string> = {
  A: "Automated", HA: "Human-assisted", HM: "Human-managed",
  O: "Operator-run", C: "Confederate", CA: "Confederate-assisted",
  CR: "Confederate required", "~amb": "Ambient", "?": "Unknown",
};

export const LEAD_LABEL: Record<string, string> = {
  "0": "", sd: "Same day", "1d": "1 day",
  "3d": "2–3 days", "1w": "1 week", "2w": "2 weeks",
  "4w": "4 weeks", "8w": "8 weeks",
};

export const DETECTION_LABEL: Record<string, string> = {
  n: "", l: "Low", m: "Medium", s: "Significant",
  i: "Incident-level", S: "Situational", D: "Delayed", t: "Transient", "?": "Unknown",
};

export const REVERSIBILITY_LABEL: Record<string, string> = {
  e: "Easy", t: "Trivial", m: "Moderate", d: "Difficult", x: "Irreversible", "?": "Unknown",
};

export const LANDSCAPE_LABEL: Record<string, string> = {
  a: "Action", i: "Identity", "+": "Action + Identity",
};

const LEGACY_CHAR: Record<string, string> = {
  e: "ephemeral", p: "personal", s: "social", w: "world mark",
};

export function decodeLegacy(legacy: string): string {
  return [...legacy].map((c) => LEGACY_CHAR[c] ?? c).join(" + ");
}
