#!/usr/bin/env bash
set -euo pipefail

# Upgrade pip and setuptools using system Python
# pip 24.0 has CVE-2025-8869, fixed in 25.3+
# setuptools 68.1.2 has GHSA-5rjg-fvgr-3xxf, GHSA-cx63-2mw6-8hw5, PYSEC-2025-49
# Using --upgrade to always get the latest versions (staying up to date is lower risk than falling behind)
# Using --break-system-packages as this is an isolated container environment
# Using --ignore-installed to bypass debian RECORD file issue
python3 -m pip install --break-system-packages --ignore-installed --no-cache-dir --upgrade pip setuptools
