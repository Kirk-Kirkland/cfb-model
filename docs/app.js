let DATA = null;
let sortKey = 'kickoff_iso';
let sortDir = 1;

function tierClass(t) {
  if (!t) return 'neutral';
  if (t === 'Strong edge' || t === 'BET' || t === 'Side') return 'good';
  if (t === 'Edge' || t === 'LEAN') return 'lean';
  if (t === 'Pass' || t === 'No bet: FCS') return 'neutral';
  if (t === 'Check news') return 'bad';
  return 'neutral';
}

function fmtEdge(v) {
  if (v === null || v === undefined) return '—';
  return (v > 0 ? '+' : '') + v.toFixed(1);
}

async function load() {
  const res = await fetch('data.json?_=' + Date.now());
  DATA = await res.json();
  render();
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
      <div class="sub">${p.game} &middot; ${p.kickoff} &middot; edge ${fmtEdge(p.edge)}</div>
      <div class="sub bet-only-if">Bet only if line is ${p.bet_only_if}</div>
    </div>`).join('') || '<div class="sub">No qualifying plays this build.</div>';
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
        <div class="bet-sub bet-only-if">Bet only if line is ${b.bet_only_if}</div>
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
