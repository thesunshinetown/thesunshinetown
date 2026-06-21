# The Sunshine Town — thesunshinetown.com

A static website about Newport, New Hampshire: history, events, and local news.

## Files

- `index.html` — the whole site (one page, three sections + about)
- `events.json` — upcoming events; edit this to update the Events section
- `news.json` — local news items; edit this to update the News section
- `update_news.py` — optional starter script for pulling local RSS feeds automatically

## Getting this live at thesunshinetown.com (GitHub Pages + daily auto-updates)

1. **Create a GitHub repo** and push all these files into it, including the
   `.github/workflows/update-news.yml` file and `requirements.txt`.
2. **Turn on GitHub Pages**: repo Settings → Pages → set the source to your
   main branch, root folder. GitHub gives you a `yourname.github.io/repo`
   URL immediately.
3. **Point your domain at it**: register thesunshinetown.com with any
   registrar, add a `CNAME` file to the repo containing just
   `thesunshinetown.com`, and in your registrar's DNS settings add the
   records GitHub's Pages docs specify (an `A` record pointing at GitHub's
   IPs, or a `CNAME` if using a subdomain). GitHub's own Pages settings page
   shows you exactly what's needed once you type in the custom domain.
4. **That's it for hosting.** The site is now live and will redeploy
   automatically any time a file in the repo changes — including when the
   Actions workflow updates `news.json`.

### How the daily automation works

`.github/workflows/update-news.yml` runs once a day (currently 11:00 UTC —
edit the `cron` line if you want a different time) and:
1. Checks out the repo
2. Installs `feedparser` (from `requirements.txt`)
3. Runs `update_news.py`, which pulls headlines from the feeds listed in
   `FEEDS` and filters them down with `KEYWORD_FILTER` so a statewide feed
   doesn't drown out actual Newport/Sullivan County stories
4. Commits the refreshed `news.json` back to the repo, which triggers
   GitHub Pages to redeploy automatically

You can also trigger it manually any time from the repo's **Actions** tab
(the `workflow_dispatch` trigger) instead of waiting for the schedule.

**Before relying on this:** the two feed URLs in `update_news.py` (Eagle
Times and NH Union Leader) are good candidates for Sullivan County coverage,
but I couldn't verify they still resolve from here — feed URLs change when
sites redesign. Open the workflow's Actions log after the first run; if a
feed fails, the script just skips it and logs why, so check there first if
`news.json` ends up empty.

### Events

`events.json` isn't wired into the automation since events (concerts,
markets, town meetings) don't usually come from RSS — keep adding those by
hand, or let me know if there's a specific town calendar/Facebook events
page you'd like pulled in instead.

---

## Older notes (alternate update paths, in case you want them later)

## A note on content

The history section uses facts adapted (in my own words, not copied) from public
sources — primarily the Wikipedia article on Newport, NH, and the town's own
historical chronology page. Worth double-checking dates against the Newport
Historical Society if accuracy matters a lot to you, since older local-history
sources sometimes disagree on exact years.
