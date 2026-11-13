#!/usr/bin/env python3
"""Write today's GitHub Chronicle entry.

Creates daily/YYYY/MM/YYYY-MM-DD.md with:
  * new entries from the official GitHub Changelog RSS feed (title, link, date)
  * "On this day in GitHub history" when a milestone matches today's month/day
  * a rotating milestone deep-dive when the feed fails or has nothing new
and refreshes the "Latest updates" section of README.md.

Standard library only. Exactly one daily file per day; reruns are no-ops.
Usage: python scripts/daily.py [--date YYYY-MM-DD] [--dry-run]
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import email.utils
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEED_URL = "https://github.blog/changelog/feed/"
CONFIG = ROOT / ".github" / "chronicle.json"
MILESTONES = ROOT / "data" / "milestones.json"
STATE = ROOT / "data" / "state.json"
README = ROOT / "README.md"
DAILY = ROOT / "daily"
START, END = "<!-- LATEST:START -->", "<!-- LATEST:END -->"
MAX_NEW, MAX_SEEN, LATEST_N = 15, 1500, 7


def output(key: str, value: str) -> None:
    """Expose a value to later GitHub Actions steps."""
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")


def add_years(day: dt.date, years: int) -> dt.date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:  # February 29
        return day.replace(year=day.year + years, day=28)


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def fetch_feed() -> list[dict]:
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "github-chronicle/1.0 (+https://github.com)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    items = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or link).strip()
        published = None
        raw = item.findtext("pubDate")
        if raw:
            try:
                published = email.utils.parsedate_to_datetime(raw).astimezone(dt.timezone.utc)
            except (TypeError, ValueError):
                published = None
        if title and link:
            items.append({"title": title, "link": link, "id": guid or link, "published": published})
    return items


def when(m: dict) -> str:
    if m.get("month") and m.get("day"):
        return f"{calendar.month_name[m['month']]} {m['day']}, {m['year']}"
    if m.get("month"):
        return f"{calendar.month_name[m['month']]} {m['year']}"
    return str(m["year"])


def md_escape(text: str) -> str:
    return re.sub(r"([\[\]|])", r"\\\1", " ".join(text.split()))


def build_entry(today: dt.date, new_items: list[dict], milestones: list[dict], feed_error: str | None):
    lines = [f"# 📅 GitHub Chronicle, {today.strftime('%A, %B')} {today.day}, {today.year}", ""]
    headline_parts = []

    on_this_day = [m for m in milestones if m.get("month") == today.month and m.get("day") == today.day]
    if on_this_day:
        lines += ["## 🗓️ On this day in GitHub history", ""]
        for m in on_this_day:
            ago = today.year - m["year"]
            lines += [f"**{m['year']}, {ago} year{'s' if ago != 1 else ''} ago: {m['title']}**", "",
                      m["summary"], "", f"Source: <{m['source']}>", ""]
        headline_parts.append(f"on this day: {on_this_day[0]['title']}")

    if new_items:
        lines += [f"## 🆕 New on the GitHub Changelog ({len(new_items)})", "",
                  "| Published (UTC) | Update |", "|---|---|"]
        for it in new_items:
            stamp = it["published"].strftime("%Y-%m-%d %H:%M") if it["published"] else "n/a"
            lines.append(f"| {stamp} | [{md_escape(it['title'])}]({it['link']}) |")
        lines += ["", f"_Source: [GitHub Changelog]({FEED_URL.replace('feed/', '')})_", ""]
        headline_parts.insert(0, f"{len(new_items)} changelog update{'s' if len(new_items) != 1 else ''}")
    else:
        pick = milestones[today.toordinal() % len(milestones)]
        reason = (f"The GitHub Changelog feed could not be read today ({feed_error})."
                  if feed_error else "No new GitHub Changelog entries since the last run.")
        key = lambda m: (m["year"], m.get("month") or 0, m.get("day") or 0)
        later = sorted((m for m in milestones if key(m) > key(pick)), key=key)
        lines += ["## 🔎 Milestone deep-dive", "", f"_{reason} Here is a look back instead._", "",
                  f"### {pick['title']}", "", f"**{when(pick)}** · _{pick['category']}_ · era: _{pick['era']}_", "",
                  pick["summary"], "",
                  f"_{today.year - pick['year']} year{'' if today.year - pick['year'] == 1 else 's'} ago. "
                  + (f"Next in the chronicle: **{later[0]['title']}** ({when(later[0])})._" if later else "The most recent milestone in the chronicle._"),
                  "", f"Source: <{pick['source']}> · More from this era: [timeline/](../../../timeline/)", ""]
        headline_parts.insert(0, f"deep-dive: {pick['title']}")

    lines += ["---", "", "_Generated by [`scripts/daily.py`](../../../scripts/daily.py). "
              "Spotted a mistake? [Open an issue](../../../../../issues/new/choose)._", ""]
    return "\n".join(lines), "; ".join(headline_parts)


def refresh_readme(today: dt.date) -> None:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        return
    files = sorted(DAILY.glob("*/*/*.md"), reverse=True)[:LATEST_N]
    rows = ["| Date | Highlights |", "|---|---|"]
    for f in files:
        body = f.read_text(encoding="utf-8")
        heads = [h[3:].strip() for h in body.splitlines() if h.startswith("## ")]
        links = re.findall(r"\| \[([^\]]+)\]\(", body)
        sample = "; ".join(md_escape(x) for x in links[:2]) if links else ""
        summary = ", ".join(heads) + (f": {sample}" if sample else "")
        rel = f.relative_to(ROOT).as_posix()
        rows.append(f"| [{f.stem}]({rel}) | {summary} |")
    block = (f"{START}\n_Last updated {today.isoformat()} by the Daily Chronicle workflow. "
             f"Full log in [`daily/`](daily/)._\n\n" + "\n".join(rows) + f"\n{END}")
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    README.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", help="override today's date (YYYY-MM-DD, UTC)")
    ap.add_argument("--dry-run", action="store_true", help="print the entry without writing files")
    args = ap.parse_args()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(dt.timezone.utc).date()

    config = load_json(CONFIG, {})
    start = dt.date.fromisoformat(config.get("start_date", today.isoformat()))
    years = int(config.get("stop_after_years", 5))
    if today >= add_years(start, years):
        print(f"Chronicle automation ended on {add_years(start, years)} ({years} years after {start}). Nothing to do.")
        output("changed", "false")
        output("stopped", "true")
        return 0

    target = DAILY / f"{today:%Y}" / f"{today:%m}" / f"{today.isoformat()}.md"
    if target.exists():
        print(f"{target.relative_to(ROOT)} already exists; nothing to do.")
        output("changed", "false")
        return 0

    milestones = load_json(MILESTONES, {}).get("milestones", [])
    if not milestones:
        print("data/milestones.json is missing or empty", file=sys.stderr)
        return 1
    state = load_json(STATE, {"seen": [], "last_run": None})
    seen = list(state.get("seen", []))
    seen_set = set(seen)

    feed_error = None
    try:
        items = fetch_feed()
    except Exception as exc:  # network, HTTP or XML errors all fall back to a deep-dive
        items, feed_error = [], type(exc).__name__
        print(f"warning: could not read feed: {exc}", file=sys.stderr)

    first_run = not seen and state.get("last_run") is None
    new_items = [it for it in items if it["id"] not in seen_set]
    if first_run:  # don't dump the whole archive on day one; show the last 24h-ish
        cutoff = dt.datetime.combine(today, dt.time(), dt.timezone.utc) - dt.timedelta(days=2)
        new_items = [it for it in new_items if it["published"] and it["published"] >= cutoff]
    new_items = sorted(new_items, key=lambda i: i["published"] or dt.datetime.min.replace(tzinfo=dt.timezone.utc),
                       reverse=True)[:MAX_NEW]

    content, headline = build_entry(today, new_items, milestones, feed_error)
    if args.dry_run:
        print(content)
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    for it in items:  # mark everything currently in the feed as seen
        if it["id"] not in seen_set:
            seen.append(it["id"])
            seen_set.add(it["id"])
    state = {"seen": seen[-MAX_SEEN:], "last_run": today.isoformat()}
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    refresh_readme(today)

    title = f"Daily chronicle {today.isoformat()}: {headline}"
    title = re.sub(r"[\r\n]+", " ", title)[:200]
    print(f"wrote {target.relative_to(ROOT)}\n{title}")
    output("changed", "true")
    output("title", title)
    output("file", target.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
