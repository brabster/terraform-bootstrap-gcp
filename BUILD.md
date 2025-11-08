# Building the Container Image

## Standard Build

To build the image with default settings (SSL verification enabled):

```bash
docker build -t terraform-bootstrap-gcp:latest .
```

## Building in Environments with SSL Interception

If you're building in an environment with SSL interception (such as corporate proxies or development environments with mkcert), use the `SKIP_SSL_VERIFY` build argument:

```bash
docker build --build-arg SKIP_SSL_VERIFY=true -t terraform-bootstrap-gcp:latest .
```

This will:
- Skip SSL certificate verification for wget when downloading GPG keys
- Skip SSL certificate verification for apt when accessing third-party repositories
- Configure pip to trust PyPI hosts without SSL verification

**Security Note**: Even with SSL verification disabled, the build maintains supply chain integrity through:
- GPG fingerprint verification of all downloaded signing keys
- GPG signature verification of all installed packages
- SHA256 checksum verification of downloaded binaries

## 12-Factor App Compliance

This approach follows [12-factor app principles](https://12factor.net/config) by:
- Keeping configuration (SSL verification behavior) separate from code
- Using environment variables (via build args) to control behavior
- Maintaining the same codebase for all environments
- Defaulting to secure behavior (SSL verification enabled)

The build scripts automatically adapt to the environment without requiring code changes.
