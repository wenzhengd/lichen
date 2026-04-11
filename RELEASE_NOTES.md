# Draft Release Notes: v0.1.0

## Summary

`lichen-stim` is now the standalone PyPI distribution for the `lichen` import
package, extracted from the monorepo layout and ready for publication.

## Highlights

- Standalone packaging in `pyproject.toml` under the `lichen-stim` distribution name.
- Root-relative install, test, and build commands in `README.md`.
- Explicit inclusion of `README.md`, `LICENSE`, `CHANGELOG.md`, tests, and the validation notebook in source distributions.
- Notebook bootstrap updated to discover `src/lichen` from the repository root.
- CI workflow added for install, test, and build validation.

## Validation

- `python -m pip install -e .`
- `python -m unittest discover -s tests -t . -q`
- `python -m build`
- wheel install in an isolated environment
- sdist install in an isolated environment

## Release Tag

- Tag name: `v0.1.0`
- Create the tag after merging this PR to `main`.
