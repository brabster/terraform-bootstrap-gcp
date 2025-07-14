#!/bin/sh
# This script executes the auth.py script from within its dedicated virtual environment,
# passing along any command-line arguments.
/opt/auth-venv/bin/python /opt/auth-venv/bin/auth.py "$@"
