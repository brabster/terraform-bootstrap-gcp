# syntax=docker/dockerfile:1

FROM docker.io/ubuntu:latest

ARG BUILD_DATE
ARG VCS_REF

LABEL org.opencontainers.image.title="terraform-bootstrap-gcp"
LABEL org.opencontainers.image.description="This repository contains a container image build (Dockerfile).\nThe image is for use in VSCode in GitHub Codespaces and GitHub actions. We want to produce a single image that works well with both.\nThis image MUST follow good practice for building images, and MUST follow good practices for securing images.\n\nThe image will be rebuilt on a daily basis, and must pick up the latest updates as part of that rebuild.\n\nThe image supports Python 3-based development and should use the latest version of Python available.\nIt also includes the latest version of the gcloud command line tools."
LABEL org.opencontainers.image.url="https://github.com/brabster/terraform-bootstrap-gcp"
LABEL org.opencontainers.image.source="https://github.com/brabster/terraform-bootstrap-gcp"
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.revision=$VCS_REF
LABEL org.opencontainers.image.licenses="MIT"

COPY scripts/ /tmp/scripts/

# Install third party software
# Point gcloud tooling at installed python and delete bundled python (removed cryptography vulnerability, reduces image size)
ENV CLOUDSDK_PYTHON=/usr/bin/python
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends gnupg lsb-release wget \
    && rm -rf /var/lib/apt/lists/* \
    && chmod +x /tmp/scripts/* \
    && /tmp/scripts/setup_python.sh \
    && /tmp/scripts/apt_install_thirdparty.sh "https://apt.releases.hashicorp.com/gpg" "terraform" "https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
    && /tmp/scripts/apt_install_thirdparty.sh "https://packages.cloud.google.com/apt/doc/apt-key.gpg" "google-cloud-cli" "https://packages.cloud.google.com/apt cloud-sdk main" \
    && rm -rf /usr/lib/google-cloud-sdk/platform/bundledpythonunix \
    && /tmp/scripts/install_osv_scanner.sh \
    && rm -rf /tmp/scripts

USER ubuntu

WORKDIR /home/ubuntu

# Pre-warm pip cache
COPY requirements.txt .
RUN VENV_PATH=$(mktemp -d) \
    && python3 -m venv "$VENV_PATH" \
    && . "$VENV_PATH"/bin/activate \
    && pip install -r requirements.txt \
    && pip freeze > .preinstalled_requirements.txt \
    && rm -rf "$VENV_PATH" \
    && rm requirements.txt
