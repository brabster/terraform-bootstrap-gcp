---
prompt: |
  Write a rules file using the template in 00-rules-template.md to describe best practices when writing bash shell scripts for use interactively and in automated contexts like CI/CD systems.
---

# Rules for Bash Scripting

## Guiding Principles

- Write scripts that are reliable, maintainable, and secure.
- Scripts should be idempotent, meaning they can be run multiple times with the same outcome.

## Core Rules

- **Fail Fast**: Use `set -e` to exit the script immediately if a command fails. Use `set -u` to treat unset variables as an error, and `set -o pipefail` to ensure that a pipeline command returns a non-zero exit code if any command in the pipeline fails.
- **Shebang**: Always start your script with `#!/bin/env bash` to specify the interpreter.
- **Error Handling**: Check the exit codes of commands to handle errors gracefully. An exit status of 0 indicates success, while any non-zero value signifies an error.
- **Use `trap` for Cleanup**: The `trap` command allows you to execute cleanup actions if the script is terminated unexpectedly.

## Best Practices

- **Comments**: Use comments to explain complex logic and improve readability.
- **Functions**: Break down your code into functions to structure your script and avoid repetition.
- **Variable Naming**: Use clear and descriptive variable names.
- **Keep it Simple**: A script should ideally do one thing well. For complex tasks, consider splitting them into multiple scripts.
- **Never Hardcode Secrets**: Use environment variables or a secure vault to manage sensitive information like API keys and passwords.
- **Validate Inputs**: Always validate user inputs to prevent command injection and other vulnerabilities.
- **Use Absolute Paths**: Specifying absolute paths for files and commands can prevent the execution of unintended commands.
- **Linting and Static Analysis**: Use tools like `shellcheck` to identify potential issues in your scripts before they become problems.
- **Version Control**: Store your scripts in a version control system like Git to track changes and collaborate with your team.
- **Testing**: Test your scripts in a safe environment before deploying them to production.
- **Logging**: Implement logging to help with debugging and troubleshooting. Redirect standard error to a log file to keep your output clean.
- **Dependency Management**: Be mindful of external dependencies. Document them clearly and, when possible, stick to built-in shell commands to improve portability.
- **Configuration Management**: Separate configuration from your scripts by using configuration files. This makes your scripts more flexible and reusable.

## Anti-Patterns

- **Hardcoding secrets**: Do not hardcode secrets directly in the script.
- **Ignoring errors**: Do not ignore errors, as this can lead to unexpected behavior.
- **Using non-portable features**: Avoid using features that are not available in all shells.

## References

- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [The Open Web Application Security Project (OWASP) Bash scripting cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Bash_Cheat_Sheet.html)

## TL;DR

- Use `set -euo pipefail` to make your scripts more robust.
- Write idempotent scripts that can be run multiple times without causing issues.
