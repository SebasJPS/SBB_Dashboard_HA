# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [Unreleased]

## [0.3.1] - 2026-03-01

### Fixed
- Corrected `hacs.json` schema for HACS validation compatibility.
- Added required brand assets for HACS (`icon.png`, `logo.png`).
- Completed integration metadata for better HACS discovery.

## [0.3.0] - 2026-03-01

### Added
- HACS custom integration `sbb_dashboard_cards` with config flow and options flow.
- Automatic generation of dashboard and package YAML files from selected entities.
- Service `sbb_dashboard_cards.generate_files` to regenerate output files.
- Translation files for English and German.
- HACS metadata (`hacs.json`) and public installation docs.

### Changed
- Repository structure updated from static mockup toward installable integration workflow.
- README rewritten for HACS-first setup.
