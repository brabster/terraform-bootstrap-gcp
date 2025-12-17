#!/usr/bin/env bash

apt-get update

# Install Python, venv and pip
apt-get install -y python3 python3-venv python3-pip

# Create a global alias for 'python' to 'python3'
ln -s /usr/bin/python3 /usr/bin/python

# Upgrade pip and setuptools to latest versions to mitigate vulnerabilities
# pip 24.0 has CVE-2025-8869, fixed in 25.3+
# setuptools 68.1.2 has GHSA-5rjg-fvgr-3xxf, GHSA-cx63-2mw6-8hw5, PYSEC-2025-49
# Using --break-system-packages is safe in a container where we control the entire environment
# Using --ignore-installed to avoid issues with uninstalling Debian-packaged versions
# Using --upgrade to always get the latest versions (staying up to date is lower risk than falling behind)
python3 -m pip install --no-cache-dir --break-system-packages --ignore-installed --upgrade pip setuptools

# Remove old vulnerable versions to ensure clean security scans
# The upgraded versions in /usr/local take precedence, but removing old versions prevents false positives in scans
rm -rf /usr/lib/python3/dist-packages/pip \
       /usr/lib/python3/dist-packages/pip-[0-9]* \
       /usr/lib/python3/dist-packages/setuptools \
       /usr/lib/python3/dist-packages/setuptools-[0-9]* \
       /usr/share/python-wheels/pip-[0-9]*.whl \
       /usr/share/python-wheels/setuptools-[0-9]*.whl
