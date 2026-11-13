# Changelog

All notable changes to the structure of this project are documented here. The daily log itself lives in [`daily/`](daily/) and is bundled into monthly `vYYYY.MM` releases.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/) for structural releases.

## [1.0.0] - 2026-11-13

### Added
- README with a sourced, year-by-year history of GitHub from 2007 to 2025 and a Mermaid timeline.
- Era deep-dives in `timeline/`.
- `data/milestones.json`, machine-readable milestones with dates and sources.
- `scripts/daily.py` and the **Daily Chronicle** workflow: one pull request per day, auto-merged, recording GitHub Changelog updates and "on this day" anniversaries.
- **Monthly Release** workflow that publishes `vYYYY.MM` releases from the daily log.
- **Validate** workflow for contributions.
- Contributing guide, code of conduct, security policy, issue and pull request templates, citation metadata.
