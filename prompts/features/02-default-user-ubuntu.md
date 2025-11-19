---
prompt: |
  Using template 00-feature-template.md and rules in rules, create an implementation plan for changing the default user in Dockerfile to the ubuntu user created by default with UID 1000, GID 1000 in the ubuntu:rolling image. Ensure that the docker-publish workflow is extended to check that the default user is ubuntu and has the correct UID/GID. Flag any potential issues with this approach in the devcontainer, Codespaces and GitHub actions contexts. Write the implementation plan to features and stop for review.
refinement: |
  Based on the user's request and an analysis of the repository, this plan outlines the steps to change the default user in the production Docker image to `ubuntu`.
---

# Feature Implementation: Default Docker User to `ubuntu`

## 1. Clarification and Context

- **Goals:**
  - Modify the root `Dockerfile` to set the default user to `ubuntu` (UID 1000, GID 1000).
  - The `ubuntu` user's home directory `/home/ubuntu` will be created and used as the working directory.
  - Extend the `docker-publish.yml` GitHub Actions workflow to include a test that verifies the user, UID, and GID in the built container image.

- **Assumptions:**
  - The `ubuntu:rolling` base image includes a user named `ubuntu` with UID 1000 and a group named `ubuntu` with GID 1000. This is standard for Ubuntu base images.
  - The change is targeted at the production/CI image defined in `/Dockerfile`, not the development container defined in `/.devcontainer/Dockerfile`.

- **Non-Goals:**
  - This change will not affect the user (`vscode`) or configuration of the dev container environment used for Codespaces.

## 2. Pre-Mortem Analysis

- **Potential Showstoppers:**
  - If the base image `ubuntu:rolling` changes and no longer includes the `ubuntu` user/group with the expected UID/GID, the build could fail. The planned verification step will catch this.

- **External Dependencies:**
  - The plan depends on the user/group configuration of the `docker.io/ubuntu:rolling` base image.

- **Potential Issues & Mitigations:**
  - **File Permissions:** Processes inside the container will run as the `ubuntu` user. This is the desired behavior and is not expected to cause issues.
  - **Dev Container Context:** There is no direct impact on the dev container or Codespaces, as they use `/.devcontainer/Dockerfile`, which is not being modified. This isolates the change to the production image.
  - **GitHub Actions Context:** The `docker-publish.yml` workflow is not affected by the user change *within* the image it builds. The new verification step will be added to the existing `image_test` job to ensure correctness.

## 3. Implementation Plan

- **High-Level Steps:**
  1.  Modify the root `Dockerfile` to remove the creation of the `vscode` user and switch to the `ubuntu` user.
  2.  Update the `docker-publish.yml` workflow to add a verification step for the user configuration.

- **Code-Level Changes:**

  - **File:** `/Dockerfile`
    - **Action:** Modify the final `RUN` command and subsequent `USER` and `WORKDIR` instructions.
    - **Current Snippet:**
      ```dockerfile
      RUN apt-get update \
          && ... \
          && /tmp/scripts/install_osv_scanner.sh \
          && useradd -ms /bin/bash vscode \
          && rm -rf /tmp/scripts

      USER vscode

      WORKDIR /home/vscode
      ```
    - **New Snippet:**
      ```dockerfile
      RUN apt-get update \
          && ... \
          && /tmp/scripts/install_osv_scanner.sh \
          && rm -rf /tmp/scripts

      USER ubuntu

      WORKDIR /home/ubuntu
      ```
    - **Rationale:** The `ubuntu` user is assumed to exist in the base image. The `WORKDIR` instruction will create the `/home/ubuntu` directory if it doesn't exist, but it will be owned by `root`. The subsequent `COPY` and `RUN` commands will be executed as the `ubuntu` user, which has write permissions in its home directory.

  - **File:** `/.github/workflows/docker-publish.yml`
    - **Action:** Add user verification checks to the `image_test` job.
    - **Current Snippet (`image_test` job):**
      ```yaml
        - name: test
          run: |
            docker load -i ${{ runner.temp }}/candidate_image.tar
            docker run --rm candidate_image:latest bash -c " \
              set -e && \
              echo '--- Checking Terraform ---' && terraform --version && \
              echo '--- Checking gcloud ---' && gcloud --version && \
              echo '--- Checking Python ---' && python --version \
              echo '--- Checking osv-scanner ---' && osv-scanner --version \
            "
      ```
    - **New Snippet (`image_test` job):**
      ```yaml
        - name: test
          run: |
            docker load -i ${{ runner.temp }}/candidate_image.tar
            docker run --rm candidate_image:latest bash -c " \
              set -e && \
              echo '--- Checking Terraform ---' && terraform --version && \
              echo '--- Checking gcloud ---' && gcloud --version && \
              echo '--- Checking Python ---' && python --version && \
              echo '--- Checking osv-scanner ---' && osv-scanner --version && \
              echo '--- Checking user ---' && \
              if [ \"$(whoami)\" != 'ubuntu' ]; then echo 'User is not ubuntu'; exit 1; fi && \
              if [ \"$(id -u)\" != '1000' ]; then echo 'UID is not 1000'; exit 1; fi && \
              if [ \"$(id -g)\" != '1000' ]; then echo 'GID is not 1000'; exit 1; fi && \
              echo 'User checks passed.' \
            "
      ```

## 4. Validation and Testing

- **CI/CD:** The primary validation is the new test step in the `image_test` job of the `docker-publish.yml` workflow. A failure in this test will prevent the image from being published.
- **Manual:** An engineer can validate the change locally by building the image and running `docker run --rm -it <image_name> id` to inspect the user (`uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu)`).

## 5. Threat Model Impact

- **Summary of Changes:** The change replaces a custom non-root user (`vscode`) with a standard non-root user (`ubuntu`). This is a neutral change from a security standpoint and aligns with the principle of using standard, well-known configurations.
- **Asset Identification:** No new assets are introduced.
- **Threat Identification:** No new threats are introduced. The attack surface is substantively unchanged.
- **Mitigation Strategies:** The practice of using a non-root user is maintained.

## TL;DR

The plan is to modify the `Dockerfile` to use the standard `ubuntu` user (UID/GID 1000) instead of the custom `vscode` user. A verification step will be added to the `docker-publish.yml` CI workflow to ensure the user configuration is correct in all new image builds. This change is isolated to the production image and will not impact the Codespaces dev container.
