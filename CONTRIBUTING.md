# Contributing to GitHub Chronicle

Thanks for helping keep the history of GitHub accurate! 🎉

## Ground rules

1. **Every fact needs a source.** Prefer primary sources (the GitHub Blog, GitHub Changelog, official press releases), then reputable press. Wikipedia is fine as a pointer but not as the only source for a new claim.
2. **No guessing.** If only the month or year is well established, set `day` (and `month`) to `null`.
3. **Neutral tone.** Describe what happened; skip hype.

## Branches

| Branch | Purpose |
|---|---|
| `main` | Published history. Receives the daily automated PR and reviewed PRs from `dev`. |
| `dev` | Integration branch for human contributions. Branch from here. |
| `daily/YYYY-MM-DD` | Short-lived, created and deleted by the Daily Chronicle workflow. |

## Adding or fixing a milestone

1. Fork the repo and create a branch from `dev`.
2. Edit [`data/milestones.json`](data/milestones.json). Required fields: `id` (kebab-case, unique), `year`, `month`, `day`, `era` (`origins`, `growth`, `microsoft`, `ai`), `category`, `title`, `summary`, `source` (https URL).
3. If the milestone belongs in the main story, update the matching year in `README.md` and the era file in `timeline/`.
4. Run the checks locally:
   ```bash
   python -m json.tool data/milestones.json > /dev/null
   python scripts/daily.py --dry-run
   ```
5. Open a pull request into `dev` and fill in the template.

## Reporting a mistake

Use the **Bug report** issue form for wrong dates, broken links or automation problems, and **Milestone suggestion** for new history.

By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
