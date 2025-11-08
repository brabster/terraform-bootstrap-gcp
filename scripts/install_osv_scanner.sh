#!/bin/env bash

set -euo pipefail

TMP_DIR=$(mktemp -d)
cd $TMP_DIR

RELEASE_URL=https://github.com/google/osv-scanner/releases/latest/download
SKIP_SSL_VERIFY=${SKIP_SSL_VERIFY:-false}

# Determine wget SSL options based on environment
WGET_SSL_OPTS=""
if [ "$SKIP_SSL_VERIFY" = "true" ]; then
  WGET_SSL_OPTS="--no-check-certificate"
fi

wget $WGET_SSL_OPTS -q ${RELEASE_URL}/osv-scanner_linux_amd64
wget $WGET_SSL_OPTS -q ${RELEASE_URL}/osv-scanner_SHA256SUMS
egrep 'osv-scanner_linux_amd64$' osv-scanner_SHA256SUMS | sha256sum --check

cp osv-scanner_linux_amd64 /usr/local/bin/osv-scanner
chmod +x /usr/local/bin/osv-scanner
rm -rf $TMP_DIR
