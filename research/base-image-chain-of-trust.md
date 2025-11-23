# Base image chain of trust analysis

## Executive summary

This document analyzes the chain of trust from the base image (`ubuntu:latest` from Docker Hub) used in the terraform-bootstrap-gcp container build. The analysis identifies gaps in the current chain of trust, compares with Ubuntu ISO verification, investigates alternative base images, and proposes improvements to strengthen provenance verification while maintaining simplicity and auditability.

**Key findings:**

- The current base image (`docker.io/ubuntu:latest`) lacks cryptographic attestations that can be independently verified
- **Comparison with ISO:** The Docker image is equally trustworthy to Ubuntu ISO installations - both use Canonical signatures and lack build provenance
- **Alternative base images:** No viable alternatives provide both Ubuntu/APT compatibility and better verification (investigated: Chainguard, Distroless, Red Hat UBI, Debian, alternative registries)
- Docker Hub images support Docker Content Trust for signature verification, though not enforced by default
- The project currently provides attestations for its own build outputs but cannot verify the provenance of its foundation

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

## Comparison with Ubuntu ISO image verification

### How Ubuntu ISO images are verified

Ubuntu ISO images provide a stronger, more traditional verification model:

1. **Download artifacts:**
   - ISO image file (e.g., `ubuntu-24.04-live-server-amd64.iso`)
   - SHA256SUMS file (contains checksums for all ISO variants)
   - SHA256SUMS.gpg (GPG signature of the checksums file)

2. **Verification process:**
   ```bash
   # Import Ubuntu signing key from keyserver
   # NOTE: Verify the key fingerprint from https://ubuntu.com/tutorials/how-to-verify-ubuntu
   # before importing. The fingerprint below is for Ubuntu 24.04 LTS.
   gpg --keyserver hkps://keyserver.ubuntu.com --recv-keys 0x843938DF228D22F7B3742BC0D94AA3F0EFE21092
   
   # Verify the signature on the checksums file
   gpg --verify SHA256SUMS.gpg SHA256SUMS
   
   # Verify the ISO matches the signed checksum
   sha256sum -c SHA256SUMS 2>&1 | grep ubuntu-24.04-live-server-amd64.iso
   ```

3. **Trust chain:**
   - Ubuntu signing key (published on keyservers, documented on ubuntu.com)
   - → GPG signature on SHA256SUMS file
   - → Checksum in SHA256SUMS file
   - → ISO image file

This provides cryptographic proof that:
- The checksums file was signed by Ubuntu's official key
- The ISO content matches the signed checksum
- The image has not been tampered with since signing

### How Docker images are verified (current state)

Docker Hub Ubuntu images have a different verification model:

1. **Docker Content Trust (optional):**
   ```bash
   export DOCKER_CONTENT_TRUST=1
   docker pull ubuntu:latest
   ```
   
   This verifies:
   - The image was signed by the publisher (Canonical)
   - The image content matches the signed digest
   - The image has not been tampered with since signing

2. **Trust chain:**
   - Docker Hub's Notary infrastructure
   - → Publisher signature (Canonical's signing key)
   - → Image manifest and layers
   - → Container image

### Comparative analysis

**Similarities:**
- Both use cryptographic signatures from Canonical
- Both verify content integrity (checksums/digests match)
- Both confirm the artifact came from the official publisher
- Both rely on trusting Canonical's signing keys

**Key differences:**

| Aspect | Ubuntu ISO | Docker Hub Image |
|--------|-----------|------------------|
| **Verification enforcement** | Manual but documented process | Optional, not enabled by default |
| **Build provenance** | None (both lack SLSA-style provenance) | None |
| **Trust documentation** | Well-documented on ubuntu.com | Less prominent documentation |
| **Key distribution** | Public keyservers | Docker Hub's Notary infrastructure |
| **Industry standard** | GPG signatures (traditional) | Docker Content Trust/Notary |
| **Verification complexity** | 3 manual steps | 1 environment variable |

**Trustworthiness comparison:**

From a cryptographic standpoint, the image built from the Docker Hub base provides **equivalent trust guarantees** to an installation from the ISO:

1. **Both lack build provenance:** Neither the ISO nor Docker image provides information about how it was built, from what source code, or in what environment. You're trusting Canonical's build process in both cases.

2. **Both use cryptographic signatures:** Both can be verified to come from Canonical using their signing keys. The Docker Hub image uses Docker Content Trust (Notary), while the ISO uses traditional GPG signatures.

3. **Both rely on the same authority:** In both cases, you're ultimately trusting Canonical as the publisher and their key management practices.

4. **Both have optional verification:** While ISO verification is documented and encouraged, it's still optional. Similarly, Docker Content Trust is available but not enforced by default.

**Practical differences:**

In practice, ISO verification is more commonly performed:
- ISO verification is prominently documented on ubuntu.com
- The verification process is well-known in the Linux community
- System administrators routinely verify ISO checksums
- Docker Content Trust is less widely known and rarely enabled

This means that while the cryptographic guarantees are equivalent, ISO installations are more likely to be verified in practice.

**Where Docker images are weaker:**

- **Discoverability:** ISO verification is prominently documented; Docker Content Trust is less visible
- **Default behavior:** ISO users often verify explicitly; Docker users rarely enable DCT
- **Documentation:** ISO verification process is well-known; DCT is less familiar to many users

**Conclusion:**

The trust model is fundamentally the same: cryptographic signatures from Canonical verifying content integrity. The Docker image is not inherently less trustworthy than the ISO, but the verification mechanisms are less commonly used in practice. The real limitation for both is the lack of build provenance (SLSA attestations) showing how the artifacts were created.

## Investigation of alternative base images

### Requirements for alternative base images

To be a viable replacement for `ubuntu:latest`, an alternative must:

1. **Technical compatibility:**
   - Support APT package manager (or fully compatible alternative)
   - Work with third-party Debian/Ubuntu repositories (HashiCorp, Google Cloud SDK)
   - Provide Python 3.12+ and other standard Ubuntu packages
   - Maintain binary compatibility for installed software

2. **Security improvements:**
   - Provide cryptographic attestations or SLSA provenance
   - Verifiable build process
   - Integration with existing verification tools (gh CLI, cosign, etc.)

3. **Operational requirements:**
   - Regular security updates
   - Long-term support/stability
   - Minimal complexity increase
   - Documented and auditable

### Investigated alternatives

#### 1. Chainguard Images (cgr.dev)

**Description:** Chainguard provides hardened, minimal container images with built-in attestations.

**Ubuntu compatibility:**
- Chainguard offers `wolfi-base` (their own APK-based distribution)
- No direct Ubuntu or Debian-based image with APT support
- Would require complete rewrite to use APK instead of APT

**Verification capabilities:**
- ✅ SLSA provenance attestations
- ✅ SBOM (Software Bill of Materials)
- ✅ Signatures via Sigstore/cosign
- ✅ Daily security updates

**Assessment:** **Rejected**
- Requires APK package manager (incompatible with APT)
- HashiCorp and Google Cloud SDK repos are Debian/Ubuntu focused
- Complete architecture change violates simplicity principle
- Would need to rebuild entire image from scratch

#### 2. Google Distroless

**Description:** Minimal container images with only application and runtime dependencies.

**Ubuntu compatibility:**
- Debian-based but highly minimal
- No package manager included
- No shell included
- Cannot install additional packages

**Verification capabilities:**
- ✅ Reproducible builds
- ✅ SBOM available
- ⚠️ Limited attestations (not SLSA provenance)

**Assessment:** **Rejected**
- Lacks package manager needed to install Terraform, gcloud, etc.
- Cannot be used as a base for building development environments
- Designed for minimal runtime containers, not build environments

#### 3. Ubuntu LTS via alternative registries

**Investigated:** Whether Canonical publishes Ubuntu images with attestations to other registries (GHCR, GitLab, etc.)

**Findings:**
- Canonical's primary distribution is Docker Hub
- GitHub Container Registry has some Canonical organizations but no official Ubuntu base images with attestations
- GitLab Container Registry: Similar situation
- Amazon ECR Public: Mirrors of Docker Hub images without additional attestations

**Assessment:** **Rejected**
- No evidence of Ubuntu images with GitHub/SLSA attestations on any public registry
- Alternative registries are typically mirrors without enhanced verification

#### 4. Red Hat Universal Base Image (UBI)

**Description:** Red Hat's freely redistributable base images with enterprise security.

**Ubuntu compatibility:**
- ❌ RPM-based (dnf/yum), not APT
- Different package naming and structure
- Third-party repos for HashiCorp/Google use RPM format

**Verification capabilities:**
- ✅ Well-documented supply chain
- ✅ Signed packages
- ✅ Security errata tracking
- ⚠️ Different ecosystem than Ubuntu

**Assessment:** **Rejected**
- Not Ubuntu compatible (different package ecosystem)
- Would require complete rewrite of installation logic
- Large ecosystem change increases complexity
- Many third-party tools document Ubuntu/Debian, not RHEL

#### 5. Debian official images

**Description:** Debian is Ubuntu's upstream distribution.

**Ubuntu compatibility:**
- ✅ APT package manager
- ✅ Similar package structure
- ⚠️ Some Ubuntu-specific packages may differ
- ⚠️ Third-party repos may need Debian-specific configuration

**Verification capabilities:**
- Docker Hub official image (same as Ubuntu)
- Docker Content Trust available
- ❌ No SLSA attestations
- Same trust model as Ubuntu

**Assessment:** **Rejected**
- Same verification limitations as Ubuntu images
- Additional compatibility risks (Ubuntu-specific packages)
- No security benefit; moves problem sideways
- Less familiar to Ubuntu-focused users

### Alternative base images: Conclusion

**No viable alternative exists** that provides:
- Ubuntu/APT compatibility
- Better cryptographic verification than current Ubuntu image
- Maintained simplicity

All alternatives either:
- Use different package ecosystems (RPM, APK) requiring complete rewrite
- Lack package managers needed for development environments
- Have the same verification limitations as current Ubuntu images
- Add significant complexity without solving the provenance gap

**Recommendation:** Continue with `docker.io/ubuntu:latest` and focus on transparency and documentation of the trust model, as implemented in this PR.

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

**Investigated in detail (see "Investigation of alternative base images" section):**
- Chainguard images: Use APK instead of APT, complete rewrite required
- Google Distroless: No package manager, cannot install required tools
- Red Hat UBI: RPM-based, different ecosystem
- Debian: Same verification limitations as Ubuntu
- Ubuntu via alternative registries: No attestations available

**Rejected because:**
- No alternative provides both Ubuntu/APT compatibility AND better verification
- All options either require complete architecture rewrite or provide no security benefit
- Maintains current approach as the least complex option with acceptable trust model

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

After thorough investigation including comparison with Ubuntu ISO verification and analysis of alternative base images, the current approach with `docker.io/ubuntu:latest` represents the optimal balance of security, simplicity, and functionality.

### Key findings

1. **Trust comparison:** The Docker Hub Ubuntu image is equally trustworthy to an Ubuntu ISO installation. Both:
   - Use Canonical's cryptographic signatures
   - Verify content integrity
   - Lack build provenance (SLSA attestations)
   - Rely on trusting Canonical's build process

2. **Alternative base images:** No viable alternatives exist that provide both:
   - Ubuntu/APT compatibility (required for HashiCorp and Google Cloud SDK repositories)
   - Better cryptographic verification than current Ubuntu images
   
   All investigated alternatives (Chainguard, Distroless, Red Hat UBI, Debian) either require complete architecture rewrites or provide no security improvements.

3. **Verification options:** Docker Content Trust provides the same type of cryptographic verification as Ubuntu ISO signatures (publisher identity and content integrity), though it lacks build provenance.

### Implemented approach

The improvements focus on transparency and auditability:

1. **Transparency:** Explicitly document the trust model and its limitations
2. **Auditability:** Create audit trail of base images used through CI logging
3. **Guidance:** Provide consumers with Docker Content Trust verification instructions
4. **Pragmatism:** Accept that complete cryptographic verification from source to final image is not currently achievable with Ubuntu base images

These changes:

- **Maintain simplicity:** No complex architectural changes or new dependencies
- **Improve transparency:** Make trust boundaries explicit rather than implicit
- **Enable auditability:** Track which base images were used for each build
- **Respect reality:** Acknowledge limitations rather than creating false assurance

The chain of trust from the project's source code to published image remains intact and verifiable. The gap at the base image layer is acknowledged and documented, allowing consumers to evaluate the risk in context of their specific requirements.

### Why not switch base images?

As detailed in the "Investigation of alternative base images" section, no viable alternatives exist that provide both Ubuntu/APT compatibility and better cryptographic verification. Switching would require either abandoning Ubuntu's ecosystem or accepting the same verification limitations with a different vendor.

Switching would add complexity without solving the fundamental issue: base image build provenance is not available from any major distribution.

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
