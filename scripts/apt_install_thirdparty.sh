#!/bin/env bash

# Documentation for this script:
#
# This script automates the installation of a software package via APT,
# including setting up its GPG key and APT source list.
#
# Usage:
#   ./apt_install_thirdparty <GPG_KEY_URL> <EXE_NAME> <APT_SOURCE>
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
# Example Usage:
#   ./apt_install_thirdparty \
#       "https://apt.releases.hashicorp.com/gpg" \
#       "terraform" \
#       "https://apt.releases.hashicorp.com $(lsb_release -cs) main"

# Based on eg. https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

set -euo pipefail

GPG_KEY_URL=$1
EXE_NAME=$2
KEYRING_PATH="/usr/share/keyrings/${EXE_NAME}.gpg"
APT_SOURCE=$3

wget -O- "${GPG_KEY_URL}" | gpg --dearmor -o "${KEYRING_PATH}"

## Print the fingerprint of the key
gpg --no-default-keyring --keyring "${KEYRING_PATH}" --fingerprint

## Set up the apt source list
echo "deb [signed-by=${KEYRING_PATH}] ${APT_SOURCE}" > /etc/apt/sources.list.d/${EXE_NAME}.list

apt-get update
apt-get install -y --no-install-recommends "${EXE_NAME}"

## clean up to reduce image size
rm -rf /var/lib/apt/lists/*