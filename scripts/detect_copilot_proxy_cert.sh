#!/bin/env bash

# Documentation for this script:
#
# This script detects if running in a GitHub Copilot coding agent environment
# and locates the intercepting proxy certificate if present.
#
# Usage:
#   ./detect_copilot_proxy_cert.sh
#
# Output:
#   Prints the path to the proxy certificate file if found, or empty string if not found.
#
# Exit codes:
#   0 - Success (whether certificate is found or not)
#
# Detection logic:
#   1. Checks for COPILOT_API_URL environment variable (indicates Copilot environment)
#   2. Searches /usr/local/share/ca-certificates/ for mkcert development CA certificates
#   3. Returns the first matching certificate path

set -euo pipefail

# Check if we're in a Copilot environment
if [[ -z "${COPILOT_API_URL:-}" ]]; then
    # Not in Copilot environment
    exit 0
fi

# Look for the mkcert proxy certificate
CERT_PATH=$(find /usr/local/share/ca-certificates/ -name "mkcert_development_CA_*.crt" -type f 2>/dev/null | head -n 1 || true)

if [[ -n "${CERT_PATH}" && -f "${CERT_PATH}" ]]; then
    echo "${CERT_PATH}"
fi
