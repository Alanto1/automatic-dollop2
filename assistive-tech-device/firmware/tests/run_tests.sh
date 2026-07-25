#!/usr/bin/env bash
# Builds and runs the HapticMapper desktop unit tests with a bare g++ - no
# Arduino toolchain, no external test framework, no network access needed.
# Exits non-zero if any test fails (or if the build fails), so this is
# CI/hook-friendly as well as fine to run by hand.
set -euo pipefail

cd "$(dirname "$0")"

g++ -std=c++17 -Wall -Wextra -O2 -o test_haptic_mapper test_haptic_mapper.cpp

./test_haptic_mapper
