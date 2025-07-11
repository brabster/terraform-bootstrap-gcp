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

for metadata_file in ${PROJECT_DIR}/uncommitted/*.json; do
  IMAGE=$(jq -r '.image_name' "$metadata_file")
  SIZE=$(jq -r '.image_size' "$metadata_file")
  
  sarif_file="${metadata_file%.json}.sarif"

  FIXES_AVAILABLE=$(jq '[.runs[0].tool.driver.rules[] | select(.help.text | contains("listed fixed versions")) | .id]|sort|unique|length' "$sarif_file")
  UNIQUE_VULNERABILITIES=$(jq '[.runs[0].results[].ruleId]|unique|length' "$sarif_file")
  
  echo "| $IMAGE | $SIZE | $UNIQUE_VULNERABILITIES | $FIXES_AVAILABLE |" >> $REPORT_FILE
done
