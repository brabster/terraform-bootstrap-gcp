---
prompt: |
  Write a rules file using the template in 00-rules-template.md to describe best practices when writing dockerfiles for use interactively and in automated contexts like CI/CD systems.
---

# Rules for Dockerfiles

## Guiding Principles

- Dockerfiles should be clear, concise, and easy to understand.
- Images should be as small as possible while still containing all necessary dependencies.
- Security is a primary concern; images should be secure by default.

## Core Rules

- Use official and trusted base images.
- Employ multi-stage builds to separate build-time dependencies from runtime dependencies.
- Minimize the number of layers by combining related commands.
- Use a `.dockerignore` file to exclude unnecessary files and directories.
- Avoid running containers as the root user. Create and switch to a non-root user.
- Each new command should be placed on a new line, with appropriate continuation characters.
  - For example, RUN commands should be continued with a `\` character ending a line and an appropriately indented `&&` on the next.

## Best Practices

- Default to a rolling tag like `latest` or `rolling` to ensure base images are continuously updated. This intentionally trades stability for security, forcing immediate attention to breaking changes and preventing silent vulnerability accumulation.
- Leverage build cache for faster builds.
- Use `COPY` instead of `ADD` unless you need `ADD`'s specific features (e.g., unpacking archives).
- Keep image dependencies to a minimum.
- Lint and scan Dockerfiles and images for vulnerabilities.

## Anti-Patterns

- Storing secrets in Dockerfiles.
- Installing unnecessary packages.
- Running `apt-get upgrade` or `dist-upgrade` in a container.
- Using a single layer for the entire application.

## References

- [Docker documentation: Best practices for writing Dockerfiles](https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/)
- [Snyk: 10 Dockerfile best practices for security](https://snyk.io/blog/10-dockerfile-best-practices-for-security/)

## TL;DR

- Use multi-stage builds, non-root users, and official images to create small, secure Docker images.
- Keep your Dockerfiles clean and your dependencies minimal.
