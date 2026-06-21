"""
update_news.py

Starter script to refresh news.json from local RSS feeds.
Run this daily via a cron job (or a scheduled GitHub Action / Render cron job)
on whatever server hosts the site.

Setup:
    pip install feedparser

Usage:
    python update_news.py

This pulls the most recent items from the FEEDS list below, keeps only a
handful of the freshest ones, and overwrites news.json in this same folder.
Edit FEEDS to point at whichever local sources you have permission to pull from
(town announcements, local paper RSS feeds, etc). Always check a feed's terms
of use before pulling it automatically.
"""

import json
import datetime
import feedparser

FEEDS = [
    # The Eagle Times covers Claremont, Newport, and the rest of Sullivan
    # County. Verify this still resolves before relying on it long-term --
    # feed URLs change when sites get redesigned.
    "https://www.eagletimes.com/feed/",

    # NH Union Leader's general feed (statewide, but often carries Sullivan
    # County stories). Swap for a more specific section feed if you find one.
    "https://www.unionleader.com/news/rss/",
]

# Optional: simple keyword filter so a statewide feed (like Union Leader's)
# doesn't flood the page with unrelated stories. Leave empty to disable.
KEYWORD_FILTER = ["newport", "sullivan county", "sugar river", "claremont"]

MAX_ITEMS = 12


def pull_feed(url):
    parsed = feedparser.parse(url)
    items = []
    source_name = parsed.feed.get("title", url)
    for entry in parsed.entries[:15]:
        title = entry.get("title", "Untitled")
        summary = (entry.get("summary", "") or "")[:280]
        haystack = (title + " " + summary).lower()

        if KEYWORD_FILTER and not any(kw in haystack for kw in KEYWORD_FILTER):
            continue

        items.append({
            "date": entry.get("published", "")[:16] or datetime.date.today().isoformat(),
            "source": source_name,
            "headline": title,
            "summary": summary,
            "link": entry.get("link", ""),
        })
        if len(items) >= 5:
            break
    return items


def main():
    all_items = []
    for feed_url in FEEDS:
        try:
            all_items.extend(pull_feed(feed_url))
        except Exception as e:
            print(f"Skipped {feed_url}: {e}")

    all_items = all_items[:MAX_ITEMS]

    output = {
        "updated": datetime.date.today().isoformat(),
        "items": all_items if all_items else [
            {
                "date": datetime.date.today().isoformat(),
                "source": "system",
                "headline": "No feeds configured yet",
                "summary": "Add RSS feed URLs to the FEEDS list in update_news.py.",
                "link": "",
            }
        ],
    }

    with open("news.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(output['items'])} items to news.json")


if __name__ == "__main__":
    main()
