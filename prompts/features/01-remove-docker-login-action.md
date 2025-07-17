---
Feature Name: Remove docker/login-action GitHub action
Feature Description: This feature removes the `docker/login-action` GitHub action from the `docker-publish.yml` workflow. This is to eliminate Docker as a GitHub actions supplier. The replacement will be to use `docker login` and pipe the password from a secret.
Success Criteria:
- The `docker/login-action` is removed from `.github/workflows/docker-publish.yml`.
- The `docker-publish.yml` workflow continues to successfully publish images.
- Docker is removed as a supplier from the project.
References:
- .github/workflows/docker-publish.yml
---
