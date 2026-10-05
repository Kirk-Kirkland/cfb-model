let DATA = null;
let RECORD = null;
let sortKey = 'kickoff_iso';
let sortDir = 1;

function tierClass(t) {
  if (!t) return 'neutral';
  if (t === 'Strong edge' || t === 'BET' || t === 'BET (check news)' || t === 'Side') return 'good';
  if (t === 'Edge' || t === 'LEAN') return 'lean';
  if (t === 'Pass' || t === 'No bet: FCS') return 'neutral';
  return 'neutral';
}

function fmtEdge(v) {
  if (v === null || v === undefined) return '—';
  return (v > 0 ? '+' : '') + v.toFixed(1);
}

function fmtConf(v) {
  return v === null || v === undefined ? '—' : (v * 100).toFixed(1) + '%';
}

async function load() {
  const res = await fetch('data.json?_=' + Date.now());
  DATA = await res.json();
  render();
  loadRecord();
}

async function loadRecord() {
  try {
    const res = await fetch('record.json?_=' + Date.now());
    if (!res.ok) throw new Error(res.status);
    RECORD = await res.json();
  } catch (e) {
    document.getElementById('recordSummary').innerHTML =
      '<div class="sub">No graded record published yet.</div>';
    return;
  }
  renderRecord();
}

function render() {
  const m = DATA.meta;
  document.getElementById('meta').textContent =
    `${m.season} · Week ${m.week} · ${m.games} games · Last updated: ${new Date(m.generated_at).toLocaleString()}`;
  renderTop3();
  renderBestBets();
  renderGames();
  renderRatings();
  renderQB();
}

function renderTop3() {
  const el = document.getElementById('top3');
  el.innerHTML = DATA.top3.map(p => `
    <div class="top3-card">
      <div class="rank">Top ${p.rank}</div>
      <div class="bet">${p.bet}</div>
      <div class="sub">${p.game} &middot; ${p.kickoff} &middot; edge ${fmtEdge(p.edge)} &middot; est. hit rate ${fmtConf(p.confidence)}</div>
      <div class="sub bet-only-if">Bet only if line is ${p.bet_only_if}</div>
      ${firstLine(p)}
    </div>`).join('') || '<div class="sub">No qualifying plays this build.</div>';
}

function firstLine(b) {
  if (b.first_line === undefined || b.first_line === null) return '';
  const now = parseFloat(b.bet.split(' ')[1]);
  const moved = now - b.first_line;
  const when = b.first_seen_at ? new Date(b.first_seen_at).toLocaleString([], {weekday: 'short', hour: 'numeric', minute: '2-digit'}) : '';
  return `<div class="sub">First posted at ${b.first_line} (${when})${moved ? ` &middot; line has moved ${moved > 0 ? '+' : ''}${moved}` : ''}</div>`;
}

function fmtClv(v) {
  if (v === null || v === undefined) return '&mdash;';
  const cls = v > 0 ? 'good' : v < 0 ? 'bad' : 'neutral';
  return `<span class="pill ${cls}">${v > 0 ? '+' : ''}${v}</span>`;
}

function renderBestBets() {
  const el = document.getElementById('bestbets');
  if (!DATA.best_bets.length) {
    el.innerHTML = '<div class="sub">No qualifying plays this build.</div>';
    return;
  }
  el.innerHTML = DATA.best_bets.map(b => `
    <div class="bet-card">
      <span class="tier-tag tier-${b.tier}">${b.tier === '1' || b.tier === '2' ? 'TOTAL ' + b.tier : b.tier}</span>
      <div class="info">
        <div class="bet-title">${b.bet} <span style="color:var(--muted);font-weight:400;">(${b.game})</span></div>
        <div class="bet-sub">${b.kickoff} &middot; ${b.note}</div>
        <div class="bet-sub bet-only-if">Bet only if line is ${b.bet_only_if} &middot; est. hit rate ${fmtConf(b.confidence)}</div>
        ${firstLine(b)}
      </div>
      <div class="edge">${fmtEdge(b.edge)}</div>
    </div>`).join('');
}

function renderGames() {
  const search = document.getElementById('search').value.toLowerCase();
  const tierFilter = document.getElementById('tierFilter').value;
  let rows = DATA.games.filter(g => {
    if (search && !g.matchup.toLowerCase().includes(search) &&
        !g.home.toLowerCase().includes(search) && !g.away.toLowerCase().includes(search)) return false;
    if (tierFilter && g.side_tier !== tierFilter && g.total_tier !== tierFilter) return false;
    return true;
  });
  rows.sort((a, b) => {
    const av = a[sortKey], bv = b[sortKey];
    if (av === null || av === undefined) return 1;
    if (bv === null || bv === undefined) return -1;
    if (av < bv) return -1 * sortDir;
    if (av > bv) return 1 * sortDir;
    return 0;
  });
  const body = document.getElementById('gamesBody');
  body.innerHTML = rows.map(g => `
    <tr>
      <td>${g.kickoff_et}</td>
      <td>${g.matchup}</td>
      <td>${g.side_pick || '—'}</td>
      <td>${fmtEdge(g.edge)}</td>
      <td>${g.side_tier ? `<span class="pill ${tierClass(g.side_tier)}">${g.side_tier}</span>` : ''}</td>
      <td>${g.total_pick || '—'}</td>
      <td>${fmtEdge(g.total_edge)}</td>
      <td>${g.total_tier ? `<span class="pill ${tierClass(g.total_tier)}">${g.total_tier}</span>` : ''}</td>
    </tr>`).join('');
}

function renderRatings() {
  const body = document.getElementById('ratingsBody');
  body.innerHTML = DATA.ratings.map((r, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${r.team}</td>
      <td>${r.off.toFixed(3)}</td>
      <td>${r.deff.toFixed(3)}</td>
      <td>${r.net.toFixed(3)}</td>
      <td>${r.sp ?? '—'}</td>
      <td>${r.pace ?? '—'}</td>
    </tr>`).join('');
}

function renderQB() {
  const body = document.getElementById('qbBody');
  body.innerHTML = (DATA.qb_values || []).map(q => `
    <tr>
      <td>${q.team}</td>
      <td>${q.starter}</td>
      <td>${q.backup}</td>
      <td>${q.value.toFixed(1)}</td>
    </tr>`).join('');
}

function stat(label, value, sub, cls) {
  return `<div class="stat ${cls || ''}">
      <div class="stat-label">${label}</div>
      <div class="stat-value">${value}</div>
      <div class="stat-sub">${sub || ''}</div>
    </div>`;
}

function recCls(t) {
  if (!t.n || t.pct === null) return '';
  return t.pct > 52.4 ? 'good' : 'bad';
}

function clvStat(label, c) {
  if (!c || !c.n) return stat(label, '&mdash;', 'starts week 6', '');
  return stat(label, `${c.avg > 0 ? '+' : ''}${c.avg} pts`,
    `beat the close ${c.beat}-${c.lost} &middot; ${c.same} unchanged`,
    c.avg > 0 ? 'good' : c.avg < 0 ? 'bad' : '');
}

function renderRecord() {
  const r = RECORD, all = r.all_bets, live = r.published_only, t3 = r.top3;
  document.getElementById('recordSummary').innerHTML =
    stat('All qualifying totals', `${all.w}-${all.l}`,
         `${all.pct}% &plusmn; ${all.se} &middot; ${all.units > 0 ? '+' : ''}${all.units.toFixed(2)} units &middot; ROI ${all.roi > 0 ? '+' : ''}${all.roi}%`,
         recCls(all)) +
    stat('Published live only', live.n ? `${live.w}-${live.l}` : '&mdash;',
         live.n ? `${live.pct}% &middot; weeks ${r.meta.published_weeks.join(', ')}` : 'nothing graded yet',
         recCls(live)) +
    stat('Top 3 of the week', t3.n ? `${t3.w}-${t3.l}` : '&mdash;',
         t3.n ? `${t3.pct}% on ${t3.n} bets` : '', recCls(t3)) +
    stat('Break-even', `${r.meta.break_even_pct}%`, 'at -110 odds', '') +
    clvStat('CLV vs posted line', r.clv && r.clv.posted) +
    clvStat('CLV vs first line', r.clv && r.clv.first);

  const n = all.n, lo = (all.pct - all.se).toFixed(1), hi = (all.pct + all.se).toFixed(1);
  document.getElementById('recordCaveat').innerHTML =
    `Read this honestly. ${n} graded bets is a small sample. One standard error puts the true hit rate somewhere around ` +
    `${lo}% to ${hi}%, which straddles the ${r.meta.break_even_pct}% break-even, so this record does not yet prove an edge either way. ` +
    `The walk-forward backtest says ~53%. Judge the model on that number, not on a hot or cold month. ` +
    (r.meta.reconstructed_weeks.length
      ? `<br><br><strong>Week${r.meta.reconstructed_weeks.length > 1 ? 's' : ''} ${r.meta.reconstructed_weeks.join(', ')} ` +
        `${r.meta.reconstructed_weeks.length > 1 ? 'were' : 'was'} rebuilt after the fact</strong>, before this site existed. ` +
        (r.meta.reconstruction_warning || '')
      : '');

  document.getElementById('recordWeeksBody').innerHTML = r.by_week.map(w => `
    <tr>
      <td>${w.week}</td>
      <td>${w.w}-${w.l}${w.push ? '-' + w.push : ''}</td>
      <td>${w.pct}%</td>
      <td>${w.units > 0 ? '+' : ''}${w.units.toFixed(2)}</td>
      <td>${w.roi > 0 ? '+' : ''}${w.roi}%</td>
      <td>${w.published && w.clv && w.clv.n ? `${w.clv.avg > 0 ? '+' : ''}${w.clv.avg} (${w.clv.beat}-${w.clv.lost})` : '&mdash;'}</td>
      <td><span class="pill ${w.published ? 'good' : 'neutral'}">${w.published ? 'published live' : 'reconstructed'}</span></td>
    </tr>`).join('');

  document.getElementById('recordPicksBody').innerHTML = r.picks.map(p => `
    <tr>
      <td>${p.week}</td>
      <td>${p.game}${p.top3 ? ` <span class="pill lean">Top ${p.top3}</span>` : ''}</td>
      <td>${p.bet}</td>
      <td>${fmtEdge(p.edge)}</td>
      <td>${p.first_line ?? '&mdash;'}</td>
      <td>${p.published ? (p.close_total ?? '&mdash;') : '&mdash;'}</td>
      <td>${p.published ? fmtClv(p.first_line != null ? p.clv_first : p.clv) : '&mdash;'}</td>
      <td class="muted-cell">${p.score || '&mdash;'}</td>
      <td>${p.actual_total ?? '&mdash;'}</td>
      <td>${p.result ? `<span class="pill ${p.result === 'WIN' ? 'good' : p.result === 'LOSS' ? 'bad' : 'neutral'}">${p.result}</span>` : '&mdash;'}</td>
    </tr>`).join('');
}

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

document.getElementById('search').addEventListener('input', renderGames);
document.getElementById('tierFilter').addEventListener('change', renderGames);
document.querySelectorAll('#gamesTable th[data-key]').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.key;
    if (sortKey === key) sortDir *= -1; else { sortKey = key; sortDir = 1; }
    renderGames();
  });
});

load();
