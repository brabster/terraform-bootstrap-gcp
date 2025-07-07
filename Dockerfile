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

RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y --no-install-recommends gnupg lsb-release wget \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && wget -O- https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-cloud-cli \
    && rm -rf /var/lib/apt/lists/*

## https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null \
    && gpg --no-default-keyring --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg --fingerprint \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends terraform \
    && terraform -install-autocomplete \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m vscode

USER vscode

CMD ["/bin/bash"]
