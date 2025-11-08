#!/bin/env bash

# Documentation for this script:
#
# This script builds the Docker image, automatically detecting and using
# the intercepting proxy certificate when running in a GitHub Copilot
# coding agent environment.
#
# Usage:
#   ./build_image.sh [PROXY_CERT_PATH] [docker build options]
#
# Arguments:
#   PROXY_CERT_PATH - Optional. Path to proxy certificate. If not provided,
#                     auto-detection will be attempted.
#
# Examples:
#   ./build_image.sh -t candidate_image:latest .
#   ./build_image.sh /path/to/cert.pem -t myimage:tag .
#
# The script will:
#   1. Use the provided proxy cert path if given as first argument
#   2. Otherwise, auto-detect if running in a Copilot environment
#   3. Build with BuildKit, adding --secret arg only when cert is available

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export DOCKER_BUILDKIT=1

# Check if first argument is a file (proxy cert path)
PROXY_CERT_PATH=""
if [[ $# -gt 0 && -f "$1" ]]; then
    PROXY_CERT_PATH="$1"
    shift
else
    # Auto-detect proxy certificate
    PROXY_CERT_PATH=$("${SCRIPT_DIR}/detect_copilot_proxy_cert.sh")
fi

# Build with optional proxy certificate
if [[ -n "${PROXY_CERT_PATH}" ]]; then
    echo "Using proxy certificate: ${PROXY_CERT_PATH}"
    docker build --secret id=proxy_cert,src="${PROXY_CERT_PATH}" "$@"
else
    docker build "$@"
fi
