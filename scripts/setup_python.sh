#!/usr/bin/env bash
set -euo pipefail

# Create Python virtual environment with latest pip and setuptools
# This isolates Python packages from the system installation
# pip 24.0 has CVE-2025-8869, fixed in 25.3+
# setuptools 68.1.2 has GHSA-5rjg-fvgr-3xxf, GHSA-cx63-2mw6-8hw5, PYSEC-2025-49
# Using --upgrade to always get the latest versions (staying up to date is lower risk than falling behind)
python3 -m venv /opt/python-venv
/opt/python-venv/bin/python -m pip install --no-cache-dir --upgrade pip setuptools
