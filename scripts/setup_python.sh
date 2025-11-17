#!/bin/env bash

apt-get update

# Install Python, venv and pip - we'll set an env var to prevent installations to system for a better error message
apt-get install -y python3 python3-venv python3-pip

# Upgrade pip, setuptools and wheel to latest versions and replace the outdated wheel files
# This ensures that new virtual environments created with 'python3 -m venv' use the latest versions
pip3 install --upgrade pip setuptools wheel
# Remove old wheel files and download latest versions
rm -f /usr/share/python-wheels/pip-*.whl
rm -f /usr/share/python-wheels/setuptools-*.whl
rm -f /usr/share/python-wheels/wheel-*.whl
pip3 download --dest /usr/share/python-wheels/ --no-deps pip setuptools wheel

# Remove pip to prevent accidental system-wide package installations
apt-get remove -y python3-pip
apt-get autoremove -y

# Create a global alias for 'python' to 'python3'
ln -s /usr/bin/python3 /usr/bin/python

# pip not installed, so no need to warn about accidental system installs
#echo "PIP_REQUIRE_VIRTUALENV=true" >> /etc/environment
