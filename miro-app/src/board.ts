// board.ts — Miro card parsing and board state reading.

import type { ArcData, ArcMeta, CardMeta } from "./types.js";

export interface RawCard {
  title?: string;
  description?: string;
  x?: number;
}

/**
 * Parse the optional key=value metadata from a card description.
 * Accepted keys: phase, day, gm/group_mode, ep/expected_participation, early_exit.
 */
export function parseCardDescription(desc: string): CardMeta {
  const meta: CardMeta = {};
  if (!desc) return meta;
  const tokens = desc.trim().split(/[\s\n]+/);
  for (const tok of tokens) {
    const eq = tok.indexOf("=");
    if (eq < 0) continue;
    const k = tok.slice(0, eq).toLowerCase();
    const v = tok.slice(eq + 1);
    if (k === "phase") meta.phase = v;
    else if (k === "day") meta.day = parseInt(v, 10);
    else if (k === "gm" || k === "group_mode") meta.group_mode = v;
    else if (k === "ep" || k === "expected_participation") meta.expected_participation = parseFloat(v);
    else if (k === "early_exit") meta.early_exit = v;
  }
  return meta;
}

/**
 * Extract the play ID from a card title.
 * Accepts the raw ID ("certified_mail"), a human-readable name ("Certified Mail"),
 * or a title with trailing notes ("certified_mail — day 3", "Certified Mail (act 1)").
 */
export function extractPlayId(title: string): string {
  return (
    title
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "_")
      .replace(/^[^a-z]+/, "")
      .split(/[^a-z0-9_]/)[0]
      ?.replace(/_+$/, "") ?? ""
  );
}

export function cardsToArcPlays(cards: RawCard[]): Array<{ id: string } & CardMeta> {
  return cards
    .slice()
    .sort((a, b) => (a.x ?? 0) - (b.x ?? 0))
    .map((card) => {
      const id = extractPlayId(card.title ?? "");
      const meta = parseCardDescription(card.description ?? "");
      return { id, ...meta };
    })
    .filter((el): el is { id: string } & CardMeta => Boolean(el.id));
}

export function cardsToArcJson(cards: RawCard[], arcMeta: ArcMeta): Partial<ArcData> {
  const plays = cardsToArcPlays(cards);
  const earlyExitCard = plays.find((p) => p.early_exit);
  return {
    arc_type: arcMeta.arcType,
    audience_scale: arcMeta.audienceScale,
    plays,
    early_exit: arcMeta.earlyExit || earlyExitCard?.early_exit || "",
  };
}

export async function readBoardState(): Promise<RawCard[]> {
  try {
    const selected = await miro.board.getSelection();
    const cards = selected.filter(
      (i): i is MiroSdk.CardItem => i.type === "card",
    );
    if (cards.length >= 1) return cards;
    return await miro.board.get({ type: "card" });
  } catch (e) {
    console.error("Miro board read error:", e);
    return [];
  }
}
