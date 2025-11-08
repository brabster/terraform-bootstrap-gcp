#!/usr/bin/env bash
#
# Runs pre-flight checks to verify the environment has the required tools and
# user configuration before proceeding with a workflow.
#
# Exits with a non-zero status if any check fails.

set -euo pipefail

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

  echo "--- Checking git completion ---"
  # Verify bash-completion package is installed and git completion file exists
  if [[ ! -f /usr/share/bash-completion/bash_completion ]]; then
    echo "Error: bash-completion is not installed." >&2
    exit 1
  fi
  if [[ ! -f /usr/share/bash-completion/completions/git ]]; then
    echo "Error: git completion file not found." >&2
    exit 1
  fi
  # Source git completion to verify it can be loaded
  # shellcheck disable=SC1091
  source /usr/share/bash-completion/completions/git
  if complete -p git &>/dev/null; then
    echo "Git completion is available."
  else
    echo "Error: Git completion could not be loaded." >&2
    exit 1
  fi

  check_user_context

  echo
  echo "All pre-flight checks passed successfully."
}

# Execute the main function, passing all script arguments.
main "$@"