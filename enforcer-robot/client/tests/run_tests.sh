#!/usr/bin/env bash
# Sesame client tests, entirely against FakeTransport. No robot, no WiFi,
# no serial port, no pyserial. Bare python3.
set -euo pipefail
cd "$(dirname "$0")"
python3 test_sesame.py
