#!/bin/env bash

apt-get update

# Install Python, venv and pip - we'll set an env var to prevent installations to system for a better error message
apt-get install -y python3 python3-venv

# Create a global alias for 'python' to 'python3'
ln -s /usr/bin/python3 /usr/bin/python

# pip not installed, so no need to warn about accidental system installs
#echo "PIP_REQUIRE_VIRTUALENV=true" >> /etc/environment
