## Project overview

This repository produces container images for data-centric development on Google Cloud Platform. The images include Terraform, Google Cloud SDK, and Python. They are designed for use in GitHub Codespaces and GitHub Actions.

The container images are used for data processing systems using Python, dbt and GCP. The README file and any other documentation must always reflect what the repository does and how it works. Changes to the README file can be proposed, but must be carefully considered to minimise impact to consumers.

## Project goals and principles

- Security, stability, sustainability and simplicity are priorities for this project
- Minimize dependencies and maintain a clear, auditable supply chain
- Default to rolling/latest versions for automatic security updates
- Fail loudly and securely rather than silently
- Write in Associated Press style with plain British English (avoid jargon, em-dashes, and smart quotes)
- Use sentence case for headings, labels, and badges
- Make minimal changes - don't reformat code unnecessarily
- Ensure README and documentation always reflect what the project actually does
- Where possible, ensure that a push to GitHub Actions is not required to exercise and test things and instead capabilities and features can be tested interactively first
- The number of dependencies must be minimised
- Trust for a dependency must be determined primarily based on the methods described at https://snyk.io/advisor
- Trusted maintainers and suppliers take responsibility for the transitive dependencies of their projects. Only direct dependencies need to be considered
- Each dependency must be annotated at point of inclusion with a comment declaring the maintaining party
- A list of all direct dependencies and maintaining parties must be called out in a README section

## Agent environment

The agent operates in GitHub Copilot environment, and is limited by strict firewall rules. If these rules might be causing a problem, stop, summarise the issue and wait for advice

## Build and test

The project uses Docker to build container images:

```bash
# Build the image
docker build -t candidate_image:latest .

# Test the image
cat scripts/validate_image.sh | docker run --rm -i candidate_image:latest bash

# Scan for vulnerabilities
scripts/install_osv_scanner.sh
scripts/run_osv_scanner.sh scan image candidate_image:latest
```

The CI/CD pipeline (`.github/workflows/docker-publish.yml`) automatically builds, tests, scans for vulnerabilities, and publishes images daily.

## Supply chain security

- All dependencies must automatically update to latest versions when the image is built
- Every dependency must be annotated with its maintaining party
- Only add software from explicitly trusted maintainers
- Python packages must have a Snyk Advisor package health score greater than 80 (check at https://snyk.io/advisor/python/packagename)
- NEVER ADD ANY SOFTWARE FROM A MAINTAINER THAT IS NOT EXPLICITLY TRUSTED
- Dependencies include: GitHub actions, Docker base images, operating system packages, installed libraries and applications, Python packages, and dbt packages

## Code style and contribution guidelines

- Commit messages should describe **why** the change was made, not what was changed
- Test interactively before pushing to GitHub Actions when possible
- Keep responses concise and to the point

### Bash scripting

- Write scripts that are reliable, maintainable, and secure
- Scripts should be idempotent, meaning they can be run multiple times with the same outcome
- Use `set -euo pipefail` to make scripts more robust (fail fast, treat unset variables as errors, fail on pipeline errors)
- Always start scripts with `#!/bin/env bash` to specify the interpreter
- Use comments to explain complex logic
- Break down code into functions to avoid repetition
- Use clear and descriptive variable names
- Never hardcode secrets - use environment variables or a secure vault
- Validate inputs to prevent command injection
- Use absolute paths for files and commands
- Use tools like `shellcheck` to identify potential issues
- Implement logging to help with debugging

### Dockerfile best practices

- Dockerfiles should be clear, concise, and easy to understand
- Images should be as small as possible while still containing all necessary dependencies
- Security is a primary concern; images should be secure by default
- Use official and trusted base images
- Default to a rolling tag like `latest` or `rolling` to ensure base images are continuously updated (trades stability for security)
- Employ multi-stage builds to separate build-time dependencies from runtime dependencies
- Minimize the number of layers by combining related commands
- Use a `.dockerignore` file to exclude unnecessary files
- Avoid running containers as the root user - create and switch to a non-root user
- Each new command should be on a new line with appropriate continuation characters (`\` and `&&`)
- Use `COPY` instead of `ADD` unless you need ADD's specific features
- Keep image dependencies to a minimum
- Never store secrets in Dockerfiles

## Code quality and refactoring

When implementing features:

- **Eliminate duplication**: Extract common values and logic to single locations
- **Simplify conditionals**: Prefer clear one-liners over multi-line if/else when logic is simple
- **Document technical decisions**: When using features in non-obvious ways, document:
  - Why this approach was chosen
  - What alternatives were considered and why they were rejected
  - Links to official documentation
  - Quotes from documentation when relevant
  - Acknowledgement when using features pragmatically rather than as intended
- **Remove unused code**: Clean up build args, variables, or code from earlier approaches
- **Think in parameters**: Identify when branches only differ by a parameter value

## Pull request reviews

The AI performing a pull request review is an expert in modern engineering practices with a specialism in security.

Code reviews must include:

- a review of what has changed for any security issues or improvements that could be made
- whether the `CHANGELOG.md` file includes the current PR. If it does not, the reviewer should propose an entry for the PR, following the layout and content of existing entries
- whether the `README.md` file reflects what the project actually does

The reviewer must strive to identify impactful changes, rather than cosmetic or stylistic changes.

## Changelog requirements

All changelog entries must include:

- A **Security** section that analyzes the security posture impact of the change
- The security analysis should include:
  - Direct security implications of the change (e.g., reduced attack surface, improved authentication)
  - **Supply Chain Posture Impact** or **Threat Model Impact** subsection explaining how the change affects security
  - **Security Posture Impact** conclusion (Positive, Neutral, or Negative)
- See existing entries in `CHANGELOG.md` for examples of the required format and level of detail

## Responding to review feedback

When addressing code review comments:

- **Ask for clarification** if the request is ambiguous before making changes
- **Explain constraints** when suggested approaches aren't feasible (e.g., Dockerfile syntax limitations)
- **Support claims with evidence**: Always back up claims with facts and documentation. Only claim something is "standard" or "recommended" if you can cite specific authoritative sources. Verify claims before making them.
- **Iterate on documentation**: Refine explanations based on reviewer questions
- **Test thoroughly** after each change to ensure functionality is preserved
- **Clean up comprehensively**: If feedback identifies one unused artifact, check for others from the same approach

