#!/usr/bin/env python3
"""
validate_plays.py

Validates all plays in plays.yaml against plays_schema.json.
Reports errors and exits non-zero if any validation fails.

Usage:
    python validate_plays.py
    python validate_plays.py --yaml plays.yaml --schema plays_schema.json
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).parent
YAML_FILE = ROOT / "plays.yaml"
SCHEMA_FILE = ROOT / "plays_schema.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate plays.yaml against JSON Schema")
    parser.add_argument("--yaml", default=str(YAML_FILE), help="Path to plays.yaml")
    parser.add_argument("--schema", default=str(SCHEMA_FILE), help="Path to plays_schema.json")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only print errors")
    args = parser.parse_args()

    yaml_path = Path(args.yaml)
    schema_path = Path(args.schema)

    if not yaml_path.exists():
        print(f"ERROR: {yaml_path} not found", file=sys.stderr)
        return 1
    if not schema_path.exists():
        print(f"ERROR: {schema_path} not found", file=sys.stderr)
        return 1

    # Load schema
    schema = json.loads(schema_path.read_text())

    # Load plays
    with yaml_path.open(encoding="utf-8") as f:
        plays = list(yaml.safe_load_all(f))

    if not args.quiet:
        print(f"Validating {len(plays)} plays in {yaml_path.name}...")

    # Validate each play
    errors: list[tuple[str, str]] = []
    validator = jsonschema.Draft7Validator(schema)

    for play in plays:
        if not isinstance(play, dict):
            errors.append(("?", f"Non-dict document: {type(play)}"))
            continue
        pid = play.get("id", "<no id>")
        for error in validator.iter_errors(play):
            path = ".".join(str(p) for p in error.absolute_path) or "(root)"
            errors.append((pid, f"{path}: {error.message}"))

    # Check for duplicate IDs
    ids = [p.get("id") for p in plays if isinstance(p, dict)]
    seen: set[str] = set()
    for pid in ids:
        if pid in seen:
            errors.append((pid, "Duplicate ID"))
        seen.add(pid)

    # Report
    if errors:
        print(f"\n{'ERROR' if not args.quiet else ''}  {len(errors)} validation error(s):\n")
        for pid, msg in errors:
            print(f"  [{pid}] {msg}")
        return 1

    if not args.quiet:
        print(f"OK  All {len(plays)} plays valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
