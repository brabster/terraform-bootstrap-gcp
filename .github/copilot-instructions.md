## Project overview

This repository produces container images for data-centric development on Google Cloud Platform. The images include Terraform, Google Cloud SDK, Python, and dbt-bigquery. They are designed for use in GitHub Codespaces and GitHub Actions.

**Always review `GEMINI.md` for complete project information, goals, and principles.**

## Project goals and principles

- Security, stability, sustainability and simplicity are priorities for this project
- Minimize dependencies and maintain a clear, auditable supply chain
- Default to rolling/latest versions for automatic security updates
- Fail loudly and securely rather than silently
- Write in Associated Press style with plain British English (avoid jargon, em-dashes, and smart quotes)
- Use sentence case for headings, labels, and badges
- Make minimal changes - don't reformat code unnecessarily
- Ensure README and documentation always reflect what the project actually does

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
- Python packages must have a Snyk Advisor package health score greater than 80
- Review the detailed rules in `prompts/rules/03-supply-chain-security.md`

## Code style and contribution guidelines

- Follow rules documented in `prompts/rules/` directory
- Bash scripts must follow practices in `prompts/rules/01-bash-scripting-rules.md`
- Dockerfile changes must follow `prompts/rules/02-dockerfile-best-practices.md`
- Commit messages should describe **why** the change was made, not what was changed
- Test interactively before pushing to GitHub Actions when possible

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

- review of `GEMINI.md` to understand the goals and style of the project
- a review of what has changed for any security issues or improvements that could be made
- whether the `CHANGELOG.md` file includes the current PR. If it does not, the reviewer should propose an entry for the PR, following the layout and content of existing entries
- whether the `README.md` file reflects what the project actually does

The reviewer must strive to identify impactful changes, rather than cosmetic or stylistic changes.

## Responding to review feedback

When addressing code review comments:

- **Ask for clarification** if the request is ambiguous before making changes
- **Explain constraints** when suggested approaches aren't feasible (e.g., Dockerfile syntax limitations)
- **Be precise with claims**: Only claim something is "standard" or "recommended" if you can cite specific documentation
- **Iterate on documentation**: Refine explanations based on reviewer questions
- **Test thoroughly** after each change to ensure functionality is preserved
- **Clean up comprehensively**: If feedback identifies one unused artifact, check for others from the same approach

