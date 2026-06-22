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
import re
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
# non-news content that sometimes slips into broad search feeds. Google News
# titles end in " - PublisherName", so publisher names belong here too --
# that's the only reliable way to catch them, since feedparser doesn't
# consistently expose a separate machine-readable source field for this feed.
BLOCKLIST = [
    "for sale", "used cars", "car for sale", "vehicles for sale",
    "mpg", "dealership", "lease deal", "$", "price drop",
    "shop now", "coupon", "promo code", "% off",
    "realtor.com", "zillow", "redfin", "trulia", "homes.com",
    "cars.com", "autotrader", "carfax", "the weather channel",
]

MAX_ITEMS = 12


def clean_summary(raw):
    """Google News summaries are HTML snippets (an <a> tag plus a trailing
    <font> tag wrapper). Strip all tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", "", raw or "")
    text = text.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip()[:280]


def split_publisher(title):
    """Google News titles are formatted 'Headline - Publisher'. Split on the
    last ' - ' so multi-word headlines with hyphens aren't broken early."""
    if " - " in title:
        headline, publisher = title.rsplit(" - ", 1)
        return headline.strip(), publisher.strip()
    return title.strip(), ""


def pull_feed(url):
    parsed = feedparser.parse(url)
    items = []
    feed_title = parsed.feed.get("title", url)
    for entry in parsed.entries[:15]:
        raw_title = entry.get("title", "Untitled")
        raw_summary = entry.get("summary", "")
        haystack = (raw_title + " " + raw_summary).lower()

        if KEYWORD_FILTER and not any(kw in haystack for kw in KEYWORD_FILTER):
            continue

        if BLOCKLIST and any(bad in haystack for bad in BLOCKLIST):
            continue

        headline, publisher = split_publisher(raw_title)

        items.append({
            "date": entry.get("published", "")[:16] or datetime.date.today().isoformat(),
            "source": publisher or feed_title,
            "headline": headline,
            "summary": clean_summary(raw_summary),
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
