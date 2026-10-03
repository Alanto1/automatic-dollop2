#!/usr/bin/env bash
# Geometry tests for scene.py. Bare python3 - no ultralytics, no OpenCV, no
# video file, no model download. Runs in well under a second and is the
# thing to re-run after touching any threshold in scene.py.
set -euo pipefail
cd "$(dirname "$0")"
python3 test_scene.py
