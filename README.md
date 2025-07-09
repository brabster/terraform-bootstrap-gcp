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

The base image is `ubuntu:rolling`. The rolling release is used to match the developer's local environment and to reduce the number of detected vulnerabilities compared to the LTS version. This choice helps to minimize the supply chain and provides more control over the installed software.

## What's included

The container image includes the latest versions of the following tools:

- **Base Image**: `ubuntu:rolling`
- **Infrastructure as Code**: `terraform`
- **Cloud SDK**: Google Cloud SDK (`gcloud`, `gsutil`, `bq`)
- **Language**: `python` and `pip`. `pip` cache contains the latest `dbt-bigquery` dependencies.

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

You can use this image to run jobs in your GitHub Actions workflows. Pinning to a specific date is recommended for stability.

**Example: Pinning to a specific version**
```yaml
jobs:
  deploy-infra:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/brabster/terraform-bootstrap-gcp
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
  "features": {}
}
```

This configures Codespaces to use the pre-built image, giving you access to all the included tools.

