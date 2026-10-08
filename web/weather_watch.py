"""
Weather watch: forecast wind, gusts and rain at kickoff for every outdoor game
this week, plus any active tropical system from the National Hurricane Center.

Why (data/studies/weather.json, 2021-25, 3,558 games):
  - At the CLOSE the market prices weather: windy and wet games go Under the
    closing total about as often as calm ones (49-53%). No edge there.
  - From OPEN to CLOSE it does not happen at once. Totals fell 1.4 points on
    average in 15-20 mph wind, 1.7 at 20+, 2.7 when wind 15+ met rain. Unders
    at the OPENING number hit 58.8% (n=192) at 15-20 mph and 80% (n=29) in
    wind-plus-rain. That gap is the anticipation edge: see the storm coming
    before the number moves.
  - Upper bound only: those games are graded on observed weather, and a
    forecast on Monday is not that. So this is a watch list, not a bet rule.

Free sources, no key: Open-Meteo forecast, NHC CurrentStorms.json.
Needs CFBD_API_KEY only to look up venue coordinates (2 calls).
"""
import os, sys, json, math, datetime, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NHC = 'https://www.nhc.noaa.gov/CurrentStorms.json'
METEO = ('https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
         '&hourly=wind_speed_10m,wind_gusts_10m,precipitation_probability,precipitation'
         '&wind_speed_unit=mph&precipitation_unit=inch&timezone=UTC&start_date={d}&end_date={d}')


def getj(url, tries=3):
    import time
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            err = e
            time.sleep(2 * (i + 1))
    print(f'  weather watch: {url[:60]}... failed ({err})', file=sys.stderr)
    return None


def miles(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3959 * 2 * math.asin(math.sqrt(h))


def storms():
    j = getj(NHC) or {}
    out = []
    for s in j.get('activeStorms', []):
        try:
            out.append(dict(name=s.get('name'), kind=s.get('classification'),
                            intensity=s.get('intensity'),
                            pos=(float(s['latitudeNumeric']), float(s['longitudeNumeric']))))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def venues(season, week):
    """game_id -> (lat, lon) for outdoor venues, via CFBD."""
    if not os.environ.get('CFBD_API_KEY'):
        return {}
    import cfb_engine as E
    games = E.cfbd('games', year=season, week=week, seasonType='regular')
    V = {v['id']: v for v in E.cfbd('venues')}
    out = {}
    for g in games:
        v = V.get(g.get('venueId'))
        if v and v.get('latitude') is not None and not v.get('dome'):
            out[str(g['id'])] = (v['latitude'], v['longitude'])
    return out


def risk(w):
    """Storm risk: the conditions where totals fell most open-to-close."""
    if not w:
        return None
    if (w.get('gust') or 0) >= 35 or ((w.get('wind') or 0) >= 15 and (w.get('pop') or 0) >= 60):
        return 'high'
    if (w.get('wind') or 0) >= 12 or (w.get('pop') or 0) >= 70:
        return 'watch'
    return None


def watch(season, week, games):
    """game_id -> forecast at kickoff + risk + nearest tropical system."""
    loc = venues(season, week)
    act = storms()
    now = datetime.datetime.now(datetime.timezone.utc)
    out = {}
    for g in games:
        gid = str(g['game_id'])
        if gid not in loc:
            continue
        try:
            ko = datetime.datetime.fromisoformat(g['kickoff_iso'].replace('Z', '+00:00'))
        except (KeyError, ValueError, AttributeError):
            continue
        if ko < now or (ko - now).days > 15:
            continue
        lat, lon = loc[gid]
        j = getj(METEO.format(lat=lat, lon=lon, d=ko.date()))
        if not j:
            continue
        h = j['hourly']
        key = ko.strftime('%Y-%m-%dT%H:00')
        if key not in h['time']:
            continue
        i = h['time'].index(key)
        w = dict(wind=h['wind_speed_10m'][i], gust=h['wind_gusts_10m'][i],
                 pop=h['precipitation_probability'][i], rain_in=h['precipitation'][i])
        if act:
            near = min(act, key=lambda s: miles((lat, lon), s['pos']))
            w['storm'] = dict(name=near['name'], kind=near['kind'],
                              miles=round(miles((lat, lon), near['pos'])))
        w['risk'] = risk(w)
        out[gid] = w
    print(f'  weather watch: {len(out)} outdoor games, '
          f'{sum(1 for w in out.values() if w["risk"] == "high")} high risk, '
          f'{len(act)} active tropical system(s)', file=sys.stderr)
    return out
