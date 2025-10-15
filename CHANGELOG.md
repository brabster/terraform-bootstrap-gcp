# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased] - Switch to Ubuntu LTS Base Image

### Changed

- Changed base image from `ubuntu:rolling` to `ubuntu:latest` to use the latest LTS release instead of the rolling release. This ensures compatibility with third-party software repositories, as new rolling releases may not be immediately supported by all package maintainers.

  - **Context:** The HashiCorp apt repository did not have a release file for Ubuntu "questing" (25.10), which is the current rolling release. This caused the Docker build to fail during apt-get update when attempting to install Terraform.
  - **Impact:** The image will now use Ubuntu's latest LTS release, which has broader support from third-party software vendors and is more stable for production use.

## [[#9](https://github.com/brabster/terraform-bootstrap-gcp/pull/9)] - Check OSV-Scanner Exit Code

### Security

- Improved the reliability of the vulnerability scanner by ensuring the build fails on scanner execution errors.

  - **Threat Model Impact:** This change mitigates the threat of undetected `osv-scanner` failures, which could lead to a false sense of security regarding image vulnerabilities. By failing the build on `osv-scanner` execution errors, we ensure that any issues with the scanning process are immediately visible and addressed, preventing the deployment of potentially unverified images.
  - **Security Posture Impact:** Positive
