// library.ts — play library browser: search, filters, favorites, frecency, drag.

import type { MechIndex, PlayInfo, StripMap } from "./types.js";
import {
  AUTONOMY_LABEL,
  BEAT_COLOR_CLASS,
  BEAT_ORDER,
  BEAT_WORD,
  COST_LABEL,
  DETECTION_LABEL,
  LANDSCAPE_LABEL,
  LEAD_LABEL,
  PHASE_FULL,
  REVERSIBILITY_LABEL,
  decodeLegacy,
  detRow,
  esc,
  humanName,
  intBars,
} from "./utils.js";

// ── FAVORITES ─────────────────────────────────────────────────────────────────

const FAV_KEY = "score-favs";

let favs: Set<string> = (() => {
  try { return new Set(JSON.parse(localStorage.getItem(FAV_KEY) ?? "[]") as string[]); }
  catch { return new Set<string>(); }
})();

function saveFavs(): void {
  localStorage.setItem(FAV_KEY, JSON.stringify([...favs]));
}

// ── FRECENCY ──────────────────────────────────────────────────────────────────

const FRECENCY_KEY = "score-frecency";

interface FrecencyEntry { t: number; n: number; }

function loadFrecency(): Record<string, FrecencyEntry> {
  try { return JSON.parse(localStorage.getItem(FRECENCY_KEY) ?? "{}") as Record<string, FrecencyEntry>; }
  catch { return {}; }
}

export function touchFrecency(id: string): void {
  const frec = loadFrecency();
  const e = frec[id] ?? { t: 0, n: 0 };
  frec[id] = { t: Date.now(), n: e.n + 1 };
  localStorage.setItem(FRECENCY_KEY, JSON.stringify(frec));
}

function frecencyScore(id: string, frec: Record<string, FrecencyEntry>): number {
  const e = frec[id];
  if (!e) return 0;
  const ageHours = (Date.now() - e.t) / 3_600_000;
  return e.n / (ageHours + 1);
}

// ── FILTERS & STATE ───────────────────────────────────────────────────────────

interface LibFilters {
  query: string;
  beat: string;
  phase: string;
  favOnly: boolean;
  sort: "beat" | "frecency";
}

let libFilters: LibFilters = { query: "", beat: "", phase: "", favOnly: false, sort: "beat" };
export let libRendered = false;

// Data refs injected by initLibrary()
let _stripsMap: StripMap | null = null;
let _mechIndex: MechIndex | null = null;
let _playInfo: PlayInfo = {};

// ── RENDER ────────────────────────────────────────────────────────────────────

export function renderLibrary(): void {
  if (!_stripsMap) return;
  const out = document.getElementById("lib-output");
  if (!out) return;
  const { query, beat, phase } = libFilters;
  const q = query.toLowerCase();

  const plays = Object.values(_stripsMap).filter((p) => {
    if (libFilters.favOnly && !favs.has(p.id)) return false;
    if (q) {
      const mechs = (_mechIndex?.[p.id] ?? p.mechanisms).join(" ");
      const haystack = `${p.id} ${humanName(p.id)} ${mechs}`.toLowerCase();
      if (!haystack.includes(q)) return false;
    }
    if (beat && p.beat !== beat) return false;
    if (phase && !p.arc_fits_phase(phase)) return false;
    return true;
  });

  if (libFilters.sort === "frecency") {
    const frec = loadFrecency();
    plays.sort((a, b) => {
      const diff = frecencyScore(b.id, frec) - frecencyScore(a.id, frec);
      if (diff !== 0) return diff;
      const bo = (BEAT_ORDER[a.beat] ?? 9) - (BEAT_ORDER[b.beat] ?? 9);
      return bo !== 0 ? bo : a.id.localeCompare(b.id);
    });
  } else {
    plays.sort((a, b) => {
      const bo = (BEAT_ORDER[a.beat] ?? 9) - (BEAT_ORDER[b.beat] ?? 9);
      return bo !== 0 ? bo : a.id.localeCompare(b.id);
    });
  }

  const libCountEl = document.getElementById("lib-count");
  if (libCountEl) libCountEl.textContent = `${plays.length} of ${Object.keys(_stripsMap).length}`;

  if (!plays.length) {
    out.innerHTML = "<p class='empty-msg'>No plays match.</p>";
    libRendered = true;
    return;
  }

  out.innerHTML = plays
    .map((p) => {
      const info = _playInfo[p.id] ?? {};
      const btClass = BEAT_COLOR_CLASS[p.beat] ?? "";
      const beatWord = BEAT_WORD[p.beat] ?? p.beat;

      const phases = p.arc_codes
        .filter((c) => c !== "*")
        .map((c) => PHASE_FULL[c] ?? c)
        .join(" · ");

      const mechs = _mechIndex?.[p.id] ?? p.mechanisms;
      const mechStr = mechs.map((m) => humanName(m)).join(" · ");

      const leadStr = LEAD_LABEL[p.lead_time] ?? "";
      const detStr = DETECTION_LABEL[p.detection] ?? "";
      const revStr = REVERSIBILITY_LABEL[p.reversibility] ?? "";
      const landscapeStr = LANDSCAPE_LABEL[p.landscape] ?? "";
      const legacyStr = p.legacy ? decodeLegacy(p.legacy) : "";
      const groupStr = p.group_role && p.group_role !== "s"
        ? (p.group_role === "e" ? "Ensemble" : p.group_role === "lo" ? "Lottery / selection" : p.group_role)
        : "";
      const autoStr = AUTONOMY_LABEL[p.autonomy] ?? p.autonomy;
      const costStr = COST_LABEL[p.cost] ?? p.cost;

      const detail = [
        info.desc ? `<p class="lib-det-desc">${esc(info.desc)}</p>` : "",
        info.invite ? `<div class="lib-det-row lib-det-id"><span class="lib-det-label">ID</span><span class="lib-det-val lib-det-mono">${esc(p.id)}</span></div>` : "",
        detRow("Phases", phases),
        detRow("Mechanics", mechStr),
        detRow("Cost", costStr),
        leadStr ? detRow("Setup", leadStr) : "",
        detRow("Format", autoStr),
        groupStr ? detRow("Group", groupStr) : "",
        detRow("Plane", landscapeStr),
        legacyStr ? detRow("Legacy", legacyStr) : "",
        detStr ? detRow("Detection risk", detStr, "lib-det-warn") : "",
        revStr && !["Easy", "Trivial"].includes(revStr) ? detRow("Reversibility", revStr) : "",
        p.synergizes.length ? detRow("Pairs with", p.synergizes.join(", "), "lib-det-mono") : "",
        p.contraindicated_after.length ? detRow("Avoid after", p.contraindicated_after.join(", "), "lib-det-warn lib-det-mono") : "",
        p.requires.length ? detRow("Requires", p.requires.join(", "), "lib-det-mono") : "",
        p.persona_bound ? `<div class="lib-det-row"><span class="lib-det-label"></span><span class="lib-det-badge">Persona-bound</span></div>` : "",
      ].join("");

      return `<div class="lib-play" data-id="${esc(p.id)}" data-title="${esc(humanName(p.id))}">
        <div class="lib-play-row">
          <span class="lib-drag-handle miro-draggable" draggable="true" data-id="${esc(p.id)}" data-title="${esc(humanName(p.id))}" title="Drag to board">⠿</span>
          <div class="lib-name-col">
            <span class="lib-name">${esc(humanName(p.id))}</span>
            ${info.invite ? `<span class="lib-invite" title="${esc(info.invite)}">${esc(info.invite)}</span>` : `<span class="lib-id" title="${esc(p.id)}">${esc(p.id)}</span>`}
          </div>
          <div class="lib-right">
            <span class="beat-chip ${btClass}">${esc(beatWord)}</span>
            <span class="lib-int">${intBars(p.intensity_int)}</span>
            <button class="lib-star${favs.has(p.id) ? " lib-star-on" : ""}" data-id="${esc(p.id)}" title="${favs.has(p.id) ? "Starred" : "Star this play"}">${favs.has(p.id) ? "★" : "☆"}</button>
          </div>
        </div>
        <div class="lib-play-detail" hidden>
          ${detail}
        </div>
      </div>`;
    })
    .join("");

  libRendered = true;
}

// ── EVENT HANDLERS ────────────────────────────────────────────────────────────

export function onLibSearch(): void {
  const input = document.getElementById("lib-search") as HTMLInputElement | null;
  libFilters.query = input?.value.trim() ?? "";
  renderLibrary();
}

export function onLibFilter(group: string, value: string): void {
  if (group === "beat") libFilters.beat = value;
  else if (group === "phase") libFilters.phase = value;
  else if (group === "favs") libFilters.favOnly = value === "1";

  document.querySelectorAll<HTMLButtonElement>(`.filter-btn[data-filter="${group}"]`).forEach((b) => {
    const active = b.dataset["value"] === value;
    b.classList.toggle("active", active);
    b.setAttribute("aria-checked", active ? "true" : "false");
  });

  libRendered = false;
  renderLibrary();
}

export function onSortChange(sort: "beat" | "frecency"): void {
  libFilters.sort = sort;
  document.querySelectorAll<HTMLButtonElement>(".sort-btn").forEach((b) => {
    const active = b.dataset["sort"] === sort;
    b.classList.toggle("active", active);
    b.setAttribute("aria-checked", active ? "true" : "false");
  });
  libRendered = false;
  renderLibrary();
}

// ── LIBRARY NAVIGATION ────────────────────────────────────────────────────────

/** Switch to the library tab and expand the given play. onTabSwitch is called to activate the tab. */
export function showInLibrary(id: string, onTabSwitch: (tab: string) => void): void {
  onTabSwitch("library");
  requestAnimationFrame(() => {
    const playEl = document.querySelector<HTMLElement>(`.lib-play[data-id="${CSS.escape(id)}"]`);
    if (!playEl) return;
    playEl.scrollIntoView({ block: "center", behavior: "smooth" });
    const detail = playEl.querySelector<HTMLElement>(".lib-play-detail");
    if (detail?.hidden) {
      detail.hidden = false;
      touchFrecency(id);
    }
  });
}

// ── DRAG + BOARD EVENTS ────────────────────────────────────────────────────────

export function initDraggable(
  onTabSwitch: (tab: string) => void,
  getStripsMap: () => typeof _stripsMap,
): void {
  const libOut = document.getElementById("lib-output");
  libOut?.addEventListener("dragstart", (e) => {
    const handle = (e.target as HTMLElement).closest<HTMLElement>(".lib-drag-handle");
    if (!handle) { e.preventDefault(); return; }
    const id = handle.dataset["id"] ?? "";
    if (e.dataTransfer) {
      e.dataTransfer.effectAllowed = "copy";
      e.dataTransfer.setData("text/plain", id);
    }
  });

  try {
    miro.board.ui.on("selection:update", async () => {
      const sel = await miro.board.getSelection();
      const cards = sel.filter((i): i is MiroSdk.CardItem => i.type === "card");
      if (cards.length !== 1) return;
      const { extractPlayId } = await import("./board.js");
      const id = extractPlayId(cards[0]!.title ?? "");
      if (!id || !getStripsMap()?.[id]) return;
      showInLibrary(id, onTabSwitch);
    });

    miro.board.ui.on("drop", async ({ x, y, target }) => {
      let id = target.dataset["id"] ?? "";
      let title = target.dataset["title"] ?? "";
      if (!id) {
        const play = target.closest<HTMLElement>(".lib-play");
        if (!play) return;
        id = play.dataset["id"] ?? "";
        title = play.dataset["title"] ?? id;
      }
      if (!id) return;
      touchFrecency(id);
      await miro.board.createCard({ title: title || id, x, y });
    });
  } catch {
    // Running outside Miro (dev preview)
  }
}

// ── LIB OUTPUT CLICK HANDLER ──────────────────────────────────────────────────

export function initLibOutputClicks(onTabSwitch: (tab: string) => void): void {
  const out = document.getElementById("lib-output");
  if (!out) return;

  out.addEventListener("click", (e) => {
    const target = e.target as Element;

    if (target.classList.contains("lib-drag-handle")) {
      const play = (target as HTMLElement).closest<HTMLElement>(".lib-play");
      if (!play) return;
      const id = play.dataset["id"] ?? "";
      const title = play.dataset["title"] ?? id;
      if (!id) return;
      touchFrecency(id);
      try {
        void miro.board.createCard({ title: title || id }).catch((err: unknown) => {
          console.error("createCard failed:", err);
        });
      } catch {
        // Running outside Miro
      }
      return;
    }

    if (target.classList.contains("lib-star")) {
      const btn = target as HTMLElement;
      const id = btn.dataset["id"] ?? "";
      if (!id) return;
      if (favs.has(id)) {
        favs.delete(id);
        btn.textContent = "☆";
        btn.classList.remove("lib-star-on");
        btn.title = "Star this play";
      } else {
        favs.add(id);
        btn.textContent = "★";
        btn.classList.add("lib-star-on");
        btn.title = "Starred";
      }
      saveFavs();
      if (libFilters.favOnly) { libRendered = false; renderLibrary(); }
      return;
    }

    const play = target.closest(".lib-play") as HTMLElement | null;
    if (!play) return;
    const detail = play.querySelector<HTMLElement>(".lib-play-detail");
    if (detail) {
      const wasHidden = detail.hidden;
      detail.hidden = !wasHidden;
      if (wasHidden) touchFrecency(play.dataset["id"] ?? "");
    }
  });

  // Plan output: click play name to jump to library
  const planOut = document.getElementById("plan-output");
  planOut?.addEventListener("click", (e) => {
    const btn = (e.target as Element).closest<HTMLElement>(".play-lib-link");
    if (!btn) return;
    const id = btn.dataset["id"] ?? "";
    if (id) showInLibrary(id, onTabSwitch);
  });
}

// ── INIT ──────────────────────────────────────────────────────────────────────

export function initLibrary(deps: {
  stripsMap: StripMap;
  mechIndex: MechIndex;
  playInfo: PlayInfo;
  onTabSwitch: (tab: string) => void;
}): void {
  _stripsMap = deps.stripsMap;
  _mechIndex = deps.mechIndex;
  _playInfo = deps.playInfo;

  const searchEl = document.getElementById("lib-search");
  searchEl?.addEventListener("input", onLibSearch);

  document.querySelectorAll<HTMLButtonElement>(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", () =>
      onLibFilter(btn.dataset["filter"] ?? "", btn.dataset["value"] ?? ""),
    );
  });

  document.querySelectorAll<HTMLButtonElement>(".sort-btn").forEach((btn) => {
    btn.addEventListener("click", () =>
      onSortChange((btn.dataset["sort"] ?? "beat") as "beat" | "frecency"),
    );
  });

  initLibOutputClicks(deps.onTabSwitch);
  initDraggable(deps.onTabSwitch, () => _stripsMap);
}
