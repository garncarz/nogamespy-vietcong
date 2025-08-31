#!/usr/bin/env bash

# Detect Python version for the build path
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
BUILD_PATH="build/lib.linux-x86_64-${PYTHON_VERSION}"

PYTHONPATH=.:${BUILD_PATH} py.test --cov-report html --cov=nogamespy --cov-report term $@
echo "Coverage files created:"
ls -la .coverage* 2>/dev/null || echo "No .coverage files found"
