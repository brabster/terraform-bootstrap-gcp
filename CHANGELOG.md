# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [[#66](https://github.com/brabster/terraform-bootstrap-gcp/pull/66)] - Replace global venv with system pip to eliminate venv detection issues

### Added

- Added python3-pip package to runtime dependencies for Python package management
- Added comprehensive smoke tests in validate_image.sh to verify:
  - Python is not in a venv (sys.prefix == sys.base_prefix)
  - Users can create local venvs without issues
  - The user script pattern from the original issue works correctly

### Changed

- Replaced global venv approach with system pip upgraded using `--break-system-packages` flag
- Simplified Dockerfile by removing multi-stage build (no longer needed)
- Updated setup_python.sh to upgrade pip and setuptools directly on system Python

### Removed

- Removed builder stage from Dockerfile (no longer building venv)
- Removed venv creation and copying logic
- Removed PATH manipulation for venv
- Removed CLOUDSDK_PYTHON environment variable (uses system Python directly)

### Fixed

- Fixed venv detection confusion where Python reported `sys.prefix != sys.base_prefix` as True
- Fixed permission errors when users tried to install packages (original issue)
- Fixed compatibility issues with Python tools (poetry, tox, IDEs) that check venv status

### Rationale

The previous approach used a Python virtual environment at `/opt/python-venv` as the system Python installation. While this achieved the goal of having updated pip and setuptools versions, it created several issues:

1. **Venv detection confusion**: Python reported it was in a venv, causing user scripts that check `sys.prefix != sys.base_prefix` to skip creating local venvs and try to install globally, leading to permission errors
2. **Non-standard pattern**: Most Python containers use system pip or build from source, not a global venv
3. **Tool compatibility**: Python tools may behave unexpectedly when detecting a venv
4. **User expectations**: Sophisticated users expect system Python, not a venv

The new approach uses system pip with `--break-system-packages` flag to upgrade pip and setuptools directly. This:
- Eliminates venv detection confusion completely
- Follows standard container patterns
- Maintains the security goal of having current pip/setuptools versions
- Provides more predictable behavior for users
- Improves compatibility with Python tooling

### Security

- No change to security vulnerabilities or attack surface
- Maintains upgraded pip and setuptools versions (same security posture)
- Simpler architecture reduces complexity and potential for misconfiguration
- The `--break-system-packages` flag is intended for isolated environments like containers
- Still maintains separation from Ubuntu's package management

  - **Security Posture Impact:** Neutral to slightly positive. This change maintains the same security benefits (updated pip/setuptools) while reducing architectural complexity. The simplified single-stage build is easier to audit and maintain. The change does not introduce new attack vectors or vulnerable components.

## [[#62](https://github.com/brabster/terraform-bootstrap-gcp/pull/62)] - Test build process on PR instead of when merged

### Added

- Pull request builds now publish temporary Docker images with `pr-<number>` tags for testing before merge.
- Pull request trigger added to CI workflow with the same path filters as main branch pushes.
- Automated cleanup workflow deletes PR images when the pull request is closed or merged.
- Python scripts for workflow orchestration with argparse-based CLI interfaces (`push_image.py`, `cleanup_pr_image.py`).
- Shared utilities module (`github_actions_utils.py`) for common GitHub Actions functionality.
- Comprehensive unit test suite (30 tests) for workflow scripts, running before Docker build to fail fast.

### Changed

- CI workflow now runs on pull request events in addition to pushes to main and daily schedule.
- Publish job uses conditional logic to apply different tagging strategies based on the trigger event.
- README updated to document the new build triggers and PR-specific tagging strategy.

### Rationale

Maintainers need to verify that pull requests produce valid, tested artifacts before merging to avoid discovering issues after merge. The previous workflow only built and tested on push to main, meaning issues could only be caught after merge when they are more disruptive to fix.

This change allows maintainers to test PR builds in the same environment consumers will use, with the same build, scan, and validation steps. PR images are published with temporary `pr-<number>` tags that do not affect the production `latest` or SHA tags used by consumers, preventing confusion while enabling thorough pre-merge testing.

### Security

- No change to the container image contents or runtime security posture.
- PR images undergo the same vulnerability scanning and validation as main branch builds.
- PR images are published to the same container registry with temporary tags, allowing security verification before merge.

  - **Threat Model Impact:** This change does not affect the runtime threat model of the container images themselves. Both PR and main branch images are built from the same Dockerfile and undergo identical vulnerability scanning. The change affects the CI/CD pipeline by enabling earlier detection of security issues in pull requests before they reach the main branch. This follows the principle of shift-left security: identifying and fixing vulnerabilities as early as possible in the development lifecycle. PR images are clearly labeled with temporary tags (`pr-<number>`) that distinguish them from production tags (`latest` and SHA), preventing accidental use of test images in production environments.
## [[#63](https://github.com/brabster/terraform-bootstrap-gcp/pull/63)] - Add ca-certificates package for Terraform installation

### Added

- Added ca-certificates package (Canonical) to Dockerfile apt-get install command and documented it in inline comments.

### Rationale

The ca-certificates package is required for HTTPS certificate validation during the Terraform installation process. Without it, the apt_install_thirdparty.sh script fails when downloading GPG keys and configuring third-party apt repositories over HTTPS. This package provides the system-wide certificate trust store containing Mozilla's CA certificate bundle.

### Security

- Fixed build failures when installing Terraform due to missing HTTPS certificate validation capabilities.
- Added explicit dependency on Canonical's certificate trust store for HTTPS operations.

  - **Supply Chain Posture Impact:** Makes an implicit dependency explicit, improving transparency. The Terraform installation required HTTPS certificate validation but was failing without ca-certificates. By explicitly installing and documenting this package, we clarify our reliance on Canonical's Mozilla CA certificate bundle for trust decisions in all HTTPS operations during the build process. The package receives regular security updates through Ubuntu.
  - **Security Posture Impact:** Positive

## [[#61](https://github.com/brabster/terraform-bootstrap-gcp/pull/61)] - Refactor Dockerfile to multi-stage build to remediate OS-level vulnerabilities

### Changed

- Refactored Dockerfile to use multi-stage build pattern with separate `builder` and final stages.
- Modified `setup_python.sh` to create a Python virtual environment in `/opt/python-venv` instead of installing pip and setuptools system-wide.
- Python packages (pip, setuptools) are now installed in a virtual environment in the builder stage and copied to the final image.

### Removed

- Removed build-essential, binutils, python3-venv, and python3-pip from the final image by isolating them in the builder stage.
- Removed vulnerable media library dependencies (libpng1.6, libde265, libjpeg-turbo) that were previously pulled in as transitive dependencies of build tools.
- Removed python-pip package vulnerabilities by using virtual environment instead of system-wide installation.

### Rationale

The previous single-stage build included build tools (build-essential, binutils, patch) and their transitive dependencies (media libraries like libpng, libjpeg) in the final image. These were only needed to compile and install the latest pip and setuptools from PyPI but served no purpose at runtime. A multi-stage build isolates these dependencies in a temporary builder stage, then copies only the compiled artifacts (Python virtual environment) to the final image.

The builder stage installs:
1. **python3-venv**: Creates isolated Python environments
2. **build-essential**: Provides compilers and build tools needed for pip package compilation

The final stage receives only the Python virtual environment containing the upgraded pip and setuptools, without any build tools or their dependencies.

### Security

- Reduced known vulnerabilities from 42 to 26 (38% reduction).
- Reduced vulnerable packages from 22 to 17 (23% reduction).
- Removed 5 vulnerable packages: binutils (7 vulnerabilities), python-pip (5 vulnerabilities), libde265 (2 vulnerabilities), libpng1.6 (1 vulnerability), libjpeg-turbo (1 vulnerability).
- Removed 16 total vulnerabilities (4 High, 7 Medium, 5 Low).

  - **Supply Chain Posture Impact:** This change significantly reduces the image's attack surface by eliminating build tools and their transitive dependencies from the runtime environment. Build tools like binutils, gcc, and patch could be exploited by an attacker who gains access to the running container to compile malicious code or exploit vulnerabilities in these tools. Media libraries like libpng and libjpeg, pulled in as transitive dependencies, introduced additional vulnerabilities despite never being used. The multi-stage build ensures only runtime dependencies are present in the final image, following the principle of least privilege and defense in depth. The Python virtual environment approach also provides better isolation and version control for Python packages.
  - **Security Posture Impact:** Positive

## [[#57](https://github.com/brabster/terraform-bootstrap-gcp/pull/57)] - Remove build-time packages to reduce attack surface

### Removed

- Removed gnupg, lsb-release, and wget packages after they are used during image build. These packages are only needed for setting up third-party apt repositories (Terraform and Google Cloud CLI) and downloading the OSV scanner binary, but serve no purpose at runtime.
- Removed unminimize utility from the Ubuntu base image as it is not applicable to this production container's purpose.

### Changed

- Modified Dockerfile to purge build-time packages (gnupg, lsb-release, wget) and unnecessary utilities (unminimize) using `apt-get purge --auto-remove` in the same RUN layer where they are installed.

### Rationale

Build-time packages remain in the final image even though they are only needed during the build process. By removing these packages after use in the same RUN layer, we reduce the image's attack surface without affecting functionality. The packages removed are:

1. **gnupg**: Used for GPG key verification when adding third-party apt repositories. After repositories are configured and packages installed, GPG verification is no longer needed at runtime.
2. **lsb-release**: Used to determine the Ubuntu version codename for apt source configuration. Not needed after repositories are set up.
3. **wget**: Used to download GPG keys and the OSV scanner binary during build. Not needed after these files are downloaded.
4. **unminimize**: Ubuntu base image utility for restoring packages in minimal images. Not applicable to this container's use case.

Comprehensive analysis confirmed that all remaining packages are essential for runtime operations and cannot be removed without breaking documented functionality. Analysis documented in `research/remaining-vulnerabilities-analysis.md` and `research/package-optimization-summary.md`.

### Security

- Reduced known vulnerabilities from 33 to 31 (6% reduction).
- Reduced vulnerable packages from 19 to 18 (5% reduction).
- Reduced image size from 954MB to 950MB (4MB reduction).
- Removed 4 packages that could be exploited at runtime despite only being needed during build.
- All 31 remaining vulnerabilities have been analyzed and confirmed that zero additional packages can be removed without breaking essential functionality.

  - **Threat Model Impact:** This change reduces the container's attack surface by removing packages that are not needed at runtime. Build-time tools like gnupg, wget, and lsb-release could be exploited by an attacker who gains access to the running container, even though these tools serve no legitimate purpose after the image is built. By removing them, we eliminate potential attack vectors while maintaining all documented functionality. The removal follows the principle of least privilege: only include what is necessary for runtime operations. Each removed package had associated vulnerabilities that are now eliminated from the runtime environment.
  - **Security Posture Impact:** Positive

## [[#55](https://github.com/brabster/terraform-bootstrap-gcp/pull/55)] - Fix Python package vulnerabilities

### Changed

- Upgraded pip and setuptools to latest versions to fix vulnerabilities. Versions are automatically upgraded on each image build to stay current with security patches.
- Fixed pip 24.0 vulnerability CVE-2025-8869 (GHSA-4xh5-x5gv-qwph).
- Fixed setuptools 68.1.2 vulnerabilities GHSA-5rjg-fvgr-3xxf, GHSA-cx63-2mw6-8hw5, and PYSEC-2025-49.
- Modified `scripts/setup_python.sh` to install python3-pip, upgrade pip and setuptools to latest versions using pip with --break-system-packages flag, and remove old vulnerable package files.
- Added pip and setuptools to README dependencies table.

### Fixed

- Fixed CVE-2025-8869 in pip 24.0: pip's fallback tar extraction doesn't check symbolic links point to extraction directory (Medium severity: 5.9).
- Fixed GHSA-5rjg-fvgr-3xxf in setuptools 68.1.2: Path traversal vulnerability in PackageIndex.download leading to arbitrary file write.
- Fixed GHSA-cx63-2mw6-8hw5 in setuptools 68.1.2: Command injection via package URL.
- Fixed PYSEC-2025-49 in setuptools 68.1.2.

### Rationale

This change addresses all Python package vulnerabilities that can be safely fixed without changing the base image or risking instability. The remaining vulnerabilities (Go stdlib in Google Cloud SDK and Ubuntu system packages) cannot be fixed because:

1. Go stdlib 1.25.3 vulnerabilities are in Google Cloud SDK's bundled gcloud-crc32c binary and require Google to update the Cloud SDK.
2. All Ubuntu package vulnerabilities show "No fix available" as they are already the latest versions available in Ubuntu 24.04 repositories.

The fix uses `--break-system-packages` flag which is safe in a container environment where we control the entire environment and don't need to worry about system package manager conflicts.

### Security

- Successfully mitigated 4 known vulnerabilities in Python packages (pip and setuptools).
- Removed old vulnerable package files to ensure security scanners don't detect false positives.
- Remaining vulnerabilities cannot be fixed without upstream updates or changing the base image.

  - **Supply Chain Posture Impact:** This change improves the security posture by ensuring that Python packages used in the container are up-to-date with the latest security fixes. The pip vulnerability (CVE-2025-8869) could allow path traversal when extracting packages, while the setuptools vulnerabilities could enable command injection and arbitrary file write. By upgrading these packages, we reduce the attack surface for supply chain attacks that might leverage vulnerable Python package management tools. The removal of old vulnerable files ensures that security scanners accurately reflect the actual security posture without false positives from unused legacy files.
  - **Security Posture Impact:** Positive

## [[#49](https://github.com/brabster/terraform-bootstrap-gcp/pull/49)] - Deduplicate vulnerability reports in GitHub Security tab

### Added

- New script `scripts/deduplicate_sarif.sh` to post-process osv-scanner SARIF output and remove duplicate vulnerability reports.
- SARIF validation to ensure proper structure before processing.
- Comprehensive error handling for missing files, invalid SARIF structure, and jq processing failures.

### Changed

- Modified the `docker-publish.yml` workflow to deduplicate SARIF results before uploading to GitHub Code Scanning.
- osv-scanner now outputs to `osv_scan_results_raw.sarif`, which is processed to create the deduplicated `osv_scan_results.sarif`.

### Fixed

- Fixed issue where duplicate vulnerabilities appeared in the GitHub Security tab even though osv-scanner includes partialFingerprints in its output.
- Reduced duplicate vulnerability reports by approximately 50% based on testing with ubuntu:latest image.

### Rationale

The osv-scanner tool includes partialFingerprints in its SARIF output to help identify duplicate findings, but GitHub's Security tab was still displaying duplicates. This occurs when osv-scanner reports the same vulnerability multiple times with identical ruleId and fingerprint values, typically when a vulnerability affects multiple package layers or paths. The deduplication script uses jq to remove these duplicates based on the combination of ruleId and partialFingerprints.primaryLocationLineHash, ensuring each unique vulnerability is reported only once while preserving all other SARIF structure and metadata.

### Security

- Improves the signal-to-noise ratio in security scanning by eliminating duplicate vulnerability reports.
- Makes security alerts more actionable by showing the actual number of unique vulnerabilities.
- Does not filter out any unique vulnerabilities - only removes exact duplicates with identical ruleId and fingerprint.
- Maintains all SARIF structure and metadata, ensuring no security information is lost during deduplication.

  - **Threat Model Impact:** This change improves the effectiveness of vulnerability management by providing an accurate count of unique security issues. Duplicate reports can lead to alert fatigue and make it harder to prioritize remediation efforts. By deduplicating results, security teams can focus on addressing each unique vulnerability without confusion from repeated alerts. The deduplication logic is conservative, only removing entries that have identical ruleId and fingerprint combinations, ensuring no distinct vulnerabilities are hidden.
  - **Security Posture Impact:** Positive

## [[#45](https://github.com/brabster/terraform-bootstrap-gcp/pull/45)] - Add attestation to published Docker images

### Added

- Build provenance attestations for all published Docker images using GitHub's `actions/attest-build-provenance` action.
- Documentation in README explaining attestation benefits and how consumers can verify image provenance.
- Instructions for verifying attestations using the GitHub CLI.

### Changed

- Updated the publish job in the docker-publish.yml workflow to include `id-token: write` and `attestations: write` permissions.
- Modified the image push step to capture the image digest for use in attestation.

### Rationale

Build provenance attestations provide cryptographic proof of an artifact's origin and build process. This enables consumers to verify that images were built by the official GitHub Actions workflow and have not been tampered with. The attestation includes metadata such as the commit SHA, workflow, and build environment, creating an auditable trail for supply chain security.

### Security

- Attestations enable consumers to verify image authenticity before use, reducing the risk of supply chain attacks.
- Signed attestations create an auditable trail linking published images to their source code and build process.
- The attestation signature is created using GitHub's OIDC token, which proves the workflow's identity without requiring long-lived credentials.
- Consumers can integrate attestation verification into their CI/CD pipelines to enforce supply chain security policies.

  - **Supply Chain Posture Impact:** This change significantly improves the supply chain security posture by providing cryptographic proof of provenance for all published artifacts. Attestations enable consumers to verify that images were built by the expected workflow, detect tampering, and establish trust in the build process. This addresses a critical gap in software supply chain security by making the build process transparent and verifiable. The attestations are signed using GitHub's Sigstore infrastructure, which follows industry best practices for artifact signing and verification.
  - **Security Posture Impact:** Positive

## [[#42](https://github.com/brabster/terraform-bootstrap-gcp/pull/42)] - Remove dbt-bigquery cache warming

### Removed

- Removed dbt-bigquery cache warming from the Docker build process.
- Deleted requirements.txt file used for pre-warming the pip cache.
- Removed dbt-bigquery from the dependencies table in README as it is no longer pre-installed.

### Changed

- Updated README to remove documentation about pre-warmed pip cache for dbt-bigquery.

### Rationale

The cache warming provided minimal benefit while adding complexity to the build process and image size. Users can install dbt-bigquery and other Python packages as needed for their specific use case.

### Security

- Removing pre-installed Python packages reduces the attack surface by eliminating dependencies that may not be needed by all users.
- Simplifies the supply chain by removing dbt-bigquery and its transitive dependencies from the image.

  - **Supply Chain Posture Impact:** This change improves the project's supply chain security posture by removing unnecessary dependencies from the base image. Users now explicitly install only the Python packages they need, reducing the number of packages that must be monitored for vulnerabilities. This aligns with the principle of minimal dependencies and reduces the image's attack surface.
  - **Security Posture Impact:** Positive

## [[#36](https://github.com/brabster/terraform-bootstrap-gcp/pull/36)] - Add git CLI completion support

### Added

- Git CLI completion now works in interactive bash shells via the bash-completion package.
- Added bash-completion package (maintained by Canonical) to enable tab completion for git commands.
- Made git an explicit dependency rather than relying on it as a transitive dependency of Terraform.
- Added validation check to verify git completion files are present in the image.

### Changed

- Updated dependencies table in README to include git and bash-completion.

### Fixed

- Fixed issue where git CLI completion was not working in the container. Fixes #8.

### Security

- Making git an explicit dependency improves supply chain transparency by documenting all direct dependencies rather than relying on transitive dependencies.

  - **Supply Chain Posture Impact:** This change improves the project's supply chain security posture by making git a documented, explicit dependency. Previously, git was only installed as a transitive dependency of Terraform, which could lead to unexpected behavior if Terraform's dependencies change. By explicitly declaring git and bash-completion as dependencies (both maintained by Canonical), we ensure that these packages are intentionally included, versioned consistently with the rolling update strategy, and clearly documented for security audits.
  - **Security Posture Impact:** Positive

## [[#32](https://github.com/brabster/terraform-bootstrap-gcp/pull/32)] - Fix build failures in Copilot environment with auto-detection of intercepting proxy

### Added

- New script `scripts/build_image.sh` to automatically handle Docker builds in Copilot environments with intercepting proxies.
- Auto-detection of Copilot environment using the `COPILOT_API_URL` environment variable, integrated directly into the build script.

### Changed

- Simplified error handling in `scripts/apt_install_thirdparty.sh` to show errors naturally without verbose explanations.
- Changed wget from quiet mode (`-q`) to normal mode to make proxy-related errors visible.
- Updated README with instructions for using the new build script and automatic Copilot environment detection.

### Fixed

- Fixed issue where GPG key downloads failed with "gpg: no valid OpenPGP data found" error in Copilot coding agent environment.
- Fixed confusing error messages that made it difficult to diagnose intercepting proxy issues.

### Security

- Automatic proxy certificate detection only activates when `COPILOT_API_URL` environment variable is present, minimizing risk of false positives.
- The proxy certificate is only used if explicitly found in the expected system location (`/usr/local/share/ca-certificates/`).
- No automatic trust of arbitrary certificates - only certificates already installed by the host system are used.

## [[#22](https://github.com/brabster/terraform-bootstrap-gcp/pull/22)] - Add support for intercepting proxy certificates in Docker builds

### Added

- Added support for building Docker images in environments with intercepting proxies, such as GitHub Copilot coding agent environments.
- New script `scripts/install_proxy_cert.sh` to install custom CA certificates into the system trust store during Docker build.
- Updated Dockerfile to accept an optional `proxy_cert` build secret for injecting proxy CA certificates.
- Updated README with instructions for building with intercepting proxy support.

### Changed

- Switched base image from `ubuntu:rolling` to `ubuntu:latest` to avoid compatibility issues with third-party package repositories that may not immediately support newly released Ubuntu versions. Fixes #12.

### Security

- The proxy certificate installation is strictly opt-in and requires manual configuration.
- Build fails with a clear error message if a certificate path is specified but the file does not exist.
- No automatic detection or configuration to prevent accidental trust of unintended certificates.
- When using an intercepting proxy, trust is placed in the proxy to perform TLS validation with source systems. In GitHub's hosted environments, this validation is performed by GitHub's infrastructure.

## [[#14](https://github.com/brabster/terraform-bootstrap-gcp/pull/14)] - Set Up Copilot Instructions

### Added

- Enhanced `.github/copilot-instructions.md` with comprehensive guidance for GitHub Copilot coding agent, including project overview, build and test instructions, supply chain security guidelines, code style conventions, and references to project documentation.

## [[#9](https://github.com/brabster/terraform-bootstrap-gcp/pull/9)] - Check OSV-Scanner Exit Code

### Security

- Improved the reliability of the vulnerability scanner by ensuring the build fails on scanner execution errors.

  - **Threat Model Impact:** This change mitigates the threat of undetected `osv-scanner` failures, which could lead to a false sense of security regarding image vulnerabilities. By failing the build on `osv-scanner` execution errors, we ensure that any issues with the scanning process are immediately visible and addressed, preventing the deployment of potentially unverified images.
  - **Security Posture Impact:** Positive
