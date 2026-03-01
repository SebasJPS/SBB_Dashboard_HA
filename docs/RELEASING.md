# Releasing

## Versioning Rules

- Use Semantic Versioning: `MAJOR.MINOR.PATCH`.
- Keep `VERSION` and `custom_components/sbb_dashboard_cards/manifest.json` in sync.
- Add release notes in `CHANGELOG.md`.

## Release Steps

1. Update version in:
- `VERSION`
- `custom_components/sbb_dashboard_cards/manifest.json`

2. Add a new entry in `CHANGELOG.md` with date and changes.

3. Run local validation:

```bash
python3 scripts/ci/validate_repo.py
```

4. Commit and push to `main`.

5. Create and push a tag matching `VERSION`:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

6. GitHub Actions workflow `Release` will:
- Validate repository
- Verify tag/version match
- Build `dist/sbb_dashboard_cards.zip`
- Publish release asset to GitHub release

## Notes

- HACS users typically install from the repository directly.
- The release zip is useful for manual installation or pinned release workflows.
