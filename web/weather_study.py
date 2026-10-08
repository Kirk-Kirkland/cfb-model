"""
Weather study: does the totals market price bad weather, and when?

Two questions, 2021-2025 regular season, FBS games with a posted total:

1. At the CLOSE, do windy / wet games still go Under more than the line says?
   If yes, the market under-adjusts and a weather rule has an edge at any time.
2. From OPEN to CLOSE, how far do totals fall in bad weather? That gap is the
   most an early bettor could capture by anticipating the storm. Caveat: the
   weather here is what was observed at the game, not what was forecast when
   the line opened, so this is an upper bound, not a promise.

Writes data/studies/weather.json and prints a table. Needs CFBD_API_KEY.
Usage:  python web/weather_study.py
"""
import os, sys, json, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb_engine as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEASONS = range(2021, 2026)


def pick_line(lines):
    """DraftKings if present, else the first book with both open and close."""
    ok = [l for l in lines if l.get('overUnder') is not None]
    for l in ok:
        if l['provider'].replace(' ', '').lower() == 'draftkings':
            return l
    for l in ok:
        if l.get('overUnderOpen') is not None:
            return l
    return ok[0] if ok else None


def rows():
    out = []
    for s in SEASONS:
        games = {g['id']: g for g in E.cfbd('games', year=s, seasonType='regular')}
        lines = {l['id']: l for l in E.cfbd('lines', year=s, seasonType='regular')}
        wx = {w['id']: w for w in E.cfbd('games/weather', year=s, seasonType='regular')}
        for gid, g in games.items():
            if g.get('homePoints') is None or g.get('awayPoints') is None:
                continue
            if g.get('homeClassification') != 'fbs' or g.get('awayClassification') != 'fbs':
                continue
            l = pick_line((lines.get(gid) or {}).get('lines', []))
            w = wx.get(gid)
            if not l or not w or w.get('gameIndoors'):
                continue
            close, opn = l.get('overUnder'), l.get('overUnderOpen')
            out.append(dict(season=s, close=close, open=opn,
                            actual=g['homePoints'] + g['awayPoints'],
                            wind=w.get('windSpeed'), precip=w.get('precipitation'),
                            cond=(w.get('weatherCondition') or '')))
    return out


def summarize(rs):
    n = len(rs)
    if not n:
        return dict(n=0)
    vs_close = [r['actual'] - r['close'] for r in rs]
    over = sum(1 for v in vs_close if v > 0)
    under = sum(1 for v in vs_close if v < 0)
    mv = [r['close'] - r['open'] for r in rs if r['open'] is not None]
    under_open = [r for r in rs if r['open'] is not None]
    uo = sum(1 for r in under_open if r['actual'] < r['open'])
    oo = sum(1 for r in under_open if r['actual'] > r['open'])
    return dict(n=n,
                avg_vs_close=round(st.mean(vs_close), 2),
                under_pct_vs_close=round(under / (over + under) * 100, 1) if over + under else None,
                avg_move_open_to_close=round(st.mean(mv), 2) if mv else None,
                under_pct_vs_open=round(uo / (uo + oo) * 100, 1) if uo + oo else None)


def main():
    rs = rows()
    wind_b = [('<10', 0, 10), ('10-15', 10, 15), ('15-20', 15, 20), ('20+', 20, 999)]
    out = dict(seasons=list(SEASONS), games=len(rs), by_wind={}, by_rain={}, storm={})
    for name, lo, hi in wind_b:
        out['by_wind'][name] = summarize([r for r in rs if r['wind'] is not None and lo <= r['wind'] < hi])
    wet = lambda r: (r['precip'] or 0) >= 0.1 or any(k in r['cond'].lower() for k in ('rain', 'storm', 'shower'))
    out['by_rain']['dry'] = summarize([r for r in rs if not wet(r)])
    out['by_rain']['wet'] = summarize([r for r in rs if wet(r)])
    # Storm proxy: wind 15+ AND wet. The tropical-system case.
    out['storm']['wind15_and_wet'] = summarize([r for r in rs if (r['wind'] or 0) >= 15 and wet(r)])
    out['storm']['everything_else'] = summarize([r for r in rs if not ((r['wind'] or 0) >= 15 and wet(r))])
    d = os.path.join(ROOT, 'data', 'studies')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'weather.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    print(f'cfbd calls: {E.CALLS[0]}')


if __name__ == '__main__':
    main()
