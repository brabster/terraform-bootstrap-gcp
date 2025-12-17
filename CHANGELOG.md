# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
