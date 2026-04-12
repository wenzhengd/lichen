# Contributing

`lichen-q` is a standalone Python package with import name `lichen`.

## Setup

From the repository root:

```bash
python -m pip install -e .[dev]
```

## Tests

Run the test suite before sending changes:

```bash
python -m pytest -q
```

## Build

Verify the package builds cleanly:

```bash
python -m build
```

## Release notes

- Keep `CHANGELOG.md` updated for release-worthy changes.
- Keep `RELEASE_NOTES.md` in sync when preparing a new GitHub release.

## Style

- Prefer small, focused changes.
- Avoid reintroducing monorepo-specific paths or imports.
- Keep the import package name `lichen` unchanged.

## Pull Requests

- Add a short summary of the change.
- Mention any packaging or release impact.
- Include validation notes if you changed packaging, install behavior, or notebooks.
