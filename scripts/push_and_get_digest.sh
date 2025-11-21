#!/bin/env bash

# Documentation for this script:
#
# This script pushes a Docker image to a registry and extracts the image digest
# from the push output. The digest uniquely identifies the image content and is
# required for build provenance attestation.
#
# Usage:
#   ./push_and_get_digest.sh <LOCAL_IMAGE> <REGISTRY_TAG> [<ADDITIONAL_TAG> ...]
#
# Arguments:
#   LOCAL_IMAGE   - The local Docker image name/tag to push (e.g., candidate_image:latest)
#   REGISTRY_TAG  - The first registry tag to push to (e.g., ghcr.io/owner/repo:sha123)
#   ADDITIONAL_TAG(S) - Optional additional tags to push (e.g., ghcr.io/owner/repo:latest)
#
# Output:
#   Prints the image digest to stdout in the format: sha256:...
#   This digest can be captured and used for attestation purposes.
#
# Examples:
#   # Push to single tag
#   ./push_and_get_digest.sh candidate_image:latest ghcr.io/myorg/myrepo:abc123
#
#   # Push to multiple tags
#   ./push_and_get_digest.sh candidate_image:latest \
#       ghcr.io/myorg/myrepo:abc123 \
#       ghcr.io/myorg/myrepo:latest
#
# Exit codes:
#   0 - Success, digest extracted and printed
#   1 - Error (invalid arguments, push failed, or digest extraction failed)

set -euo pipefail

# Validate arguments
if [[ $# -lt 2 ]]; then
    echo "Error: Insufficient arguments" >&2
    echo "Usage: $0 <LOCAL_IMAGE> <REGISTRY_TAG> [<ADDITIONAL_TAG> ...]" >&2
    exit 1
fi

LOCAL_IMAGE="$1"
shift
REGISTRY_TAGS=("$@")

# Verify local image exists
if ! docker image inspect "${LOCAL_IMAGE}" >/dev/null 2>&1; then
    echo "Error: Local image '${LOCAL_IMAGE}' not found" >&2
    exit 1
fi

# Tag and push the first registry tag, capturing the digest from push output
# docker push outputs the digest in the format "digest: sha256:... size: ..."
# We extract the digest directly from this output
FIRST_TAG="${REGISTRY_TAGS[0]}"
echo "Tagging ${LOCAL_IMAGE} as ${FIRST_TAG}" >&2
docker tag "${LOCAL_IMAGE}" "${FIRST_TAG}"

echo "Pushing ${FIRST_TAG}..." >&2
PUSH_OUTPUT=$(docker push "${FIRST_TAG}" 2>&1)

# Extract digest using grep with Perl regex
# Format: digest: sha256:[64 hex characters]
DIGEST=$(echo "$PUSH_OUTPUT" | grep -oP 'digest: \K(sha256:[a-f0-9]{64})' || true)

if [[ -z "${DIGEST}" ]]; then
    echo "Error: Failed to extract digest from push output" >&2
    echo "Push output was:" >&2
    echo "$PUSH_OUTPUT" >&2
    exit 1
fi

# Push additional tags if provided
# All tags reference the same image content, so share the same digest
if [[ ${#REGISTRY_TAGS[@]} -gt 1 ]]; then
    for tag in "${REGISTRY_TAGS[@]:1}"; do
        echo "Tagging ${LOCAL_IMAGE} as ${tag}" >&2
        docker tag "${LOCAL_IMAGE}" "${tag}"
        echo "Pushing ${tag}..." >&2
        docker push "${tag}" >&2
    done
fi

# Output the digest to stdout for capture by caller
echo "${DIGEST}"
