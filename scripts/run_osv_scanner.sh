#!/bin/env bash
#
# Wraps the osv-scanner command to handle exit codes.
#
# Exit code 0: successful scan, no vulnerabilities found.
# Exit code 1: successful scan, vulnerabilities were found.
# Other non-zero status codes indicate an error occurred.
# See: https://google.github.io/osv-scanner/output/#return-codes
#
# This script exits with 0 if the osv-scanner exit code is 0 or 1,
# and exits with 1 otherwise.

set -e

osv-scanner "$@"
exit_code=$?

echo "osv-scanner exited with code: $exit_code"

if [ $exit_code -eq 0 ] || [ $exit_code -eq 1 ]; then
  exit 0
else
  exit 1
fi
