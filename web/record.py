"""
Grade every card this site has ever published and write docs/record.json.

Sources, kept separate on purpose:
  data/history/<season>_wk<N>.json        cards actually published live by publish.py
  data/reconstructed/<season>_wk<N>.json  cards rebuilt after the fact, for weeks
                                          that ran before the site existed

Reconstructed weeks are flagged so the page can show them apart from the live
record. A rebuilt card is not the same evidence as one that was public before
kickoff, and the page says so.

Only qualifying totals (tier 1 and 2) are graded. Sides are never bet by the
model, and LEAN picks are below the betting threshold, so neither counts.

Finals come from the public ESPN scoreboard. No API key needed.

Usage:  python web/record.py --season 2026
"""
import os, sys, json, glob, argparse, urllib.request, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import odds as O

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def espn_finals(season, week):
    url = (f'https://site.api.espn.com/apis/site/v2/sports/football/college-football/'
           f'scoreboard?dates={season}&week={week}&seasontype=2&groups=80&limit=400')
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            d = json.load(r)
    except Exception as e:
        print(f'  week {week}: ESPN fetch failed ({e})')
        return {}
    out = {}
    for e in d.get('events', []):
        c = e['competitions'][0]
        if c['status']['type']['state'] != 'post':
            continue
        cs = c['competitors']
        try:
            h = [x for x in cs if x['homeAway'] == 'home'][0]
            a = [x for x in cs if x['homeAway'] == 'away'][0]
            o = (c.get('odds') or [{}])[0]
            out[str(e['id'])] = dict(total=int(h['score']) + int(a['score']),
                                     score=f"{a['team']['location']} {a['score']} @ "
                                           f"{h['team']['location']} {h['score']}",
                                     # ESPN keeps the last DraftKings number on a
                                     # finished game: the closing total.
                                     close=o.get('overUnder'))
        except (IndexError, TypeError, ValueError):
            continue
    return out


def closing_total(gid, finals):
    """Closing total for one game: the scoreboard's, else the game summary's."""
    f = finals.get(gid) or {}
    if f.get('close') is not None:
        return f['close']
    try:
        url = ('https://site.api.espn.com/apis/site/v2/sports/football/'
               f'college-football/summary?event={gid}')
        with urllib.request.urlopen(url, timeout=30) as r:
            for p in json.load(r).get('pickcenter') or []:
                if p.get('overUnder') is not None:
                    return p['overUnder']
    except Exception:
        pass
    return None


def clv(side, bet_line, close):
    """Points of closing line value. Positive = the market moved toward the bet
    after it was made (an Over bet at 45 that closed 47 is +2)."""
    if bet_line is None or close is None:
        return None
    return round((close - bet_line) if side == 'Over' else (bet_line - close), 1)


def grade_card(card, finals, published, snaps=()):
    gid = {g['matchup']: str(g['game_id']) for g in card.get('games', [])}
    kick = {g['matchup']: g.get('kickoff_iso') for g in card.get('games', [])}
    top = {t['game']: t['rank'] for t in card.get('top3', [])}
    out = []
    for b in card.get('best_bets', []):
        if b.get('type') != 'Total' or b.get('tier') not in ('1', '2'):
            continue
        try:
            side, line = b['bet'].split()
            line = float(line)
        except ValueError:
            continue
        g_id = gid.get(b['game'], '')
        f = finals.get(g_id)
        res, total, score, close = None, None, None, None
        if f:
            total, score = f['total'], f['score']
            res = 'PUSH' if total == line else ('WIN' if (total > line) == (side == 'Over') else 'LOSS')
            close = closing_total(g_id, finals)
        fs = (card.get('first_seen') or {}).get(f"{b['game']}|{side}") or {}
        first_line = fs.get('line')
        # Pinnacle's no-vig total from the last snapshot before kickoff. The
        # sharpest close available, so CLV against it is the real test.
        nc = O.near_close(snaps, g_id, kick.get(b['game'])) if snaps else None
        pin_close = nc['pin_fair'] if nc else None
        bet_at = first_line if first_line is not None else line
        out.append(dict(week=card['meta']['week'], game=b['game'], bet=b['bet'],
                        edge=b.get('edge'), top3=top.get(b['game']), result=res,
                        actual_total=total, score=score, published=published,
                        close_total=close, clv=clv(side, line, close),
                        first_line=first_line, first_seen_at=fs.get('at'),
                        clv_first=clv(side, first_line, close),
                        pin_close=pin_close, clv_pin=clv(side, bet_at, pin_close),
                        gs_flag=bool(b.get('gs_flag')),
                        garbage_share=b.get('garbage_share')))
    return out


def tally(picks):
    w = sum(1 for p in picks if p['result'] == 'WIN')
    l = sum(1 for p in picks if p['result'] == 'LOSS')
    p_ = sum(1 for p in picks if p['result'] == 'PUSH')
    n = w + l
    # -110 units: a win returns 0.909, a loss costs 1.
    units = round(w * 0.909091 - l, 2)
    return dict(w=w, l=l, push=p_, n=n,
                pct=round(w / n * 100, 1) if n else None,
                units=units, roi=round(units / n * 100, 1) if n else None,
                # 1 SE on a coin-flip-ish rate, the honest error bar
                se=round(50 / n ** 0.5, 1) if n else None)


def clv_tally(picks, key):
    v = [p[key] for p in picks if p.get(key) is not None]
    if not v:
        return dict(n=0, avg=None, beat_pct=None, beat=0, lost=0, same=0)
    beat, lost = sum(x > 0 for x in v), sum(x < 0 for x in v)
    return dict(n=len(v), avg=round(sum(v) / len(v), 2),
                beat=beat, lost=lost, same=len(v) - beat - lost,
                beat_pct=round(beat / len(v) * 100, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--season', type=int, default=datetime.date.today().year)
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs', 'record.json'))
    a = ap.parse_args()

    cards = []
    for pat, pub in ((os.path.join(ROOT, 'data', 'history', f'{a.season}_wk*.json'), True),
                     (os.path.join(ROOT, 'data', 'reconstructed', f'{a.season}_wk*.json'), False)):
        for f in sorted(glob.glob(pat)):
            try:
                cards.append((json.load(open(f)), pub, os.path.basename(f)))
            except Exception as e:
                print(f'  skipped {os.path.basename(f)}: {e}')

    seen = set()
    picks = []
    warn = ''
    for card, pub, name in sorted(cards, key=lambda c: (c[0]['meta']['week'], not c[1])):
        wk = card['meta']['week']
        if wk in seen:                      # a live card always wins over a rebuild
            print(f'  {name}: week {wk} already graded from a published card, skipped')
            continue
        seen.add(wk)
        if not pub:
            warn = warn or card['meta'].get('reconstruction_warning', '')
        finals = espn_finals(a.season, wk)
        got = grade_card(card, finals, pub, O.load_snapshots(a.season, wk) if pub else ())
        picks += got
        print(f'  week {wk} ({"published" if pub else "reconstructed"}): {len(got)} picks, '
              f'{sum(1 for p in got if p["result"])} graded')

    # Early 5: the Monday card, graded on its own at the line it was posted at.
    early = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'early', f'{a.season}_wk*.json'))):
        try:
            card = json.load(open(f))
        except Exception as e:
            print(f'  skipped {os.path.basename(f)}: {e}')
            continue
        wk = card['meta']['week']
        finals = espn_finals(a.season, wk)
        snaps = O.load_snapshots(a.season, wk)
        gid = {g['matchup']: str(g['game_id']) for g in card.get('games', [])}
        kick = {g['matchup']: g.get('kickoff_iso') for g in card.get('games', [])}
        for pk in card['picks']:
            side, line = pk['bet'].split()
            line = float(line)
            g_id = gid.get(pk['game'], '')
            fin = finals.get(g_id)
            res = total = close = None
            if fin:
                total = fin['total']
                res = 'PUSH' if total == line else ('WIN' if (total > line) == (side == 'Over') else 'LOSS')
                close = closing_total(g_id, finals)
            nc = O.near_close(snaps, g_id, kick.get(pk['game'])) if snaps else None
            pin_close = nc['pin_fair'] if nc else None
            early.append(dict(week=wk, rank=pk['rank'], game=pk['game'], bet=pk['bet'],
                              posted_at=card['meta']['posted_at'], result=res,
                              actual_total=total, close_total=close, clv=clv(side, line, close),
                              pin_close=pin_close, clv_pin=clv(side, line, pin_close)))
    early_graded = [p for p in early if p['result']]

    graded = [p for p in picks if p['result']]
    live = [p for p in graded if p['published']]
    out = dict(
        meta=dict(season=a.season, generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  weeks=sorted(seen),
                  published_weeks=sorted({p['week'] for p in graded if p['published']}),
                  reconstructed_weeks=sorted({p['week'] for p in graded if not p['published']}),
                  break_even_pct=52.4, reconstruction_warning=warn),
        all_bets=tally(graded),
        published_only=tally(live),
        top3=tally([p for p in graded if p['top3']]),
        top3_published=tally([p for p in live if p['top3']]),
        # Standing prediction registered 2026-09-28. See PREDICTION.md.
        # The rule is NOT applied: flagged bets are still on the card. This only
        # keeps score, so the claim can be judged on games nobody has seen yet.
        prediction=dict(
            registered='2026-09-28', threshold=0.20, from_week=6,
            claim='Model Unders on teams with combined garbage-time share above '
                  '0.20 hit under 50%, against a 52.4% break-even.',
            flagged=tally([p for p in graded if p.get('gs_flag') and p['week'] >= 6]),
            unflagged=tally([p for p in graded if not p.get('gs_flag') and p['week'] >= 6])),
        # Closing line value. Grades how the market moved after the pick, which
        # settles far faster than win/loss: a bettor who keeps beating the
        # close is beating the market, whatever this month's record says.
        #   posted: vs the line on the graded card (the last pre-kickoff run)
        #   first:  vs the first line the pick ever appeared at (from week 6;
        #           the number available to someone betting it early)
        clv=dict(posted=clv_tally([p for p in graded if p['published']], 'clv'),
                 first=clv_tally([p for p in graded if p['published']], 'clv_first'),
                 top3_first=clv_tally([p for p in graded if p['published'] and p['top3']], 'clv_first'),
                 # vs Pinnacle's no-vig near-close, from the first line where known
                 pinnacle=clv_tally([p for p in graded if p['published']], 'clv_pin')),
        early5=dict(record=tally(early_graded),
                    clv=clv_tally(early_graded, 'clv'),
                    clv_pin=clv_tally(early_graded, 'clv_pin'),
                    picks=early),
        by_week=[dict(week=w,
                      published=any(p['published'] for p in graded if p['week'] == w),
                      clv=clv_tally([p for p in graded if p['week'] == w], 'clv'),
                      clv_first=clv_tally([p for p in graded if p['week'] == w], 'clv_first'),
                      **tally([p for p in graded if p['week'] == w]))
                 for w in sorted({p['week'] for p in graded})],
        picks=sorted(picks, key=lambda p: (p['week'], -abs(p['edge'] or 0))))
    with open(a.out, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nall qualifying totals : {out['all_bets']['w']}-{out['all_bets']['l']} "
          f"({out['all_bets']['pct']}% +/- {out['all_bets']['se']})  "
          f"{out['all_bets']['units']:+} units  ROI {out['all_bets']['roi']:+}%")
    print(f"published live only   : {out['published_only']['w']}-{out['published_only']['l']} "
          f"({out['published_only']['pct']}%)")
    print(f"top 3 of the week     : {out['top3']['w']}-{out['top3']['l']} ({out['top3']['pct']}%)")
    c = out['clv']['posted']
    if c['n']:
        print(f"CLV vs posted line    : avg {c['avg']:+} pts, beat the close {c['beat']}-{c['lost']}-{c['same']} ({c['beat_pct']}%)")
    c = out['clv']['pinnacle']
    if c['n']:
        print(f"CLV vs Pinnacle close : avg {c['avg']:+} pts, beat {c['beat']}-{c['lost']}-{c['same']} ({c['beat_pct']}%)")
    c = out['clv']['first']
    if c['n']:
        print(f"CLV vs first line     : avg {c['avg']:+} pts, beat the close {c['beat']}-{c['lost']}-{c['same']} ({c['beat_pct']}%)")
    e = out['early5']['record']
    if early:
        print(f"early 5               : {e['w']}-{e['l']} on {len(early)} posted picks")
    print(f"wrote {a.out}")


if __name__ == '__main__':
    main()
