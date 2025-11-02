## Project overview

This repository produces container images for data-centric development on Google Cloud Platform. The images include Terraform, Google Cloud SDK, Python, and dbt-bigquery. They are designed for use in GitHub Codespaces and GitHub Actions.

**Always review `GEMINI.md` for complete project information, goals, and principles.**

## Project goals and principles

- Security, stability, sustainability and simplicity are priorities for this project
- Minimize dependencies and maintain a clear, auditable supply chain
- Default to rolling/latest versions for automatic security updates
- Fail loudly and securely rather than silently
- Write in Associated Press style with plain English (avoid jargon, em-dashes, and smart quotes)
- Use sentence case for headings, labels, and badges
- Make minimal changes - don't reformat code unnecessarily
- Ensure README and documentation always reflect what the project actually does

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

## Pull request reviews

The AI performing a pull request review is an expert in modern engineering practices with a specialism in security.

Code reviews must include:

- review of `GEMINI.md` to understand the goals and style of the project
- a review of what has changed for any security issues or improvements that could be made
- whether the `CHANGELOG.md` file includes the current PR. If it does not, the reviewer should propose an entry for the PR, following the layout and content of existing entries
- whether the `README.md` file reflects what the project actually does

The reviewer must strive to identify impactful changes, rather than cosmetic or stylistic changes.

