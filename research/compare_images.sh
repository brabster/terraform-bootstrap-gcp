#!/bin/env bash

set -euo pipefail

IMAGE=$1

# Sanitize the image name to create a valid filename.
SANITIZED_IMAGE_NAME=$(echo "$IMAGE" | tr /: -)
mkdir -p uncommitted
SCAN_OUTPUT_FILENAME="uncommitted/${SANITIZED_IMAGE_NAME}.sarif"
METADATA_FILENAME="uncommitted/${SANITIZED_IMAGE_NAME}.json"

# Docker operations
docker pull "$IMAGE"
SIZE=$(docker images --format "{{.Size}}" "$IMAGE")

# Scan the image
osv-scanner scan image --format sarif --output "$SCAN_OUTPUT_FILENAME" "$IMAGE" || true

docker rmi "$IMAGE"

# Create metadata file
jq -n --arg image_name "$IMAGE" --arg image_size "$SIZE" \
  '{image_name: $image_name, image_size: $image_size}' > "$METADATA_FILENAME"

# Output paths
echo "sarif_path=${SCAN_OUTPUT_FILENAME}" >> "$GITHUB_OUTPUT"
echo "metadata_path=${METADATA_FILENAME}" >> "$GITHUB_OUTPUT"
