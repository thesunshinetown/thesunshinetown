"""
update_events.py

Pulls upcoming events from the Town of Newport, NH's official calendar feed
and writes them into events.json. Run daily via the GitHub Actions workflow
(same pattern as update_news.py).

Setup:
    pip install icalendar requests

Usage:
    python update_events.py

Source: https://www.newportnh.gov/calendar/ical/export.ics
This is the town's own iCal export, so it's authoritative -- but note it's
weighted toward government meetings (Selectboard, Planning Board, ZBA, etc.)
rather than community events like concerts or markets. Add more feeds to
FEEDS below if you find a Chamber of Commerce or library calendar with its
own iCal export.
"""

import json
import datetime
import requests
from icalendar import Calendar

FEEDS = [
    "https://www.newportnh.gov/calendar/ical/export.ics",
]

# How many days ahead to include.
LOOKAHEAD_DAYS = 45

# Max events to keep in the final list.
MAX_EVENTS = 20

CATEGORY_HINTS = {
    "selectmen": "Town Government",
    "selectboard": "Town Government",
    "planning board": "Town Government",
    "zoning": "Town Government",
    "zba": "Town Government",
    "conservation": "Town Government",
    "library": "Library",
    "recreation": "Recreation",
    "airport": "Town Government",
    "fire": "Town Government",
}


def guess_category(title):
    lowered = title.lower()
    for hint, category in CATEGORY_HINTS.items():
        if hint in lowered:
            return category
    return "Community"


def fetch_events(url):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    cal = Calendar.from_ical(resp.content)

    today = datetime.date.today()
    cutoff = today + datetime.timedelta(days=LOOKAHEAD_DAYS)

    events = []
    for component in cal.walk("VEVENT"):
        dtstart = component.get("dtstart")
        if not dtstart:
            continue
        dt = dtstart.dt
        # dt may be a date or datetime depending on the feed entry
        if isinstance(dt, datetime.datetime):
            event_date = dt.date()
            time_str = dt.strftime("%-I:%M %p")
        else:
            event_date = dt
            time_str = "All day"

        if event_date < today or event_date > cutoff:
            continue

        title = str(component.get("summary", "Untitled event"))
        location = str(component.get("location", "")) or "Newport, NH"

        events.append({
            "date": event_date.isoformat(),
            "time": time_str,
            "title": title,
            "location": location,
            "category": guess_category(title),
        })

    return events


def main():
    all_events = []
    for url in FEEDS:
        try:
            all_events.extend(fetch_events(url))
        except Exception as e:
            print(f"Skipped {url}: {e}")

    all_events.sort(key=lambda e: e["date"])
    all_events = all_events[:MAX_EVENTS]

    output = {
        "updated": datetime.date.today().isoformat(),
        "events": all_events if all_events else [
            {
                "date": datetime.date.today().isoformat(),
                "time": "",
                "title": "No upcoming events found",
                "location": "",
                "category": "system",
            }
        ],
    }

    with open("events.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(output['events'])} events to events.json")


if __name__ == "__main__":
    main()
