# Vegas Gonzo Picks

Automated college football picks site. `web/cfb_engine.py` is the original model
(opponent-adjusted EPA ratings blended with SP+ and FPI, weighted against the market
line, from [collegefootballdata.com](https://collegefootballdata.com)). `web/publish.py`
runs it headlessly and writes `docs/data.json`, which the static dashboard in `docs/`
reads and displays. GitHub Actions runs `publish.py` on a schedule so the site updates
itself with no manual editing.

## One-time setup

1. Push this repo to GitHub.
2. In the repo, go to **Settings > Secrets and variables > Actions > New repository
   secret**, name it `CFBD_API_KEY`, and paste in your [CFBD](https://collegefootballdata.com/key)
   API key. (Free tier is enough: one run uses ~25-30 calls, well under the 1,000/month cap.)
3. Go to **Settings > Pages**, set **Source** to "Deploy from a branch", branch `main`,
   folder `/docs`. Save. The site will be live at `https://<username>.github.io/<repo>/`
   within a minute or two.
4. Go to **Actions > Publish weekly picks > Run workflow** to trigger the first run
   manually (don't wait for the schedule).

## How it updates

`.github/workflows/weekly.yml` runs the model **Sunday 12pm ET** and
**Thursday 9am ET** (ahead of Thursday-night games) as the main picks runs,
plus **Sunday 8pm and Monday 7am ET** runs to catch opening lines, and a **Saturday 8am ET** weather check (same full run, meant to catch late
wind/rain shifts rather than redefine the week's picks). Each run commits the
fresh `docs/data.json`, and the live site picks it up automatically. You can
also trigger a run any time from the
**Actions** tab ("Run workflow"), optionally forcing a specific week number.

## Lines and CLV

Lines come from ESPN's DraftKings feed first, then the CFBD feed as a backup
(CFBD lags by a day or more early in the week). Each game shows its source in
`line_src`.

Every pick records the **first line it appeared at** (`first_seen` in the
week's history file). It never changes once written, even if later runs move
or drop the pick. `web/record.py` pulls each game's closing total from ESPN and
grades **closing line value**: points the market moved toward the pick after it
was posted. CLV settles much faster than win/loss, so it is the quickest honest
read on whether the model beats the market.

## Sharp lines (The Odds API)

With a repo secret `ODDS_API_KEY` set, every picks run and the separate
**Odds snapshot** workflow (`.github/workflows/odds.yml`) pull totals from
~16 books including Pinnacle. Each pick then shows Pinnacle's no-vig total,
whether that sharp number agrees with the pick against DraftKings, and the best
number at any US book. Snapshots land in `data/odds/`, and the last one before
each kickoff is the near-close that `record.py` grades **CLV vs Pinnacle**
against. The sharp read is informational: it never adds or removes a bet.

Budget: 2 credits a pull, about 25 pulls a week, so ~215 of the free plan's
500 monthly credits. Without the secret all of this is skipped.

## Injuries (optional)

`data/injuries.json` is an optional list the model adds as a manual margin
adjustment, e.g.:

```json
[
  {"team": "Kansas", "pts": 3.0, "active": true}
]
```

`team` must match CFBD's exact team name. `pts` is points the team's expected
margin drops by (their QB/star being out). Edit this file directly on GitHub
(it's picked up on the next scheduled or manual run) - no Excel needed.

## Local development

```bash
pip install -r requirements.txt
export CFBD_API_KEY=your_key_here     # PowerShell: $env:CFBD_API_KEY = "your_key_here"
python web/publish.py --season 2026   # writes docs/data.json
python -m http.server 8000 -d docs    # then open http://localhost:8000
```

## What's not automated

The original workbook (`web/cfb_engine.py`, still here and runnable standalone)
also tracks personal bet history, props entries, and payouts - those need real
bets entered by hand, so they're intentionally left out of the automated site.
Run `python web/cfb_engine.py --week N` directly if you still want that Excel
workbook for your own tracking.

## Reference tools (not part of the publish workflow)

`web/backtest.py` and `web/ev_tools.py` are standalone scripts for offline
model validation and bet-sizing math - `publish.py` and the GitHub Actions
workflow never import them. `backtest.py` needs `pandas`/`scikit-learn` (not
in `requirements.txt`, since CI doesn't need them); install separately to use
it locally.
