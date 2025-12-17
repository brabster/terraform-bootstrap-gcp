[![Docker image CI](https://github.com/brabster/terraform-bootstrap-gcp/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/brabster/terraform-bootstrap-gcp/actions/workflows/docker-publish.yml)
[![GitHub license](https://img.shields.io/github/license/brabster/terraform-bootstrap-gcp)](https://github.com/brabster/terraform-bootstrap-gcp/blob/main/LICENSE)

# Development container for lean data-centric development on GCP

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND under the [MIT License](LICENCE).** Commercial use is permitted, but the author recommends copying or forking to avoid supply chain risks. Clarity and minimialism are goals to support realistic consumer auditing.

This repository provides a Docker container image for cloud and data engineering. It includes essential tools for working with Google Cloud Platform, Terraform, and Python.

The image is built and published to the GitHub Container Registry every day. This process ensures it has the latest software versions and security updates.

It is designed for temporary development environments, including:
- **GitHub Codespaces**: For a pre-built cloud development environment.
- **GitHub Actions**: For building and testing infrastructure and data pipelines.

## Base image

The base image is `ubuntu:latest`. This tag provides the latest LTS release and is updated automatically when new LTS versions are released. LTS releases receive the same security updates as other Ubuntu releases. This choice avoids compatibility issues with third-party package repositories that may not immediately support newly released Ubuntu versions.

## Dependencies

This image relies on the following direct dependencies. Maintainers of these dependencies are responsible for their transitive dependencies. The latest versions are installed when the image is built.

| Component              | Dependency         | Maintainer                 |
| ---------------------- | ------------------ | -------------------------- |
| Base image             | `ubuntu:rolling`   | Canonical                  |
| Infrastructure as Code | `terraform`        | HashiCorp                  |
| Cloud SDK              | Google Cloud SDK   | Google                     |
| Language               | `python`           | Python Software Foundation |
| Package manager        | `pip`              | Python Software Foundation |
| Build tools            | `setuptools`       | Python Software Foundation |
| Version control        | `git`              | Canonical                  |
| Shell completion       | `bash-completion`  | Canonical                  |

## Image tagging strategy

The image has two types of tags:

- **`latest`**: This tag always points to the most recent daily build.
- **git SHA**: A tag with the git SHA of the commit that triggered the build is created for each build. This allows for pinning to a specific version of the image should the need arise.

## Supply chain security

Each published image includes a cryptographically signed attestation that provides build provenance information. This attestation proves that the image was built by this repository's GitHub Actions workflow and allows you to verify the image before use.

### Benefits of attestation

- **Authenticity**: Verify that the image was built by the official workflow, not by an unauthorised party.
- **Integrity**: Confirm that the image content has not been tampered with since it was built.
- **Transparency**: Access build metadata including the exact commit, workflow, and build environment that produced the image.
- **Compliance**: Meet supply chain security requirements for your organisation or regulatory framework.

### Verifying attestations

You can verify the attestation using the GitHub CLI:

```sh
gh attestation verify oci://ghcr.io/brabster/terraform-bootstrap-gcp:latest --owner brabster
```

This command checks that:
1. The attestation signature is valid and was created by GitHub Actions.
2. The image digest matches the attested content.
3. The attestation was created by a workflow in this repository.

For automated verification in your CI/CD pipeline, see [GitHub's attestation documentation](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds).

## How to use

### GitHub container registry

The image is publicly available on the GitHub Container Registry.

- **Image Name**: `ghcr.io/brabster/terraform-bootstrap-gcp`


### Running the container

To start an interactive session in the container:

```sh
docker run -it --rm ghcr.io/brabster/terraform-bootstrap-gcp:latest
```

### Using in GitHub actions

You can use this image to run jobs in your GitHub Actions workflows.

**Example: Pinning to a specific version**
```yaml
jobs:
  deploy-infra:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/brabster/terraform-bootstrap-gcp:latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          ...


      - name: Run terraform plan
        run: terraform plan
```

### Using in GitHub codespaces

To use this image for your development environment in GitHub Codespaces, create a `.devcontainer/devcontainer.json` file in your repository.

**Example: Using the latest image**
```json
{
  "image": "ghcr.io/brabster/terraform-bootstrap-gcp"
}
```

This configures Codespaces to use the pre-built image, giving you access to all the included tools.

## Building the image

### Building locally

The recommended way to build the image is using the build script, which handles intercepting proxy environments:

```sh
bash scripts/build_image.sh -t candidate_image:latest .
```

The build script automatically detects GitHub Copilot coding agent environments (using the `COPILOT_API_URL` environment variable) and configures the build to use the intercepting proxy certificate if present.
For environments with an intercepting proxy that is not automatically detected, you can manually provide the proxy's CA certificate using the build script:

```sh
bash scripts/build_image.sh /path/to/proxy-ca.pem -t candidate_image:latest .
```

**Note on intercepting proxies:** When using an intercepting proxy, the proxy terminates the TLS connection and re-encrypts it with its own certificate. This means you are trusting the proxy to properly validate the original server's certificate. In GitHub's hosted environments, this validation is performed by GitHub's infrastructure.
