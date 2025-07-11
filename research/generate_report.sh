#!/bin/env bash

set -euo pipefail

PROJECT_DIR=$(dirname "$0")/..
REPORT_FILE="${PROJECT_DIR}/uncommitted/vulnerabilities_comparison.md"

echo "# Vulnerability Comparison Report" > $REPORT_FILE
echo "" >> $REPORT_FILE
echo "This report compares the vulnerabilities of several container images." >> $REPORT_FILE
echo "" >> $REPORT_FILE
echo "| Image | Size | Unique vulnerabilities | Fixes available |" >> $REPORT_FILE
echo "|---|---|---|---|" >> $REPORT_FILE

for sarif_file in ${PROJECT_DIR}/uncommitted/*.sarif; do
  IMAGE=$(basename "$sarif_file" .sarif | tr - \n/)
  SIZE=$(jq -r '.runs[0].properties.image_size' "$sarif_file")
  FIXES_AVAILABLE=$(jq '[.runs[0].results[] | select(.fixes != null)] | length' "$sarif_file")
  UNIQUE_VULNERABILITIES=$(jq -r '.runs[0].results[].ruleId' "$sarif_file" | sort | uniq | wc -l | tr -d ' ')
  
  echo "| $IMAGE | $SIZE | $UNIQUE_VULNERABILITIES | $FIXES_AVAILABLE |" >> $REPORT_FILE
done
