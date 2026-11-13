#!/usr/bin/env python3
"""Print release notes (Markdown) for one month of the daily log.

Usage: python scripts/monthly_notes.py YYYY-MM
Exit code 3 when the month has no entries.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) != 2 or not re.fullmatch(r"\d{4}-\d{2}", sys.argv[1]):
        print(__doc__, file=sys.stderr)
        return 2
    year, month = sys.argv[1].split("-")
    files = sorted((ROOT / "daily" / year / month).glob("*.md"))
    if not files:
        print(f"no daily entries for {year}-{month}", file=sys.stderr)
        return 3
    changelog_links, on_this_day, deep_dives = [], [], []
    for f in files:
        body = f.read_text(encoding="utf-8")
        changelog_links += re.findall(r"\| \[([^\]]+)\]\((https?://[^)]+)\) \|", body)
        on_this_day += [(f.stem, t) for t in re.findall(r"^\*\*(\d{4}, .+?)\*\*$", body, flags=re.M)]
        deep_dives += [(f.stem, t) for t in re.findall(r"^### (.+)$", body, flags=re.M)]
    out = [f"## 📦 GitHub Chronicle, {year}-{month}", "",
           f"This release bundles **{len(files)} daily entries** from `daily/{year}/{month}/`.", ""]
    if changelog_links:
        out += [f"### 🆕 GitHub shipped ({len(changelog_links)} changelog updates)", ""]
        out += [f"- [{t}]({u})" for t, u in changelog_links[:60]]
        if len(changelog_links) > 60:
            out.append(f"- ...and {len(changelog_links) - 60} more in the daily files")
        out.append("")
    if on_this_day:
        out += ["### 🗓️ Anniversaries this month", ""] + [f"- {d}: {t}" for d, t in on_this_day] + [""]
    if deep_dives:
        out += ["### 🔎 Deep-dives", ""] + [f"- {d}: {t}" for d, t in deep_dives] + [""]
    out += ["### 📂 Daily files", ""] + [f"- [`{f.stem}`](daily/{year}/{month}/{f.name})" for f in files]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
