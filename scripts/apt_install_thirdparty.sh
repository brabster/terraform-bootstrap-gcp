#!/bin/env bash

# Documentation for this script:
#
# This script automates the installation of a software package via APT,
# including setting up its GPG key and APT source list.
#
# Usage:
#   ./apt_install_thirdparty <GPG_KEY_URL> <EXE_NAME> <APT_SOURCE> [EXPECTED_FINGERPRINT]
#
# Arguments:
#   <GPG_KEY_URL>  - The URL to the GPG public key for the software's repository.
#                    This key is used to verify the authenticity of the packages.
#                    Example: https://apt.releases.hashicorp.com/gpg
#
#   <EXE_NAME>     - The name of the executable or package to be installed.
#                    This will also be used to name the GPG keyring file
#                    and the APT source list file.
#                    Example: terraform
#
#   <APT_SOURCE>   - The APT repository source string. This specifies
#                    where apt should look for the packages.
#                    Example: https://apt.releases.hashicorp.com $(lsb_release -cs) main
#
#   [EXPECTED_FINGERPRINT] - Optional. The expected GPG key fingerprint to verify
#                            against. If provided, the script will fail if the
#                            downloaded key's fingerprint doesn't match.
#                            Example: 798AEC654E5C15428C8E42EEAA16FCBCA621E701
#
# Environment Variables:
#   SKIP_SSL_VERIFY - Set to "true" to skip SSL certificate verification.
#                     Defaults to "false". Used in environments with SSL interception.
#
# Example Usage:
#   ./apt_install_thirdparty \
#       "https://apt.releases.hashicorp.com/gpg" \
#       "terraform" \
#       "https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
#       "798AEC654E5C15428C8E42EEAA16FCBCA621E701"

# Based on eg. https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

set -euo pipefail

GPG_KEY_URL=$1
EXE_NAME=$2
KEYRING_PATH="/usr/share/keyrings/${EXE_NAME}.gpg"
APT_SOURCE=$3
EXPECTED_FINGERPRINT=${4:-}
SKIP_SSL_VERIFY=${SKIP_SSL_VERIFY:-false}

# Determine wget SSL options based on environment
WGET_SSL_OPTS=""
if [ "$SKIP_SSL_VERIFY" = "true" ]; then
  WGET_SSL_OPTS="--no-check-certificate"
fi

wget $WGET_SSL_OPTS -v -O- "${GPG_KEY_URL}" | gpg --dearmor -o "${KEYRING_PATH}"

## Print the fingerprint of the key
gpg --no-default-keyring --keyring "${KEYRING_PATH}" --fingerprint

## Verify fingerprint if expected fingerprint was provided
if [[ -n "${EXPECTED_FINGERPRINT}" ]]; then
  echo "Verifying GPG key fingerprint..."
  ACTUAL_FINGERPRINT=$(gpg --no-default-keyring --keyring "${KEYRING_PATH}" --fingerprint | grep -oP '[0-9A-F]{4}(\s+[0-9A-F]{4}){9}' | tr -d ' ')
  EXPECTED_FINGERPRINT_NORMALIZED=$(echo "${EXPECTED_FINGERPRINT}" | tr -d ' ')
  
  if [[ "${ACTUAL_FINGERPRINT}" != "${EXPECTED_FINGERPRINT_NORMALIZED}" ]]; then
    echo "ERROR: GPG key fingerprint mismatch!" >&2
    echo "Expected: ${EXPECTED_FINGERPRINT_NORMALIZED}" >&2
    echo "Actual:   ${ACTUAL_FINGERPRINT}" >&2
    exit 1
  fi
  echo "GPG key fingerprint verified successfully."
fi

## Set up the apt source list
echo "deb [signed-by=${KEYRING_PATH}] ${APT_SOURCE}" > /etc/apt/sources.list.d/${EXE_NAME}.list

## Configure apt to skip SSL verification for this source if needed (GPG verification still applies)
if [ "$SKIP_SSL_VERIFY" = "true" ]; then
  cat > /etc/apt/apt.conf.d/99${EXE_NAME}-no-check-cert <<EOF
Acquire::https::$(echo "${APT_SOURCE}" | awk '{print $1}' | sed 's|https://||' | cut -d'/' -f1)::Verify-Peer "false";
Acquire::https::$(echo "${APT_SOURCE}" | awk '{print $1}' | sed 's|https://||' | cut -d'/' -f1)::Verify-Host "false";
EOF
fi

apt-get update
apt-get install -y --no-install-recommends "${EXE_NAME}"

## clean up to reduce image size
rm -rf /var/lib/apt/lists/*