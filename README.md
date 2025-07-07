This repository contains a container image build (Dockerfile).
The image is for use in VSCode in GitHub Codespaces and GitHub actions. We want to produce a single image that works well with both.
This image MUST follow good practice for building images, and MUST follow good practices for securing images.

The image will be rebuilt on a daily basis, and must pick up the latest updates as part of that rebuild.

The image supports Python 3-based development and should use the latest version of Python available.
It also includes the latest version of the gcloud command line tools.
