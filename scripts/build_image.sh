#!/bin/env bash

# Documentation for this script:
#
# This script builds the Docker image, automatically detecting and using
# the intercepting proxy certificate when running in a GitHub Copilot
# coding agent environment.
#
# Usage:
#   ./build_image.sh [docker build options]
#
# Examples:
#   ./build_image.sh -t candidate_image:latest .
#   ./build_image.sh -t myimage:tag --no-cache .
#
# The script will:
#   1. Detect if running in a Copilot environment with an intercepting proxy
#   2. Automatically include the proxy certificate in the build if found
#   3. Pass through all other arguments to docker build

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect proxy certificate
PROXY_CERT_PATH=$("${SCRIPT_DIR}/detect_copilot_proxy_cert.sh")

if [[ -n "${PROXY_CERT_PATH}" ]]; then
    echo "Detected GitHub Copilot environment with intercepting proxy"
    echo "Using proxy certificate: ${PROXY_CERT_PATH}"
    
    # Build with BuildKit and proxy certificate
    DOCKER_BUILDKIT=1 docker build \
        --secret id=proxy_cert,src="${PROXY_CERT_PATH}" \
        "$@"
else
    # Standard build without proxy certificate
    docker build "$@"
fi
