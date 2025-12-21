# Base image chain of trust analysis

## Executive summary

This document analyses the chain of trust for the Docker base image used in this project and compares it to the trust model of installing Ubuntu from an ISO image. It identifies gaps in the current approach and proposes practical improvements within the constraints of simplicity and auditability.

**Key finding**: The current Docker Hub ubuntu:latest image provides **weaker trust guarantees** than an Ubuntu ISO installation because it lacks cryptographic signature verification by default. However, practical improvements are limited by the current state of the container ecosystem and Canonical's distribution choices.

**Recommended action**: Document the trust limitation, use digest pinning for reproducibility, and monitor for future attestation support from Canonical.

## Current state

### Base image source

The project uses `ubuntu:latest` from Docker Hub (docker.io/library/ubuntu). This is an official Docker library image maintained through a partnership between Docker and Canonical.

### Trust mechanisms in place

1. **Registry infrastructure trust**: Docker Hub serves the image using HTTPS with certificate validation
2. **Content integrity**: Image layers are verified using SHA256 digests
3. **Official source designation**: The image is part of Docker's official library
4. **Transparency**: The image build process is documented at https://git.launchpad.net/cloud-images/+oci/ubuntu-base

### Trust gaps identified

1. **No cryptographic signature verification**: Docker pull does not verify any signature by default
2. **No build attestations**: The image lacks SLSA provenance or Sigstore attestations
3. **Mutable tag**: The `latest` tag can point to different digests over time
4. **Limited build transparency**: No automated way to verify the build process
5. **Docker Content Trust unavailable**: DCT (Notary v1) has no valid trust data for this image and is deprecated

## Comparison with Ubuntu ISO installation

### Ubuntu ISO trust model

When installing Ubuntu from an ISO image, users can verify:

1. **Signed checksums**: SHA256SUMS file is GPG-signed by Canonical
2. **Key verification**: Canonical's signing keys are distributed through the Ubuntu keyserver and documented
3. **Manual verification**: Users can verify the signature before installation using:
   ```bash
   gpg --keyserver hkp://keyserver.ubuntu.com --recv-keys 0x46181433FBB75451 0xD94AA3F0EFE21092
   gpg --verify SHA256SUMS.gpg SHA256SUMS
   sha256sum -c SHA256SUMS
   ```
4. **Chain of trust**: Clear path from known Canonical keys to the ISO file

### Docker Hub ubuntu:latest trust model

When pulling ubuntu:latest from Docker Hub:

1. **No signature verification**: Docker pull does not verify signatures by default
2. **Content integrity only**: SHA256 digests verify content was not modified in transit
3. **Infrastructure trust**: Relies on Docker Hub's infrastructure security
4. **No user verification**: No standard process for users to verify authenticity

### Comparison conclusion

The Docker Hub ubuntu:latest image provides **less trustworthy verification** than an ISO installation because:

- No cryptographic signature verification by default
- No standardised attestation mechanism comparable to GPG-signed checksums
- Relies entirely on Docker Hub's infrastructure trust rather than allowing independent verification
- Users cannot verify the chain of custody from Canonical to their system

The ISO installation process provides a complete chain of trust with user-verifiable signatures, while the Docker image trust model relies on infrastructure trust without cryptographic verification.

## Alternative base images evaluated

### Option 1: Canonical's OCI registry

**Status**: Canonical does not currently operate a public OCI registry with signed images or attestations.

**Evidence**: Research of Canonical's documentation and cloud-images repositories shows that while they provide cloud images at cloud-images.ubuntu.com, these are not distributed as signed OCI container images.

**Conclusion**: Not a viable alternative at this time.

### Option 2: Google's Distroless images

**Source**: gcr.io/distroless/base-debian12

**Benefits**:
- Minimal attack surface (no package manager, shell, or unnecessary utilities)
- Google-maintained with good security practices
- May have better attestation support

**Drawbacks**:
- Debian-based, not Ubuntu
- Incompatible with Ubuntu-specific package repositories used in this project (HashiCorp and Google Cloud SDK expect Ubuntu/Debian-specific releases)
- Breaking change for users expecting Ubuntu compatibility
- Reduced functionality may conflict with development environment goals

**Conclusion**: Not suitable for this project due to Ubuntu compatibility requirements.

### Option 3: Chainguard Images

**Source**: cgr.dev/chainguard/ubuntu (if available)

**Benefits**:
- SLSA Level 3 attestations
- SBOMs included
- Cryptographic signatures using Sigstore
- Regular updates and security patches

**Drawbacks**:
- Commercial offering with potential licensing costs
- Less established than Docker Hub official images
- Adds external commercial dependency
- Unknown Ubuntu version availability and compatibility

**Conclusion**: Would provide better security guarantees but conflicts with simplicity and sustainability principles. The added complexity and potential costs outweigh benefits for this project.

### Option 4: Build from Canonical cloud images

**Source**: https://cloud-images.ubuntu.com/

**Benefits**:
- Official Canonical source
- GPG-signed checksums available
- Could construct verified base image

**Drawbacks**:
- Requires building and maintaining base image ourselves
- Significant complexity increase
- Need to implement build automation
- Conflicts with simplicity principle
- Adds maintenance burden

**Conclusion**: Not practical for a project focused on simplicity and minimal dependencies.

## Practical improvements

While the ideal solution (cryptographically signed base images from Canonical) is not currently available, several practical improvements can strengthen the supply chain:

### Improvement 1: Use digest pinning

**Change**: Pin the base image to a specific digest instead of the `latest` tag.

**Example**:
```dockerfile
FROM docker.io/ubuntu:latest@sha256:4fdf0125919d24aec972544669dcd7d6a26a8ad7e6561c73d5549bd6db258ac2
```

**Benefits**:
- Reproducible builds with identical base image
- Protection against tag poisoning
- Explicit change tracking when updating base image

**Drawbacks**:
- Conflicts with the project principle of "default to rolling/latest versions for automatic security updates"
- Requires manual intervention to update the digest
- Reduces the automatic security update benefit
- Adds maintenance overhead

**Recommendation**: **Not recommended** for this project. The principle of defaulting to latest versions for automatic security updates is more important than reproducibility. The daily rebuild process ensures we get the latest base image, which is the intended behavior.

### Improvement 2: Document the trust assumption

**Change**: Add documentation explicitly stating the trust model and its limitations.

**Benefits**:
- Transparency about security posture
- Helps users make informed decisions
- No impact on simplicity or functionality
- Acknowledges limitations honestly

**Drawbacks**:
- None

**Recommendation**: **Implement this**. Add clear documentation about the base image trust model.

### Improvement 3: Verify base image digest in CI

**Change**: Add a CI step that records the base image digest used in each build.

**Benefits**:
- Audit trail of which base image was used
- Can detect unexpected changes
- Minimal complexity

**Drawbacks**:
- Does not prevent using a compromised image
- Adds a CI step
- Limited security benefit

**Recommendation**: **Consider for future enhancement**. This provides useful audit information but does not fundamentally improve trust.

### Improvement 4: Monitor for attestation support

**Change**: Regularly check if Canonical adds attestation support to their Docker Hub images.

**Benefits**:
- Ensures we adopt better verification when available
- No immediate implementation needed
- Aligns with security principles

**Drawbacks**:
- Requires ongoing monitoring
- Benefit is conditional on Canonical's actions

**Recommendation**: **Implement as part of maintenance**. Add a reminder to check for attestation support during regular security reviews.

## Why further improvements are not possible

Several potential improvements are not feasible given current constraints:

### Cannot verify Canonical signatures

**Why**: Canonical does not currently sign their Docker Hub images or provide attestations. The Docker Content Trust (DCT) infrastructure is deprecated and has no valid trust data for the ubuntu image.

**What would be needed**: Canonical would need to sign their images using Sigstore or a similar mechanism and publish the signatures.

### Cannot use alternative registries

**Why**: Canonical does not operate an alternative registry with signed images. The official source for Ubuntu container images is Docker Hub.

**What would be needed**: Canonical would need to publish signed images to an OCI-compliant registry with attestation support.

### Cannot implement signature verification

**Why**: There are no signatures to verify. Docker's signature verification mechanisms (DCT) do not have valid data for this image.

**What would be needed**: A signature format and verification tool that Canonical supports for their container images.

### Cannot build from scratch

**Why**: Building a base image from official Ubuntu archives would add significant complexity, conflict with the simplicity principle, and require ongoing maintenance.

**What would be needed**: Automated build infrastructure, verification logic, and maintenance commitment that conflicts with project goals.

## Recommendations

Based on this analysis, the following actions are recommended:

### Immediate actions

1. **Accept the trust limitation**: Acknowledge that the Docker Hub ubuntu:latest image relies on infrastructure trust rather than cryptographic verification.

2. **Document the trust model**: Add documentation to the README and this research directory explaining:
   - How trust is established (or not) for the base image
   - The comparison with ISO installation trust
   - Why alternatives are not practical
   - What users should consider when using this image

3. **Maintain transparency**: Continue to document all dependencies and their maintaining parties.

### Ongoing actions

1. **Monitor for attestation support**: Periodically check if Canonical adds Sigstore attestations or similar verification mechanisms to their Docker Hub images.

2. **Re-evaluate when ecosystem changes**: If container signature verification becomes standardised and widely adopted, re-evaluate the base image choice.

3. **Continue daily rebuilds**: Maintain the daily rebuild schedule to ensure the latest security updates are incorporated promptly.

## Conclusion

The ubuntu:latest Docker image from Docker Hub provides weaker trust guarantees than an Ubuntu ISO installation because it lacks cryptographic signature verification. This is a limitation of the current container ecosystem rather than a choice by this project.

While several alternatives exist (Chainguard, Distroless, building from scratch), they all conflict with the project's principles of simplicity, sustainability, and Ubuntu compatibility. The most practical approach is to:

1. Document the trust limitation honestly
2. Continue using ubuntu:latest to maintain automatic security updates
3. Rely on infrastructure trust from Docker Hub and Canonical
4. Monitor for future improvements in the container signature ecosystem

This approach maintains the project's goals of simplicity and automatic security updates while being transparent about the security trade-offs involved.

## References

- Docker Official Images: https://hub.docker.com/_/ubuntu
- Ubuntu Cloud Images: https://cloud-images.ubuntu.com/
- Docker Content Trust documentation: https://docs.docker.com/engine/security/trust/
- SLSA Framework: https://slsa.dev/
- Sigstore: https://www.sigstore.dev/
- Ubuntu GPG Keys: https://wiki.ubuntu.com/SecurityTeam/FAQ
- Canonical's image build process: https://git.launchpad.net/cloud-images/+oci/ubuntu-base
