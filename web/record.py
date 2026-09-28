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
import os, json, glob, argparse, urllib.request, datetime

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
            out[str(e['id'])] = dict(total=int(h['score']) + int(a['score']),
                                     score=f"{a['team']['location']} {a['score']} @ "
                                           f"{h['team']['location']} {h['score']}")
        except (IndexError, TypeError, ValueError):
            continue
    return out


def grade_card(card, finals, published):
    gid = {g['matchup']: str(g['game_id']) for g in card.get('games', [])}
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
        f = finals.get(gid.get(b['game'], ''))
        res, total, score = None, None, None
        if f:
            total, score = f['total'], f['score']
            res = 'PUSH' if total == line else ('WIN' if (total > line) == (side == 'Over') else 'LOSS')
        out.append(dict(week=card['meta']['week'], game=b['game'], bet=b['bet'],
                        edge=b.get('edge'), top3=top.get(b['game']), result=res,
                        actual_total=total, score=score, published=published,
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
        got = grade_card(card, finals, pub)
        picks += got
        print(f'  week {wk} ({"published" if pub else "reconstructed"}): {len(got)} picks, '
              f'{sum(1 for p in got if p["result"])} graded')

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
        by_week=[dict(week=w,
                      published=any(p['published'] for p in graded if p['week'] == w),
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
    print(f"wrote {a.out}")


if __name__ == '__main__':
    main()
