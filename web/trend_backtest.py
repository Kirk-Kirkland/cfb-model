"""
Walk-forward test: does the team totals trend add to the model?

For seasons 2022-2025, rebuild the totals model week by week (weeks 4-14) with
team_model(), which only uses games before the week being predicted. For each
game compute:

  model total  adj = pt + blowout + option adj   (same as publish.py, no weather)
  trend        avg of both teams' season-to-date (actual - closing total),
               0 until a team has 3 games with a line

Then three questions, each graded at the OPENING and the CLOSING total:

 1. Model alone: 4+ point edges, hit rate.
 2. Trend alone: fade it. Under when trend >= +2, Over when trend <= -2.
    Thresholds fixed before looking (2 points), not tuned.
 3. Model + trend: adj + k * trend, k fit ONLY on seasons before the one being
    graded (2023 uses 2022, 2024 uses 2022-23, 2025 uses 2022-24).

Caveat recorded with the output: the model's own coefficients (C_POSS) were
fit on 2023-25, so the model-alone numbers are flattering. The comparison that
matters is model vs model + trend under the same conditions.

Writes data/studies/trend_backtest.json. Needs CFBD_API_KEY.
"""
import os, sys, json, statistics as st, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb_engine as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEASONS = [2022, 2023, 2024, 2025]
OPT = set(E.CONSTS['OPT_TEAMS'])


def pick_line(lines):
    ok = [l for l in lines if l.get('overUnder') is not None]
    for l in ok:
        if l['provider'].replace(' ', '').lower() == 'draftkings':
            return l
    for l in ok:
        if l.get('overUnderOpen') is not None:
            return l
    return ok[0] if ok else None


def rebuild(season):
    D = dict(games={s: E.cfbd('games', year=s, seasonType='regular') for s in (season - 1, season)},
             adv={s: E.cfbd('stats/game/advanced', year=s, excludeGarbageTime='true') for s in (season - 1, season)},
             drives={s: E.cfbd('drives', year=s, seasonType='regular') for s in (season - 1, season)},
             ret=E.cfbd('player/returning', year=season), tal=E.cfbd('talent', year=season))
    lines = {l['id']: l for l in E.cfbd('lines', year=season, seasonType='regular')}
    saved = E.CONSTS['PRIOR2026']
    E.CONSTS['PRIOR2026'] = {}          # 2026-specific roster prior: not valid for past seasons
    rows = []
    try:
        for wk in range(4, 15):
            try:
                out, _, _ = E.team_model(D, season, wk)
            except Exception as e:
                print(f'  {season} wk{wk}: {e}', file=sys.stderr)
                continue
            for x in out:
                g = x['g']
                if g.get('homePoints') is None or g.get('awayPoints') is None:
                    continue
                l = pick_line((lines.get(g['id']) or {}).get('lines', []))
                if not l:
                    continue
                spread = l.get('spread') if l.get('spread') is not None else l.get('spreadOpen')
                two_opt = sum(t in OPT for t in (g['homeTeam'], g['awayTeam'])) == 2
                any_opt = any(t in OPT for t in (g['homeTeam'], g['awayTeam']))
                adj = (x['pt'] + E.CONSTS['C_SPREAD'] * abs(spread or 0)
                       + (E.CONSTS['OPT_ADJ'] if any_opt else 0))
                rows.append(dict(season=season, week=wk, id=g['id'], home=g['homeTeam'], away=g['awayTeam'],
                                 fcs=x['fcs'], two_opt=two_opt, adj=adj,
                                 close=l['overUnder'], open=l.get('overUnderOpen'),
                                 actual=g['homePoints'] + g['awayPoints'], start=g.get('startDate') or ''))
    finally:
        E.CONSTS['PRIOR2026'] = saved
    # Season-to-date trend, from games already played (any game with a line)
    allg = []
    for g in D['games'][season]:
        if g.get('homePoints') is None:
            continue
        l = pick_line((lines.get(g['id']) or {}).get('lines', []))
        if l:
            allg.append((g['week'], g.get('startDate') or '', g['homeTeam'], g['awayTeam'],
                         g['homePoints'] + g['awayPoints'] - l['overUnder']))
    allg.sort()
    for r in rows:
        h = [d for (w, s, ht, at, d) in allg if w < r['week'] and r['home'] in (ht, at)]
        a = [d for (w, s, ht, at, d) in allg if w < r['week'] and r['away'] in (ht, at)]
        r['trend'] = (st.mean(h) + st.mean(a)) / 2 if len(h) >= 3 and len(a) >= 3 else 0.0
    return rows


def grade(rows, pred_key, line_key, thresh=4.0):
    w = l = 0
    for r in rows:
        line = r.get(line_key)
        if line is None or r['fcs'] or r['two_opt']:
            continue
        edge = r[pred_key] - line
        if abs(edge) < thresh or r['actual'] == line:
            continue
        if (r['actual'] > line) == (edge > 0):
            w += 1
        else:
            l += 1
    return dict(w=w, l=l, n=w + l, pct=round(w / (w + l) * 100, 1) if w + l else None)


def grade_trend(rows, line_key, t=2.0):
    w = l = 0
    for r in rows:
        line = r.get(line_key)
        if line is None or r['fcs'] or abs(r['trend']) < t or r['actual'] == line:
            continue
        under = r['trend'] > 0          # been going over -> fade with the Under
        if (r['actual'] < line) == under:
            w += 1
        else:
            l += 1
    return dict(w=w, l=l, n=w + l, pct=round(w / (w + l) * 100, 1) if w + l else None)


def fit_k(train):
    x = np.array([r['trend'] for r in train if not r['fcs']])
    y = np.array([r['actual'] - r['adj'] for r in train if not r['fcs']])
    x_c, y_c = x - x.mean(), y - y.mean()
    return float((x_c @ y_c) / (x_c @ x_c)) if (x_c @ x_c) > 0 else 0.0


def mae(rows, key):
    v = [abs(r['actual'] - r[key]) for r in rows if not r['fcs']]
    return round(st.mean(v), 3) if v else None


def main():
    data = {s: rebuild(s) for s in SEASONS}
    out = dict(caveat='Model coefficients were fit on 2023-25; model-alone numbers are flattering. '
                      'Compare model vs model+trend, not either vs break-even.',
               seasons={}, totals={})
    pooled = collections.defaultdict(list)
    for s in SEASONS[1:]:
        train = [r for p in SEASONS if p < s for r in data[p]]
        k = fit_k(train)
        test = data[s]
        for r in test:
            r['adj_trend'] = r['adj'] + k * r['trend']
        res = dict(k=round(k, 3), games=len(test),
                   model_close=grade(test, 'adj', 'close'), model_open=grade(test, 'adj', 'open'),
                   combo_close=grade(test, 'adj_trend', 'close'), combo_open=grade(test, 'adj_trend', 'open'),
                   trend_close=grade_trend(test, 'close'), trend_open=grade_trend(test, 'open'),
                   mae_model=mae(test, 'adj'), mae_combo=mae(test, 'adj_trend'))
        out['seasons'][s] = res
        for key in ('model_close', 'model_open', 'combo_close', 'combo_open', 'trend_close', 'trend_open'):
            pooled[key].append(res[key])
        print(s, json.dumps(res))
    for key, v in pooled.items():
        w, l = sum(x['w'] for x in v), sum(x['l'] for x in v)
        out['totals'][key] = dict(w=w, l=l, n=w + l, pct=round(w / (w + l) * 100, 1) if w + l else None)
    out['k_final'] = round(fit_k([r for s in SEASONS for r in data[s]]), 3)
    # Agreement: model 4+ edge AND the trend fade (|trend| >= 2) on the same side,
    # vs model 4+ edge where the trend fights it. Seasons 2023-25, closing total.
    agree = fight = neutral = (0, 0)
    def add(t, win): return (t[0] + win, t[1] + (not win))
    for s in SEASONS[1:]:
        for r in data[s]:
            if r['fcs'] or r['two_opt'] or r['actual'] == r['close']:
                continue
            edge = r['adj'] - r['close']
            if abs(edge) < 4:
                continue
            win = (r['actual'] > r['close']) == (edge > 0)
            if abs(r['trend']) < 2:
                neutral = add(neutral, win)
            elif (edge > 0) == (r['trend'] < 0):      # model Over and trend says Over (been under)
                agree = add(agree, win)
            else:
                fight = add(fight, win)
    pct = lambda t: dict(w=t[0], l=t[1], n=sum(t), pct=round(t[0] / sum(t) * 100, 1) if sum(t) else None)
    out['model_with_trend'] = dict(agree=pct(agree), fight=pct(fight), no_trend=pct(neutral))
    print('model x trend', json.dumps(out['model_with_trend']))
    out['cfbd_calls'] = E.CALLS[0]
    d = os.path.join(ROOT, 'data', 'studies')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'trend_backtest.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out['totals'], indent=2), 'k_final', out['k_final'], 'calls', E.CALLS[0])


if __name__ == '__main__':
    main()
