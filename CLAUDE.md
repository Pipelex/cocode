# cocode — Coding Rules

cocode is an AI-powered codebase analysis CLI built on Pipelex (repo→text extraction, changelog generation, doc updates, doc/code drift proofreading).

## Commands

> Ensure the Python virtual environment is set up before running any of these. For standard installations the venv is `.venv` — activate it (or use the `.venv/bin/...` entry points) so `pipelex`, `pytest`, `ruff`, etc. resolve correctly.

### Linting

After making code changes, always lint with `make agent-check`.

```bash
make agent-check
# If `make` is unavailable, run the "agent-check" target's commands one by one
# (targets: fix-unused-imports format lint pyright mypy).
```

This fixes unused imports, formats and lints with Ruff, and type-checks with Pyright and Mypy. Fix any issues it reports before proceeding.

### Cleaning Derived Files

If the linters or pytest collection get confused after you erase or move files, clean the derived caches:

```bash
make cleanderived
```

### Running Tests

`make agent-test` runs the test suite and is **critical at the end of a coding session** to verify everything is good before wrapping up. It is silent on success and only prints output on failure.

```bash
make agent-test
# If `make` is unavailable, look up the "agent-test" target in the Makefile and run it manually.
```

During local development it's fine to run only the tests relevant to your changes — e.g. `make t TEST=TestClassName` or `.venv/bin/pytest -x -q tests/path/to/test_module.py`.
