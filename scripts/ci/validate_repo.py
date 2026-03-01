#!/usr/bin/env python3
"""Repository validation checks for CI."""

from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOMAIN = "sbb_dashboard_cards"
MANIFEST_PATH = ROOT / "custom_components" / DOMAIN / "manifest.json"
HACS_PATH = ROOT / "hacs.json"
VERSION_PATH = ROOT / "VERSION"
SERVICES_PATH = ROOT / "custom_components" / DOMAIN / "services.yaml"
STRINGS_PATH = ROOT / "custom_components" / DOMAIN / "strings.json"
EN_TRANSLATION_PATH = ROOT / "custom_components" / DOMAIN / "translations" / "en.json"
DE_TRANSLATION_PATH = ROOT / "custom_components" / DOMAIN / "translations" / "de.json"
PY_FILES = [
    ROOT / "custom_components" / DOMAIN / "__init__.py",
    ROOT / "custom_components" / DOMAIN / "config_flow.py",
    ROOT / "custom_components" / DOMAIN / "const.py",
    ROOT / "custom_components" / DOMAIN / "generator.py",
    ROOT / "scripts" / "generate_dashboard.py",
]

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_versions(manifest: dict[str, Any], version_text: str) -> None:
    manifest_version = str(manifest.get("version", "")).strip()
    _assert(bool(SEMVER_RE.match(manifest_version)), "manifest.json version must be SemVer (x.y.z)")
    _assert(
        manifest_version == version_text,
        f"VERSION file ({version_text}) must match manifest version ({manifest_version})",
    )


def check_manifest(manifest: dict[str, Any]) -> None:
    _assert(manifest.get("domain") == DOMAIN, f"manifest domain must be '{DOMAIN}'")
    _assert(manifest.get("config_flow") is True, "manifest config_flow must be true")
    _assert(manifest.get("integration_type") == "helper", "manifest integration_type must be 'helper'")


def check_hacs(hacs_data: dict[str, Any]) -> None:
    _assert(
        str(hacs_data.get("name", "")).strip() == "SBB Dashboard Cards",
        "hacs.json name must be 'SBB Dashboard Cards'",
    )
    _assert("homeassistant" in hacs_data, "hacs.json must define minimum homeassistant version")


def check_json_validity() -> None:
    for path in (STRINGS_PATH, EN_TRANSLATION_PATH, DE_TRANSLATION_PATH):
        _load_json(path)


def check_yaml_validity() -> None:
    with SERVICES_PATH.open("r", encoding="utf-8") as handle:
        yaml.safe_load(handle)


def check_python_syntax() -> None:
    for path in PY_FILES:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")


def main() -> int:
    try:
        manifest = _load_json(MANIFEST_PATH)
        hacs_data = _load_json(HACS_PATH)
        version_text = VERSION_PATH.read_text(encoding="utf-8").strip()
        _assert(bool(SEMVER_RE.match(version_text)), "VERSION must be SemVer (x.y.z)")
        check_versions(manifest, version_text)
        check_manifest(manifest)
        check_hacs(hacs_data)
        check_json_validity()
        check_yaml_validity()
        check_python_syntax()
    except Exception as exc:  # noqa: BLE001
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    print("Validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
