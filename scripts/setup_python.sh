#!/bin/env bash

apt-get update

# Install Python, venv and pip - we'll set an env var to prevent installations to system for a better error message
apt-get install -y python3 python3-venv

# Create a global alias for 'python' to 'python3' and set pip to only run in a venv
tee /etc/python_setup.sh <<EOF
alias python=python3
export PIP_REQUIRE_VIRTUALENV=true
EOF


