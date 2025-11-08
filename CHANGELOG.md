# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
