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
    total_bet=4, total_lean=3, total_bigedge=10,
    big_spread=24, wind_thresh=12, wind_pen=0.3,
    blow=E.CONSTS['C_SPREAD'], opta=E.CONSTS['OPT_ADJ'], opt_teams=set(E.CONSTS['OPT_TEAMS']),
    top_n=3,
)

# Estimated hit rate. ONE number for every qualifying bet, on purpose.
# The old per-edge buckets [(4,.528),(5,.532),(6,.520),(8,.550),(10,.630)] were removed
# 2026-09-26: they did not reproduce on a clean rebuild (the 10+ bucket came back at
# 53.7%, 8-10 at 49.3%). Each bucket held 95-274 bets against a 3-5 pt margin of error,
# so the differences were always inside the noise. Edge SIZE does not rank bets.
# 0.53 is the midpoint of three independent rebuilds: 52.9%, 53.2%, 53.6-54.1%.
# Break-even at -110 is 52.4%.
EST_HIT_RATE = 0.53


def confidence_for(edge):
    return EST_HIT_RATE if abs(edge) >= 4 else None


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
    """The lowest week that still has a game left to play.

    Do NOT use CFBD's calendar windows for this. They are contiguous blocks that
    run Monday to Monday, so week N's window stays 'current' all the way through
    Sunday night, long after week N's last game has ended. A Sunday run would
    republish the week that just finished instead of building the week ahead.
    That is exactly what happened on 2026-09-27: the noon run rebuilt week 4
    while week 5's opening totals were already posted.

    Asking the games feed instead is unambiguous. A week is finished when every
    one of its games has a final score; the week to build is the first one that
    is not."""
    games = E.cfbd('games', year=season, seasonType='regular')
    now = datetime.datetime.now(datetime.timezone.utc)
    weeks = {}
    for g in games:
        if g.get('week') is None:
            continue
        done = g.get('homePoints') is not None and g.get('awayPoints') is not None
        started = False
        if g.get('startDate'):
            try:
                started = datetime.datetime.fromisoformat(
                    g['startDate'].replace('Z', '+00:00')) <= now
            except ValueError:
                pass
        w = weeks.setdefault(g['week'], dict(total=0, settled=0))
        w['total'] += 1
        # "settled" means it can no longer be bet: final, or already kicked off
        w['settled'] += 1 if (done or started) else 0
    for wk in sorted(weeks):
        if weeks[wk]['settled'] < weeks[wk]['total']:
            return wk
    return max(weeks) if weeks else 1


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
    TBE, TLE, TCN = D_IN['total_bet'], D_IN['total_lean'], D_IN['total_bigedge']
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
            # No check-news pass either: 10+ edges hit 63% in walk-forward testing,
            # so they're a BET (with a nudge to glance at news first), not a pass.
            if fcs:
                total_tier = 'No bet: FCS'
            elif sum(1 for t in (g['homeTeam'], g['awayTeam'])
                     if t in E.CONSTS['OPT_TEAMS']) == 2:
                # Added 2026-09-30 after a reader challenged the Navy/Air Force pick.
                #
                # The model measures pace in PLAYS per game. Option offenses run long
                # clock-draining drives, so they post high play counts while producing
                # very few possessions. The model had Navy at 61.7 and Air Force at
                # 68.5 plays against a 59.7 FBS average, and read that as scoring.
                #
                # When only one team runs it the opponent still plays normally and the
                # existing -3.4 adjustment roughly covers it. When BOTH run it, both
                # sides of the game collapse and the adjustment (an OR, applied once)
                # does not come close. Walk-forward 2023-25: the model ran 15.3 points
                # high on these, too high in five of six.
                #
                # Every service academy head-to-head since 2021 (n=15) averaged 32.7
                # points, median 30. Exactly one cleared 45.5.
                #
                # Fifteen games is not enough to fit a new constant on, and fitting
                # one is how the per-edge confidence tiers got built and then
                # collapsed. So these are simply not bet until the pace term is
                # rebuilt on possessions instead of plays.
                total_tier = 'No bet: two option teams'
            elif abs(total_edge) >= TCN:
                total_tier = 'BET (check news)'
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

        # `sel` feeds the Best Bets card. Anything tiered "No bet: ..." must not
        # reach it, or the game drops off the All Games table and still shows up
        # as a pick. That is exactly what happened to Navy/Air Force on
        # 2026-09-30: the tier was set correctly and the pick was published
        # anyway. See CORRECTIONS.md.
        if dk_total is not None and not str(total_tier).startswith('No bet'):
            sel.append(dict(key=row['matchup'], gid=gid, kick=g['startDate'], te=total_edge,
                             ou=dk_total, sp=dk_spread if dk_spread is not None else 0, wind=wind or 0,
                             option=option_adj != 0, model_total_adj=adj_total))
    return games, sel


def build_best_bets(sel):
    """Totals only - sides are not bet (walk-forward tuning found no side edge).
    No check-news pass: 10+ pt edges hit 63% in walk-forward testing and are a
    BET (with a nudge to glance at news first), not a pass - the old pass rule
    cost 7 points of win rate."""
    picks = []
    for s in sel:
        a = abs(s['te'])
        note_opt = ' Option-team total adj applied.' if s['option'] else ''
        if a >= D_IN['total_bigedge']:
            picks.append(('1', s, f"{'Over' if s['te'] > 0 else 'Under'} {s['ou']:g}",
                          '10+ pt edge: strongest bucket in walk-forward testing (63%). Glance at injury and weather news, then bet.' + note_opt))
        elif a >= D_IN['total_bet']:
            note = 'Totals edge 4+ pts.' + note_opt
            if s['wind'] >= 12:
                note += f" Wind {round(s['wind'])} mph."
            picks.append(('1' if abs(s['sp']) < 24 else '2', s, f"{'Over' if s['te'] > 0 else 'Under'} {s['ou']:g}", note))
    order = {'1': 0, '2': 1}
    picks.sort(key=lambda p: (order[p[0]], p[1]['kick']))
    out = [dict(tier=t, game=s['key'], kickoff=et(s['kick']), bet=bet, type='Total',
                edge=round(s['te'], 2), confidence=confidence_for(s['te']), note=note,
                bet_only_if=bet_line_for(bet, s))
           for (t, s, bet, note) in picks]

    # Top N (default 3): largest absolute total edge first, no 4-7 pt preference.
    top = sorted(picks, key=lambda p: -abs(p[1]['te']))[:D_IN['top_n']]
    top3 = [dict(rank=i + 1, game=s['key'], kickoff=et(s['kick']), bet=bet, type='Total',
                 edge=round(s['te'], 2), confidence=confidence_for(s['te']), bet_only_if=bet_line_for(bet, s))
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


def garbage_shares(season, week):
    """Fraction of each team's offensive plays that the garbage-time filter drops,
    from that team's games BEFORE `week` only.

    Why this exists: see PREDICTION.md. The filter is right for rating a team but
    the market still prices the late scoring, so the model drifts to Unders on
    teams it strips heavily. This measures how heavily.

    One extra CFBD call. Returns {team: share} plus the league median as a
    fallback for teams with too few games.
    """
    try:
        incl = E.cfbd('stats/game/advanced', year=season, excludeGarbageTime='false')
        excl = E.cfbd('stats/game/advanced', year=season, excludeGarbageTime='true')
    except Exception as e:
        print(f'  garbage shares unavailable ({e}); rule not applied', file=sys.stderr)
        return {}, None
    ep = {(s['gameId'], s['team']): s['offense'].get('plays')
          for s in excl if s.get('week') is not None and s['week'] < week}
    acc = {}
    for s in incl:
        if s.get('week') is None or s['week'] >= week:
            continue
        pi = s['offense'].get('plays')
        pe = ep.get((s['gameId'], s['team']))
        if not pi or pe is None:
            continue
        acc.setdefault(s['team'], []).append(max(0.0, 1.0 - pe / pi))
    out = {t: sum(v) / len(v) for t, v in acc.items() if len(v) >= 2}
    med = sorted(out.values())[len(out) // 2] if out else None
    return out, med


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

    # Dated prediction, not a live filter. See PREDICTION.md. Games are flagged
    # and graded separately; nothing is removed from the card.
    GS_THRESHOLD = 0.20
    shares, med = garbage_shares(a.season, week)
    flagged = 0
    for g in games:
        hs = shares.get(g['home'], med)
        as_ = shares.get(g['away'], med)
        g['garbage_share'] = round(hs + as_, 4) if (hs is not None and as_ is not None) else None
        g['gs_flag'] = bool(
            g['garbage_share'] is not None
            and g['garbage_share'] > GS_THRESHOLD
            and (g.get('total_pick') or '').startswith('Under')
            and g.get('total_tier') in ('BET', 'LEAN'))
        flagged += g['gs_flag']
    for b in best_bets + top3:
        m = next((g for g in games if g['matchup'] == b['game']), None)
        if m:
            b['garbage_share'] = m['garbage_share']
            b['gs_flag'] = m['gs_flag']
    print(f'  garbage-share rule: {flagged} game(s) flagged at threshold {GS_THRESHOLD}',
          file=sys.stderr)

    rat = build_ratings(ratings, D)
    qb_vals = build_qb_values(qbv)

    payload = dict(
        meta=dict(season=a.season, week=week, generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   cfbd_calls=E.CALLS[0], games=len(games),
                   gs_threshold=GS_THRESHOLD, gs_flagged=flagged),
        games=games, best_bets=best_bets, top3=top3, ratings=rat, qb_values=qb_vals,
    )

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    os.makedirs(a.history_dir, exist_ok=True)
    # The history file is the track record. Once a game in a saved card has
    # kicked off, that card is what the public saw and it is never rewritten.
    # On 2026-09-27 a Sunday run rebuilt week 4 after every game was final and
    # replaced a real 17-pick 8-9 card with a 20-pick 10-10 one. Guard against
    # that regardless of how the run was triggered.
    hpath = os.path.join(a.history_dir, f'{a.season}_wk{week}.json')
    locked = False
    if os.path.exists(hpath):
        try:
            prior = json.load(open(hpath))
            now = datetime.datetime.now(datetime.timezone.utc)
            for g in prior.get('games', []):
                if not g.get('kickoff_iso'):
                    continue
                try:
                    if datetime.datetime.fromisoformat(
                            g['kickoff_iso'].replace('Z', '+00:00')) <= now:
                        locked = True
                        break
                except ValueError:
                    continue
        except Exception:
            locked = False
    if locked:
        # The site must show the same card that is being graded. Before
        # 2026-10-03 this branch protected only the history file and still
        # wrote the fresh rebuild to docs/data.json, so after the first kickoff
        # the live site showed a different Top 3 than the published, graded
        # card (week 5: the Saturday run showed WMU/BUFF, BGSU/M-OH, MIA/CLEM
        # instead of UVA/FSU, PSU/NU, MTSU/KU). Publish the locked card instead.
        print(f'  history for week {week} is locked (a game has kicked off); '
              f'keeping the card that was published and showing it on the site',
              file=sys.stderr)
        live = dict(prior)
        live['meta'] = dict(prior.get('meta', {}), locked=True,
                            checked_at=payload['meta']['generated_at'])
        with open(a.out, 'w') as f:
            json.dump(live, f, indent=2)
    else:
        with open(a.out, 'w') as f:
            json.dump(payload, f, indent=2)
        with open(hpath, 'w') as f:
            json.dump(payload, f, indent=2)
    print(json.dumps(dict(out=a.out, season=a.season, week=week, games=len(games),
                           best_bets=len(best_bets), cfbd_calls=E.CALLS[0])))


if __name__ == '__main__':
    main()
