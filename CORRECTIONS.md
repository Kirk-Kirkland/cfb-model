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

---

## 2026-09-30: pace rebuilt on possessions instead of plays

The real repair behind the entry above. The Navy/Air Force exclusion was a patch;
this is the defect it was patching.

**The change.** `PACE` is now possessions (drives) per game, not plays per game.
Plays is a broken proxy for scoring volume: a long clock-draining drive is many
plays and one possession. Option offenses live on those, so the model saw high
play counts and read scoring. Navy showed 61.7 plays and Air Force 68.5 against
a 59.7 FBS average. On possessions they are 10.4 and 10.0 against an 11.6 mean,
which is the truth.

The totals coefficients were refit on possessions (`C_POSS`), since the old ones
were fit against a different quantity and swapping the input alone would have
made things worse.

**Walk-forward 2023-25, totals at 4+ edge:**

| | Record | Hit | MAE |
|---|---|---|---|
| Plays | 478-426 | 52.9% | 13.00 |
| Possessions | 442-377 | **54.0%** | **12.94** |

By season: 2023 53.4% vs 53.5%, 2024 54.2% vs 53.6%, 2025 50.7% vs 55.3%. The
hit-rate gain is carried almost entirely by 2025 and should not be treated as a
reliable +1.1 points. What holds across every cut is MAE, including on games with
no option team (12.87 to 12.82). This ships as a defect repair, not an edge
discovery.

Possessions alone does **not** fix option games (42.1% to 45.9%, n=38, still below
break-even), so the two-option exclusion stays.

**Effect on Navy/Air Force:** model total falls from 61.0 to 49.5 against a 45.5
market. An 11.5 point error removed from one game.

**Kept separate on purpose:** QB snap share is a per-play quantity and still uses
plays per game, now stored as `plays_pg`. Feeding it possessions would have
inflated every share by roughly 70%. The two are named differently so they do not
get confused again.

**This takes effect in week 6, not week 5.** The possessions model produces a
materially different week 5 card, and the week 5 picks were already published
Monday and posted publicly. Replacing them now would mean the track record grades
picks nobody saw. Week 5 is graded as posted. Week 6 is the first card from the
possessions model.

---

## 2026-10-03: live site showed a different card than the one being graded

**What happened.** Once a week's first game kicks off, `publish.py` locks the
history file so the graded card can't change. But it still wrote the fresh
rebuild to `docs/data.json`. So every run after Thursday kickoff put a new card
on the site that nobody was graded on. On Saturday of week 5 the site's Top 3 was
WMU/BUFF, BGSU/M-OH and MIA/CLEM, built by the possessions engine that was
supposed to start in week 6. The published, graded Top 3 was UVA/FSU, PSU/NU and
MTSU/KU.

**Fix.** When the week is locked, the site now shows the locked card (with
`meta.locked = true`). Week 5's site data was restored to the published card.
No picks or results changed.
