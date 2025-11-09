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
  "image": "ghcr.io/brabster/terraform-bootstrap-gcp",
  "customizations": {
    "vscode": {
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash"
      }
    }
  }
}
```

This configures Codespaces to use the pre-built image, giving you access to all the included tools. The `terminal.integrated.defaultProfile.linux` setting ensures bash is used as the default terminal shell in VSCode.

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
