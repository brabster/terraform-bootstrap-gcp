# syntax=docker/dockerfile:1

FROM python:3-slim

ARG BUILD_DATE
ARG VCS_REF

LABEL org.opencontainers.image.title="terraform-bootstrap-gcp"
LABEL org.opencontainers.image.description="This repository contains a container image build (Dockerfile).\nThe image is for use in VSCode in GitHub Codespaces and GitHub actions. We want to produce a single image that works well with both.\nThis image MUST follow good practice for building images, and MUST follow good practices for securing images.\n\nThe image will be rebuilt on a daily basis, and must pick up the latest updates as part of that rebuild.\n\nThe image supports Python 3-based development and should use the latest version of Python available.\nIt also includes the latest version of the gcloud command line tools."
LABEL org.opencontainers.image.url="https://github.com/brabster/terraform-bootstrap-gcp"
LABEL org.opencontainers.image.source="https://github.com/brabster/terraform-bootstrap-gcp"
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.revision=$VCS_REF
LABEL org.opencontainers.image.licenses="MIT"

COPY scripts/apt_install_thirdparty /usr/local/bin/apt_install_thirdparty

RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y --no-install-recommends gnupg lsb-release wget \
    && python -m pip install --upgrade pip setuptools \
    && rm -rf /var/lib/apt/lists/* \
    && chmod +x /usr/local/bin/apt_install_thirdparty \
    && useradd -m vscode

# Terraform, maintained by HashiCorp
RUN apt_install_thirdparty "https://apt.releases.hashicorp.com/gpg" "terraform" "https://apt.releases.hashicorp.com $(lsb_release -cs) main"

# gcloud CLI, maintained by Google
RUN apt_install_thirdparty "https://packages.cloud.google.com/apt/doc/apt-key.gpg" "google-cloud-cli" "https://packages.cloud.google.com/apt cloud-sdk main"

# osv-scanner, maintained by Google
COPY scripts/install_osv_scanner /usr/local/bin/install_osv_scanner
RUN install_osv_scanner

USER vscode

WORKDIR /home/vscode

# Pre-warm pip cache
COPY requirements.txt .
RUN VENV_PATH=$(mktemp -d) \
    && python -m venv "$VENV_PATH" \
    && . "$VENV_PATH"/bin/activate \
    && pip install -r requirements.txt \
    && rm -rf "$VENV_PATH" \
    && rm requirements.txt

CMD ["/bin/bash"]
