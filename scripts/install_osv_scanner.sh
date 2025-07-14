#!/bin/env bash

set -euo pipefail

TMP_DIR=$(mktemp -d)
cd $TMP_DIR

VERSIONED_PATH=https://github.com/google/osv-scanner/releases/download/v2.0.3/

wget -q ${VERSIONED_PATH}/osv-scanner_linux_amd64
wget -q ${VERSIONED_PATH}/osv-scanner_SHA256SUMS
egrep 'osv-scanner_linux_amd64$' osv-scanner_SHA256SUMS | sha256sum --check

cp osv-scanner_linux_amd64 /usr/local/bin/osv-scanner
chmod +x /usr/local/bin/osv-scanner
rm -rf $TMP_DIR