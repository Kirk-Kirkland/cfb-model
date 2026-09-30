# Corrections

Mistakes found after a card was published, what caused them, and what changed.
Entries are appended, never edited or removed.

---

## 2026-09-30: Navy / Air Force Over 45.5 pulled from the Week 5 card

**The pick.** Published Monday 2026-09-28 at 12:38 PM ET as the week's top play.
Model total 61.0 against a market of 45.5, an edge of +12.5, the largest the
model has produced this season.

**Who caught it.** A reader reviewing the five posted totals wrote: "This is the
one where his claimed +12.5-point edge bothers me most. Navy runs on about 78% of
its plays and Air Force about 82%, which naturally drains clock and reduces
possessions... I just don't see evidence for a model projection anywhere near 58
points."

He was right, and the reason is worse than he knew.

**Root cause: the model measures pace in plays, not possessions.**

Option offenses run long, clock-draining drives. They post high play counts while
producing very few possessions. The model had Navy at 61.7 plays per game and
Air Force at 68.5, against an FBS average of 59.7, and read that as scoring
volume. It is the opposite.

There was a patch for this, a −3.4 point adjustment on games involving Army, Navy
or Air Force, fit on 78 games. But it is coded as an `OR` and fires exactly once.
Navy versus Air Force has two option offenses and still received a single −3.4.
When one team runs the option the opponent still plays normally and the patch
roughly covers it. When both do, the whole game collapses and it does not come
close.

**The evidence.**

Walk-forward 2023-25, model residual by number of option teams in the game:

| | n | Residual (actual − projected) |
|---|---|---|
| No option team | 1,880 | +0.07 |
| One option team | 72 | +5.22 |
| **Two option teams** | **6** | **−15.27** |

Too high in five of those six.

Every service academy head-to-head since 2021 (n=15): 26, 35, 30, 23, 20, 37, 23,
26, 28, 41, 23, 44, 65, 37, 33. Mean **32.7**, median **30**. Exactly one cleared
45.5.

The model said 61.

**The fix.** Games with two option teams are now tiered `No bet: two option
teams` and never reach the card.

Fifteen games is not enough to fit a new constant on, and fitting one on a sample
that size is how the per-edge confidence tiers reached 63% and then collapsed to
53.7% on a clean rebuild. So nothing was fit. The games are simply excluded until
the pace term is rebuilt on possessions rather than plays, which is the real
repair.

**Also worth recording, because the same reader raised it.** He argued the posted
edges were larger than the evidence supports. Checked:

- Model MAE on totals, walk-forward 2023-25: **13.00 points**
- Market MAE over the same games: **12.58 points**

The market is more accurate than the model on average. A "+12.5 edge" is the gap
between two numbers, one of which is worse, not a forecast that the game runs 12
points over. The 4+ edge threshold still tests at roughly 53%, but the edge
figures printed on the picks graphics imply a precision this model does not have.
That was a presentation error and it was fair to call out.

**What this cost.** Navy/Air Force was the top play of the week and would have
been graded as a published pick. It is being pulled before kickoff, with this
note, rather than quietly dropped.

**Second bug, found while fixing the first.** Setting the tier was not enough.
`build_best_bets` reads a separate list that the tier never touched, so the first
republish tiered Navy/Air Force `No bet: two option teams` and still printed it as
the week's top play. The guard on that list checked only for FCS opponents. It now
excludes anything tiered `No bet`. Verified: the game is off `best_bets` and off
the Top 3.

**Credit where it belongs.** Jason raised this matchup on Monday 2026-09-28, the
same day the card was published, and pulled the last five Navy/Air Force results:
26, 23, 23, 41, 65. He was told the model's existing option adjustment had already
accounted for the style and that the pick should stand. That was wrong, and it was
asserted without checking the code. The adjustment fires once, not twice, and the
pace term underneath it was broken. It took an outside reader raising the same
objection two days later before the code was actually opened.

The lesson is not about option offenses. When the model disagrees with the market
by double digits, that is the model making an extraordinary claim and it gets
audited before publication, not after someone complains.
