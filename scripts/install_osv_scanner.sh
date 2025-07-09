#!/bin/env bash

set -euo pipefail

TMP_DIR=$(mktemp -d)
cd $TMP_DIR

wget -q https://github.com/google/osv-scanner/releases/latest/download/osv-scanner_linux_amd64
wget -q https://github.com/google/osv-scanner/releases/latest/download/osv-scanner_SHA256SUMS
egrep 'osv-scanner_linux_amd64$' osv-scanner_SHA256SUMS | sha256sum --check

cp osv-scanner_linux_amd64 /usr/local/bin/osv-scanner
chmod +x /usr/local/bin/osv-scanner
rm -rf $TMP_DIR