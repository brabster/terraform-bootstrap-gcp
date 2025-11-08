# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
