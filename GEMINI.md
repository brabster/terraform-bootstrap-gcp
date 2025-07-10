## General

- This project produces one or more container images.
- The container images are used to data processing systems using Python, dbt and GCP.
- The container images are used in GitHub Codespaces and GitHub actions.
- The README file and any other documentation must always reflect what the repository does and how it works.
- Changes to the README file can be proposed, but must be carefully considered to minimise impact to consumers.
- Review the README file and note any further goals, principles and practices described there.
- Established good or best practice should be followed, with any deviations documented.
- Ask me questions to clarify project goals and my intent.
- Don't congratulate me for my interactions, keep your responses concise and to the point.

## Supply chains

- A dependency is any software used or consumed in the creation of this image.
- All dependencies should automatically update when the image is built.
- The number of dependencies must be minimised.
- Trust for a dependency must be determined primarily based the methods described at https://snyk.io/advisor. Review the factors desribed there.
- An overall package health score for an example Python package "mypackage" can be obtained from https://snyk.io/advisor/python/mypackage. Use this service to ensure that all packages have a package health score greater than 80.
- Trusted maintainers and suppliers take responsibility for the transitive dependencies of their projects. Only direct dependencies need to be considered.
- Each dependency must be annotated at point of inclusion with a comment declaring the maintaining party.
- A list of all dependencies and maintaining parties must be called out in a README section.

## Changes

- Minimise changes, for example do not reformat a file or block as part of adding an instruction.
- Suggest meaningful points to commit, along with commit messages that aim to describe *why the change was made* which is important for readers to understand, not *what was changed* which is obvious from the diff.
- Maintain a summary of our conversations in GEMINI_LOG.md, with each entry containing the date and time when the interaction started and ended. The log maintains a chronological ordering. Prompt me to update the summary when we commit. Do not change existing content, merge new content in.

## Style

- Writing style should follow associated press style guidelines.
- Jargon should only be used where necessary, aim for plain english.
- Do not use em-dashes or smart quotes.
- Use sentence case including capitalised proper nouns and brand names for headings, labels and badges