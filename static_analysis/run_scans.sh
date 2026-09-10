#!/usr/bin/env bash
# Show why a naive home-grown checker is not enough, then run real tools.
# Usage: bash static_analysis/run_scans.sh
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

hr() { printf '\n%s\n' "════════════════════════════════════════════════════════════"; }

hr; echo " 1) NAIVE analyzer (substring matching) — fast but blind"; hr
echo "-- unsafe_case.py (uses '+': naive tool DOES flag it) --"
python static_analysis/static_analyzer.py static_analysis/unsafe_case.py
echo "-- safe_false_positive.py (constant, not user input: FALSE POSITIVE) --"
python static_analysis/static_analyzer.py static_analysis/safe_false_positive.py
echo "-- app/app.py (real SQLi is an f-string/%: naive tool MISSES it) --"
python static_analysis/static_analyzer.py app/app.py

hr; echo " 2) bandit — real SAST, catches what the naive tool misses"; hr
if command -v bandit >/dev/null 2>&1; then
  bandit -q -r app static_analysis || true
else
  echo "(install with: pip install bandit)"
fi

hr; echo " 3) semgrep — pattern SAST with security rules"; hr
if command -v semgrep >/dev/null 2>&1; then
  semgrep --quiet --error --config static_analysis/.semgrep.yml app || true
else
  echo "(install with: pip install semgrep)"
fi

hr; echo " 4) pip-audit — dependency / supply-chain scanning (SCA)"; hr
if command -v pip-audit >/dev/null 2>&1; then
  pip-audit -r requirements.txt || true
else
  echo "(install with: pip install pip-audit)"
fi

hr
echo "In a real project these run in CI. GitHub offers CodeQL code scanning,"
echo "Dependabot (dependency alerts) and secret scanning for free on public repos."
