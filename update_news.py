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
    # Google News RSS search feeds are far more reliable than guessing at a
    # specific outlet's feed URL -- this one pulls any recent coverage
    # mentioning Newport, NH from across the web.
    "https://news.google.com/rss/search?q=%22Newport%2C+NH%22+OR+%22Newport%2C+New+Hampshire%22&hl=en-US&gl=US&ceid=US:en",

    # A second feed focused on the wider Sullivan County area, in case the
    # first one comes up thin on any given day.
    "https://news.google.com/rss/search?q=%22Sullivan+County%22+New+Hampshire&hl=en-US&gl=US&ceid=US:en",
]

# Items must mention the town/area to be kept (cheap relevance check).
# Leave empty to disable.
KEYWORD_FILTER = ["newport"]

# Items get dropped if they look like classifieds, car listings, or other
# non-news content that sometimes slips into broad search feeds.
BLOCKLIST = [
    "for sale", "used cars", "car for sale", "vehicles for sale",
    "mpg", "dealership", "lease deal", "$", "price drop",
    "shop now", "coupon", "promo code", "% off",
]

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

        if BLOCKLIST and any(bad in haystack for bad in BLOCKLIST):
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
