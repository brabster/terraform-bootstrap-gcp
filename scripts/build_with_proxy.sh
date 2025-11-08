#!/usr/bin/env bash

# Documentation for this script:
#
# This script provides a convenient wrapper for building the Docker image
# with support for intercepting proxy certificates.
#
# Usage:
#   ./build_with_proxy.sh [CERT_PATH]
#
# Arguments:
#   [CERT_PATH]  - Optional path to the proxy CA certificate file.
#                  If not provided, builds without proxy certificate support.
#
# Examples:
#   # Build without proxy certificate
#   ./build_with_proxy.sh
#
#   # Build with GitHub Copilot proxy certificate
#   ./build_with_proxy.sh /home/runner/work/_temp/runtime-logs/mkcert/rootCA.pem
#
#   # Build with custom proxy certificate
#   ./build_with_proxy.sh /path/to/my-proxy-ca.pem

set -euo pipefail

readonly IMAGE_NAME="candidate_image:latest"
readonly CERT_PATH="${1:-}"

# Prepare build arguments
BUILD_ARGS=(-t "${IMAGE_NAME}")

if [[ -z "${CERT_PATH}" ]]; then
    echo "Building without proxy certificate support..."
else
    if [[ ! -f "${CERT_PATH}" ]]; then
        echo "Error: Certificate file not found at '${CERT_PATH}'" >&2
        echo "Please provide a valid certificate path or omit the argument to build without proxy support" >&2
        exit 1
    fi
    
    echo "Building with proxy certificate from '${CERT_PATH}'..."
    BUILD_ARGS+=(--secret "id=proxy_cert,src=${CERT_PATH}")
fi

# Build the image with common arguments and optional secret
DOCKER_BUILDKIT=1 docker build "${BUILD_ARGS[@]}" .

echo
echo "Build completed successfully!"
