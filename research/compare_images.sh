#!/bin/env bash

set -euo pipefail

IMAGE=$1

# Sanitize the image name to create a valid filename.
SANITIZED_IMAGE_NAME=$(echo "$IMAGE" | tr /: -)
mkdir -p uncommitted
SCAN_OUTPUT_FILENAME="uncommitted/${SANITIZED_IMAGE_NAME}.sarif"

# Docker operations
docker pull "$IMAGE"
SIZE=$(docker images --format "{{.Size}}" "$IMAGE")

# Scan the image
osv-scanner scan image --format sarif --output "$SCAN_OUTPUT_FILENAME" "$IMAGE" || true

docker rmi "$IMAGE"

# Inject the image size into the SARIF report for the generate-report job to use.
jq --arg image_size "$SIZE" '.runs[0].properties.image_size = $image_size' "$SCAN_OUTPUT_FILENAME" > tmp.sarif && mv tmp.sarif "$SCAN_OUTPUT_FILENAME"

# Output the path of the generated SARIF file for the workflow to use.
echo "sarif_path=${SCAN_OUTPUT_FILENAME}" >> "$GITHUB_OUTPUT"
