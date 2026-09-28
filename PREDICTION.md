# Standing prediction: the garbage-time Under trap

**Registered 2026-09-28, before week 5 games kicked off.**
**Nothing in this file may be edited after that date except to append results.**

## The claim

When the model says Under on a game whose two teams have a **combined garbage-time
play share above 0.20**, that bet loses more often than it wins.

Concretely, from week 6 of 2026 onward, those bets should hit **under 50%**,
against a 52.4% break-even and a ~53% baseline for the model's other picks.

If they hit 52.4% or better over 100+ graded bets, this prediction is wrong and
this file says so.

## Where it came from

Jason raised it on 2026-09-28 after watching Florida play Auburn and Ole Miss.
Florida scored 24 in the second half of a one-score game and 21 in the fourth
quarter of the next one. His point: the model's garbage-time filter throws those
points away, but they still count on the scoreboard.

His first version of the mechanism was that such teams should go Over more often.
**That failed.** Over rates by combined-share quartile, 1,933 games 2023-25:
49.6%, 54.0%, 53.1%, 49.8%. Flat.

His second version was sharper: the market already prices a prolific offense, so
the Over edge is gone before it reaches us. That predicts something checkable
that has nothing to do with win rates, and it held:

| Combined share quartile | Market total minus model total |
|---|---|
| Bottom | −2.19 |
| 2nd | −1.27 |
| 3rd | −1.11 |
| Top | −0.25 |

Monotonic, correlation +0.149. The market lifts its number about 2 points on
these teams. The model's number barely moves (53.2 to 53.5). So the model gets
pushed into Unders by the thing it discards: it calls Under on 35% of low-share
games but 45% of top-quartile ones.

## What the backtest showed

Model record 2023-25, all edge sizes:

| | Record | Hit |
|---|---|---|
| Model Under, low share | 184-155 | 54.3% |
| **Model Under, high share** | **196-213** | **47.9%** |
| Model Over, low share | 345-281 | 55.1% |
| Model Over, high share | 285-274 | 51.0% |

Walk-forward, threshold picked only on seasons before the one scored:

| Season | No rule | Skipping flagged bets |
|---|---|---|
| 2024 | 54.2% | 57.2% |
| 2025 | 50.7% | 52.8% |
| Both | 52.5% (292-264) | **55.1% (245-200)** |

The 113 skipped bets went 47-64, **42.3%**, about 2.1 SE below break-even.

Threshold sensitivity, record of skipped bets: 0.18 → 47.1%, 0.20 → 45.6%,
0.22 → 42.3%, 0.25 → 45.7%, 0.30 → 44.6%. Stable across the range, so 0.20 was
chosen as a round number inside it rather than the 0.22 peak.

## Why it is registered instead of adopted

Every finding in this project so far came from trying things against the same
four seasons and keeping what looked good. That is how the per-edge confidence
tiers got built, and they collapsed from 63% to 53.7% on a clean rebuild.

This one arrived in the opposite order: a mechanism proposed from watching games,
a first version that failed, a sharpened version confirmed through a quantity
unrelated to betting records, and only then a trading implication. That is worth
more. It is still 1.7 standard errors on two test seasons.

So the rule is **not applied**. No bet is removed from any card. Games are
flagged in `docs/data.json` as `gs_flag`, and `web/record.py` grades flagged
picks separately. The site keeps betting them. We find out.

## How to check it

`docs/record.json` carries `gs_flagged` and `gs_unflagged` tallies from week 6
onward. Each week's card is committed to this repo before kickoff, so the flags
are timestamped and cannot be applied after the fact.

## Two ways this gets ruined

1. **Moving the threshold.** 0.20 is fixed. If someone re-tunes it mid-season the
   test is dead and the result means nothing.
2. **Calling it early.** A 6-1 stretch is six bets. 100 graded bets minimum, and
   even then the answer is a direction, not a certainty.

## Results

*(appended as weeks complete, never edited)*

| Week | Flagged bets | Record | Running |
|---|---|---|---|
| | | | |
