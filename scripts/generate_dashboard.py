#!/usr/bin/env python3
"""Generate dashboard YAML from template + entity mapping."""

from __future__ import annotations

import argparse
import pathlib
import shutil
import sys

import yaml

TOKEN_BY_KEY = {
    "light_main": "__LIGHT_MAIN__",
    "camera_main": "__CAMERA_MAIN__",
    "light_hall": "__LIGHT_HALL__",
    "switch_pump": "__SWITCH_PUMP__",
    "lock_door": "__LOCK_DOOR__",
}


def load_mapping(path: pathlib.Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML map/object.")

    missing = [key for key in TOKEN_BY_KEY if key not in data]
    if missing:
        raise ValueError(
            f"Missing keys in {path}: {', '.join(missing)}"
        )

    mapping: dict[str, str] = {}
    for key in TOKEN_BY_KEY:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Key '{key}' in {path} must be a non-empty string.")
        mapping[key] = value.strip()
    return mapping


def generate(template_path: pathlib.Path, output_path: pathlib.Path, mapping: dict[str, str]) -> None:
    template_text = template_path.read_text(encoding="utf-8")
    rendered = template_text

    for key, token in TOKEN_BY_KEY.items():
        rendered = rendered.replace(token, mapping[key])

    unresolved = [token for token in TOKEN_BY_KEY.values() if token in rendered]
    if unresolved:
        raise ValueError(
            f"Template still contains unresolved token(s): {', '.join(unresolved)}"
        )

    # Validate final YAML before writing
    yaml.safe_load(rendered)
    output_path.write_text(rendered, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Home Assistant dashboard YAML.")
    parser.add_argument(
        "--entities",
        default="config/entities.yaml",
        help="Path to user entity mapping YAML (default: config/entities.yaml)",
    )
    parser.add_argument(
        "--example",
        default="config/entities.example.yaml",
        help="Path to example entity mapping YAML (default: config/entities.example.yaml)",
    )
    parser.add_argument(
        "--template",
        default="dashboard_template.yaml",
        help="Path to dashboard template YAML (default: dashboard_template.yaml)",
    )
    parser.add_argument(
        "--output",
        default="dashboard_mockup.yaml",
        help="Path to write generated dashboard YAML (default: dashboard_mockup.yaml)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize entities file from example if missing.",
    )
    args = parser.parse_args()

    entities_path = pathlib.Path(args.entities)
    example_path = pathlib.Path(args.example)
    template_path = pathlib.Path(args.template)
    output_path = pathlib.Path(args.output)

    if args.init and not entities_path.exists():
        if not example_path.exists():
            print(f"Error: example file not found: {example_path}", file=sys.stderr)
            return 1
        entities_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(example_path, entities_path)
        print(f"Created {entities_path} from {example_path}.")
        print("Fill in your entity IDs, then run this script again without --init.")
        return 0

    try:
        mapping = load_mapping(entities_path)
        generate(template_path, output_path, mapping)
    except FileNotFoundError as exc:
        print(f"Error: file not found: {exc}", file=sys.stderr)
        if exc.args and str(exc.args[0]).endswith("entities.yaml"):
            print(
                "Hint: run with --init to create config/entities.yaml from the example file.",
                file=sys.stderr,
            )
        return 1
    except (ValueError, yaml.YAMLError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Generated: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
