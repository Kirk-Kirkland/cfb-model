"""
Render the week's Early 5 as a 1080x1920 TikTok graphic.

    python web/graphic.py --season 2026 --week 6 --out early5_wk6.png

Reads data/early/<season>_wk<N>.json (the frozen Monday card) and the CLV
record from docs/record.json. No edges are printed: the model's edge figures
imply more precision than it has (see CORRECTIONS.md, 2026-09-30). No
sportsbook names. Needs Playwright with a Chromium build.
"""
import os, sys, json, argparse, datetime, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def kick(s):
    # 'Fri 10/09 09:00 PM' -> ('FRI', '9:00 PM')
    day, _, t, ampm = s.split()
    return day.upper(), f"{int(t.split(':')[0])}:{t.split(':')[1]} {ampm}"


def build(season, week):
    card = json.load(open(os.path.join(ROOT, 'data', 'early', f'{season}_wk{week}.json')))
    names = {g['matchup']: (g['away'], g['home']) for g in card['games']}
    posted = datetime.datetime.fromisoformat(card['meta']['posted_at']) - datetime.timedelta(hours=4)
    posted_s = posted.strftime('%a %-m/%-d').upper() + ' · ' + posted.strftime('%-I:%M %p') + ' ET'

    clv_line = ''
    try:
        rec = json.load(open(os.path.join(ROOT, 'docs', 'record.json')))
        c = rec['clv']['posted']
        if c['n'] and (c['beat'] + c['lost']):
            clv_line = (f"Our picks beat the closing line <b>{c['beat']} of {c['beat'] + c['lost']}</b> "
                        f"times it moved")
    except Exception:
        pass

    rows = []
    for p in card['picks']:
        side, line = p['bet'].split()
        away, home = names.get(p['game'], p['game'].split('@'))
        day, t = kick(p['kickoff'])
        cut = p['bet_only_if'].replace('at or below', 'Play to').replace('at or above', 'Play to')
        if cut.endswith('.0'):
            cut = cut[:-2]
        rows.append(f"""
        <div class="pick">
          <div class="rank">{p['rank']}</div>
          <div class="body">
            <div class="teams">{html.escape(away)} <span>@</span> {html.escape(home)}</div>
            <div class="when">{day} {t} ET</div>
          </div>
          <div class="bet {side.lower()}">
            <div class="side">{side.upper()}</div>
            <div class="num">{line}</div>
            <div class="cut">{cut}</div>
          </div>
        </div>""")

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ width:1080px; height:1920px; overflow:hidden; font-family:'Inter',sans-serif; color:#f4f6fb;
      background:
        radial-gradient(1200px 700px at 50% -8%, rgba(56,189,248,.28), transparent 60%),
        radial-gradient(900px 600px at 110% 105%, rgba(250,204,21,.16), transparent 60%),
        repeating-linear-gradient(90deg, rgba(255,255,255,.035) 0 2px, transparent 2px 108px),
        linear-gradient(180deg,#07101f 0%,#0a1428 55%,#060b16 100%); }}
    .wrap {{ padding:165px 150px 0 50px; text-align:left; }}
    .brand {{ font-family:'Inter Display'; font-weight:800; letter-spacing:.28em; font-size:25px; color:#7dd3fc; }}
    h1 {{ font-family:'Inter Display'; font-weight:900; font-size:122px; line-height:.92; letter-spacing:-.02em; margin-top:10px;
      background:linear-gradient(180deg,#ffffff 0%,#cfe8ff 100%); -webkit-background-clip:text; color:transparent; }}
    h1 em {{ font-style:normal; color:#facc15; -webkit-text-fill-color:#facc15; }}
    .meta {{ display:flex; justify-content:space-between; margin-top:14px; font-size:29px; font-weight:600; color:#dbe4f3; }}
    .meta b {{ color:#fff; }}
    .stamp {{ display:inline-block; margin-top:14px; padding:9px 18px; border:2px solid rgba(125,211,252,.55); border-radius:999px;
      font-size:23px; font-weight:700; letter-spacing:.06em; color:#e0f2fe; }}
    .list {{ margin-top:20px; display:flex; flex-direction:column; gap:12px; }}
    .pick {{ display:flex; align-items:center; gap:16px; padding:15px 18px; border-radius:18px;
      background:linear-gradient(135deg,rgba(255,255,255,.085),rgba(255,255,255,.03));
      border:1.5px solid rgba(255,255,255,.12); box-shadow:0 10px 40px rgba(0,0,0,.35); }}
    .rank {{ font-family:'Inter Display'; font-weight:900; font-size:56px; width:42px; text-align:left; color:#facc15; }}
    .body {{ flex:1; min-width:0; }}
    .teams {{ font-weight:800; font-size:33px; line-height:1.15; color:#ffffff; }}
    .teams span {{ color:#b6c3d9; font-weight:600; }}
    .when {{ margin-top:7px; font-size:24px; font-weight:700; color:#d3dceb; letter-spacing:.04em; }}
    .bet {{ width:196px; text-align:center; padding:8px 0 10px; border-radius:16px; }}
    .bet.over {{ background:rgba(34,197,94,.14); border:2px solid rgba(74,222,128,.7); }}
    .bet.under {{ background:rgba(56,189,248,.14); border:2px solid rgba(125,211,252,.75); }}
    .side {{ font-weight:800; font-size:22px; letter-spacing:.14em; }}
    .over .side {{ color:#86efac; }} .under .side {{ color:#7dd3fc; }}
    .num {{ font-family:'Inter Display'; font-weight:900; font-size:56px; line-height:1; margin-top:2px; }}
    .cut {{ margin-top:5px; font-size:20px; font-weight:700; color:#eef2f8; }}
    .proof {{ margin-top:18px; padding:14px 18px; border-radius:16px; background:rgba(250,204,21,.09);
      border:1.5px solid rgba(250,204,21,.45); font-size:25px; line-height:1.35; color:#fde68a; }}
    .proof b {{ color:#fff; }}
    .how {{ margin-top:12px; font-size:22px; line-height:1.4; color:#d3dceb; }}
    .foot {{ margin-top:8px; font-size:18px; color:#a9b6cc; line-height:1.4; }}
    </style></head><body><div class="wrap">
      <div class="brand">VEGAS GONZO PICKS</div>
      <h1>EARLY <em>5</em></h1>
      <div class="meta"><span>College football totals &middot; <b>Week {week}</b></span></div>
      <div class="stamp">POSTED {posted_s}</div>
      <div class="list">{''.join(rows)}</div>
      {f'<div class="proof">{clv_line}. The early number is where the value is.</div>' if clv_line else ''}
      <div class="how">Lines move. If yours is past the "play to" number, pass. Graded publicly, wins and losses both.</div>
      <div class="foot">Model picks for entertainment only. 21+. Gambling problem? Call 1-800-GAMBLER.</div>
    </div>
    </body></html>"""


def build_check(season, week, blurb):
    """Midweek line check on the Early 5: posted number vs now, CLV per pick,
    plus a short blurb on what moved the market. Lines from the latest odds
    snapshot (data/odds), so it is only as fresh as that pull."""
    import odds as O
    base = build(season, week)
    style = base.split('<style>')[1].split('</style>')[0]
    card = json.load(open(os.path.join(ROOT, 'data', 'early', f'{season}_wk{week}.json')))
    snap = O.load_snapshots(season, week)[-1]
    asof = datetime.datetime.fromisoformat(snap['at']) - datetime.timedelta(hours=4)
    names = {g['matchup']: (g['away'], g['home']) for g in card['games']}
    gid = {g['matchup']: str(g['game_id']) for g in card['games']}
    rows, moves = [], []
    for p in card['picks']:
        side, line = p['bet'].split()
        line = float(line)
        now = (snap['games'].get(gid[p['game']]) or {}).get('dk')
        clv = None if now is None else ((now - line) if side == 'Over' else (line - now))
        moves.append(clv)
        cls = 'neutral' if not clv else ('good' if clv > 0 else 'bad')
        tag = 'HOLDING' if not clv else (f"+{clv:g} OUR WAY" if clv > 0 else f"{clv:g} AGAINST")
        away, home = names[p['game']]
        day, t = kick(p['kickoff'])
        rows.append(f"""
        <div class="pick">
          <div class="rank">{p['rank']}</div>
          <div class="body">
            <div class="teams">{html.escape(away)} <span>@</span> {html.escape(home)}</div>
            <div class="when">{side.upper()} {line:g} &middot; {day} {t}</div>
          </div>
          <div class="chk {cls}">
            <div class="lbl">NOW</div>
            <div class="num">{'' if now is None else f'{now:g}'}</div>
            <div class="tag">{tag}</div>
          </div>
        </div>""")
    good = sum(1 for m in moves if m and m > 0)
    bad = sum(1 for m in moves if m and m < 0)
    flat = len(moves) - good - bad
    extra = """
    .chk {{ width:196px; text-align:center; padding:8px 0 10px; border-radius:16px; }}
    .chk.good {{ background:rgba(34,197,94,.16); border:2px solid rgba(74,222,128,.8); }}
    .chk.bad {{ background:rgba(239,68,68,.14); border:2px solid rgba(248,113,113,.75); }}
    .chk.neutral {{ background:rgba(255,255,255,.06); border:2px solid rgba(255,255,255,.25); }}
    .lbl {{ font-weight:800; font-size:19px; letter-spacing:.18em; color:#eef2f8; }}
    .tag {{ margin-top:5px; font-size:19px; font-weight:800; letter-spacing:.04em; }}
    .good .tag {{ color:#86efac; }} .bad .tag {{ color:#fca5a5; }} .neutral .tag {{ color:#eef2f8; }}
    .blurb {{ margin-top:18px; padding:14px 18px; border-radius:16px; background:rgba(56,189,248,.10);
      border:1.5px solid rgba(125,211,252,.45); font-size:24px; line-height:1.38; color:#f0f9ff; }}
    .blurb b {{ color:#fff; }}
    .score {{ margin-top:14px; font-size:27px; font-weight:800; color:#fde68a; }}
    """.replace('{{', '{').replace('}}', '}')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{style}{extra}</style></head><body><div class="wrap">
      <div class="brand">VEGAS GONZO PICKS</div>
      <h1>LINE <em>CHECK</em></h1>
      <div class="meta"><span>Early 5 &middot; <b>Week {week}</b> &middot; posted Monday</span></div>
      <div class="stamp">LINES AS OF {asof.strftime('%a %-m/%-d').upper()} &middot; {asof.strftime('%-I:%M %p')} ET</div>
      <div class="blurb">{blurb}</div>
      <div class="list">{''.join(rows)}</div>
      <div class="score">{good} moved our way &middot; {bad} against &middot; {flat} holding</div>
      <div class="how">Beat the closing number and you are finding value, win or lose.</div>
      <div class="foot">Model picks for entertainment only. 21+. Gambling problem? Call 1-800-GAMBLER.</div>
    </div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--season', type=int, default=2026)
    ap.add_argument('--week', type=int, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--check', action='store_true', help='midweek line check instead of the Early 5 card')
    ap.add_argument('--blurb', default='', help='short HTML blurb for the line check')
    a = ap.parse_args()
    page = build_check(a.season, a.week, a.blurb) if a.check else build(a.season, a.week)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport=dict(width=1080, height=1920))
        pg.set_content(page)
        pg.wait_for_timeout(300)
        pg.screenshot(path=a.out, full_page=False)
        b.close()
    print(a.out)


if __name__ == '__main__':
    main()
