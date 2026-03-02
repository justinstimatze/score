// main.ts — panel entry point: wires tabs, lint/plan handlers, and all subsystems.

import { lintArc } from "./linter.js";
import { planArc } from "./planner.js";
import type { ArcMeta, Profile } from "./types.js";

import { ensureData, loadError, mechIndex, playInfo, stripsMap } from "./data.js";
import { cardsToArcJson, readBoardState, type RawCard } from "./board.js";
import { renderIssues, renderPlan } from "./render.js";
import { initLibrary, libRendered, renderLibrary } from "./library.js";
import { initProfileForm, onProfileFormChange } from "./profile.js";
import { dropDemoArc } from "./demos.js";
import { el, esc } from "./utils.js";

// ── SHARED STATE ──────────────────────────────────────────────────────────────

export let isMiro = false;
let currentCards: RawCard[] = [];
let currentProfile: Profile | null = null;
let currentArcMeta: ArcMeta = {
  arcType: "investigation",
  audienceScale: "intimate",
  earlyExit: "",
};

// ── TAB SWITCHING ─────────────────────────────────────────────────────────────

export function onTabClick(tab: string): void {
  document.querySelectorAll<HTMLButtonElement>(".tab-btn").forEach((b) => {
    b.classList.remove("active");
    b.setAttribute("aria-selected", "false");
  });
  document.querySelectorAll<HTMLElement>(".tab-panel").forEach((p) =>
    p.classList.remove("active"),
  );
  const activeBtn = el<"button">(`tab-btn-${tab}`);
  activeBtn.classList.add("active");
  activeBtn.setAttribute("aria-selected", "true");
  el<"section">(`tab-${tab}`).classList.add("active");

  if (tab === "library" && !libRendered && stripsMap) {
    renderLibrary();
  }
}

// ── LINT / PLAN HANDLERS ──────────────────────────────────────────────────────

function readArcInput(): RawCard[] {
  const ta = document.getElementById("arc-input") as HTMLTextAreaElement | null;
  if (!ta) return [];
  return ta.value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, i) => ({ title: line, x: i }));
}

async function onLintClick(): Promise<void> {
  const out = el<"div">("lint-output");
  out.innerHTML = "<div class='loading'>Checking arc…</div>";

  if (!(await ensureData())) {
    out.innerHTML = `<div class="sev-error">Data load failed: ${esc(loadError)}</div>`;
    return;
  }

  currentCards = isMiro ? await readBoardState() : readArcInput();
  if (!currentCards.length) {
    out.innerHTML = isMiro
      ? "<div class='sev-warn'>No plays found. Select cards on the board, or add plays first.</div>"
      : "<div class='sev-warn'>No plays entered. Add play IDs above, one per line.</div>";
    return;
  }

  const arcJson = cardsToArcJson(currentCards, currentArcMeta);
  const result = lintArc(arcJson, stripsMap!);

  el<"span">("play-count").textContent = `${currentCards.length} plays`;
  out.innerHTML = renderIssues(result);
}

async function onPlanClick(): Promise<void> {
  const out = el<"div">("plan-output");
  out.innerHTML = "<div class='loading'>Analyzing arc…</div>";

  if (!(await ensureData())) {
    out.innerHTML = `<div class="sev-error">Data load failed: ${esc(loadError)}</div>`;
    return;
  }

  if (!currentProfile) {
    out.innerHTML = "<div class='sev-warn'>No profile set. Expand the Profile section to create one.</div>";
    return;
  }

  if (!currentCards.length) {
    currentCards = isMiro ? await readBoardState() : readArcInput();
  }

  const arcJson = cardsToArcJson(currentCards, currentArcMeta);
  const result = planArc(arcJson, currentProfile, stripsMap!, mechIndex!);
  result.profile_name = currentProfile.name ?? "unnamed";

  out.innerHTML = renderPlan(result);
}

function onArcMetaChange(): void {
  currentArcMeta = {
    arcType: el<"div">("arc-type").dataset["value"] ?? "investigation",
    audienceScale: el<"div">("audience-scale").dataset["value"] ?? "intimate",
    earlyExit: (el<"input">("early-exit") as HTMLInputElement).value.trim(),
  };
}

// ── CUSTOM SELECT ─────────────────────────────────────────────────────────────

function closeAllDropdowns(): void {
  document.querySelectorAll<HTMLElement>(".cs-menu").forEach((m) => {
    m.hidden = true;
  });
  document.querySelectorAll<HTMLButtonElement>(".cs-trigger").forEach((t) => {
    t.setAttribute("aria-expanded", "false");
  });
}

function initCustomSelects(): void {
  document.querySelectorAll<HTMLElement>(".custom-select").forEach((cs) => {
    const trigger = cs.querySelector<HTMLButtonElement>(".cs-trigger")!;
    const menu = cs.querySelector<HTMLElement>(".cs-menu")!;
    const isProfileSelect = cs.id.startsWith("pf-");

    trigger.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = !menu.hidden;
      closeAllDropdowns();
      if (!isOpen) {
        menu.hidden = false;
        trigger.setAttribute("aria-expanded", "true");
        (menu.querySelector<HTMLElement>(".cs-option"))?.focus();
      }
    });

    menu.addEventListener("keydown", (e) => {
      const options = Array.from(menu.querySelectorAll<HTMLElement>(".cs-option"));
      const idx = options.indexOf(document.activeElement as HTMLElement);
      if (e.key === "ArrowDown") {
        e.preventDefault();
        options[(idx + 1) % options.length]?.focus();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        options[(idx - 1 + options.length) % options.length]?.focus();
      } else if (e.key === "Escape") {
        closeAllDropdowns();
        trigger.focus();
      } else if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        (document.activeElement as HTMLElement)?.click();
      }
    });

    menu.querySelectorAll<HTMLElement>(".cs-option").forEach((opt) => {
      opt.addEventListener("click", () => {
        const value = opt.dataset["value"] ?? "";
        const label = opt.textContent?.trim() ?? "";
        cs.dataset["value"] = value;
        (cs.querySelector<HTMLElement>(".cs-label") as HTMLElement).textContent = label;
        menu.querySelectorAll<HTMLElement>(".cs-option").forEach((o) =>
          o.classList.toggle("cs-selected", o === opt),
        );
        closeAllDropdowns();
        trigger.focus();
        if (isProfileSelect) onProfileFormChange();
        else onArcMetaChange();
      });
    });
  });

  document.addEventListener("click", closeAllDropdowns);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeAllDropdowns();
  });
}

// ── INIT ──────────────────────────────────────────────────────────────────────

async function init(): Promise<void> {
  // Detect whether we're inside a Miro board (always an iframe) or running standalone.
  isMiro = window !== window.top;
  document.body.classList.toggle("standalone", !isMiro);
  const arcInputWrap = document.getElementById("arc-input-wrap");
  if (arcInputWrap) arcInputWrap.hidden = isMiro;
  // Hide demo notes when user manually edits the arc input
  const arcInput = document.getElementById("arc-input");
  const demoNotes = document.getElementById("demo-notes");
  if (arcInput && demoNotes) {
    arcInput.addEventListener("input", () => { demoNotes.hidden = true; });
  }

  el<"button">("lint-btn").addEventListener("click", onLintClick);
  el<"button">("plan-btn").addEventListener("click", onPlanClick);
  el<"input">("early-exit").addEventListener("input", onArcMetaChange);

  document.querySelectorAll<HTMLButtonElement>(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => onTabClick(btn.dataset["tab"] ?? "lint"));
  });

  document.querySelectorAll<HTMLButtonElement>(".demo-btn").forEach((btn) => {
    btn.addEventListener("click", () => void dropDemoArc(btn.dataset["arc"] ?? ""));
  });

  initCustomSelects();

  initProfileForm({
    mechIndex: null,
    onProfileChange: (profile) => { currentProfile = profile; },
  });

  const dataStatusEl = el<"div">("data-status");
  await ensureData();

  if (loadError) {
    dataStatusEl.textContent = `Data error: ${loadError}`;
    dataStatusEl.className = "data-err";
  } else {
    const count = Object.keys(stripsMap ?? {}).length;
    dataStatusEl.textContent = `${count} plays`;
    dataStatusEl.className = "data-ok";

    initLibrary({
      stripsMap: stripsMap!,
      mechIndex: mechIndex!,
      playInfo: playInfo,
      onTabSwitch: onTabClick,
    });

    renderLibrary();
  }

  try {
    miro.board.ui.on("selection:update", () => {
      const badge = document.getElementById("play-count");
      if (badge) badge.textContent = "Selection changed — run Check Arc to update";
    });
  } catch {
    console.log("Running outside Miro — board events not available");
  }
}

document.addEventListener("DOMContentLoaded", init);
