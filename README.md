[![Docker image CI](https://github.com/brabster/terraform-bootstrap-gcp/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/brabster/terraform-bootstrap-gcp/actions/workflows/docker-publish.yml)
[![GitHub license](https://img.shields.io/github/license/brabster/terraform-bootstrap-gcp)](https://github.com/brabster/terraform-bootstrap-gcp/blob/main/LICENSE)

# Development container for lean data-centric development on GCP

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND under the [MIT License](LICENCE).** Commercial use is permitted, but the author recommends copying or forking to avoid supply chain risks. Clarity and minimialism are goals to support realistic consumer auditing.

This repository provides a Docker container image for cloud and data engineering. It includes essential tools for working with Google Cloud Platform, Terraform, and dbt.

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
| Data transformation    | `dbt-bigquery`     | dbt Labs                   |

The `dbt-bigquery` Python package and its dependencies are pre-loaded into the `pip` cache to reduce network requests to PyPI.

## Supply chain security

### Build attestations

Every published image includes cryptographically signed attestations that provide:

- **Build provenance**: Verifiable record of how the image was built, including source repository, commit, workflow, and build environment
- **Software Bill of Materials (SBOM)**: Complete inventory of all software components included in the image

Attestations use [Sigstore](https://www.sigstore.dev/) for signing and follow the [in-toto](https://in-toto.io/) attestation format. They are stored in GitHub's attestation registry and linked to the image.

### Verifying attestations

You can verify an image's attestations using the GitHub CLI:

```sh
# Verify build provenance
gh attestation verify oci://ghcr.io/brabster/terraform-bootstrap-gcp:latest --owner brabster

# View the SBOM
gh attestation verify oci://ghcr.io/brabster/terraform-bootstrap-gcp:latest --owner brabster --format json | jq -r '.verificationResult.statement.predicate.Data' | base64 -d | jq .
```

This verification confirms:
- The image was built from this repository
- The exact commit used to build the image
- The image was built in GitHub Actions (not on a developer workstation)
- The image has not been tampered with since it was built

## Image tagging strategy

The image has two types of tags:

- **`latest`**: This tag always points to the most recent daily build.
- **git SHA**: A tag with the git SHA of the commit that triggered the build is created for each build. This allows for pinning to a specific version of the image should the need arise.

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

To build the image locally:

```sh
docker build -t candidate_image:latest .
```

### Building with intercepting proxy support

If you are building in an environment with an intercepting proxy (such as GitHub Copilot), you need to provide the proxy's CA certificate:

```sh
DOCKER_BUILDKIT=1 docker build \
  --secret id=proxy_cert,src=/path/to/proxy-ca.pem \
  -t candidate_image:latest \
  .
```

The build will fail with a clear error message if you specify a certificate path that does not exist. If you do not provide a certificate, the build proceeds without proxy support.

**Note on intercepting proxies:** When using an intercepting proxy, the proxy terminates the TLS connection and re-encrypts it with its own certificate. This means you are trusting the proxy to properly validate the original server's certificate. In GitHub's hosted environments, this validation is performed by GitHub's infrastructure.
