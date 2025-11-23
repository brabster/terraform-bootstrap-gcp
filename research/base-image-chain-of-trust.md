# Base image chain of trust analysis

## Executive summary

This document analyzes the chain of trust from the base image (`ubuntu:latest` from Docker Hub) used in the terraform-bootstrap-gcp container build. The analysis identifies gaps in the current chain of trust and proposes improvements to strengthen provenance verification while maintaining simplicity and auditability.

**Key findings:**

- The current base image (`docker.io/ubuntu:latest`) lacks cryptographic attestations that can be independently verified
- Docker Hub images are distributed via Docker Content Trust, but this is not enforced by default in Docker builds
- Ubuntu's official Docker images are built by Canonical, but the build process and provenance are not transparently verifiable
- The project currently provides attestations for its own build outputs but cannot verify the integrity of its foundation

**Recommendation:** Document the chain of trust limitations transparently and implement digest pinning with documented verification procedures to strengthen trust while maintaining the rolling update strategy.

## Current state: docker.io/ubuntu:latest

### Image source and distribution

The current Dockerfile uses:
```dockerfile
FROM docker.io/ubuntu:latest
```

This pulls from Docker Hub's official Ubuntu repository, which is managed by Canonical. The image is distributed through Docker Hub's content delivery network.

### Available trust mechanisms

**Docker Content Trust (DCT):**
- Docker Hub supports Docker Content Trust using Notary for image signing
- DCT must be explicitly enabled (`DOCKER_CONTENT_TRUST=1`)
- Not enforced by default in Docker builds
- Verifies publisher identity and image integrity but does not provide build provenance

**Image digests:**
- Ubuntu images have stable SHA256 digests
- Current digest: `sha256:c35e29c9450151419d9448b0fd75374fec4fff364a27f176fb458d472dfc9e54`
- Digests verify content integrity but not source authenticity

**OCI labels:**
- Images include basic metadata labels
- No cryptographic attestations in image manifest
- Limited provenance information

### Trust model limitations

1. **No attestations:** Docker Hub images do not provide GitHub-style attestations with SLSA provenance
2. **Opaque build process:** Canonical's build infrastructure and process are not transparently documented or verifiable
3. **Manual verification required:** No automated way to verify the image was built by Canonical from the expected source
4. **Weak link:** While the project provides attestations for its own images, consumers cannot verify the complete chain from base image through final artifact

## Chain of trust gap

The current architecture has a verified chain from the project's build output backwards to the project's source code, but has an unverified gap at the foundation:

```
[Verified Chain]
Final Image (ghcr.io/brabster/terraform-bootstrap-gcp:latest)
  ├─ Attestation: ✅ GitHub Actions
  ├─ Provenance: ✅ Commit, workflow, environment
  └─ Base Image: ❌ No verifiable provenance
      └─ docker.io/ubuntu:latest
          └─ Trust: Manual (Canonical's reputation)
```

This gap means:
- Consumers can verify the project's build but not the base layer
- Supply chain attestations are incomplete
- The trust model relies on Canonical's reputation rather than cryptographic proof

## Proposed improvements

After investigating available options, no Ubuntu base images currently provide GitHub-style attestations or other easily verifiable cryptographic provenance that would integrate seamlessly with the project's existing tooling. The following improvements can strengthen the chain of trust while maintaining simplicity:

### 1. Document the trust model explicitly

**Approach:** Add clear documentation explaining the trust assumptions for the base image

**Implementation:**
- Document in README that the base image trust relies on Canonical's reputation and Docker Hub's infrastructure
- Explain that while the project provides attestations, the base image does not have verifiable cryptographic provenance
- Provide guidance for consumers on evaluating this risk

**Benefits:**
- Transparency about supply chain trust boundaries
- Helps consumers make informed decisions
- Demonstrates due diligence

### 2. Reference base image by digest in documentation

**Approach:** Document the specific digest used in each release while maintaining the rolling tag in the Dockerfile

**Current Dockerfile (unchanged):**
```dockerfile
FROM docker.io/ubuntu:latest
```

**Additional documentation:** In release notes and README, document:
- The specific digest that `ubuntu:latest` resolved to during the build
- How to verify the digest matches between documentation and image
- Instructions for consumers who want to verify the base image digest

**Example documentation addition:**
```markdown
The current image was built using ubuntu:latest which resolved to:
- Digest: sha256:c35e29c9450151419d9448b0fd75374fec4fff364a27f176fb458d472dfc9e54
- Date: 2025-11-23
```

**Benefits:**
- Maintains automatic updates (keeps `latest` in Dockerfile)
- Provides audit trail of base images used
- Enables verification without preventing updates
- Minimal complexity increase

### 3. Add base image verification to CI

**Approach:** Add a CI step that captures and logs the base image digest

**Implementation:**
Add to the build workflow:
```yaml
- name: Capture base image digest
  run: |
    docker pull ubuntu:latest
    DIGEST=$(docker inspect ubuntu:latest --format='{{index .RepoDigests 0}}')
    echo "Base image digest: $DIGEST"
    echo "BASE_IMAGE_DIGEST=$DIGEST" >> $GITHUB_ENV
```

**Benefits:**
- Creates audit trail in CI logs
- No change to Dockerfile or image
- Enables tracking base image changes over time
- Could be enhanced later to alert on base image changes

### 4. Consider Docker Content Trust for verification

**Approach:** Document how consumers can enable Docker Content Trust to verify image signatures

**Implementation:**
Add to README:
```markdown
### Verifying base image integrity

Docker Hub's official Ubuntu images are signed with Docker Content Trust. 
To verify signatures when pulling:

```bash
export DOCKER_CONTENT_TRUST=1
docker pull ubuntu:latest
```

Note: This verifies the publisher signature but does not provide build provenance.
```

**Benefits:**
- Uses existing Docker Hub infrastructure
- Provides cryptographic signature verification
- No changes to build process
- Educates consumers about available verification options

**Limitations:**
- Does not provide build provenance (only publisher signatures)
- Requires manual enablement
- Different from project's GitHub attestation approach

### Recommended implementation order

1. **Immediate:** Document trust model explicitly (improvement #1)
2. **Short-term:** Reference base image digest in documentation (improvement #2)
3. **Short-term:** Add base image digest capture to CI (improvement #3)
4. **Optional:** Document Docker Content Trust verification (improvement #4)

### Combined impact

These improvements do not close the attestation gap completely, but they:
- Make the trust boundaries explicit and transparent
- Create an audit trail of base images used
- Provide verification options for consumers
- Maintain the simplicity principle (no complex changes)
- Stay aligned with the auditability principle (clear documentation)

## Alternative approaches considered and rejected

### 1. Switch to GitHub Container Registry Ubuntu images

**Approach:** Use `ghcr.io/canonical/ubuntu:latest`

**Investigated and rejected because:**
- Canonical's Ubuntu images on GHCR either do not exist or are not publicly accessible
- No evidence found of GitHub attestations for Ubuntu base images
- Would not actually solve the provenance gap

### 2. Enable Docker Content Trust for builds

**Approach:** Set `DOCKER_CONTENT_TRUST=1` in build environment

**Rejected because:**
- Adds complexity without providing build provenance
- Only verifies publisher signatures, not build process
- Inconsistent with project's existing attestation approach
- Can still be documented as an option for consumers (see improvement #4)

### 3. Pin to specific image digest in Dockerfile

**Approach:** Use `FROM ubuntu@sha256:...` in Dockerfile

**Rejected because:**
- Prevents automatic security updates
- Contradicts project's rolling update strategy
- Still does not solve provenance verification
- Adds significant maintenance burden
- Security through obscurity rather than verification

### 4. Build from Ubuntu source

**Approach:** Build Ubuntu base image from scratch

**Rejected because:**
- Massive complexity increase
- Requires Ubuntu build infrastructure
- Violates simplicity principle
- Duplicates Canonical's work
- Creates unsustainable maintenance burden

### 5. Use alternative base image with attestations

**Approach:** Switch to a different base image that provides attestations (e.g., Google's Distroless, Chainguard)

**Rejected because:**
- Distroless images lack package managers needed for the project's requirements
- Would require complete rearchitecture of the image
- Chainguard images require commercial licensing
- Ubuntu LTS is well-suited to the project's needs
- The problem would still exist, just shifted to a different vendor

## Implementation plan

### Phase 1: Documentation (immediate)

1. **Update README - Base image section**
   - Add subsection explaining trust model
   - Document base image verification limitations
   - Reference this analysis document

2. **Create or update supply chain security documentation**
   - Explain the trust boundaries
   - Document what is and is not cryptographically verifiable
   - Provide guidance for consumers

### Phase 2: CI enhancement (short-term)

1. **Add base image digest capture**
   - Modify `docker-publish.yml` workflow
   - Capture and log digest of base image used
   - Store digest for audit trail

2. **Document digest in release artifacts**
   - Add digest to build logs
   - Consider adding to image labels
   - Enable tracking of base image changes over time

### Phase 3: Consumer guidance (optional)

1. **Add Docker Content Trust documentation**
   - Document how to enable DCT
   - Explain what it verifies (and what it doesn't)
   - Provide examples

### Validation steps

1. Review documentation changes for clarity and accuracy
2. Test CI modifications don't break existing builds
3. Verify digest capture works correctly
4. Ensure documentation is visible and useful

### Rollback plan

All changes are additive (documentation and logging). No rollback needed as there are no breaking changes to the Dockerfile or build process.

## Conclusion

After thorough investigation, there is currently no Ubuntu base image available with GitHub-style attestations or easily verifiable cryptographic build provenance. This represents a gap in the chain of trust that cannot be completely closed without significant compromise to the project's principles of simplicity and automatic updates.

The proposed improvements focus on:

1. **Transparency:** Explicitly document the trust model and its limitations
2. **Auditability:** Create audit trail of base images used through CI logging
3. **Guidance:** Provide consumers with information to make informed decisions
4. **Pragmatism:** Accept that complete cryptographic verification from source to final image is not currently achievable with Ubuntu base images

These changes:

- **Maintain simplicity:** No complex architectural changes or new dependencies
- **Improve transparency:** Make trust boundaries explicit rather than implicit
- **Enable auditability:** Track which base images were used for each build
- **Respect reality:** Acknowledge limitations rather than creating false assurance

The chain of trust from the project's source code to published image remains intact and verifiable. The gap at the base image layer is acknowledged and documented, allowing consumers to evaluate the risk in context of their specific requirements.

### Key takeaway

The project's attestations prove that the image was built by the specified GitHub Actions workflow from the specified source code. However, these attestations cannot verify the provenance of the base Ubuntu image itself. This limitation is inherent to using official Ubuntu images from Docker Hub and cannot be resolved without either:
- Waiting for Canonical to provide attestations for their images
- Switching to a fundamentally different base image approach (rejected for complexity reasons)
- Building base images from source (rejected for simplicity and maintenance reasons)

The recommended approach is to transparently document this limitation while providing as much verification and auditability as practical within these constraints.

## References

- Canonical Ubuntu OCI images: https://hub.docker.com/_/ubuntu
- GitHub attestations: https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations
- SLSA provenance: https://slsa.dev/spec/v1.0/provenance
- Docker Content Trust: https://docs.docker.com/engine/security/trust/
- OCI image specification: https://github.com/opencontainers/image-spec
