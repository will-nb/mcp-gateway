#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

log_note() { printf "\e[38;5;12m[pre-commit]\e[0m %s\n" "$1"; }
log_err()  { printf "\e[38;5;196m[pre-commit]\e[0m %s\n" "$1" 1>&2; }

# 1) Formatting + Lint (best-effort)
if command -v ruff >/dev/null 2>&1; then
  log_note "Auto-formatting Python sources with ruff format (app, tests)"
  ruff format app tests || {
    log_err "ruff format failed. Please fix formatting manually."; exit 1;
  }
  # Stage any formatting changes so this commit includes them
  git add -A

  log_note "Running ruff lint (app, tests)"
  ruff check app tests || {
    log_err "Ruff lint errors found. Fix before commit."; exit 1;
  }
else
  log_note "ruff not found; skipping format/lint checks (install ruff to enable)."
fi

# 2) Quick unit tests (run whole tests if no unit split)
if [ -d tests/unit ]; then
  log_note "Running unit tests (pytest tests/unit -x)"
  pytest -q tests/unit -x
else
  log_note "Running tests (pytest tests -x)"
  pytest -q tests -x
fi
