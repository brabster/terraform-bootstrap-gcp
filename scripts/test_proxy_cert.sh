#!/usr/bin/env bash

# Test script to verify that the proxy certificate is properly installed
# and HTTPS connections work during the build process.

set -euo pipefail

echo "Testing proxy certificate installation..."

# Test 1: Verify certificate is installed in system trust store
if [ -f /etc/ssl/certs/proxy-ca.pem ]; then
    echo "✓ Proxy certificate is installed at /etc/ssl/certs/proxy-ca.pem"
else
    echo "✗ Proxy certificate not found (this is OK if building without proxy support)"
    exit 0
fi

# Test 2: Test HTTPS connection to a known endpoint
echo "Testing HTTPS connection..."
if wget -q --spider https://www.google.com; then
    echo "✓ HTTPS connection successful"
else
    echo "✗ HTTPS connection failed"
    exit 1
fi

# Test 3: Test GPG key download (this was failing before)
echo "Testing GPG key download..."
if wget -q -O- "https://apt.releases.hashicorp.com/gpg" | gpg --dearmor > /dev/null 2>&1; then
    echo "✓ GPG key download successful"
else
    echo "✗ GPG key download failed"
    exit 1
fi

echo
echo "All proxy certificate tests passed!"
