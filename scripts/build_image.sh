#!/usr/bin/env bash

# Documentation for this script:
#
# This script builds the Docker image with automatic detection of the Copilot
# coding agent environment and injection of the intercepting proxy certificate.
#
# Usage:
#   ./build_image.sh [DOCKER_BUILD_ARGS...]
#
# Arguments:
#   DOCKER_BUILD_ARGS - Optional additional arguments to pass to docker build
#
# Example Usage:
#   ./build_image.sh -t myimage:latest
#   ./build_image.sh --no-cache -t myimage:latest
#
# Environment Detection:
#   In the GitHub Copilot coding agent environment, this script automatically
#   detects the proxy certificate at NODE_EXTRA_CA_CERTS and passes it to
#   the Docker build using BuildKit secrets.
#
# The script will:
# 1. Check if running in Copilot environment (COPILOT_AGENT_ACTION is set)
# 2. If yes, verify the proxy certificate exists at NODE_EXTRA_CA_CERTS
# 3. Pass the certificate to Docker build using --secret flag
# 4. If not in Copilot or certificate not found, build without proxy support

set -euo pipefail

# Build arguments start empty
BUILD_ARGS=()

# Check if we're in the Copilot coding agent environment
if [[ -n "${COPILOT_AGENT_ACTION:-}" ]]; then
    echo "Detected GitHub Copilot coding agent environment"
    
    # Check if the proxy certificate environment variable is set
    if [[ -n "${NODE_EXTRA_CA_CERTS:-}" ]]; then
        echo "Found proxy certificate path: ${NODE_EXTRA_CA_CERTS}"
        
        # Verify the certificate file exists
        if [[ -f "${NODE_EXTRA_CA_CERTS}" ]]; then
            echo "Proxy certificate file exists, adding to build secrets"
            BUILD_ARGS+=(--secret "id=proxy_cert,src=${NODE_EXTRA_CA_CERTS}")
        else
            echo "Warning: Proxy certificate path is set but file does not exist at ${NODE_EXTRA_CA_CERTS}" >&2
            echo "Building without proxy certificate support" >&2
        fi
    else
        echo "No proxy certificate path found in NODE_EXTRA_CA_CERTS" >&2
        echo "Building without proxy certificate support" >&2
    fi
else
    echo "Not in Copilot coding agent environment, building without proxy certificate"
fi

# Set DOCKER_BUILDKIT to enable BuildKit features if not already set
export DOCKER_BUILDKIT=1

# Build the image, passing through any additional arguments
echo "Running: docker build ${BUILD_ARGS[@]} $@"
docker build "${BUILD_ARGS[@]}" "$@"
