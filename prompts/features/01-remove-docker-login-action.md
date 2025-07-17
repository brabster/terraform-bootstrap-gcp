---
Feature Name: Remove docker/login-action GitHub action
Feature Description: This feature removes the `docker/login-action` GitHub action from the `docker-publish.yml` workflow. This is to eliminate Docker as a GitHub actions supplier. The replacement will be to use `docker login` and pipe the password from a secret.
Success Criteria:
- The `docker/login-action` is removed from `.github/workflows/docker-publish.yml`.
- The `docker-publish.yml` workflow continues to successfully publish images.
- Docker is removed as a supplier from the project.
Threat Model Impact:
- **Summary of Changes:** This change reduces the supply chain attack surface by removing the `docker/login-action` and replacing it with a direct call to the Docker CLI.
- **Asset Identification:** The primary asset is the `GITHUB_TOKEN` secret, which is used to authenticate to the GitHub Container Registry.
- **Threat Identification:** The previous threat was the potential for the `docker/login-action` to be compromised, which could lead to the exfiltration of the `GITHUB_TOKEN`.
- **Mitigation Strategies:** By removing the third-party action, we eliminate its potential for compromise. The new method uses the Docker CLI directly with the `--password-stdin` flag, which is a secure way to handle the secret, preventing it from being exposed in shell history or process lists. Trust is now placed on the already-trusted GitHub runner environment.
References:
- .github/workflows/docker-publish.yml
---