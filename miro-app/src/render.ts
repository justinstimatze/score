// render.ts — HTML rendering for linter and planner output.

import { lintArc } from "./linter.js";
import type { PlanEntry, PlanEntryError, PlanResult } from "./types.js";
import { BEAT_LABEL, esc, humanName } from "./utils.js";

// ── LINTER OUTPUT ─────────────────────────────────────────────────────────────

const SEV_CLASS = { ERROR: "sev-error", WARN: "sev-warn", INFO: "sev-info" } as const;
const SEV_ICON = { ERROR: "✖", WARN: "▲", INFO: "ℹ" } as const;

export function renderIssues(result: ReturnType<typeof lintArc>): string {
  const { issues, errors, warns, infos } = result;
  const bShape = result.beatShape;
  const bMix = result.beatMix;
  const lMix = result.legacyMix;

  if (!issues.length && !bShape) return "<p class='ok'>No issues.</p>";

  const statusClass = errors.length ? "status-fail" : warns.length ? "status-warn" : "status-pass";
  const statusText = errors.length ? "Errors" : warns.length ? "Warnings" : "Pass";

  let html = `<div class="status-bar ${statusClass}">${statusText}: ${errors.length} error${errors.length === 1 ? "" : "s"}, ${warns.length} warning${warns.length === 1 ? "" : "s"}, ${infos.length} note${infos.length === 1 ? "" : "s"}</div>`;

  if (bShape) {
    html += `<div class="beat-block">
      <div class="beat-shape">${esc(bShape)}</div>
      <div class="beat-meta">${esc(bMix)}</div>
      ${lMix ? `<div class="beat-meta legacy">${esc(lMix)}</div>` : ""}
    </div>`;
  }

  for (const group of [errors, warns, infos]) {
    for (const iss of group) {
      const cls = SEV_CLASS[iss.severity] ?? "sev-info";
      const icon = SEV_ICON[iss.severity] ?? "ℹ";
      const pos = iss.position >= 0 ? `[${iss.position + 1}] ` : "[arc] ";
      html += `<div class="issue ${cls}">
        <span class="sev-icon">${icon}</span>
        <span class="issue-pos">${pos}</span>
        <span class="issue-id">${esc(iss.play_id)}</span>
        <span class="issue-msg"> — ${esc(iss.message)}</span>
      </div>`;
    }
  }
  return html;
}

// ── PLANNER OUTPUT ────────────────────────────────────────────────────────────

function isPlanEntryError(item: PlanEntry | PlanEntryError): item is PlanEntryError {
  return "error" in item;
}

export function renderPlan(result: PlanResult): string {
  if (!result?.plan?.length) return "<p class='ok'>No plays to plan.</p>";

  let html = `<div class="plan-header">Profile: ${esc(result.profile_name ?? "unnamed")}`;
  if (result.warning_count > 0) {
    html += ` · <span class="warn-tag">⚠ ${result.warning_count} profile warnings</span>`;
  }
  html += "</div>";

  for (const p of result.plan) {
    if (isPlanEntryError(p)) {
      html += `<div class="plan-play plan-error"><button class="play-id play-lib-link" data-id="${esc(p.id)}">${esc(humanName(p.id))}</button> — ${esc(p.error)}</div>`;
      continue;
    }
    const bucketClass = `eng-${p.engagement_bucket}`;
    const beatLabel = BEAT_LABEL[p.beat] ?? p.beat;
    const warnHtml = p.warnings.length
      ? `<div class="play-warnings">${p.warnings.map((w) => `<div class="play-warn">⚠ ${esc(w)}</div>`).join("")}</div>`
      : "";
    const failHtml =
      p.top_failure_pct > 5
        ? `<span class="failure">${esc(p.top_failure_mode)} (${p.top_failure_pct}%)</span>`
        : "";
    const recovHtml = p.top_recovery
      ? `<span class="recovery"> → ${esc(humanName(p.top_recovery))}</span>`
      : "";

    html += `<div class="plan-play">
      <div class="play-header">
        <span class="play-pos">${p.position}.</span>
        <button class="play-id play-lib-link" data-id="${esc(p.id)}">${esc(humanName(p.id))}</button>
        <span class="beat-tag">${esc(beatLabel)}</span>
        <span class="eng-badge ${bucketClass}">${esc(p.engagement_bucket)} (${p.engagement_pct}%)</span>
        <span class="coverage-tag">${esc(p.coverage_tag)}</span>
        ${p.persona_bound_tag ? `<span class="pb-tag">${esc(p.persona_bound_tag)}</span>` : ""}
      </div>
      ${failHtml || recovHtml ? `<div class="play-fail">${failHtml}${recovHtml}</div>` : ""}
      ${warnHtml}
    </div>`;
  }
  return html;
}
