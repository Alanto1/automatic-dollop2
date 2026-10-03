#!/usr/bin/env bash
# Runs the mood state machine's desktop unit tests with a bare python3 - no
# pytest, no virtualenv, no robot, no network access needed. Exits non-zero
# if any test fails, so this is CI/hook-friendly as well as fine to run by
# hand while the printer is still broken and no parts have arrived.
set -euo pipefail

cd "$(dirname "$0")"

python3 test_mood.py
