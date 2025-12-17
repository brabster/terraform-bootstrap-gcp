#!/bin/env bash
#
# Deduplicates SARIF results based on ruleId and partialFingerprints.primaryLocationLineHash.
# This resolves duplicate vulnerabilities in the GitHub Security tab that occur when
# osv-scanner reports the same vulnerability multiple times with identical fingerprints.
#
# Usage: deduplicate_sarif.sh <input_sarif> <output_sarif>
#
# Exit codes:
#   0 - Success
#   1 - Invalid arguments or file not found
#   2 - jq processing failed

set -euo pipefail

# Validate arguments
if [ $# -ne 2 ]; then
  echo "Usage: $0 <input_sarif> <output_sarif>" >&2
  exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: Input file '$INPUT_FILE' not found" >&2
  exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed" >&2
  exit 1
fi

echo "Deduplicating SARIF results from '$INPUT_FILE'"

# Count original results
ORIGINAL_COUNT=$(jq '.runs[0].results | length' "$INPUT_FILE")
echo "Original results count: $ORIGINAL_COUNT"

# Deduplicate results using unique_by on ruleId + partialFingerprints.primaryLocationLineHash
# This preserves all other SARIF structure and only removes duplicate vulnerability reports
jq '.runs[0].results |= unique_by(.ruleId + .partialFingerprints.primaryLocationLineHash)' \
  "$INPUT_FILE" > "$OUTPUT_FILE"

# Validate output was created
if [ ! -f "$OUTPUT_FILE" ]; then
  echo "Error: Failed to create output file '$OUTPUT_FILE'" >&2
  exit 2
fi

# Count deduplicated results
DEDUPLICATED_COUNT=$(jq '.runs[0].results | length' "$OUTPUT_FILE")
REMOVED_COUNT=$((ORIGINAL_COUNT - DEDUPLICATED_COUNT))

echo "Deduplicated results count: $DEDUPLICATED_COUNT"
echo "Removed $REMOVED_COUNT duplicate results"
echo "Successfully deduplicated SARIF results to '$OUTPUT_FILE'"
