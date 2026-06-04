# Brief: promote pipelex's "validate + dry-run all libraries" into a public API

**Status:** not started. This is a *brief*, not a plan — the follow-up session should write its own plan from a cold start.

**Audience:** a fresh session that knows nothing about how we got here. Read this top to bottom first.

## TL;DR

pipelex 0.31 (the release that just reworked the dry-run system) exposes **no public function** for "load all pipeline libraries and dry-run every pipe." The only implementation lives in a private module, `pipelex/cli/commands/validate/_validate_core.py` (`do_validate_all_libraries_and_dry_run`), tangled together with CLI concerns (telemetry tagging, `typer.echo`, `typer.Exit` error handlers).

Because there was no public surface, **cocode had to reimplement the orchestration by hand** from lower-level public primitives. That reimplementation is the thing we now want to delete. We will instead add a proper public API on the **pipelex** side and have cocode consume it.

The dry-run release is being finalized right now, so this is the moment to get the public contract right — ship it *with* the breaking change, not as a later follow-up.

## How we got here

A prior session bumped cocode's `pipelex` dependency to a much newer version (0.31.0, git rev `fa15d15c...`) and fixed `make check` + `make test`. See memory `cocode-pipelex-config-sync.md` for the full set of breakages (moved modules, `Path`-not-`str` utils, deck/config drift vs the live gateway, the `preliminary_text`-in-sequence regression).

One of those fixes is the seed for this brief. cocode's `cocode/validation_cli.py` originally imported `do_validate_all_libraries_and_dry_run` straight out of the private `_validate_core` module. We removed that private import and replaced it with hand-rolled helpers built from public primitives:

- `cocode/validation_cli.py` → `load_all_pipeline_libraries()` and `dry_run_all_pipes()`
- `tests/conftest.py` reuses both.

Those helpers re-derive pipelex's own canonical setup sequence: `get_library_manager().open_library()` → `set_current_library()` → `resolve_library_dirs()` → `load_libraries()`, then `BundleValidator().validate_pipes(pipes=[p for p in get_pipes() if not p.is_signature], library_id=get_current_library())`. That is plumbing that belongs in pipelex, not in every downstream consumer.

## Why this is worth doing (the agreed reasoning)

- **Private-module coupling has no semver signal.** A `_`-prefixed module is outside the package contract; it breaks on patch bumps with no warning. cocode's own test harness reaching into it is the codebase admitting the public API is incomplete.
- **Two implementations of one orchestration drift.** When pipelex changes the dry-run internals again (signature pre-pass, new model-type sweeps, library resolution), cocode's copy silently diverges → "valid in cocode, rejected by `pipelex validate`." Bad for a tool whose job includes validating pipelines.
- **Layering.** The current "core" prints, tags telemetry, and raises `typer.Exit`. Those are CLI concerns. The public function should **return structured data** (e.g. the `dict[str, DryRunOutput]` / a typed report) and raise typed exceptions; the CLI becomes a thin formatter on top.
- **The open/set/load ceremony is itself a missing abstraction.** Note that `Pipelex.make(library_dirs=...)` does **not** set the current library — you must then open/set/load by hand. That surprising, undocumented ordering contract should be encapsulated (a flag on `make()` or a single `load_libraries_and_activate(dirs)`), not memorized by every caller.
- **`is_signature` filtering shouldn't be a consumer's problem.** cocode having to know signatures exist just to skip them is leaked encapsulation.
- **Timing.** Don't ship the breaking dry-run change without its replacement migration path. Every consumer (cocode, conftest, sandbox, pipelex-api, CI gates) will otherwise write the same workaround and calcify it.

## Secure it with specs + conformance (explicitly wanted)

The workspace has a spec/conformance pair for exactly this kind of cross-repo contract: prose specs at `docs/specs/` (workspace root) and the executable pytest suite at `../conformance/`, linked bidirectionally (`> Verified by:` ⇄ `pytestmark = pytest.mark.spec(...)`, gated by `conformance/scripts/check-spec-links.py`). The new public "validate + dry-run all libraries" surface should be spec'd there and conformance-tested, so cocode and other consumers can depend on it and drift is gated rather than discovered. Treat the spec entry + conformance test as part of "done," not optional.

## Repos / mechanics

- Work happens primarily in **`../pipelex`** (workspace sibling, the source of the `pipelex` PyPI package; currently v0.31.0, dry-run release being finalized).
- Co-dev loop: point cocode at an **editable `../pipelex`** locally so you can add the API and consume it in one edit-test cycle without publishing. **Do not commit the editable path dependency** — the committed `cocode/pyproject.toml` + `uv.lock` must pin a released version / git rev. Flip cocode's pin to the new pipelex rev only once the API exists, then delete the cocode helpers.
- Definition of done spans three repos: pipelex (new public API + CLI shell refactor), docs/specs + conformance (contract), cocode (consume + delete `load_all_pipeline_libraries`/`dry_run_all_pipes`, keep `make check` and `make test` green — note `make test` hits the live Pipelex Gateway; `make gha-tests` uses `--disable-inference`).

## Anchors for the follow-up session

- cocode consumer to simplify: `cocode/validation_cli.py`, `tests/conftest.py`.
- pipelex private impl to promote/split: `pipelex/cli/commands/validate/_validate_core.py` (`do_validate_all_libraries_and_dry_run`, `execute_validate`).
- pipelex public primitives already in play: `pipelex/pipeline/bundle_validator.py` (`BundleValidator.validate_pipes` → `dict[str, DryRunOutput]`), `pipelex/hub.py` (`get_library_manager`, `set_current_library`, `resolve_library_dirs`, `get_pipes`, `get_current_library`).
- Related memory: `cocode-pipelex-config-sync.md`.

## What the follow-up session should produce

Its own plan, covering at least: the shape of the public API (likely `pipelex/validation.py` returning a structured report, plus possibly a one-call library-load-and-activate helper), the CLI shell refactor that keeps telemetry/typer behavior, the spec + conformance entries, and the cocode cleanup + repin. Get the API shape reviewed before writing a lot of code.
