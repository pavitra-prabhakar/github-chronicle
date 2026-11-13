# 📰 The daily log

One file per day, written by the [Daily Chronicle workflow](../.github/workflows/daily-chronicle.yml) and merged through its own pull request.

```
daily/
└── YYYY/
    └── MM/
        └── YYYY-MM-DD.md
```

Each entry contains, depending on the day:

- 🆕 **New on the GitHub Changelog**: every update published since the previous entry, with a link and timestamp
- 🗓️ **On this day in GitHub history**: anniversaries from [`data/milestones.json`](../data/milestones.json)
- 🔎 **Milestone deep-dive**: when there is no new changelog entry, a sourced look back at one milestone

Each month is bundled into a `vYYYY.MM` [release](../../../releases).
