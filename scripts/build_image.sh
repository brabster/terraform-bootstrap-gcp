#!/bin/env bash

# Documentation for this script:
#
# This script builds the Docker image, automatically detecting and using
# intercepting proxy certificates if present.
#
# Usage:
#   ./build_image.sh [IMAGE_TAG]
#
# Arguments:
#   [IMAGE_TAG]  - Optional. The tag for the built image.
#                  Default: candidate_image:latest
#
# Example Usage:
#   ./build_image.sh
#   ./build_image.sh myimage:v1.0
#
# The script automatically detects if an intercepting proxy certificate
# (mkcert development CA) is installed and passes it to the Docker build
# if found. This is common in GitHub Copilot coding agent environments.

set -euo pipefail

IMAGE_TAG="${1:-candidate_image:latest}"

echo "=== Docker Image Build Script ==="
echo "Target image: ${IMAGE_TAG}"
echo ""

# Auto-detect mkcert certificate (common in Copilot environments)
PROXY_CERT=""
if [ -d "/usr/local/share/ca-certificates" ]; then
    PROXY_CERT=$(find /usr/local/share/ca-certificates -name "mkcert_development_CA_*.crt" -type f | head -1 || true)
fi

if [ -n "${PROXY_CERT}" ] && [ -f "${PROXY_CERT}" ]; then
    echo "Detected intercepting proxy certificate: ${PROXY_CERT}"
    echo "Building with proxy certificate support..."
    echo ""
    
    DOCKER_BUILDKIT=1 docker build \
        --secret id=proxy_cert,src="${PROXY_CERT}" \
        -t "${IMAGE_TAG}" \
        .
else
    echo "No intercepting proxy certificate detected."
    echo "Building without proxy certificate..."
    echo ""
    
    docker build -t "${IMAGE_TAG}" .
fi

echo ""
echo "=== Build Complete ==="
echo "Image built: ${IMAGE_TAG}"
