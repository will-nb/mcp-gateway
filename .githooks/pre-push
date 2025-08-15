#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

printf "\e[38;5;12m[pre-push]\e[0m Running extended checks...\n"

if command -v ruff >/dev/null 2>&1; then
  if ! ruff format --check app tests; then
    printf "\e[38;5;196m[pre-push]\e[0m Formatting issues. Run: ruff format app tests\n" 1>&2
    exit 1
  fi
  if ! ruff check app tests; then
    printf "\e[38;5;196m[pre-push]\e[0m Ruff errors. Fix before push.\n" 1>&2
    exit 1
  fi
else
  printf "\e[38;5;12m[pre-push]\e[0m ruff not found; skipping format/lint checks.\n"
fi

# Unit tests only
if [ -d tests/unit ]; then
  pytest -q tests/unit
else
  pytest -q tests
fi
