---
name: release
description: >
  Automates the cocode release workflow: bumps the version in pyproject.toml,
  finalizes the CHANGELOG.md entry, runs quality checks, creates a
  release/vX.Y.Z branch, commits, pushes, and opens a PR to main. Use when user
  says "release", "cut a release", "bump version", "prepare a release", "make a
  release", "ship it", "create release branch", or any variation of shipping a
  new version of cocode. The user can optionally provide changelog content
  inline when invoking the skill (e.g. "/release Added new repo summary mode"),
  which will be used as the changelog entry for this version.
---

# Cocode Release Workflow

This skill handles the full release cycle for the `cocode` Python package.

Merging the release PR to `main` is what ships: `publish-pypi.yml` builds and
publishes to PyPI on every push to `main`, and `guard-branches.yml` only lets
`release/vX.Y.Z` branches merge into `main`. So the branch name, version, and
changelog have to line up exactly or the PR is blocked.

## Files touched

- **`pyproject.toml`** — the `version` field (line 3)
- **`CHANGELOG.md`** — add `[vX.Y.Z] - YYYY-MM-DD` entry (remove `[Unreleased]` if present)
- **`uv.lock`** — regenerated via `make li` (lock + install)

## Workflow

### 1. Pre-flight checks

- Read the current version from `pyproject.toml`.
- Read `CHANGELOG.md` to understand the current state.
- Run `git status` and `git log origin/main..HEAD` to assess the working tree:
  - If there are **uncommitted changes** (staged or unstaged), warn the user and
    ask whether to commit them as part of the release, stash them, or abort.
  - If there are **unpushed commits** on the current branch, list them so the
    user is aware — these will be included in the release branch.

### 2. Determine the bump type

Ask the user which kind of version bump they want — **patch**, **minor**, or
**major** — unless they already specified it. Show the current version and what
the new version would be for each option so the choice is concrete.

### 3. Run quality checks

Run `make check`. This runs ruff format, ruff lint, pyright, and mypy — the same
gate enforced by `lint-check.yml` in CI. It is the gate: if it fails, stop and
report the errors so they can be fixed before retrying. Do not proceed past this
step on failure.

Note that `make check` auto-formats with ruff, so it may modify files — include
any resulting changes in the release commit.

### 4. Ensure we're on the right branch

The release branch must be named `release/vX.Y.Z` where X.Y.Z is the **new**
version. `guard-branches.yml` rejects any other source branch merging to `main`,
so this name is not optional. All file modifications (changelog, version bump,
lock) must happen on this branch.

- If already on `release/vX.Y.Z` matching the new version, stay on it.
- If on `dev`, `main`, or any other branch, create and switch to
  `release/vX.Y.Z` from the current HEAD.
- If on a `release/` branch for a **different** version, warn the user and ask
  how to proceed.

### 5. Finalize the changelog

Add a new version entry at the top of the changelog for the release.

1. If there is an `## [Unreleased]` section, **remove it** (including any blank
   lines that follow it) and replace it with the new version heading. Any
   content that was under `[Unreleased]` becomes the content of the new version.
2. If there is no `[Unreleased]` section, insert the new version heading
   directly after the `# Changelog` title.
3. **Never add an `[Unreleased]` heading.** The changelog should only contain
   concrete version entries.
4. If the user provided changelog content when invoking the skill (e.g.
   `/release Added new repo summary mode`), **merge** that content with any
   existing `[Unreleased]` content (do not discard either source). Format the
   combined content properly under the appropriate headings (e.g. `### Added`,
   `### Changed`, `### Fixed`), inferring headings from the content when
   possible. Plain bullet lists with no heading are also fine and match recent
   cocode entries — match the style of the surrounding changelog.
5. If the release has no changelog content yet (neither from an `[Unreleased]`
   section nor from inline user input), ask the user what to include before
   proceeding.
6. The result should look like:

```markdown
# Changelog

## [vX.Y.Z] - YYYY-MM-DD

### Changed
- ...

## [vPREVIOUS] - PREVIOUS-DATE
...
```

The CI check (`changelog-check.yml`) greps for the exact line
`## [vX.Y.Z] -`, so the heading must use that bracketed `v`-prefixed format.

### 6. Bump the version in pyproject.toml

Edit `pyproject.toml` line 3 to the new version string. Only change the version
field — don't touch anything else.

### 7. Lock dependencies

Run `make li` to regenerate `uv.lock` and reinstall. This keeps the lockfile in
sync with the new version in `pyproject.toml`. If this step fails, stop and
report the error.

### 8. Commit and push

Stage all release-related changes. This includes at minimum `pyproject.toml`,
`CHANGELOG.md`, and `uv.lock`, plus any formatting changes from `make check` and
any other files the user chose to include in step 1 (e.g. previously
uncommitted work that belongs in this release).

Commit with the message:

```
Release vX.Y.Z
```

Push the branch to origin with `-u` to set up tracking.

### 9. Open a PR

Create a pull request targeting `main` with:

- **Title:** `Release/vX.Y.Z` (matches cocode's existing merged-PR convention)
- **Body:** Include:
  - The changelog entries for this version (copied from CHANGELOG.md)
  - A note about the version bump from old to new

Use this format for the PR body:

```markdown
## Release vX.Y.Z

Bumps version from `A.B.C` to `X.Y.Z`.

### Changelog

<paste the changelog entries for this version here>
```

Report the PR URL back to the user.

## Important details

- The version follows semver: `MAJOR.MINOR.PATCH`.
- Always confirm the bump type with the user before making changes.
- If `make check` fails, the release is blocked — help the user fix the issues
  rather than skipping the checks.
- Merging the PR to `main` triggers `publish-pypi.yml`, which publishes the
  package to PyPI. There is no separate tag/publish step — the merge is the
  release.
- The CI will validate, before the PR can merge:
  - `version-check.yml` — the `pyproject.toml` version matches the branch name
    and is greater than the version on `main`.
  - `changelog-check.yml` — `CHANGELOG.md` has a `## [vX.Y.Z] -` entry.
  - `guard-branches.yml` — only `release/vX.Y.Z` may merge into `main`.
  - `lint-check.yml` — ruff format, ruff lint, pyright, and mypy (the `make
    check` gate).
  - `tests-check.yml` — runs `make gha-tests`.
- All checks must pass for the PR to be mergeable, so getting the changelog,
  version, branch name, and lint clean is critical.
- Today's date for the changelog entry: use the current date in `YYYY-MM-DD`
  format (run `date +%F` if unsure).
