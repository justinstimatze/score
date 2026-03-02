// data.ts — loads and exposes the three play data files.
// Call ensureData() before accessing stripsMap, mechIndex, or playInfo.

import { loadStrips } from "./linter.js";
import type { MechIndex, PlayInfo, StripMap } from "./types.js";

export let stripsMap: StripMap | null = null;
export let mechIndex: MechIndex | null = null;
export let playInfo: PlayInfo = {};
export let loadError: string | null = null;

let loading: Promise<boolean> | null = null;

export function ensureData(): Promise<boolean> {
  if (stripsMap && mechIndex) return Promise.resolve(true);
  if (loading) return loading;
  loading = _load();
  return loading;
}

async function _load(): Promise<boolean> {
  try {
    const [stripsRes, mechRes, infoRes] = await Promise.all([
      fetch("./plays_strips.json"),
      fetch("./plays_mechanisms.json"),
      fetch("./plays_info.json"),
    ]);
    if (!stripsRes.ok) throw new Error(`plays_strips.json: ${stripsRes.status}`);
    if (!mechRes.ok) throw new Error(`plays_mechanisms.json: ${mechRes.status}`);

    const stripsData = (await stripsRes.json()) as Array<{ id: string; strip: string }>;
    const mechData = (await mechRes.json()) as unknown;

    stripsMap = loadStrips(stripsData);
    mechIndex = Array.isArray(mechData)
      ? Object.fromEntries(
          (mechData as Array<{ id?: string; play_id?: string; mechanisms?: string[] }>).map(
            (e) => [e.id ?? e.play_id, e.mechanisms ?? []],
          ),
        )
      : (mechData as MechIndex);

    if (Object.keys(mechIndex ?? {}).length === 0) {
      console.warn(
        "plays_mechanisms.json loaded but produced an empty mechIndex — " +
        "check file format (expected array of {id, mechanisms} or object keyed by play ID)",
      );
    }

    if (infoRes.ok) {
      playInfo = (await infoRes.json()) as PlayInfo;
    }
    return true;
  } catch (e) {
    loadError = (e as Error).message;
    loading = null; // allow retry
    return false;
  }
}
