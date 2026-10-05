"""
Render the week's Early 5 as a 1080x1920 TikTok graphic.

    python web/graphic.py --season 2026 --week 6 --out early5_wk6.png

Reads data/early/<season>_wk<N>.json (the frozen Monday card) and the CLV
record from docs/record.json. No edges are printed: the model's edge figures
imply more precision than it has (see CORRECTIONS.md, 2026-09-30). No
sportsbook names. Needs Playwright with a Chromium build.
"""
import os, json, argparse, datetime, html

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
    .wrap {{ padding:84px 64px 0; }}
    .brand {{ font-family:'Inter Display'; font-weight:800; letter-spacing:.32em; font-size:28px; color:#7dd3fc; }}
    h1 {{ font-family:'Inter Display'; font-weight:900; font-size:150px; line-height:.92; letter-spacing:-.02em; margin-top:18px;
      background:linear-gradient(180deg,#ffffff 0%,#cfe8ff 100%); -webkit-background-clip:text; color:transparent; }}
    h1 em {{ font-style:normal; color:#facc15; -webkit-text-fill-color:#facc15; }}
    .meta {{ display:flex; justify-content:space-between; margin-top:26px; font-size:30px; font-weight:600; color:#a9b8d4; }}
    .meta b {{ color:#fff; }}
    .stamp {{ display:inline-block; margin-top:22px; padding:12px 22px; border:2px solid rgba(125,211,252,.55); border-radius:999px;
      font-size:26px; font-weight:700; letter-spacing:.08em; color:#bae6fd; }}
    .list {{ margin-top:36px; display:flex; flex-direction:column; gap:16px; }}
    .pick {{ display:flex; align-items:center; gap:28px; padding:20px 26px; border-radius:24px;
      background:linear-gradient(135deg,rgba(255,255,255,.085),rgba(255,255,255,.03));
      border:1.5px solid rgba(255,255,255,.12); box-shadow:0 10px 40px rgba(0,0,0,.35); }}
    .rank {{ font-family:'Inter Display'; font-weight:900; font-size:66px; width:60px; text-align:center; color:#facc15; }}
    .body {{ flex:1; min-width:0; }}
    .teams {{ font-weight:800; font-size:35px; line-height:1.15; }}
    .teams span {{ color:#7d8aa5; font-weight:600; }}
    .when {{ margin-top:10px; font-size:26px; font-weight:600; color:#93a3c0; letter-spacing:.04em; }}
    .bet {{ width:220px; text-align:center; padding:10px 0 12px; border-radius:20px; }}
    .bet.over {{ background:rgba(34,197,94,.14); border:2px solid rgba(74,222,128,.7); }}
    .bet.under {{ background:rgba(56,189,248,.14); border:2px solid rgba(125,211,252,.75); }}
    .side {{ font-weight:800; font-size:26px; letter-spacing:.18em; }}
    .over .side {{ color:#86efac; }} .under .side {{ color:#7dd3fc; }}
    .num {{ font-family:'Inter Display'; font-weight:900; font-size:64px; line-height:1; margin-top:2px; }}
    .cut {{ margin-top:8px; font-size:22px; font-weight:600; color:#c7d2e6; }}
    .proof {{ margin-top:28px; padding:20px 26px; border-radius:22px; background:rgba(250,204,21,.09);
      border:1.5px solid rgba(250,204,21,.45); font-size:28px; line-height:1.35; color:#fde68a; }}
    .proof b {{ color:#fff; }}
    .how {{ margin-top:18px; font-size:25px; line-height:1.4; color:#93a3c0; }}
    .foot {{ margin-top:18px; font-size:22px; color:#6f7d98; line-height:1.45; }}
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--season', type=int, default=2026)
    ap.add_argument('--week', type=int, required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    page = build(a.season, a.week)
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
