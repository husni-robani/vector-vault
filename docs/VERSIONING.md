# Versioning & Release Strategy

## Application Versioning

Vector Vault follows **Semantic Versioning** (SemVer): `MAJOR.MINOR.PATCH`

| Segment | Rules for this project |
|---|---|
| **MAJOR** | Breaking data migrations, breaking API contract changes, major architectural shifts (e.g., Tauri desktop release) |
| **MINOR** | New phases completed, new features (new use cases, frontend views, adapters) |
| **PATCH** | Bug fixes, documentation, dependency updates, internal refactoring |

**Pre-MVP convention:** `0.MINOR.PATCH` — e.g., `0.1.0` = Phase 0 complete.

The version is stored in a single `VERSION` file at the project root. Both backend and frontend must read from this file.

## Branch Model

Vector Vault uses a simplified release-branch model (inspired by Git Flow, without `develop`):

| Branch | Created from | Merged into | Lifespan | Purpose |
|---|---|---|---|---|
| `main` | — | — | Permanent | Always releasable. Tags are created here. |
| `release/<version>` | `main` | `main` | One milestone | Integration branch for a release cycle |
| `feat/<name>` | `release/<version>` | `release/<version>` | Days | New features |
| `fix/<name>` | `release/<version>` | `release/<version>` | Days | Bug fixes |
| `docs/<name>` | `release/<version>` | `release/<version>` | Days | Documentation |
| `chore/<name>` | `release/<version>` | `release/<version>` | Days | Tooling, CI, config changes |

```
main  ────●────────●────────●────────●──────────→
           \        \        \        \
            \        \        \        \
     release/0.1.0  release/0.2.0  release/0.3.0  release/1.0.0
           |          |          |          |
           ├─ feat    ├─ feat    ├─ feat    ├─ feat
           ├─ feat    ├─ fix     ├─ fix     ├─ fix
           └─ chore   └─ chore   └─ docs    └─ chore
```

## Tags & Releases

Each release is tagged on `main` after the release branch is merged:

```sh
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

Tags follow the pattern `v<semver>` (e.g., `v0.1.0`, `v1.0.0`, `v2.1.0`).

GitHub Releases are created from tags. The release notes should mirror the relevant section of `CHANGELOG.md`.

## Version Bump Workflow

```
1. Create a release branch
   git checkout main
   git checkout -b release/0.1.0

2. Work on features & fixes
   git checkout -b feat/domain-entities  # from release/0.1.0
   git checkout -b feat/use-cases        # from release/0.1.0
   # merge back into release/0.1.0

3. When the release is ready:
   a. Bump version in VERSION file
   b. Update CHANGELOG.md (move [Unreleased] → new version section)
   c. Commit: "chore: bump version to v0.1.0"
   d. Merge into main:
      git checkout main
      git merge release/0.1.0
      git tag -a v0.1.0 -m "Release v0.1.0"
      git push --tags origin main
   e. Delete release branch:
      git branch -d release/0.1.0
```

## Changelog

`CHANGELOG.md` follows the [Keep a Changelog](https://keepachangelog.com/) format. An `[Unreleased]` section at the top collects changes as you develop. When releasing, rename `[Unreleased]` to the new version.

## Version Source of Truth

- A single `VERSION` file at the project root contains the version number.
- The backend reads `VERSION` at startup via `config.py` and exposes it through the `/api/health` endpoint.
- The frontend retrieves the version from the health endpoint (no duplicate version in `package.json`).
- `pyproject.toml` does not contain a version field — Vector Vault is not a published Python package.
