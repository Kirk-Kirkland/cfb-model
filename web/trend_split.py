"""
Follow-up to trend_backtest.py, asked 2026-10-11: does the team totals trend
work better at a certain point in the season, and is it cleaner when built from
conference games only (non-conference cupcakes distort early trends)?

Same walk-forward rebuild as trend_backtest.py (seasons 2022-25, weeks 4-14,
closing totals). Two trend versions per game, both from games BEFORE it only:

  all   every game with a line (the registered version, TREND.md)
  conf  conference games only, still 3+ per team

For each version, model 4+ edge picks are split into agrees / fights / none
and graded by week bucket. Trend fade alone is graded the same way.
2022 is shown on its own: the model's coefficients were fit on 2023-25, so
2022 is the only season fully out of sample for the model.

Saves per-game rows (data/studies/trend_rows.json) so later splits need no
CFBD calls, and the summary to data/studies/trend_split.json.
"""
import os, sys, json, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb_engine as E
import trend_backtest as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKETS = [('wk 4-6', 4, 6), ('wk 7-9', 7, 9), ('wk 10-14', 10, 14)]


def conf_trends(season, rows):
    games = E.cfbd('games', year=season, seasonType='regular')
    lines = {l['id']: l for l in E.cfbd('lines', year=season, seasonType='regular')}
    allg = []
    for g in games:
        if g.get('homePoints') is None or not g.get('conferenceGame'):
            continue
        l = T.pick_line((lines.get(g['id']) or {}).get('lines', []))
        if l:
            allg.append((g['week'], g['homeTeam'], g['awayTeam'],
                         g['homePoints'] + g['awayPoints'] - l['overUnder']))
    for r in rows:
        h = [d for (w, ht, at, d) in allg if w < r['week'] and r['home'] in (ht, at)]
        a = [d for (w, ht, at, d) in allg if w < r['week'] and r['away'] in (ht, at)]
        r['trend_conf'] = (st.mean(h) + st.mean(a)) / 2 if len(h) >= 3 and len(a) >= 3 else 0.0


def rec(w, l):
    return dict(w=w, l=l, n=w + l, pct=round(w / (w + l) * 100, 1) if w + l else None)


def split(rows, key):
    out = {}
    for name, lo, hi in BUCKETS + [('all weeks', 4, 14)]:
        c = dict(agrees=[0, 0], fights=[0, 0], none=[0, 0], fade=[0, 0])
        for r in rows:
            if not (lo <= r['week'] <= hi) or r['fcs'] or r['actual'] == r['close']:
                continue
            tr = r[key]
            if abs(tr) >= 2:                          # trend fade alone
                win = (r['actual'] < r['close']) == (tr > 0)
                c['fade'][0 if win else 1] += 1
            if r['two_opt']:
                continue
            edge = r['adj'] - r['close']
            if abs(edge) < 4:
                continue
            win = (r['actual'] > r['close']) == (edge > 0)
            k = 'none' if abs(tr) < 2 else ('agrees' if (edge > 0) == (tr < 0) else 'fights')
            c[k][0 if win else 1] += 1
        out[name] = {k: rec(*v) for k, v in c.items()}
    return out


def main():
    data = {}
    for s in T.SEASONS:
        rows = T.rebuild(s)
        conf_trends(s, rows)
        data[s] = rows
    d = os.path.join(ROOT, 'data', 'studies')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'trend_rows.json'), 'w') as f:
        json.dump({str(s): v for s, v in data.items()}, f, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    test = [r for s in (2023, 2024, 2025) for r in data[s]]
    out = dict(
        note='Model 4+ edge picks by trend read, closing totals. 2023-25 matches TREND.md; '
             '2022 is fully out of sample for the model coefficients.',
        trend_all_2023_25=split(test, 'trend'),
        trend_conf_2023_25=split(test, 'trend_conf'),
        trend_all_2022=split(data[2022], 'trend'),
        trend_conf_2022=split(data[2022], 'trend_conf'),
        cfbd_calls=E.CALLS[0])
    with open(os.path.join(d, 'trend_split.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
