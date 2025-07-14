**Feature abandoned**

Triggering OAuth flow involves registering a client secret, approval screens and so on. Not in a position to assume that responsibility.

Generate a prompt that instructs Gemini to perform the following tasks:

- remove the existing gcloud command line tooling install from the Docker build
- replace it with a minimal script or program to trigger the Google Cloud oauth flow

The new program should be executable by a user in a Codespace or devcontainer at the command line using the command `auth`. It should update the application default credentials (adc), and allow the project and billing project to be overridden from defaults provided by the environment variables `GOOGLE_CLOUD_PROJECT` and `GOOGLE_BILLING_PROJECT`. If `GOOGLE_BILLING_PROJECT` is not set and the value is not provided at the command line, the value of GOOGLE_CLOUD_PROJECT should be used for the billing project too. These environment variables must not be specified in the build, they can be provided when the image runs.

The solution must be as simple as possible and easy to audit. It must not introduce new supply chains from suppliers that are not explicitly trusted in the project. If no suitable tools exist, a new program may be written using the appropriate Google Cloud SDKs.

The program must be tested as part of the GitHub actions build.

Follow the prompt structure in `prompts/00-prompt-template.md`. Write the prompt as markdown and place it in the `prompts` directory as `01-remove-gcloud.md`
