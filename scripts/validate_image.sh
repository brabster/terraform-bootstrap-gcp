#!/usr/bin/env bash
#
# Runs pre-flight checks to verify the environment has the required tools and
# user configuration before proceeding with a workflow.
#
# Exits with a non-zero status if any check fails.

set -euo pipefail

# Verifies that git CLI completion is available.
# Exits with a clear error message if check fails.
check_git_completion() {
  echo "--- Checking git completion ---"
  
  if [[ ! -f /usr/share/bash-completion/completions/git ]]; then
    echo "Error: Git completion file not found at /usr/share/bash-completion/completions/git" >&2
    exit 1
  fi
  
  if [[ ! -f /usr/share/bash-completion/bash_completion ]]; then
    echo "Error: bash-completion not installed" >&2
    exit 1
  fi
  
  echo "Git completion is available."
}

# Verifies that the script is running as the expected user ('ubuntu') with
# the expected UID and GID ('1000').
# Exits with a clear error message if checks fail.
check_user_context() {
  echo "--- Checking user ---"
  local expected_user="ubuntu"
  local expected_uid="1000"
  local expected_gid="1000"

  local current_user
  current_user=$(whoami)
  if [[ "${current_user}" != "${expected_user}" ]]; then
    echo "Error: User is '${current_user}', but expected '${expected_user}'." >&2
    exit 1
  fi

  local current_uid
  current_uid=$(id -u)
  if [[ "${current_uid}" != "${expected_uid}" ]]; then
    echo "Error: UID is '${current_uid}', but expected '${expected_uid}'." >&2
    exit 1
  fi

  local current_gid
  current_gid=$(id -g)
  if [[ "${current_gid}" != "${expected_gid}" ]]; then
    echo "Error: GID is '${current_gid}', but expected '${expected_gid}'." >&2
    exit 1
  fi

  echo "User checks passed."
}

# Verifies that Python package installation works in the global venv.
# Tests installing a package to ensure permissions are correct.
# Exits with a clear error message if check fails.
check_python_package_installation() {
  echo "--- Checking Python package installation in global venv ---"
  
  # Try to install wheel (Python Packaging Authority) to test permissions
  # wheel is a core Python packaging tool from PyPA, the same trusted maintainer as pip
  if ! pip install --no-cache-dir wheel; then
    echo "Error: Failed to install Python package in global venv" >&2
    exit 1
  fi
  
  # Verify the package was installed
  if ! python -c "import wheel"; then
    echo "Error: Package installed but cannot be imported" >&2
    exit 1
  fi
  
  echo "Python package installation in global venv works correctly."
}

# Verifies that creating and using a local virtual environment works.
# Tests the common workflow of creating a venv and installing packages.
# Exits with a clear error message if check fails.
check_local_venv_creation() {
  echo "--- Checking local venv creation and package installation ---"
  
  local test_venv_dir
  test_venv_dir=$(mktemp -d)
  
  # Create a local venv
  if ! python -m venv "${test_venv_dir}/test-venv"; then
    echo "Error: Failed to create local venv" >&2
    rm -rf "${test_venv_dir}"
    exit 1
  fi
  
  # Activate and install a package
  if ! "${test_venv_dir}/test-venv/bin/pip" install --no-cache-dir requests; then
    echo "Error: Failed to install package in local venv" >&2
    rm -rf "${test_venv_dir}"
    exit 1
  fi
  
  # Verify the package works
  if ! "${test_venv_dir}/test-venv/bin/python" -c "import requests"; then
    echo "Error: Package installed in local venv but cannot be imported" >&2
    rm -rf "${test_venv_dir}"
    exit 1
  fi
  
  rm -rf "${test_venv_dir}"
  echo "Local venv creation and package installation works correctly."
}

# The main entry point for the script.
main() {
  echo "--- Checking Terraform ---"
  terraform --version

  echo "--- Checking gcloud ---"
  gcloud --version

  echo "--- Checking Python ---"
  python --version

  echo "--- Checking osv-scanner ---"
  osv-scanner --version

  check_git_completion

  check_user_context

  check_python_package_installation

  check_local_venv_creation

  echo
  echo "All pre-flight checks passed successfully."
}

# Execute the main function, passing all script arguments.
main "$@"