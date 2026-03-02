#!/usr/bin/env python3
"""
plays_to_yaml.py

Converts plays.md (source of truth) to plays.yaml.

Each play becomes a YAML document separated by ---
plays.yaml is then the source of truth; plays.md is generated from it.

Usage:
    python3 plays_to_yaml.py
    python3 plays_to_yaml.py --plays plays.md --out plays.yaml
"""

import re
import sys
import argparse
from pathlib import Path

PLAYS_FILE = Path(__file__).parent / "plays.md"
OUT_FILE = Path(__file__).parent / "plays.yaml"


# Fields that are lists (split on · or /)
LIST_FIELDS = {
    "MECHANISMS", "SYNERGIZES_WITH", "CONTRAINDICATED_AFTER",
    "REQUIRES", "CHANNEL", "LEGACY_SCOPE", "ARC_FIT",
}

# Map from MD field name (UPPERCASE) to YAML key (lowercase)
FIELD_MAP = {
    "MECHANISMS": "mechanisms",
    "ARC_FIT": "arc_fit",
    "BEAT_FUNCTION": "beat_function",
    "SOMATIC": "somatic",
    "IDENTITY_INVITE": "identity_invite",
    "REINFORCE": "reinforce",
    "PERMISSION": "permission",
    "EMOTIONAL_REGISTER": "emotional_register",
    "AGENCY_DEMAND": "agency_demand",
    "FEEDBACK_TYPE": "feedback_type",
    "AGENCY_TYPE": "agency_type",
    "FRAME_REQUIREMENT": "frame_requirement",
    "TROPE_RISK": "trope_risk",
    "DETECTION_WINDOW": "detection_window",
    "REVERSIBILITY": "reversibility",
    "CHANNEL": "channel",
    "DWELL_TIME": "dwell_time",
    "REQUIRES": "requires",
    "SYNERGIZES_WITH": "synergizes_with",
    "CONTRAINDICATED_AFTER": "contraindicated_after",
    "WITNESS_STRUCTURE": "witness_structure",
    "LANDSCAPE": "landscape",
    "LEGACY_SCOPE": "legacy_scope",
    "PARTICIPANT_NOTES": "participant_notes",
}

# These fields get block scalar (|) treatment in YAML output
BLOCK_SCALAR_FIELDS = {
    "somatic", "identity_invite", "reinforce", "permission",
    "emotional_register", "participant_notes", "desc",
}


def split_list_value(raw: str) -> list[str]:
    """Split a list field on · or , or ; separators, normalizing values."""
    if not raw or raw.lower().strip() in ("none", "—", "-", "", "n/a"):
        return []
    # Split on · , or ;
    parts = re.split(r"\s*[·,;]\s*", raw)
    result = []
    for part in parts:
        part = part.strip()
        # Strip trailing parenthetical notes like "(some forms)"
        part = re.sub(r"\s*\([^)]*\)\s*$", "", part).strip()
        # Strip leading/trailing punctuation
        part = part.strip(".,;:—-")
        if part and part.lower() not in ("none", "—", "-", "n/a"):
            result.append(part)
    return result


def split_arc_fit(raw: str) -> list[str]:
    """Split arc_fit which can use / or · as separators, and may have parenthetical notes."""
    if not raw or raw.lower().strip() in ("none", "—", "-", "", "n/a"):
        return ["any"]
    # Remove parenthetical qualifiers first
    clean = re.sub(r"\([^)]*\)", "", raw)
    # Split on · or ; or / (all used as arc_fit separators)
    parts = re.split(r"[·;,/]", clean)
    result = []
    for part in parts:
        part = part.strip().strip(".,;:—-").strip()
        if part and part.lower() not in ("none", "n/a"):
            result.append(part)
    return result if result else ["any"]


def split_channel(raw: str) -> list[str]:
    """Split channel which uses · or , or / as separators."""
    if not raw or raw.lower().strip() in ("none", "—", "-", ""):
        return []
    # Split on · , or /
    parts = re.split(r"\s*[·,/]\s*", raw)
    result = []
    for part in parts:
        part = part.strip().strip(".,;:—-").strip()
        if part and part.lower() not in ("none",):
            result.append(part)
    return result


def split_legacy_scope(raw: str) -> list[str]:
    """Split legacy_scope which uses · as separator."""
    if not raw or raw.lower().strip() in ("none", "—", "-", ""):
        return ["ephemeral"]
    parts = re.split(r"\s*[·,]\s*", raw)
    result = []
    for part in parts:
        part = part.strip()
        if part and part.lower() not in ("none",):
            result.append(part)
    return result if result else ["ephemeral"]


def parse_header_line(line: str) -> dict:
    """Parse the backtick header line: `id:x` · `COST:x` · ..."""
    rec = {}
    # Extract id
    m = re.search(r"`id:([^`]+)`", line)
    if m:
        rec["id"] = m.group(1).strip()

    # Extract COST, AUTONOMY, LEAD_TIME, INTENSITY
    for field in ["COST", "AUTONOMY", "LEAD_TIME", "INTENSITY"]:
        m = re.search(r"`" + field + r":([^`]+)`", line)
        if m:
            val = m.group(1).strip()
            # Strip parenthetical notes from cost (e.g. "(~$2/month)")
            val = re.sub(r"\s*\([^)]*\)\s*", " ", val).strip()
            rec[field.lower()] = val

    return rec


def extract_title(block: str, play_id: str) -> str:
    """Extract ### Title if present, else derive from id."""
    m = re.search(r"^###\s+(.+)$", block, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Derive from id: replace _ with space and title case
    return play_id.replace("_", " ").title()


def yaml_str(s: str, indent: int = 0) -> str:
    """Format a string for YAML, choosing style based on content."""
    if not s:
        return '""'
    # If it contains special chars or is multi-line, use block or quoted
    if "\n" in s or any(c in s for c in [':', '#', '*', '&', '!', '{', '}', '[', ']', '|', '>', "'", '"']):
        return None  # signal: needs block scalar
    if len(s) > 80:
        return None  # signal: use block scalar
    # Check if needs quoting
    needs_quote = (
        s.startswith(('-', '*', '?', ':', '#', '|', '>', "'", '"', '!', '&', '%', '@', '`')) or
        s.strip() != s or
        re.match(r'^\d', s) or
        s.lower() in ('yes', 'no', 'true', 'false', 'null', 'on', 'off') or
        ': ' in s
    )
    if needs_quote:
        # Use double quotes, escape internal double quotes
        escaped = s.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return s


def format_yaml_block_scalar(s: str, indent: int) -> str:
    """Format a multi-line string as YAML block scalar (|)."""
    ind = " " * indent
    lines = s.split("\n")
    result = "|\n"
    for line in lines:
        result += ind + line + "\n"
    return result.rstrip("\n")


def format_yaml_string(key: str, value: str, indent: int = 0) -> str:
    """Format a key: value string for YAML output."""
    ind = " " * indent
    if key in BLOCK_SCALAR_FIELDS or "\n" in value or len(value) > 120:
        block = format_yaml_block_scalar(value, indent + 2)
        return f"{ind}{key}: {block}"
    else:
        v = yaml_str(value)
        if v is None:
            # Fallback to block
            block = format_yaml_block_scalar(value, indent + 2)
            return f"{ind}{key}: {block}"
        return f"{ind}{key}: {v}"


def format_yaml_list(key: str, items: list, indent: int = 0) -> str:
    """Format a key: [list] for YAML output."""
    ind = " " * indent
    if not items:
        return f"{ind}{key}: []"
    # Use flow style for short lists of simple strings
    flow = "[" + ", ".join(repr(i) if ('"' in i or "'" in i or ':' in i) else i for i in items) + "]"
    if len(flow) <= 80:
        return f"{ind}{key}: {flow}"
    # Block style
    lines = [f"{ind}{key}:"]
    for item in items:
        v = yaml_str(item)
        if v is None:
            v = f'"{item}"'
        lines.append(f"{ind}  - {v}")
    return "\n".join(lines)


def play_to_yaml_doc(play: dict) -> str:
    """Convert a play dict to a YAML document string."""
    lines = []

    # Scalar required fields in canonical order
    def add_str(key):
        val = play.get(key, "")
        if val is None:
            val = ""
        lines.append(format_yaml_string(key, val))

    def add_list(key):
        val = play.get(key, [])
        if val is None:
            val = []
        lines.append(format_yaml_list(key, val))

    add_str("id")
    add_str("title")
    add_str("cost")
    add_str("autonomy")
    add_str("lead_time")
    add_str("intensity")
    add_list("mechanisms")
    add_list("arc_fit")
    add_str("beat_function")
    add_str("somatic")
    add_str("identity_invite")
    add_str("reinforce")
    add_str("permission")
    add_str("emotional_register")
    add_str("agency_demand")
    add_str("feedback_type")
    add_str("agency_type")
    add_str("frame_requirement")
    add_str("trope_risk")
    add_str("detection_window")
    add_str("reversibility")
    add_list("channel")
    add_str("dwell_time")
    add_list("requires")
    add_list("synergizes_with")
    add_list("contraindicated_after")
    add_str("witness_structure")
    add_str("landscape")
    add_list("legacy_scope")

    # Optional participant_notes
    if play.get("participant_notes"):
        add_str("participant_notes")

    # Section
    if play.get("section"):
        lines.append(format_yaml_string("section", play["section"]))

    # desc (block scalar always)
    desc = play.get("desc", "")
    if desc:
        block = format_yaml_block_scalar(desc, 2)
        lines.append(f"desc: {block}")
    else:
        lines.append("desc: \"\"")

    # failure_modes
    fm = play.get("failure_modes", [])
    if fm:
        lines.append("failure_modes:")
        for mode in fm:
            # Escape the mode text for YAML
            safe = mode.replace("\\", "\\\\")
            if '"' in safe:
                safe = safe.replace('"', '\\"')
            # Check if it needs quoting
            if any(c in safe for c in [':', '#', '*', '&', '!', '{', '}', '[', ']', '|', '>']):
                lines.append(f'  - "{safe}"')
            elif safe.startswith(('-', "'")):
                lines.append(f'  - "{safe}"')
            else:
                lines.append(f"  - {safe}")
    else:
        lines.append("failure_modes: []")

    return "\n".join(lines)


def parse_play_block(block: str, section: str) -> dict | None:
    """Parse a single play block from plays.md text."""
    # Find the header line (starts with `id:`)
    header_match = re.search(r"^`id:[^`]+`.*$", block, re.MULTILINE)
    if not header_match:
        return None

    header_line = header_match.group(0)
    rec = parse_header_line(header_line)

    if "id" not in rec:
        return None

    play_id = rec["id"]
    rec["title"] = extract_title(block, play_id)
    rec["section"] = section

    # Parse all **FIELD:** lines
    # These can span to end of line
    bold_field_pattern = re.compile(r"^\*\*([A-Z_]+):\*\*\s*(.*)$", re.MULTILINE)

    fields_found = {}
    for m in bold_field_pattern.finditer(block):
        fname = m.group(1)
        fval = m.group(2).strip()
        fields_found[fname] = fval

    # Map fields to YAML keys
    for md_field, yaml_key in FIELD_MAP.items():
        if md_field in fields_found:
            val = fields_found[md_field]
            if md_field in LIST_FIELDS:
                if md_field == "CHANNEL":
                    rec[yaml_key] = split_channel(val)
                elif md_field == "ARC_FIT":
                    rec[yaml_key] = split_arc_fit(val)
                elif md_field == "LEGACY_SCOPE":
                    rec[yaml_key] = split_legacy_scope(val)
                else:
                    rec[yaml_key] = split_list_value(val)
            else:
                rec[yaml_key] = val
        else:
            # Set defaults for list fields
            if md_field in LIST_FIELDS:
                if md_field == "LEGACY_SCOPE":
                    rec.setdefault(FIELD_MAP[md_field], ["ephemeral"])
                else:
                    rec.setdefault(FIELD_MAP[md_field], [])
            else:
                rec.setdefault(FIELD_MAP[md_field], "")

    # Normalize enum fields
    # cost: strip extra chars
    cost_raw = rec.get("cost", "").lower()
    cost_map = {
        "free": "free", "low": "low", "mid": "mid", "high": "high",
        "ongoing": "ongoing", "varies": "varies", "goodwill": "free",
    }
    for k, v in cost_map.items():
        if k in cost_raw:
            rec["cost"] = v
            break
    else:
        if cost_raw.startswith("~"):
            rec["cost"] = "low"
        elif "$" in cost_raw and "month" in cost_raw.lower():
            rec["cost"] = "ongoing"
        else:
            rec["cost"] = cost_raw or "free"

    # intensity: normalize
    intensity_raw = rec.get("intensity", "").lower().strip()
    intensity_map = {
        "low": "low", "medium": "medium", "high": "high",
        "extreme": "extreme", "varies": "varies",
    }
    rec["intensity"] = intensity_map.get(intensity_raw, intensity_raw or "medium")

    # agency_demand: normalize
    ad_raw = rec.get("agency_demand", "").lower().strip()
    # sometimes written as "passive (initial) · high (active)" — take first token
    ad_first = ad_raw.split("(")[0].split("·")[0].strip().split()[0] if ad_raw else ""
    ad_map = {"passive": "passive", "low": "low", "medium": "medium", "high": "high"}
    rec["agency_demand"] = ad_map.get(ad_first, "passive")

    # beat_function: normalize
    bf_raw = rec.get("beat_function", "").lower().strip()
    bf_map = {
        "spike": "spike", "ramp": "ramp", "hold": "hold",
        "rest": "rest", "transition": "transition", "liminal": "liminal",
    }
    # Handle compound beat functions like "spike · transition"
    bf_first = bf_raw.split("·")[0].strip().split()[0] if bf_raw else ""
    rec["beat_function"] = bf_map.get(bf_first, bf_map.get(bf_raw, "ramp"))

    # witness_structure: normalize
    ws_raw = rec.get("witness_structure", "").lower().strip()
    ws_valid = {"none", "self", "character", "outsider", "document"}
    if ws_raw not in ws_valid:
        # Try first token
        ws_first = ws_raw.split("·")[0].strip().split()[0] if ws_raw else "none"
        rec["witness_structure"] = ws_first if ws_first in ws_valid else "none"

    # landscape: normalize
    la_raw = rec.get("landscape", "").lower().strip()
    la_valid = {"action", "identity", "both"}
    if la_raw not in la_valid:
        la_first = la_raw.split("·")[0].strip() if la_raw else "action"
        rec["landscape"] = la_first if la_first in la_valid else "action"

    # Parse desc and failure_modes from the block text
    desc, failure_modes = parse_desc_and_failures(block, header_line)
    rec["desc"] = desc
    rec["failure_modes"] = failure_modes

    return rec


def parse_desc_and_failures(block: str, header_line: str) -> tuple[str, list[str]]:
    """
    Extract the description prose and failure modes from a play block.

    Logic:
    - Remove the ### Title line
    - Remove the backtick header line
    - Remove all **FIELD:** lines
    - Everything remaining is prose (desc) OR failure mode bullets
    - Lines starting with "- " after **FAILURE MODES:** heading are failure modes
    - Everything else (non-empty non-field) is desc prose
    """
    lines = block.split("\n")

    in_failure_modes = False
    desc_parts = []
    failure_modes = []

    for line in lines:
        stripped = line.strip()

        # Skip ### title lines
        if stripped.startswith("### "):
            continue

        # Skip the header line (backtick line)
        if stripped.startswith("`id:"):
            continue

        # Detect **FAILURE MODES:** header
        if re.match(r"^\*\*FAILURE MODES:\*\*", stripped):
            in_failure_modes = True
            # There might be content on the same line after the header
            rest = re.sub(r"^\*\*FAILURE MODES:\*\*\s*", "", stripped)
            if rest and rest.startswith("- "):
                failure_modes.append(rest[2:].strip())
            continue

        # Detect **FIELD:** lines — skip them
        if re.match(r"^\*\*[A-Z_]+:\*\*", stripped):
            # Reset failure mode context if we see another bold field after FAILURE MODES
            if in_failure_modes:
                in_failure_modes = False
            continue

        # In failure modes section: collect bullet items
        if in_failure_modes:
            if stripped.startswith("- "):
                failure_modes.append(stripped[2:].strip())
            elif stripped == "" or stripped == "---":
                continue
            else:
                # Non-bullet non-empty line after FAILURE MODES — could be continuation
                # or we've left the section
                # If it's not a bullet, treat as end of failure modes
                pass
            continue

        # Everything else is potential desc
        if stripped and stripped != "---":
            desc_parts.append(stripped)
        elif not stripped:
            # Empty line — add paragraph break if we have content
            if desc_parts and desc_parts[-1] != "":
                desc_parts.append("")

    # Clean up desc: remove leading/trailing empty lines
    # Join with \n (preserve paragraph breaks as double newline)
    desc_text = "\n".join(desc_parts).strip()
    # Normalize multiple blank lines to single blank line
    desc_text = re.sub(r"\n{3,}", "\n\n", desc_text)

    # Clean up failure modes
    clean_failures = [fm.strip() for fm in failure_modes if fm.strip()]

    return desc_text, clean_failures


def parse_plays_md(text: str) -> list[dict]:
    """Parse plays.md and return list of play dicts with section tracking."""

    # We need to track both section headers and play blocks.
    # Strategy: scan line by line, tracking current section.
    # When we see a `id:xxx` line, grab the surrounding block.

    # First, identify section boundaries
    section_map = {}  # line_number -> section_name
    lines = text.split("\n")

    current_section = "Quick Filter Index"  # first section default (first plays appear in QFI)
    for i, line in enumerate(lines):
        m = re.match(r"^## (.+)", line)
        if m:
            name = m.group(1).strip()
            section_map[i] = name
            # Skip non-play sections for current_section tracking
            if name not in ("How to Use This File (Agent Planning Notes)",
                            "Quick Filter Index", "Summary", "Planning Cheatsheet"):
                current_section = name

    # Now split into play blocks using the `id:` marker
    # Each play block starts at a `id:` line and ends at the next `id:` or end
    # But we need to handle the case where blocks are separated by ---
    # and have ### headers before them

    # Find all `id:` lines and their positions
    id_positions = []
    for i, line in enumerate(lines):
        if re.match(r"^`id:[^`]+`", line.strip()):
            id_positions.append(i)

    print(f"Found {len(id_positions)} play id lines")

    plays = []
    failed = []

    for idx, start_line in enumerate(id_positions):
        # Determine end of this play block
        if idx + 1 < len(id_positions):
            end_line = id_positions[idx + 1]
        else:
            end_line = len(lines)

        # Look back up to 5 lines for a ### title
        look_back = max(0, start_line - 10)
        block_start = look_back

        # Find the actual start: look for ### or --- before this play
        actual_start = start_line
        for j in range(start_line - 1, max(0, start_line - 15), -1):
            if lines[j].strip().startswith("### "):
                actual_start = j
                break
            elif lines[j].strip() == "---":
                actual_start = j + 1
                break

        # Get the block text
        block_lines = lines[actual_start:end_line]
        # Trim trailing --- and blank lines
        while block_lines and block_lines[-1].strip() in ("---", ""):
            block_lines.pop()

        block = "\n".join(block_lines)

        # Determine section: look backwards from start_line for most recent section
        section = current_section
        for j in range(start_line, -1, -1):
            if j in section_map:
                section = section_map[j].strip()
                break

        try:
            play = parse_play_block(block, section)
            if play:
                plays.append(play)
            else:
                failed.append(f"line {start_line}: no id found")
        except Exception as e:
            failed.append(f"line {start_line}: {e}")

    if failed:
        print(f"WARNING: {len(failed)} parse failures:")
        for f in failed[:20]:
            print(f"  {f}")

    return plays


def convert(plays_path: Path, out_path: Path) -> int:
    """Convert plays.md to plays.yaml. Returns number of plays converted."""
    print(f"Reading {plays_path}...")
    text = plays_path.read_text(encoding="utf-8")

    plays = parse_plays_md(text)
    print(f"Parsed {len(plays)} plays")

    # Write YAML output
    out_lines = [
        "# plays.yaml — Score arc design system plays library",
        "# AUTO-GENERATED from plays.md by plays_to_yaml.py",
        "# This is the source of truth. plays.md is generated from this file.",
        "# Each play is a YAML document separated by ---",
        "",
    ]

    for i, play in enumerate(plays):
        out_lines.append("---")
        out_lines.append(play_to_yaml_doc(play))
        out_lines.append("")

    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Written {len(plays)} plays to {out_path}")
    print(f"File size: {out_path.stat().st_size / 1024:.0f} KB")

    return len(plays)


def main():
    parser = argparse.ArgumentParser(description="Convert plays.md to plays.yaml")
    parser.add_argument("--plays", default=str(PLAYS_FILE))
    parser.add_argument("--out", default=str(OUT_FILE))
    args = parser.parse_args()

    n = convert(Path(args.plays), Path(args.out))
    if n < 350:
        print(f"WARNING: Expected 356 plays, got {n}")
        sys.exit(1)


if __name__ == "__main__":
    main()
