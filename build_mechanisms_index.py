#!/usr/bin/env python3
"""
build_mechanisms_index.py

Parses plays.md and extracts MECHANISMS for every play.
Outputs plays_mechanisms.json: { play_id: [mechanism, ...] }

Mechanism names are normalized (lowercase, underscores) with parenthetical
annotations stripped, so they match drivermap IDs directly.

Usage:
    python build_mechanisms_index.py
    python build_mechanisms_index.py --plays plays.md --out plays_mechanisms.json
"""

import argparse
import json
import re
import yaml
from pathlib import Path

PLAYS_FILE = Path(__file__).parent / "plays.md"
YAML_FILE  = Path(__file__).parent / "plays.yaml"
OUT_FILE   = Path(__file__).parent / "plays_mechanisms.json"


def _clean_mech(raw: str) -> str | None:
    """Normalize a single mechanism token."""
    # Strip parenthetical annotations
    s = re.sub(r"\([^)]*\)", "", raw)
    # Strip punctuation except underscores and letters
    s = re.sub(r"[^\w\s]", "", s)
    s = s.strip().lower().replace(" ", "_")
    # Drop empties and pure numeric leftovers
    if not s or s.isdigit():
        return None
    return s


def parse_plays_yaml(yaml_path: Path) -> dict[str, list[str]]:
    """Load mechanisms from plays.yaml. MECHANISMS is already a list."""
    index: dict[str, list[str]] = {}
    with yaml_path.open(encoding="utf-8") as f:
        docs = list(yaml.safe_load_all(f))
    for doc in docs:
        if not doc or not isinstance(doc, dict):
            continue
        play_id = doc.get("id")
        if not play_id:
            continue
        mechs_raw = doc.get("mechanisms", [])
        if isinstance(mechs_raw, list):
            mechs = [_clean_mech(m) for m in mechs_raw]
            mechs = [m for m in mechs if m]
        else:
            # Fallback: string
            tokens = re.split(r"[·,]", str(mechs_raw))
            mechs = [_clean_mech(t) for t in tokens]
            mechs = [m for m in mechs if m]
        if mechs:
            index[play_id] = mechs
    return index


def parse_plays_md(plays_path: Path) -> dict[str, list[str]]:
    """Parse mechanisms from plays.md (legacy fallback)."""
    text = plays_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    index: dict[str, list[str]] = {}
    current_id: str | None = None

    for line in lines:
        # Play ID line: `id:play_id` · `COST:...`
        id_match = re.search(r"`id:([a-z_][a-z0-9_]*)`", line)
        if id_match:
            current_id = id_match.group(1)
            continue

        # MECHANISMS field
        if current_id and line.startswith("**MECHANISMS:**"):
            raw_value = line[len("**MECHANISMS:**"):].strip()
            # Split on · or ,
            tokens = re.split(r"[·,]", raw_value)
            mechs = []
            for tok in tokens:
                clean = _clean_mech(tok)
                if clean:
                    mechs.append(clean)
            if mechs:
                index[current_id] = mechs
            # Don't reset current_id — other fields may follow

    return index


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plays", default=str(PLAYS_FILE))
    parser.add_argument("--yaml",  default=str(YAML_FILE))
    parser.add_argument("--out",   default=str(OUT_FILE))
    args = parser.parse_args()

    yaml_path = Path(args.yaml)
    if yaml_path.exists():
        index = parse_plays_yaml(yaml_path)
        print(f"Loaded from YAML: {yaml_path}")
    else:
        print(f"WARNING: {yaml_path} not found, falling back to plays.md")
        index = parse_plays_md(Path(args.plays))

    Path(args.out).write_text(json.dumps(index, indent=2))

    mech_counts = {pid: len(v) for pid, v in index.items()}
    total_mechs = sum(mech_counts.values())
    print(f"Indexed {len(index)} plays, {total_mechs} mechanism entries "
          f"(avg {total_mechs/len(index):.1f}/play)")
    print(f"Written: {args.out}")

    # Spot-check a few
    for pid in ["mask_anonymity_passage", "environmental_narrative_space",
                "the_witness", "knowledge_frontier_seed", "false_breakthrough"]:
        mechs = index.get(pid, ["[not found]"])
        print(f"  {pid}: {mechs}")


if __name__ == "__main__":
    main()
