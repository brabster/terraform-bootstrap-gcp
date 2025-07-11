DO NOT OVERWRITE THIS FILE

A snapshot comparison, focusing on the vulnerabilies present on the image we create in this project against other candidate images for use in Codespaces, GitHub actions and the like.

- Use the osv-scanner tooling already present in the repo.
- Create an artefact that performs a point-in-time comparison.
- Scan outputs need to be captured for comparison.
- The comparison should be runnable as a GitHub action.

The snapshot must include:
- which images were compared.
- the size of each image in a human-readable format.
- the specific unique vulnerabilities in each image, as reported by osv-scanner.
- use the sarif format of osv-scanner and use the sarif spec to process the output correctly.
- ensure that the grouped vulnerabilities are used to count total vulnerabilities.
- a summary of how many vulnerabilities have fixes available, but are not applied.
- a summary of the threats exposed by the set of vulnerabilities.
- The report and SARIF files are stored in an 'uncommitted' directory.
- a conclusion describing the change in threat exposure by using this project's image compared to the others in the context of a local devcontainer, GitHub Codespaces and GitHub Actions.
- the output artefact should be stored in markdown form at uncommitted/vulnerabilities_comparison.md.
- each individual osv-scanner report should be saved named for the image it relates to in the 'uncommitted' directory.
- the output format from osv-scanner should include whether a fix is available or not.

Images to compare:
- The current default universal Codespaces image: mcr.microsoft.com/vscode/devcontainers/universal:latest
- The default ubuntu rolling image: docker.io/ubuntu:rolling
- The default Python image: mcr.microsoft.com/vscode/devcontainers/python:3
- The official Python image: docker.io/python:3
- The official Python slim image: docker.io/python:3-slim
- The gcloud cli official container image: gcr.io/google.com/cloudsdktool/google-cloud-cli:latest
- The official Terraform container image: 
- This project's image: ghcr.io/brabster/terraform-bootstrap-gcp:latest
