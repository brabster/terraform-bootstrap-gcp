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

# Verifies that Python is not in a venv (sys.prefix == sys.base_prefix).
# This ensures users won't encounter venv detection confusion.
# Exits with a clear error message if check fails.
check_python_not_in_venv() {
  echo "--- Checking Python is not in a venv ---"
  
  local is_in_venv
  is_in_venv=$(python -c 'import sys; print(sys.prefix != sys.base_prefix)')
  
  if [[ "${is_in_venv}" == "True" ]]; then
    echo "Error: Python reports it is in a venv (sys.prefix != sys.base_prefix)" >&2
    echo "  sys.prefix: $(python -c 'import sys; print(sys.prefix)')" >&2
    echo "  sys.base_prefix: $(python -c 'import sys; print(sys.base_prefix)')" >&2
    exit 1
  fi
  
  echo "Python is correctly using system installation (not in a venv)."
}

# Verifies that users can create local virtual environments.
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
  
  # Install a package in the venv
  if ! "${test_venv_dir}/test-venv/bin/pip" install --no-cache-dir wheel; then
    echo "Error: Failed to install package in local venv" >&2
    rm -rf "${test_venv_dir}"
    exit 1
  fi
  
  # Verify the package works
  if ! "${test_venv_dir}/test-venv/bin/python" -c "import wheel"; then
    echo "Error: Package installed in local venv but cannot be imported" >&2
    rm -rf "${test_venv_dir}"
    exit 1
  fi
  
  rm -rf "${test_venv_dir}"
  echo "Local venv creation and package installation works correctly."
}

# Verifies that the user script pattern from the issue works correctly.
# Simulates the script that was failing in the original issue.
# Exits with a clear error message if check fails.
check_user_script_pattern() {
  echo "--- Checking user script pattern from issue ---"
  
  local test_dir
  test_dir=$(mktemp -d)
  cd "${test_dir}"
  
  # Simulate the user's script logic
  local IS_RUNNING_IN_VENV
  IS_RUNNING_IN_VENV="$(python -c 'import sys; print(sys.prefix != sys.base_prefix)')"
  
  if [[ "${IS_RUNNING_IN_VENV}" == "False" ]]; then
    # Should create a new venv since we're not in one
    if ! python -m venv venv; then
      echo "Error: Failed to create venv in user script pattern" >&2
      cd - > /dev/null
      rm -rf "${test_dir}"
      exit 1
    fi
    
    # Install a test package
    if ! ./venv/bin/pip install --no-cache-dir requests; then
      echo "Error: Failed to install package in user script pattern" >&2
      cd - > /dev/null
      rm -rf "${test_dir}"
      exit 1
    fi
  else
    echo "Error: Script detected it's in a venv when it shouldn't be" >&2
    cd - > /dev/null
    rm -rf "${test_dir}"
    exit 1
  fi
  
  cd - > /dev/null
  rm -rf "${test_dir}"
  echo "User script pattern works correctly."
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

  check_python_not_in_venv

  check_local_venv_creation

  check_user_script_pattern

  echo
  echo "All pre-flight checks passed successfully."
}

# Execute the main function, passing all script arguments.
main "$@"