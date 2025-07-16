---
prompt: |
  Write me a rules file about best practices in supply chain security, based on 00-rules-template.md and incorporating the conversation we just had about pinning vs. latest. Also consider the contents my blog post https://tempered.works/posts/2024/05/01/how-i-do-python-data-supply-chain-security/.
---

# Rules for Supply Chain Security

## Guiding Principles

- **Trust but Verify:** Every artifact, dependency, and process in the supply chain must be verified and have clear, verifiable origins.
- **Automation is Key:** Automate security processes to reduce human error, ensure consistency, and maintain a high security posture.
- **Clarity and Transparency:** The entire software development lifecycle, from source to production, should be clear, understandable, and auditable.
- **Fail Loudly and Securely:** Prioritize immediate and obvious failure over silent insecurity. It is better for a build to break than for a vulnerability to go unnoticed.

## Core Rules

- **Use a Software Bill of Materials (SBOM):** Every build must generate a comprehensive SBOM to provide a clear inventory of all components and dependencies.
- **Verify Artifact Integrity (SLSA):** All software artifacts must have verifiable integrity. Strive to meet SLSA Level 2, which requires a hosted build service and provenance generation to prevent tampering.
- **Default to Rolling Updates:** To ensure continuous security patching, all dependencies, including base Docker images, must default to a rolling tag like `latest` or `rolling`. This is a deliberate choice to trade stability for proactive security.
- **Scan Everything:** Automatically scan all code, dependencies, and artifacts for known vulnerabilities (CVEs) at multiple points in the CI/CD pipeline.
- **Implement Strong Access Controls:** Enforce the principle of least privilege. All access to source code repositories, build systems, and artifact registries must be secured with strong authentication.

## Best Practices

- **Know Your Suppliers:** Vet all third-party and open-source dependencies. Evaluate their security practices, maintenance history, and overall trustworthiness before integration.
- **Use a Secure, Hosted Build System:** All official builds must take place on a trusted, isolated, and ephemeral build platform to protect the build process from compromise.
- **Sign Your Artifacts:** Cryptographically sign all build artifacts to provide verifiable proof of their origin and integrity.
- **Manage Vulnerability Information (VEX):** Use a Vulnerability Exploitability eXchange (VEX) to clarify the actual impact of vulnerabilities discovered in your dependencies.

## Anti-Patterns

- **Blindly Trusting Dependencies:** Using third-party code without performing any security vetting or ongoing monitoring.
- **Manual Builds for Production:** Performing official builds on developer workstations, which are not secure or reproducible environments.
- **Ignoring Vulnerability Scans:** Treating vulnerability scan results as noise or failing to act on critical findings in a timely manner.
- **Pinning Dependencies Without an Update Strategy:** Pinning a dependency version without a robust, automated process to manage and review updates, leading to silent vulnerability accumulation.

## References

- [NIST Secure Software Development Framework (SSDF)](https://csrc.nist.gov/Projects/ssdf)
- [Supply-chain Levels for Software Artifacts (SLSA)](https://slsa.dev/)
- [CNCF Software Supply Chain Best Practices](https://www.cncf.io/reports/software-supply-chain-best-practices-white-paper/)

## TL;DR

- Automate your builds on trusted infrastructure, verify everything with signatures and SBOMs, and default to rolling dependency updates to stay secure.
