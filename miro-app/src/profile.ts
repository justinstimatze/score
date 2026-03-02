// profile.ts — profile form editor, 3-slot persistence, and template loading.

import type { BigFive, MechIndex, Profile } from "./types.js";
import { esc, humanName } from "./utils.js";

// ── SLOTS ─────────────────────────────────────────────────────────────────────

const SLOT_KEY = "score-profile-slots";
const NUM_SLOTS = 3;

interface SlotData { label: string; profile: Profile | null; }

export let activeSlot = 0;

function loadSlots(): SlotData[] {
  try {
    const raw = JSON.parse(localStorage.getItem(SLOT_KEY) ?? "[]") as SlotData[];
    return Array.from({ length: NUM_SLOTS }, (_, i) => raw[i] ?? { label: `Slot ${i + 1}`, profile: null });
  } catch {
    return Array.from({ length: NUM_SLOTS }, (_, i) => ({ label: `Slot ${i + 1}`, profile: null }));
  }
}

function saveSlots(slots: SlotData[]): void {
  localStorage.setItem(SLOT_KEY, JSON.stringify(slots));
}

export let slots: SlotData[] = loadSlots();

// ── FORM → PROFILE ────────────────────────────────────────────────────────────

export function formToProfile(): Profile {
  const nameInput = document.getElementById("pf-name") as HTMLInputElement | null;
  const name = nameInput?.value.trim() || undefined;

  const activeSensBtn = document.querySelector<HTMLElement>("#pf-sensitivity .pf-seg-btn.active");
  const sensitivity = (activeSensBtn?.dataset["val"] ?? "medium") as "low" | "medium" | "high";

  const regEl = document.getElementById("pf-register") as HTMLElement | null;
  const p5_register = regEl?.dataset["value"] || undefined;

  const identEl = document.getElementById("pf-identity") as HTMLElement | null;
  const identity_invite = identEl?.dataset["value"] || undefined;

  const big_five: BigFive = {};
  document.querySelectorAll<HTMLInputElement>(".big5-slider").forEach((sl) => {
    const dim = sl.dataset["dim"] as keyof BigFive;
    if (dim) big_five[dim] = parseFloat(sl.value);
  });

  const mechanisms: Record<string, number> = {};
  document.querySelectorAll<HTMLElement>(".pf-mech-row").forEach((row) => {
    const mech = row.dataset["mech"] ?? "";
    const sl = row.querySelector<HTMLInputElement>(".pf-mech-slider");
    if (mech && sl) mechanisms[mech] = parseFloat(sl.value);
  });

  const hard_constraints: string[] = [];
  document.querySelectorAll<HTMLElement>(".pf-chip[data-val]").forEach((chip) => {
    const v = chip.dataset["val"] ?? "";
    if (v) hard_constraints.push(v);
  });

  return { name, mechanisms, big_five, sensitivity, p5_register, identity_invite, identity_negative_space: [], hard_constraints };
}

// ── PROFILE → FORM ────────────────────────────────────────────────────────────

function setCustomSelect(id: string, value: string): void {
  const cs = document.getElementById(id) as HTMLElement | null;
  if (!cs) return;
  cs.dataset["value"] = value;
  const opt = cs.querySelector<HTMLElement>(`.cs-option[data-value="${value}"]`);
  const labelEl = cs.querySelector<HTMLElement>(".cs-label");
  if (labelEl) labelEl.textContent = opt?.textContent?.trim() ?? (value || "— none —");
  cs.querySelectorAll<HTMLElement>(".cs-option").forEach((o) =>
    o.classList.toggle("cs-selected", o === opt),
  );
}

export function profileToForm(p: Profile): void {
  const nameInput = document.getElementById("pf-name") as HTMLInputElement | null;
  if (nameInput) nameInput.value = p.name ?? "";

  const sens = p.sensitivity ?? "medium";
  document.querySelectorAll<HTMLElement>("#pf-sensitivity .pf-seg-btn").forEach((btn) => {
    const active = btn.dataset["val"] === sens;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-checked", active ? "true" : "false");
  });

  setCustomSelect("pf-register", p.p5_register ?? "naive");
  setCustomSelect("pf-identity", p.identity_invite ?? "");

  const big5 = p.big_five ?? {};
  document.querySelectorAll<HTMLInputElement>(".big5-slider").forEach((sl) => {
    const dim = sl.dataset["dim"] as keyof BigFive;
    const val = big5[dim] ?? 0;
    sl.value = String(val);
    const valEl = sl.nextElementSibling as HTMLElement | null;
    if (valEl) valEl.textContent = val.toFixed(2);
  });

  renderMechRows(p.mechanisms ?? {});
  renderConstraints(p.hard_constraints ?? []);
}

// ── MECH ROWS ─────────────────────────────────────────────────────────────────

export function renderMechRows(mechanisms: Record<string, number>): void {
  const list = document.getElementById("pf-mechs");
  if (!list) return;
  const sorted = Object.entries(mechanisms).sort((a, b) => b[1] - a[1]);
  list.innerHTML = sorted.map(([id, weight]) => mechRowHtml(id, weight)).join("");
}

function mechRowHtml(id: string, weight: number): string {
  const w = Math.max(0, Math.min(1, weight));
  const pct = w.toFixed(2);
  return `<div class="pf-mech-row" data-mech="${esc(id)}">
    <span class="pf-mech-name" title="${esc(id)}">${esc(humanName(id))}</span>
    <input type="range" class="pf-mech-slider" min="0" max="1" step="0.05" value="${pct}" aria-label="${esc(humanName(id))} weight" />
    <span class="pf-mech-val" aria-live="polite">${pct}</span>
    <button class="pf-mech-remove" title="Remove ${esc(humanName(id))}" aria-label="Remove ${esc(humanName(id))}">×</button>
  </div>`;
}

export function renderConstraints(constraints: string[]): void {
  const container = document.getElementById("pf-constraints");
  if (!container) return;
  container.innerHTML = constraints
    .map((c) => `<span class="pf-chip" data-val="${esc(c)}">${esc(c)}<button class="pf-chip-x" title="Remove ${esc(c)}" aria-label="Remove constraint ${esc(c)}">×</button></span>`)
    .join("");
}

// ── ALL MECHANISMS ─────────────────────────────────────────────────────────────

let _mechIndex: MechIndex | null = null;

export function setMechIndex(mi: MechIndex): void {
  _mechIndex = mi;
}

function allMechanisms(): string[] {
  if (!_mechIndex) return [];
  const names = new Set<string>();
  Object.values(_mechIndex).forEach((mechs) => mechs.forEach((m) => names.add(m)));
  return [...names].sort();
}

// ── SLOT + STATUS HELPERS ─────────────────────────────────────────────────────

let _onProfileChange: ((profile: Profile | null) => void) | null = null;

export function onProfileFormChange(): void {
  const profile = formToProfile();
  slots[activeSlot] = { label: profile.name || `Slot ${activeSlot + 1}`, profile };
  saveSlots(slots);
  updateSlotButtons();
  const statusEl = document.getElementById("profile-status");
  if (statusEl) {
    statusEl.textContent = `✓ Active: ${profile.name ?? "unnamed"}`;
    statusEl.className = "profile-ok";
  }
  _onProfileChange?.(profile);
}

export function updateSlotButtons(): void {
  document.querySelectorAll<HTMLButtonElement>(".slot-btn").forEach((btn, i) => {
    const slot = slots[i];
    const isEmpty = !slot?.profile;
    const active = i === activeSlot;
    btn.classList.toggle("active", active);
    btn.classList.toggle("slot-empty", isEmpty);
    btn.setAttribute("aria-checked", active ? "true" : "false");
    btn.textContent = slot?.profile?.name || `Slot ${i + 1}`;
  });
}

export function switchSlot(i: number): void {
  activeSlot = i;
  const slot = slots[i];
  const statusEl = document.getElementById("profile-status");
  if (slot?.profile) {
    profileToForm(slot.profile);
    if (statusEl) {
      statusEl.textContent = `✓ Active: ${slot.profile.name ?? "unnamed"}`;
      statusEl.className = "profile-ok";
    }
    _onProfileChange?.(slot.profile);
  } else {
    profileToForm({
      mechanisms: {},
      big_five: { O: 0, C: 0, N: 0, E: 0, A: 0 },
      sensitivity: "medium",
      p5_register: "naive",
      identity_negative_space: [],
      hard_constraints: [],
    });
    if (statusEl) {
      statusEl.textContent = "No profile in slot";
      statusEl.className = "profile-empty";
    }
    _onProfileChange?.(null);
  }
  updateSlotButtons();
}

// ── MECHANISM PICKER ──────────────────────────────────────────────────────────

function renderMechOptions(query: string): void {
  const opts = document.getElementById("pf-mech-opts");
  if (!opts) return;
  const existing = new Set<string>(
    Array.from(document.querySelectorAll<HTMLElement>(".pf-mech-row"), (r) => r.dataset["mech"] ?? ""),
  );
  const all = allMechanisms();
  const q = query.toLowerCase();
  const filtered = all.filter(
    (m) => !existing.has(m) && (!q || m.includes(q) || humanName(m).toLowerCase().includes(q)),
  );
  if (!filtered.length) {
    opts.innerHTML = "<div class='pf-picker-empty'>No mechanisms found</div>";
    return;
  }
  opts.innerHTML = filtered
    .slice(0, 50)
    .map((m) => `<div class="pf-picker-opt" data-mech="${esc(m)}" role="option" tabindex="0">${esc(humanName(m))}</div>`)
    .join("");
}

function initMechPicker(): void {
  const addBtn = document.getElementById("pf-add-mech") as HTMLButtonElement | null;
  const picker = document.getElementById("pf-picker");
  const query = document.getElementById("pf-mech-query") as HTMLInputElement | null;
  const opts = document.getElementById("pf-mech-opts");
  if (!addBtn || !picker || !query || !opts) return;

  addBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    picker.hidden = !picker.hidden;
    addBtn.setAttribute("aria-expanded", picker.hidden ? "false" : "true");
    if (!picker.hidden) {
      query.value = "";
      renderMechOptions("");
      query.focus();
    }
  });

  query.addEventListener("input", () => renderMechOptions(query.value.trim()));

  const addMech = (mech: string): void => {
    if (!mech) return;
    const list = document.getElementById("pf-mechs");
    if (list) list.insertAdjacentHTML("beforeend", mechRowHtml(mech, 0.5));
    picker.hidden = true;
    addBtn.setAttribute("aria-expanded", "false");
    onProfileFormChange();
  };

  opts.addEventListener("click", (e) => {
    const opt = (e.target as HTMLElement).closest<HTMLElement>(".pf-picker-opt");
    if (opt) addMech(opt.dataset["mech"] ?? "");
  });

  opts.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const opt = (e.target as HTMLElement).closest<HTMLElement>(".pf-picker-opt");
    if (opt) { e.preventDefault(); addMech(opt.dataset["mech"] ?? ""); }
  });

  document.addEventListener("click", (e) => {
    if (!picker.hidden && !picker.contains(e.target as Node) && e.target !== addBtn) {
      picker.hidden = true;
      addBtn.setAttribute("aria-expanded", "false");
    }
  });
}

// ── PROFILE TEMPLATES ─────────────────────────────────────────────────────────

const PROFILE_TEMPLATES: Record<string, Profile> = {
  pattern_seeker: {
    name: "Pattern Seeker",
    mechanisms: {
      curiosity_exploration: 0.9,
      information_gap: 0.8,
      participant_as_detective: 0.7,
      narrative_without_exposition: 0.7,
      knowledge_frontier: 0.7,
      apophenia_induction: 0.6,
    },
    big_five: { O: 0.8, C: 0.5, N: 0.1, E: -0.2, A: 0.1 },
    sensitivity: "high",
    p5_register: "unsettled",
    identity_invite: "seeker_pattern_finder",
    identity_negative_space: [],
    hard_constraints: [],
  },
  sensualist: {
    name: "Sensualist",
    mechanisms: {
      sensory_seeking: 0.9,
      aesthetic_response: 0.8,
      flow_state: 0.7,
      somatic_awareness: 0.7,
      embodied_cognition: 0.6,
    },
    big_five: { O: 0.7, C: -0.2, N: 0.0, E: 0.2, A: 0.3 },
    sensitivity: "high",
    p5_register: "wonder",
    identity_negative_space: [],
    hard_constraints: [],
  },
  social_being: {
    name: "Social Being",
    mechanisms: {
      belonging: 0.9,
      social_synchrony: 0.8,
      group_cohesion: 0.7,
      empathetic_resonance: 0.7,
      direct_interaction: 0.6,
    },
    big_five: { O: 0.3, C: 0.2, N: 0.1, E: 0.8, A: 0.7 },
    sensitivity: "medium",
    p5_register: "opened",
    identity_negative_space: [],
    hard_constraints: [],
  },
};

export function loadTemplate(key: string): void {
  const tpl = PROFILE_TEMPLATES[key];
  if (!tpl) return;
  profileToForm(tpl);
  onProfileFormChange();
}

// ── INIT ──────────────────────────────────────────────────────────────────────

export function initProfileForm(deps: {
  mechIndex: MechIndex | null;
  onProfileChange: (profile: Profile | null) => void;
}): void {
  if (deps.mechIndex) _mechIndex = deps.mechIndex;
  _onProfileChange = deps.onProfileChange;

  document.querySelectorAll<HTMLInputElement>(".big5-slider").forEach((sl) => {
    sl.addEventListener("input", () => {
      const valEl = sl.nextElementSibling as HTMLElement | null;
      if (valEl) valEl.textContent = parseFloat(sl.value).toFixed(2);
      onProfileFormChange();
    });
  });

  document.querySelectorAll<HTMLElement>("#pf-sensitivity .pf-seg-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll<HTMLElement>("#pf-sensitivity .pf-seg-btn").forEach((b) => {
        b.classList.remove("active");
        b.setAttribute("aria-checked", "false");
      });
      btn.classList.add("active");
      btn.setAttribute("aria-checked", "true");
      onProfileFormChange();
    });
  });

  const nameInput = document.getElementById("pf-name") as HTMLInputElement | null;
  nameInput?.addEventListener("input", onProfileFormChange);

  document.querySelectorAll<HTMLButtonElement>(".slot-btn").forEach((btn) => {
    btn.addEventListener("click", () => switchSlot(parseInt(btn.dataset["slot"] ?? "0", 10)));
  });

  document.querySelectorAll<HTMLButtonElement>(".tpl-btn").forEach((btn) => {
    btn.addEventListener("click", () => loadTemplate(btn.dataset["tpl"] ?? ""));
  });

  const mechList = document.getElementById("pf-mechs");
  mechList?.addEventListener("input", (e) => {
    const target = e.target as HTMLElement;
    if (!target.classList.contains("pf-mech-slider")) return;
    const row = target.closest<HTMLElement>(".pf-mech-row");
    const valEl = row?.querySelector<HTMLElement>(".pf-mech-val");
    if (valEl) valEl.textContent = parseFloat((target as HTMLInputElement).value).toFixed(2);
    onProfileFormChange();
  });
  mechList?.addEventListener("click", (e) => {
    const btn = (e.target as HTMLElement).closest<HTMLElement>(".pf-mech-remove");
    if (!btn) return;
    btn.closest<HTMLElement>(".pf-mech-row")?.remove();
    onProfileFormChange();
  });

  const constraintInput = document.getElementById("pf-constraint-input") as HTMLInputElement | null;
  constraintInput?.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    const val = (e.target as HTMLInputElement).value.trim();
    if (!val) return;
    const container = document.getElementById("pf-constraints");
    if (container) {
      container.insertAdjacentHTML(
        "beforeend",
        `<span class="pf-chip" data-val="${esc(val)}">${esc(val)}<button class="pf-chip-x" title="Remove ${esc(val)}" aria-label="Remove constraint ${esc(val)}">×</button></span>`,
      );
    }
    (e.target as HTMLInputElement).value = "";
    onProfileFormChange();
  });

  const constraintContainer = document.getElementById("pf-constraints");
  constraintContainer?.addEventListener("click", (e) => {
    const btn = (e.target as HTMLElement).closest<HTMLElement>(".pf-chip-x");
    if (!btn) return;
    btn.closest<HTMLElement>(".pf-chip")?.remove();
    onProfileFormChange();
  });

  initMechPicker();
  updateSlotButtons();
  switchSlot(0);
}
