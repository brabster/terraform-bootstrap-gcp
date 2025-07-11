#!/bin/env bash

set -euo pipefail

IMAGE=$1

PROJECT_DIR=$(dirname "$0")/..
SCAN_OUTPUT_FILE="${PROJECT_DIR}/uncommitted/$(echo $IMAGE | tr /: -).sarif"

docker pull $IMAGE
osv-scanner scan image --format sarif --output "$SCAN_OUTPUT_FILE" "$IMAGE" || true
docker rmi $IMAGE
