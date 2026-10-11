"""
Team totals trends: does a team's over/under record so far this season predict
its next game against the closing total?

For every FBS game from week 5 on (2021-2025), each team's season-to-date
record vs the closing total and its average (actual - close) are computed from
games BEFORE that one only. Games are bucketed by the two teams' combined
tendency and graded vs the close. If the market already prices trends, every
bucket lands near 50%.

Also prints a 2026 game log for teams named in TEAMS (actual vs closing total).
Writes data/studies/team_trends.json. Needs CFBD_API_KEY.
"""
import os, sys, json, statistics as st, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb_engine as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEASONS = range(2021, 2026)
TEAMS = ['Wyoming']


def close_total(lines):
    ok = [l for l in lines if l.get('overUnder') is not None]
    for l in ok:
        if l['provider'].replace(' ', '').lower() == 'draftkings':
            return l['overUnder']
    return ok[0]['overUnder'] if ok else None


def season_rows(s):
    games = E.cfbd('games', year=s, seasonType='regular')
    lines = {l['id']: l for l in E.cfbd('lines', year=s, seasonType='regular')}
    out = []
    for g in sorted(games, key=lambda g: (g['week'], g.get('startDate') or '')):
        if g.get('homePoints') is None or g.get('awayPoints') is None:
            continue
        c = close_total((lines.get(g['id']) or {}).get('lines', []))
        if c is None:
            continue
        out.append(dict(season=s, week=g['week'], home=g['homeTeam'], away=g['awayTeam'],
                        fbs=g.get('homeClassification') == 'fbs' and g.get('awayClassification') == 'fbs',
                        actual=g['homePoints'] + g['awayPoints'], close=c))
    return out


def grade(rs):
    o = sum(1 for r in rs if r['actual'] > r['close'])
    u = sum(1 for r in rs if r['actual'] < r['close'])
    return dict(n=len(rs), over_pct=round(o / (o + u) * 100, 1) if o + u else None,
                avg_vs_close=round(st.mean([r['actual'] - r['close'] for r in rs]), 2) if rs else None)


def main():
    tested = []
    for s in SEASONS:
        hist = collections.defaultdict(list)   # team -> list of (actual - close) so far
        for r in season_rows(s):
            h, a = hist[r['home']], hist[r['away']]
            if r['fbs'] and r['week'] >= 5 and len(h) >= 3 and len(a) >= 3:
                over_rate = (sum(1 for x in h if x > 0) + sum(1 for x in a if x > 0)) / (len(h) + len(a))
                avg = (st.mean(h) + st.mean(a)) / 2
                tested.append(dict(r, prior_over_rate=over_rate, prior_avg=avg))
            hist[r['home']].append(r['actual'] - r['close'])
            hist[r['away']].append(r['actual'] - r['close'])
    out = dict(seasons=list(SEASONS), games=len(tested), by_over_rate={}, by_avg_vs_close={})
    for name, lo, hi in [('<35%', 0, .35), ('35-50%', .35, .5), ('50-65%', .5, .65), ('65%+', .65, 1.01)]:
        out['by_over_rate'][name] = grade([r for r in tested if lo <= r['prior_over_rate'] < hi])
    for name, lo, hi in [('< -7', -99, -7), ('-7 to -2', -7, -2), ('-2 to +2', -2, 2), ('+2 to +7', 2, 7), ('> +7', 7, 99)]:
        out['by_avg_vs_close'][name] = grade([r for r in tested if lo <= r['prior_avg'] < hi])
    # 2026 logs for named teams
    out['logs_2026'] = {}
    for r in season_rows(2026):
        for t in TEAMS:
            if t in (r['home'], r['away']):
                out['logs_2026'].setdefault(t, []).append(
                    dict(week=r['week'], game=f"{r['away']} @ {r['home']}", close=r['close'],
                         actual=r['actual'], result='Over' if r['actual'] > r['close'] else 'Under' if r['actual'] < r['close'] else 'Push'))
    d = os.path.join(ROOT, 'data', 'studies')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'team_trends.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
