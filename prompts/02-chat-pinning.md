# Debate Summary: Docker Image Pinning vs. Rolling Tags

This document summarizes a discussion about the trade-offs between using specific, pinned Docker image tags (e.g., `ubuntu:22.04`) versus using rolling tags (e.g., `latest` or `rolling`).

## The Initial Argument: Pin for Stability

The conventional best practice is to pin specific image versions. The primary arguments for this approach are:

- **Stability and Reproducibility:** Pinning ensures that builds are consistent over time and across different environments. It prevents unexpected failures caused by upstream changes to a `latest` tag.
- **Controlled Updates:** It allows teams to manage dependency updates as a deliberate, testable process rather than being forced to react to a breaking change.
- **Clear Traceability:** A specific version tag makes it immediately obvious what base image is being used, simplifying debugging and security audits.

## The Counter-Argument: Roll for Security

For specific contexts like internal CI/CD, dev containers, and automated data pipelines, a "fail loudly" strategy can be more effective. The arguments for using a rolling tag are:

- **Prioritizes Security over Stability:** This approach ensures the base image always includes the latest security patches by default. It accepts the risk of occasional build failures as a necessary trade-off for avoiding the "silent rot" of unpatched vulnerabilities in a neglected, pinned image.
- **Prevents Maintenance Neglect:** Pinning requires active, disciplined maintenance. In the real world, priorities shift and teams change, leading to pinned dependencies being forgotten. A rolling tag forces the issue by breaking the build, demanding immediate attention.
- **Failure is a Signal, Not a Catastrophe:** In the target contexts (CI/CD, dev tools), a broken build is a manageable inconvenience that stops work, rather than a critical production outage. It serves as an unavoidable notification that an underlying dependency has changed.
- **Reproducibility Remains Possible:** While less convenient, any build can still be reproduced by retrieving the exact image hash (`sha256:...`) from the build logs and temporarily pinning to it for debugging.

## Conclusion

The discussion concluded that for the project's specific use case, the risk of silent vulnerability accumulation in an unmaintained pinned image is greater than the risk of disruption from a rolling tag. Therefore, the chosen strategy is to **default to a rolling tag** to enforce a "fail loudly" and continuously updated security posture.