# Security Policy

GitHub Chronicle is a documentation project, but it runs automation with write access to this repository, so we take security seriously.

## Supported versions

Only the `main` branch is supported.

## Reporting a vulnerability

Please **do not** open a public issue. Use GitHub's private vulnerability reporting: go to the **Security** tab and choose **Report a vulnerability**. You can expect an initial response within 7 days.

Relevant areas include:

- The workflows in `.github/workflows/` (token permissions, injection through feed content)
- `scripts/daily.py` (parsing of the external RSS feed)

## Design notes

- Workflows use the built-in, short-lived `GITHUB_TOKEN` with the minimum permissions they need. No personal access tokens are stored in this repository.
- Feed titles are passed to shell steps through environment variables, never interpolated directly into scripts.
