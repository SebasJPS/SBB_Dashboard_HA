# SBB Dashboard Cards (HACS Integration)

Custom Home Assistant integration to generate a configurable dashboard and matching package for:

- Light card with brightness and temporary color mode (`double_tap` + timeout)
- Camera card with normal/fullscreen dashboard states
- Auto-fullscreen on event conditions (motion/doorbell/alarm)
- Optional test triggers for users without real event sensors

## HACS Installation (Recommended)

1. Add this repository in HACS as a **Custom repository** with type **Integration**.
2. Install **SBB Dashboard Cards** in HACS.
3. Restart Home Assistant.
4. Go to `Settings -> Devices & Services -> Add Integration`.
5. Add **SBB Dashboard Cards** and select your entities in the config flow.

On first setup, the integration generates:

- Dashboard file: `/config/sbb_dashboard_cards_dashboard.yaml`
- Package file: `/config/packages/sbb_dashboard_cards.yaml`

You can change both output paths in integration options.

## Home Assistant Setup

1. Ensure packages are enabled in `/config/configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

2. Restart Home Assistant after the package file is generated/updated.
3. Import the generated dashboard YAML:
- Create a YAML dashboard and point to `/config/sbb_dashboard_cards_dashboard.yaml`, or
- Copy the file content into Lovelace Raw Configuration Editor.

## Config Flow Inputs

Required entity selections:

- `light_main`
- `camera_main`
- `light_hall`
- `switch_pump`
- `lock_door`

Optional event entities:

- `event_motion`
- `event_doorbell`
- `event_alarm`

If event entities are not configured, keep `include_test_triggers = true` to use internal test helpers.

## Regenerate Files

The integration provides service:

- `sbb_dashboard_cards.generate_files`

Service fields:

- `entry_id` (optional): only generate for one config entry
- `overwrite` (default `true`): overwrite existing files or keep them

## Repository Structure

- `custom_components/sbb_dashboard_cards/`: HACS integration
- `dashboard_template.yaml`: legacy template asset
- `scripts/generate_dashboard.py`: legacy local generator (manual/non-HACS flow)

## Notes

- The integration is designed for public use: each user maps their own entities during setup.
- Existing files are not overwritten during initial setup (`overwrite=false` on first generation).
- Saving integration options regenerates files with overwrite enabled.

## Maintainer Release Workflow

- Version source: `VERSION` and `custom_components/sbb_dashboard_cards/manifest.json` must match.
- Changelog: update `CHANGELOG.md` for every release.
- CI validation runs on push/PR via `.github/workflows/validate.yml`.
- Tagged release workflow (`vX.Y.Z`) builds `dist/sbb_dashboard_cards.zip` and attaches it to GitHub release via `.github/workflows/release.yml`.
- Full release instructions: `docs/RELEASING.md`.
