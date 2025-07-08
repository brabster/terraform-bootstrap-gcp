## General

- This project produces one or more container images.
- The container images are used to data processing systems using Python, dbt and GCP.
- The container images are used in GitHub Codespaces and GitHub actions.
- The README file and any other documentation must always reflect what the repository does and how it works.
- Changes to the README file can be proposed, but must be carefully considered to minimise impact to consumers.
- Established good or best practice should be followed, with any deviations documented.
- Ask me questions to clarify project goals and my intent.

## Supply chains

- A dependency is any software used or consumed in the creation of this image.
- All dependencies should automatically update when the image is built.
- The number of dependencies must be minimised.
- Trust for a dependency must be determined primarily based the methods described at https://snyk.io/advisor. Review the factors desribed there.
- An overall package health score for an example Python package "mypackage" can be obtained from https://snyk.io/advisor/python/mypackage. Use this service to ensure that all packages have a package health score greater than 80.
- Trusted maintainers and suppliers take responsibility for the transitive dependencies of their projects. Only direct dependencies need to be considered.

## Changes

- Minimise changes, for example do not reformat a file or block as part of adding an instruction.