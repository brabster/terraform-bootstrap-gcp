[![Docker image CI](https://github.com/brabster/terraform-bootstrap-gcp/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/brabster/terraform-bootstrap-gcp/actions/workflows/docker-publish.yml)
[![Docker image size](https://img.shields.io/docker/image-size/brabster/terraform-bootstrap-gcp/latest?logo=docker)](https://github.com/brabster/terraform-bootstrap-gcp/pkgs/container/terraform-bootstrap-gcp)
[![Image last built](https://img.shields.io/docker/label?server=ghcr.io&username=brabster&repository=terraform-bootstrap-gcp&tag=latest&label=org.opencontainers.image.created&logo=docker)](https://github.com/brabster/terraform-bootstrap-gcp/pkgs/container/terraform-bootstrap-gcp)
[![GitHub license](https://img.shields.io/github/license/brabster/terraform-bootstrap-gcp)](https://github.com/brabster/terraform-bootstrap-gcp/blob/main/LICENSE)

# Development container for GCP, Terraform, and dbt

This repository provides a Docker container image for cloud and data engineering. It includes essential tools for working with Google Cloud Platform, Terraform, and dbt.

The image is built and published to the GitHub Container Registry every day. This process ensures it has the latest software versions and security updates.

It is designed for temporary development environments, including:
- **GitHub Codespaces**: For a pre-built cloud development environment.
- **GitHub Actions**: For building and testing infrastructure and data pipelines.

## What's included

The container image includes the following tools:

- **Base Image**: `python:3-slim`
- **Infrastructure as Code**: `terraform` (latest)
- **Cloud SDK**: Google Cloud SDK (`gcloud`, `gsutil`, `bq`)
- **Data Transformation**: `dbt-bigquery`
- **Language**: `python3` and `pip`

## Image tagging strategy

The image has two types of tags:

- **`latest`**: This tag always points to the most recent daily build.
- **`YYYY-MM-DD`**: A tag with the build date (for example, `2025-07-08`) is created every day. Using a date tag is recommended for production to ensure you are using a specific, stable version of the image.

## How to use

### GitHub container registry

The image is publicly available on the GitHub Container Registry.

- **Image Name**: `ghcr.io/brabster/terraform-bootstrap-gcp`

### Pulling the image

You can pull the `latest` image to your computer using Docker:

```sh
docker pull ghcr.io/brabster/terraform-bootstrap-gcp:latest
```

To pull a specific version, use its date tag:

```sh
docker pull ghcr.io/brabster/terraform-bootstrap-gcp:2025-07-08
```

### Running the container

To start an interactive session in the container:

```sh
docker run -it --rm ghcr.io/brabster/terraform-bootstrap-gcp:latest /bin/bash
```

### Using in GitHub actions

You can use this image to run jobs in your GitHub Actions workflows. Pinning to a specific date is recommended for stability.

**Example: Pinning to a specific version**
```yaml
jobs:
  deploy-infra:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/brabster/terraform-bootstrap-gcp:2025-07-08
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: 'Authenticate to Google Cloud'
        uses: 'google-github-actions/auth@v2'
        with:
          credentials_json: '${{ secrets.GCP_CREDENTIALS }}'

      - name: 'Set up Cloud SDK'
        uses: 'google-github-actions/setup-gcloud@v2'

      - name: Run terraform plan
        run: terraform plan
```

### Using in GitHub codespaces

To use this image for your development environment in GitHub Codespaces, create a `.devcontainer/devcontainer.json` file in your repository.

**Example: Using the latest image**
```json
{
  "image": "ghcr.io/brabster/terraform-bootstrap-gcp:latest",
  "features": {}
}
```

This configures Codespaces to use the pre-built image, giving you access to all the included tools.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
