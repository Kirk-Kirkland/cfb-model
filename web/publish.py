# -*- coding: utf-8 -*-
"""Runs the CFB model headlessly and writes a JSON snapshot for the static site.
No Excel involved: every formula from cfb_engine.build() is mirrored here in plain
Python so this can run unattended on GitHub Actions.

Usage:
  CFBD_API_KEY=xxxx python web/publish.py --season 2026 [--week 5] [--out ../docs/data.json]
If --week is omitted, the current week is auto-detected from the CFBD calendar.
"""
import os, sys, json, argparse, datetime, math

sys.path.insert(0, os.path.dirname(__file__))
import cfb_engine as E

# Mirrors the Inputs-tab defaults in cfb_engine.py's build() (the `inp` list).
# cfb_engine.py itself gets swapped out wholesale when the model is updated, so
# this default set lives here rather than in the engine file - keep it in sync
# by hand when the Inputs defaults change. blow/opta/opt_teams come straight
# from CONSTS since those are the engine's own canonical values.
D_IN = dict(
    hfa=3.0, w_epa=0.34, w_sp=0.33, w_fpi=0.33,
    trust_sides=0.85, trust_totals=0.75,
    sd_margin=15.25, sd_total=15.64,
    side_strong=5, side_edge=3.5,
    total_bet=4, total_lean=3, total_checknews=9,
    big_spread=24, wind_thresh=12, wind_pen=0.3,
    blow=E.CONSTS['C_SPREAD'], opta=E.CONSTS['OPT_ADJ'], opt_teams=set(E.CONSTS['OPT_TEAMS']),
)


def normsdist(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def floor_half(x):
    return math.floor(x * 2) / 2


def ceil_half(x):
    return math.ceil(x * 2) / 2


def bet_line_for(bet, s):
    """'Bet only if line is' guidance: how far the total can move before the
    edge is gone. Totals only - sides aren't bet, so there's no spread branch."""
    mt = s['model_total_adj']
    if bet.startswith('Over'):
        return f"at or below {floor_half(mt - D_IN['total_bet']):.1f}"
    return f"at or above {ceil_half(mt + D_IN['total_bet']):.1f}"


def autoweek(season):
    """CFBD's calendar weeks are contiguous, non-overlapping windows covering the
    whole season, so `now` falls in exactly one of them - the week whose games
    are next up (or in progress)."""
    cal = E.cfbd('calendar', year=season)
    reg = sorted([w for w in cal if w.get('seasonType') == 'regular'], key=lambda w: w['week'])
    now = datetime.datetime.now(datetime.timezone.utc)
    for w in reg:
        first = datetime.datetime.fromisoformat(w['firstGameStart'].replace('Z', '+00:00'))
        last = datetime.datetime.fromisoformat(w['lastGameStart'].replace('Z', '+00:00'))
        if first <= now <= last:
            return w['week']
    if reg and now < datetime.datetime.fromisoformat(reg[0]['firstGameStart'].replace('Z', '+00:00')):
        return reg[0]['week']
    return reg[-1]['week'] if reg else 1


def load_injuries(path):
    if not path or not os.path.exists(path):
        return {}
    rows = json.load(open(path))
    out = {}
    for r in rows:
        if r.get('active'):
            out.setdefault(r['team'], 0.0)
            out[r['team']] += float(r.get('pts', 0))
    return out


def book(lines, gid, prov):
    L = [x for x in lines.get(gid, {}).get('lines', []) if x.get('spread') is not None]
    for x in L:
        if x['provider'].replace(' ', '').lower() == prov.replace(' ', '').lower():
            return x
    if prov == 'DraftKings':
        for x in L:
            if x['provider'] not in ('Bovada', 'teamrankings'):
                return x
    return None


def et(z):
    d = datetime.datetime.fromisoformat(z.replace('Z', '+00:00')) - datetime.timedelta(hours=4)
    return d.strftime('%a %m/%d %I:%M %p')


def build_games(D, games_wk, injuries):
    lines = {l['id']: l for l in D['lines']}
    espn_ab = {}
    if D.get('espn'):
        for e in D['espn'].get('events', []):
            for c in e['competitions'][0]['competitors']:
                espn_ab[(e['id'], c['homeAway'])] = c['team']['abbreviation']
    fpi = {}
    if D.get('fpi'):
        for t in D['fpi']['teams']:
            fpi[int(t['team']['id'])] = t['categories'][0]['values'][0]
    SP = {r['team']: r['rating'] for r in D['sp']}

    HFA, WE, WS, WF = D_IN['hfa'], D_IN['w_epa'], D_IN['w_sp'], D_IN['w_fpi']
    TRS, TRT = D_IN['trust_sides'], D_IN['trust_totals']
    SDM, SDT = D_IN['sd_margin'], D_IN['sd_total']
    SBE, SLE = D_IN['side_strong'], D_IN['side_edge']
    TBE, TLE, TCN = D_IN['total_bet'], D_IN['total_lean'], D_IN['total_checknews']
    BIG, WTH, WPEN = D_IN['big_spread'], D_IN['wind_thresh'], D_IN['wind_pen']
    BLOW, OPTA, OPT_TEAMS = D_IN['blow'], D_IN['opta'], D_IN['opt_teams']

    games = []
    sel = []
    for x in sorted(games_wk, key=lambda x: x['g']['startDate']):
        g = x['g']
        gid = g['id']
        dk = book(lines, gid, 'DraftKings')
        bv = book(lines, gid, 'Bovada')
        neutral = g['neutralSite']
        fcs = x['fcs']
        ha = espn_ab.get((str(gid), 'home')) or g['homeTeam'][:4].upper()
        aa = espn_ab.get((str(gid), 'away')) or g['awayTeam'][:4].upper()

        dk_spread = dk.get('spread') if dk else None
        dk_total = dk.get('overUnder') if dk else None
        open_spread = dk.get('spreadOpen') if dk else None
        open_total = dk.get('overUnderOpen') if dk else None
        bv_spread = bv.get('spread') if bv else None
        home_ml = dk.get('homeMoneyline') if dk else None
        away_ml = dk.get('awayMoneyline') if dk else None

        # --- Margin model (informational only on the site - sides aren't bet) ---
        sp_margin = None
        if SP.get(g['homeTeam']) is not None and SP.get(g['awayTeam']) is not None:
            sp_margin = SP[g['homeTeam']] - SP[g['awayTeam']] + (0 if neutral else HFA)
        fpi_margin = None
        if fpi.get(g.get('homeId')) is not None and fpi.get(g.get('awayId')) is not None:
            fpi_margin = fpi[g['homeId']] - fpi[g['awayId']] + (0 if neutral else HFA)
        epa_margin = round(x['pm'], 2)
        blended = epa_margin if (sp_margin is None or fpi_margin is None) else WE * epa_margin + WS * sp_margin + WF * fpi_margin

        inj_adj = injuries.get(g['awayTeam'], 0.0) - injuries.get(g['homeTeam'], 0.0)
        model_margin = blended + inj_adj

        market_margin = -dk_spread if dk_spread is not None else None
        edge = (model_margin - market_margin) if market_margin is not None else None

        agree = None
        if edge is not None and sp_margin is not None and fpi_margin is not None:
            agree = sum(1 for c in (epa_margin, sp_margin, fpi_margin) if (c - market_margin > 0) == (edge > 0))

        final_margin = None
        cover_prob = None
        side_pick = None
        side_prob = None
        best_home = best_away = None
        if dk_spread is not None:
            best_home = dk_spread if bv_spread is None else max(dk_spread, bv_spread)
            best_away = -dk_spread if bv_spread is None else max(-dk_spread, -bv_spread)
        if market_margin is not None:
            final_margin = TRS * market_margin + (1 - TRS) * model_margin
            cover_prob = normsdist((final_margin + dk_spread) / SDM)
            side_prob = max(cover_prob, 1 - cover_prob)
            if cover_prob >= 0.5:
                side_pick = f"{g['homeTeam']} {best_home:+g}" if best_home != 0 else f"{g['homeTeam']} PK"
            else:
                side_pick = f"{g['awayTeam']} {best_away:+g}" if best_away != 0 else f"{g['awayTeam']} PK"

        side_tier = None
        if edge is not None:
            if fcs:
                side_tier = 'No bet: FCS'
            elif agree == 3 and abs(edge) >= SBE:
                side_tier = 'Edge' if abs(dk_spread) >= BIG else 'Strong edge'
            elif agree is not None and agree >= 2 and abs(edge) >= SLE:
                side_tier = 'Pass' if abs(dk_spread) >= BIG else 'Edge'
            else:
                side_tier = 'Pass'

        # --- Totals model ---
        w = D['_weather'].get(gid)
        wind = w[1] if w and w[1] is not None else None
        rain = w[2] if w else None
        temp = w[3] if w else None
        venue = w[0] if w else 'n/a'
        weather_adj = -max(0, (wind or 0) - WTH) * WPEN if wind is not None else 0.0
        blowout_adj = BLOW * abs(dk_spread) if dk_spread is not None else 0.0
        option_adj = OPTA if (g['homeTeam'] in OPT_TEAMS or g['awayTeam'] in OPT_TEAMS) else 0.0
        epa_total = round(x['pt'], 2)
        adj_total = epa_total + blowout_adj + option_adj + weather_adj

        total_edge = total_pick = total_prob = total_tier = final_total = over_prob = None
        if dk_total is not None:
            total_edge = adj_total - dk_total
            final_total = TRT * dk_total + (1 - TRT) * adj_total
            over_prob = 1 - normsdist((dk_total - final_total) / SDT)
            total_prob = max(over_prob, 1 - over_prob)
            total_pick = f"Over {dk_total:g}" if over_prob >= 0.5 else f"Under {dk_total:g}"
            # No 60+ skip rule: walk-forward testing showed 60+ totals still hit ~55%.
            if fcs:
                total_tier = 'No bet: FCS'
            elif abs(total_edge) >= TCN:
                moving_with = open_total is not None and ((dk_total - open_total > 0) == (total_edge > 0))
                total_tier = 'BET' if moving_with else 'Check news'
            elif abs(total_edge) >= TBE:
                total_tier = 'LEAN' if (dk_spread is not None and abs(dk_spread) >= BIG) else 'BET'
            elif abs(total_edge) >= TLE:
                total_tier = 'LEAN'
            else:
                total_tier = 'Pass'

        ml_edge = home_novig = model_winprob = None
        if home_ml is not None and away_ml is not None:
            hp = -home_ml / (-home_ml + 100) if home_ml < 0 else 100 / (home_ml + 100)
            ap = -away_ml / (-away_ml + 100) if away_ml < 0 else 100 / (away_ml + 100)
            home_novig = hp / (hp + ap)
            if final_margin is not None:
                model_winprob = normsdist(final_margin / SDM)
                ml_edge = model_winprob - home_novig

        row = dict(
            game_id=gid, matchup=f"{aa}@{ha}", away=g['awayTeam'], home=g['homeTeam'],
            kickoff_et=et(g['startDate']), kickoff_iso=g['startDate'], neutral=neutral, fcs=fcs,
            venue=venue, wind=wind, rain=rain, temp=temp,
            dk_spread=dk_spread, dk_total=dk_total, open_spread=open_spread, open_total=open_total,
            model_margin=round(model_margin, 2), market_margin=market_margin,
            edge=round(edge, 2) if edge is not None else None, agree=agree,
            side_pick=side_pick, side_prob=round(side_prob, 4) if side_prob is not None else None, side_tier=side_tier,
            model_total=epa_total, blowout_adj=round(blowout_adj, 2), option_adj=option_adj,
            total_edge=round(total_edge, 2) if total_edge is not None else None,
            total_pick=total_pick, total_prob=round(total_prob, 4) if total_prob is not None else None, total_tier=total_tier,
            home_ml=home_ml, away_ml=away_ml, ml_edge=round(ml_edge, 4) if ml_edge is not None else None,
        )
        games.append(row)

        if dk_total is not None and not fcs:
            sel.append(dict(key=row['matchup'], gid=gid, kick=g['startDate'], te=total_edge,
                             mv=(dk_total - open_total) if open_total else 0, ou=dk_total,
                             sp=dk_spread if dk_spread is not None else 0, wind=wind or 0,
                             option=option_adj != 0, model_total_adj=adj_total))
    return games, sel


def build_best_bets(sel):
    """Totals only - sides are not bet (walk-forward tuning found no side edge)."""
    picks = []
    for s in sel:
        a = abs(s['te'])
        note_opt = ' Option-team total adj applied.' if s['option'] else ''
        if a >= 9 and s['mv'] != 0 and (s['mv'] > 0) == (s['te'] > 0):
            picks.append(('2', s, f"{'Over' if s['te'] > 0 else 'Under'} {s['ou']:g}",
                          '7+ pt edge, line already moving our way. Half stake.' + note_opt))
        elif a >= 9:
            picks.append(('Pass', s, f"{'Over' if s['te'] > 0 else 'Under'} {s['ou']:g}",
                          'Edge too big: check news (injury/weather) first.' + note_opt))
        elif a >= 4:
            note = 'Totals edge in the backtested 4-7+ pt range.' + note_opt
            if s['wind'] >= 12:
                note += f" Wind {round(s['wind'])} mph."
            picks.append(('1' if abs(s['sp']) < 24 else '2', s, f"{'Over' if s['te'] > 0 else 'Under'} {s['ou']:g}", note))
    order = {'1': 0, '2': 1, 'Pass': 3}
    picks.sort(key=lambda p: (order[p[0]], p[1]['kick']))
    out = [dict(tier=t, game=s['key'], kickoff=et(s['kick']), bet=bet, type='Total',
                edge=round(s['te'], 2), note=note, bet_only_if=bet_line_for(bet, s))
           for (t, s, bet, note) in picks]

    # Top 3: largest absolute total edge first, no 4-7 pt preference. 9+ edges
    # still excluded unless the line moved toward our side (tier '2', not 'Pass').
    top = sorted((p for p in picks if p[0] != 'Pass'), key=lambda p: -abs(p[1]['te']))[:3]
    top3 = [dict(rank=i + 1, game=s['key'], kickoff=et(s['kick']), bet=bet, type='Total',
                 edge=round(s['te'], 2), bet_only_if=bet_line_for(bet, s))
            for i, (t, s, bet, note) in enumerate(top)]
    return out, top3


def build_ratings(ratings, D):
    SP = {r['team']: r['rating'] for r in D['sp']}
    out = []
    for r in sorted(ratings, key=lambda r: -(r['off'] - r['deff'])):
        out.append(dict(team=r['team'], off=round(r['off'], 3), deff=round(r['deff'], 3),
                         net=round(r['off'] - r['deff'], 3), pace=round(r['pace'], 1) if r['pace'] else None,
                         talent=r['tal'], sp=SP.get(r['team'])))
    return out


def build_qb_values(qbv):
    out = []
    for r in qbv:
        out.append(dict(team=r['team'], starter=r['starter'], backup=r['backup'],
                         value=round(r['val'], 1)))
    return sorted(out, key=lambda r: -r['value'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--season', type=int, default=2026)
    ap.add_argument('--week', type=int, default=None)
    ap.add_argument('--injuries', default=None)
    ap.add_argument('--out', default=os.path.join(os.path.dirname(__file__), '..', 'docs', 'data.json'))
    ap.add_argument('--history-dir', default=os.path.join(os.path.dirname(__file__), '..', 'data', 'history'))
    a = ap.parse_args()

    week = a.week or autoweek(a.season)
    D = E.load(a.season, week)
    games_wk, ratings, G = E.team_model(D, a.season, week)
    D['_weather'] = E.weather(D, games_wk)
    injuries = load_injuries(a.injuries)

    proj, cur = E.player_proj(D, a.season, week, games_wk)
    qbv = E.qb_values(D, a.season, cur, ratings)

    games, sel = build_games(D, games_wk, injuries)
    best_bets, top3 = build_best_bets(sel)
    rat = build_ratings(ratings, D)
    qb_vals = build_qb_values(qbv)

    payload = dict(
        meta=dict(season=a.season, week=week, generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   cfbd_calls=E.CALLS[0], games=len(games)),
        games=games, best_bets=best_bets, top3=top3, ratings=rat, qb_values=qb_vals,
    )

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, 'w') as f:
        json.dump(payload, f, indent=2)
    os.makedirs(a.history_dir, exist_ok=True)
    with open(os.path.join(a.history_dir, f'{a.season}_wk{week}.json'), 'w') as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(dict(out=a.out, season=a.season, week=week, games=len(games),
                           best_bets=len(best_bets), cfbd_calls=E.CALLS[0])))


if __name__ == '__main__':
    main()
