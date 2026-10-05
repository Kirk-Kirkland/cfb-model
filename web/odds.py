"""
Multi-book totals from The Odds API (https://the-odds-api.com).

Why: DraftKings alone can't tell us whether an early number is a miss or the
right price. Pinnacle is the sharpest book in the market; when DraftKings
disagrees with Pinnacle, DraftKings usually moves toward it. So for every game
we keep Pinnacle's no-vig ("fair") total alongside the DraftKings number, and
we snapshot both through the week so CLV can be graded against Pinnacle's
close, the standard way to tell whether bets beat the market.

Cost: one call = regions x markets credits. We pull regions=us,eu (Pinnacle is
in eu) and markets=totals, so 2 credits per call. The free plan is 500/month.

Key: env ODDS_API_KEY. With no key everything here is a no-op, and the model
runs exactly as it did before.

Snapshot CLI (used by .github/workflows/odds.yml):
    python web/odds.py snapshot --season 2026
appends one line per call to data/odds/<season>_wk<N>.jsonl
"""
import os, sys, json, math, datetime, difflib, unicodedata, urllib.request, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = ('https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds'
       '?apiKey={key}&regions=us,eu&markets=totals&oddsFormat=american')
# Probability per point of total near the median, from the model's total SD
# (15.64): pdf(0) = 1/(15.64*sqrt(2*pi)) = 0.0255. Used to turn Pinnacle's
# juice into a fair number: Over 44 at -103 / Under -117 is really ~43.4.
PROB_PER_PT = 0.0255
US_BOOKS = ('draftkings', 'fanduel', 'betmgm', 'caesars', 'williamhill_us', 'betrivers', 'bovada')


def key():
    return os.environ.get('ODDS_API_KEY', '').strip()


def fetch():
    k = key()
    if not k:
        return None, None
    try:
        with urllib.request.urlopen(URL.format(key=k), timeout=30) as r:
            remaining = r.headers.get('x-requests-remaining')
            return json.load(r), remaining
    except Exception as e:
        print(f'  odds api: fetch failed ({e})', file=sys.stderr)
        return None, None


def implied(price):
    return -price / (-price + 100) if price < 0 else 100 / (price + 100)


def fair_total(point, over_price, under_price):
    """No-vig total: shift the posted number by how far the juice leans."""
    po, pu = implied(over_price), implied(under_price)
    p_over = po / (po + pu)
    return round(point + (p_over - 0.5) / PROB_PER_PT, 2)


def book_totals(ev):
    out = {}
    for b in ev.get('bookmakers', []):
        for m in b.get('markets', []):
            if m.get('key') != 'totals':
                continue
            o = {x['name']: x for x in m.get('outcomes', [])}
            if 'Over' in o and 'Under' in o and o['Over'].get('point') is not None:
                out[b['key']] = dict(point=o['Over']['point'], over=o['Over']['price'],
                                     under=o['Under']['price'])
    return out


def summarize(ev):
    bt = book_totals(ev)
    pin = bt.get('pinnacle')
    us = {k: v for k, v in bt.items() if k in US_BOOKS}
    s = dict(odds_id=ev['id'], commence=ev['commence_time'],
             dk=(bt.get('draftkings') or {}).get('point'),
             pin=pin['point'] if pin else None,
             pin_fair=fair_total(pin['point'], pin['over'], pin['under']) if pin else None,
             # Best number available at a US book for each side
             us_low=min((v['point'] for v in us.values()), default=None),
             us_high=max((v['point'] for v in us.values()), default=None),
             books=len(bt))
    return s


def _norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return s.replace("'", '').replace('.', '').replace('&', 'and')


# CFBD name -> how The Odds API spells the school. Only where they differ
# enough that fuzzy matching can't bridge it.
ALIASES = {'App State': 'Appalachian State', 'Massachusetts': 'UMass',
           'UL Monroe': 'Louisiana Monroe', 'Southern Miss': 'Southern Mississippi',
           'Sam Houston': 'Sam Houston State', "Hawai'i": 'Hawaii', 'San José State': 'San Jose State'}


def _sim(cfbd_name, odds_name):
    a, b = _norm(ALIASES.get(cfbd_name, cfbd_name)), _norm(odds_name)
    if b.startswith(a + ' ') or a == b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b[:len(a) + 4]).ratio()


def match(events, games):
    """Map CFBD game_id -> odds event. Kickoff within 4h, then best name match
    on both teams. Ambiguous or weak matches are dropped, not guessed."""
    out = {}
    for g in games:
        try:
            gk = datetime.datetime.fromisoformat(g['kickoff_iso'].replace('Z', '+00:00'))
        except (KeyError, ValueError, AttributeError):
            continue
        best, score = None, 0.0
        for ev in events:
            ek = datetime.datetime.fromisoformat(ev['commence_time'].replace('Z', '+00:00'))
            if abs((ek - gk).total_seconds()) > 4 * 3600:
                continue
            sc = min(_sim(g['home'], ev['home_team']), _sim(g['away'], ev['away_team']))
            sc_flip = min(_sim(g['home'], ev['away_team']), _sim(g['away'], ev['home_team']))
            sc = max(sc, sc_flip)
            if sc > score:
                best, score = ev, sc
        if best is not None and score >= 0.75:
            out[g['game_id']] = best
    return out


def market_read(pick_side, dk_total, pin_fair):
    """Does the sharp number agree with the model's side against DraftKings?
    Over at 43.5 with Pinnacle fair 44.6 -> DK is low, sharp money agrees."""
    if dk_total is None or pin_fair is None or not pick_side:
        return None
    gap = round(pin_fair - dk_total, 2)
    lean = gap if pick_side == 'Over' else -gap
    return dict(gap=gap, sharp_agrees=lean >= 0.5, sharp_disagrees=lean <= -0.5)


def snapshot(season, week, games, events=None, remaining=None):
    """Append one snapshot for the week's games to data/odds/<season>_wk<N>.jsonl.
    Pass events already fetched to avoid spending credits twice. Returns
    {game_id: summary} for the games matched, or None with no key."""
    if events is None:
        events, remaining = fetch()
    if events is None:
        print('  odds snapshot skipped (no key or fetch failed)', file=sys.stderr)
        return None
    m = match(events, games)
    rows = {str(gid): summarize(ev) for gid, ev in m.items()}
    rec = dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               remaining=remaining, games=rows)
    d = os.path.join(ROOT, 'data', 'odds')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f'{season}_wk{week}.jsonl'), 'a') as f:
        f.write(json.dumps(rec, separators=(',', ':')) + '\n')
    print(f'  odds snapshot: {len(rows)}/{len(games)} games matched, '
          f'{remaining} credits left', file=sys.stderr)
    return rows


def load_snapshots(season, week):
    p = os.path.join(ROOT, 'data', 'odds', f'{season}_wk{week}.jsonl')
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p):
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def near_close(snaps, game_id, kickoff_iso):
    """Last snapshot of this game taken before kickoff: Pinnacle's near-close."""
    try:
        k = datetime.datetime.fromisoformat(kickoff_iso.replace('Z', '+00:00'))
    except (AttributeError, ValueError):
        return None
    best = None
    for s in snaps:
        g = s['games'].get(str(game_id))
        if not g or g.get('pin_fair') is None:
            continue
        at = datetime.datetime.fromisoformat(s['at'])
        if at <= k:
            best = dict(g, at=s['at'])
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['snapshot'])
    ap.add_argument('--season', type=int, default=datetime.date.today().year)
    a = ap.parse_args()
    # Use the current card for the week and its games; no CFBD calls needed.
    card = json.load(open(os.path.join(ROOT, 'docs', 'data.json')))
    if card['meta']['season'] != a.season:
        print('  card is for another season; skipping', file=sys.stderr)
        return
    snapshot(a.season, card['meta']['week'], card['games'])


if __name__ == '__main__':
    main()
