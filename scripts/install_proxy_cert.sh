#!/bin/env bash

# Documentation for this script:
#
# This script installs a custom CA certificate into the system trust store.
# It is designed to support Docker builds in environments with intercepting
# proxies, such as GitHub Copilot.
#
# Usage:
#   ./install_proxy_cert.sh <CERT_PATH>
#
# Arguments:
#   <CERT_PATH>  - Path to the CA certificate file to install.
#                  If empty or the file does not exist, the script exits successfully
#                  without installing anything.
#
# Example Usage:
#   ./install_proxy_cert.sh /tmp/proxy-ca.pem
#
# The script installs the certificate into the system trust store at
# /usr/local/share/ca-certificates/ and updates the certificate trust database.

set -euo pipefail

CERT_PATH="${1:-}"

# If no certificate path is provided, exit successfully
if [[ -z "${CERT_PATH}" ]]; then
    echo "No proxy certificate path provided, skipping installation"
    exit 0
fi

# If the certificate file does not exist, exit with error
if [[ ! -f "${CERT_PATH}" ]]; then
    echo "Error: Certificate file not found at '${CERT_PATH}'" >&2
    echo "Please ensure the file exists or omit the certificate path to skip installation" >&2
    exit 1
fi

echo "Installing proxy certificate from ${CERT_PATH}"

# Install ca-certificates package if not already installed
apt-get update
apt-get install -y --no-install-recommends ca-certificates
rm -rf /var/lib/apt/lists/*

# Copy the certificate to the system trust store
# The certificate must have a .crt extension for update-ca-certificates to process it
cp "${CERT_PATH}" /usr/local/share/ca-certificates/proxy-ca.crt

# Update the certificate trust database
update-ca-certificates

echo "Proxy certificate installed successfully"
