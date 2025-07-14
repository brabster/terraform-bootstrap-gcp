# Google Cloud Authentication CLI

Replace the existing `gcloud` command-line tool in the Docker build with a minimal script or program to handle the Google Cloud OAuth flow. This change will reduce the image size and attack surface by removing the full `gcloud` SDK, which is not needed for the primary purpose of this container.

## Requirements

- Remove the `gcloud` CLI installation from the `Dockerfile`.
- Create a new script or program named `auth`.
- The `auth` program must be executable by a user in a Codespace or devcontainer.
- The `auth` program must trigger the Google Cloud OAuth flow to obtain user credentials.
- The `auth` program must update the Application Default Credentials (ADC) file.
- The `auth` program must allow the user to override the default project and billing project.
- The `auth` program should accept command-line arguments for `project` and `billing-project`.
- The program must use the `GOOGLE_CLOUD_PROJECT` environment variable as the default project.
- The program must use the `GOOGLE_BILLING_PROJECT` environment variable as the default billing project.
- If `GOOGLE_BILLING_PROJECT` is not set, the value of `GOOGLE_CLOUD_PROJECT` should be used for the billing project.
- The environment variables (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_BILLING_PROJECT`) must not be set in the Dockerfile.
- The solution must be simple, minimal, and easy to audit.
- The solution must not introduce any new supply chain dependencies from untrusted suppliers.
- If no suitable tool exists, a new program may be written using the appropriate Google Cloud SDKs.
- The `auth.py` script should be copied to a directory in the container's `PATH`.
- The `auth.py` script should be aliased or renamed to `auth` so it can be executed as `auth`.

## Rules

- `GEMINI.md`

## Testing Considerations

- The `auth` program must be tested as part of the GitHub Actions build.
- The tests should verify that the ADC file is created and contains the correct information.
- The tests should verify that the project and billing project can be overridden.
- The tests should verify that the `auth` command is available and executable.

## Verification

- [ ] The `gcloud` CLI is removed from the `Dockerfile`.
- [ ] A new `auth` program is created and is executable.
- [ ] The `auth` program successfully authenticates and updates the ADC file.
- [ ] The project and billing project can be overridden via command-line arguments.
- [ ] The program is tested in the GitHub Actions build.
- [ ] The `auth` command is available in the container's `PATH`.
