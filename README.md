# Development Container for GCP, Terraform, and dbt

This repository builds and publishes a Docker container image designed for cloud and data engineering development. It provides a consistent and ready-to-use environment with essential tools for working with Google Cloud Platform (GCP), Terraform, and dbt.

The image is automatically built and published to the GitHub Container Registry daily, ensuring that it always contains the latest versions of the included tools and security updates.

It is optimized for use in ephemeral environments like:
- **GitHub Codespaces**: For a pre-configured cloud development environment.
- **GitHub Actions**: For building and testing infrastructure and data pipelines.

## What's Included

The container image comes pre-installed with the following tools:

- **Base Image**: `python:3-slim`
- **Infrastructure as Code**: `terraform` (latest)
- **Cloud SDK**: Google Cloud SDK (`gcloud`, `gsutil`, `bq`)
- **Data Transformation**: `dbt-bigquery`
- **Language**: `python3` and `pip`

## Image Tagging Strategy

The image is tagged with two different schemes:

- **`latest`**: This tag always points to the most recent daily build. Use this tag if you want to stay up-to-date automatically.
- **`YYYY-MM-DD`**: A new tag with the date of the build (e.g., `2025-07-08`) is created every day. Use a date-stamped tag to pin your workflows to a specific, stable version of the image, which is highly recommended for production environments.

## How to Use

### GitHub Container Registry

The image is publicly available on the GitHub Container Registry.

- **Image Name**: `ghcr.io/brabster/terraform-bootstrap-gcp`

### Pulling the Image

You can pull the `latest` image to your local machine using Docker:

```sh
docker pull ghcr.io/brabster/terraform-bootstrap-gcp:latest
```

To pull a specific version, use its date tag:

```sh
docker pull ghcr.io/brabster/terraform-bootstrap-gcp:2025-07-08
```

### Running the Container

To start an interactive session within the container:

```sh
docker run -it --rm ghcr.io/brabster/terraform-bootstrap-gcp:latest /bin/bash
```

### Using in GitHub Actions

You can use this image as the execution environment for jobs in your GitHub Actions workflows. Pinning to a specific date is recommended for stability.

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

### Using in GitHub Codespaces

To use this image as your development environment in GitHub Codespaces, create a `.devcontainer/devcontainer.json` file in your repository. You can use `latest` to always have the newest tools, or pin to a date for a more stable environment.

**Example: Using the latest image**
```json
{
  "image": "ghcr.io/brabster/terraform-bootstrap-gcp:latest",
  "features": {}
}
```

This will configure Codespaces to use the pre-built image, giving you immediate access to all the included tools.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
