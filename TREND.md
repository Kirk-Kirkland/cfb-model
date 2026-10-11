# Standing prediction: the team totals trend

**Registered 2026-10-11, before any week 7 game kicked off.**
**Nothing in this file may be edited after that date except to append results.**

## The claim

Each team gets a season-to-date average of (final total minus closing total),
from games already played, once it has 3 or more. A game's trend is the mean of
the two teams. When |trend| is 2 points or more:

- **trend agrees**: the model's pick is the fade of the trend (Over on teams that
  have been going under, Under on teams that have been going over).
- **trend fights**: the model's pick goes with the trend.

From week 7 of 2026 onward, model card picks the trend **fights** should hit
**under 52.4%** (break-even at -110). Picks it agrees with, or with no trend,
should do better.

If the fights group hits 52.4% or better over 100+ graded bets, this prediction
is wrong and this file says so.

## Where it came from

Jason asked on 2026-10-11 whether a team's over/under record this year means
anything, after Wyoming went under again (6 straight).

Team trends study, 2,704 FBS games 2021-25, week 5 on
(`data/studies/team_trends.json`):

| Teams' average vs the close so far | Next game goes Over |
|---|---|
| +2 to +7 (been going over) | 42% |
| -7 to -2 (been going under) | 55% |

The been-over side held in all 5 seasons, the been-under side in 4 of 5. The
market overreacts to recent results, so the edge is fading the trend.

## What was tested, walk-forward 2023-25, closing lines

`web/trend_backtest.py`, output in `data/studies/trend_backtest.json`.

| Test | Hit rate | n |
|---|---|---|
| Model alone, 4+ edges | 54.1% | 787 |
| Model + k x trend (k fit on prior seasons only) | 53.8% | |
| Trend fade alone, \|trend\| >= 2 | 55.2% | 1,059 |
| Model picks, trend fights | **46.9%** | 179 |
| Model picks, trend agrees | 54.7% | 309 |
| Model picks, no trend | 57.9% | 299 |

**As a weight inside the model it failed.** Fit out of sample, k came out
positive every year (0.15, 0.07, 0.05) and the combined number did slightly
worse. So it is not in the model's edge.

**As a check it split hard.** The 179 model picks the trend fought lost money.

## Caveats, stated up front

- The model's own coefficients were fit on 2023-25, so the 54.1% baseline is
  flattering. The comparison that matters is fights vs the rest, same conditions.
- Opening line data is too thin after 2023 to grade at the open. 2023 alone:
  trend fade 54.7% at the open (n=254).
- 179 games is not proof. A 46.9% sample that size could be a 50% coin.

## What happens now

The flag is shown on every card pick (site: "trend agrees" / "trend fights")
and graded separately in `docs/record.json` under `trend`. **No pick is removed.**
The Top 5 stays the five largest edges. If the fights group keeps losing, the
rule to skip trend-fights picks goes into the model, announced in advance with
a date, never applied quietly.

## Results

(Appended weekly from `docs/record.json`.)

### Follow-up, 2026-10-11 (same day, before week 7): timing and conference-only

Jason's question: is the trend better mid-season, once non-conference games are
out of the way? `web/trend_split.py`, output in `data/studies/trend_split.json`.

Model picks the trend fights, 2023-25: weeks 4-6 47.0% (n=66), 7-9 47.8% (46),
10-14 46.3% (67). Flat across the season. 2022, the one season fully out of
sample for the model's coefficients: 44.2% (n=52).

Trend fade alone, 2023-25: weeks 4-6 52.3%, 7-9 56.0%, 10-14 56.6%. 2022:
50.9%, 49.5%, 61.7%. The standalone fade is a week 7+ signal.

Conference games only: no improvement (fade 56.1% vs 55.2%, fights 49.5% vs
46.9%) and it cannot start until about week 7. Not adopted. The registered
version above stands unchanged.
