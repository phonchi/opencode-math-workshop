/* 做完再對照：不需要 Three.js，2D 模式也能用。
 *
 *   - 同一份資料、兩種用途（Lab 1／2／3）：左欄是沒講用途時的答案，右欄隨用途改變
 *   - 檢查漏網燈板（Lab 2）：先關掉自認多餘的檢查，再放進四個錯誤，看哪些溜過去
 * 每一組都會露出 Lab 的參考結果，所以要先按「我做完這一關了」才展開；這個紀錄只存在這台裝置。
 * 資料全在 DATA.compare（tools/island_meta.py 的 COMPARE），數字由 build 檢查與教材同源。
 */
const CMPD = DATA.compare;
const CMP_TABS = [
  ...CMPD.purpose.map(c => ({ key: c.key, label: c.label, stem: c.stem, kind: 'purpose', c })),
  { key: 'checks', label: CMPD.checks.label, stem: CMPD.checks.stem, kind: 'checks', c: CMPD.checks },
];
const cmpTab = Object.fromEntries(CMP_TABS.map(t => [t.key, t]));
const OPEN_KEY = 'aimath-island:opened:v1';
function loadOpened() {
  try { return JSON.parse(localStorage.getItem(OPEN_KEY) || '{}') || {}; } catch (e) { return {}; }
}
let opened = loadOpened();
function resetOpened() {                               // 「清除足跡」時一併清掉，閘門才會重新出現
  opened = {};
  try { localStorage.removeItem(OPEN_KEY); } catch (e) { /* 只在本頁有效 */ }
}
function setOpened(stem) {
  opened[stem] = Date.now();
  try { localStorage.setItem(OPEN_KEY, JSON.stringify(opened)); } catch (e) { /* 只在本頁有效 */ }
}

const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; };
const cmpDlg = $('cmpDialog');
let cmpKey = CMP_TABS[0].key;
const useIdx = {};                                   // 每個用途組目前選的用途
const board = { on: CMPD.checks.checks.map(() => true), ran: false };

function gate(t) {
  const box = el('div', 'cmp-gate');
  const lab = BY[t.stem];
  box.append(el('p', '', `這裡有「${lab.title}」的參考結果。還沒做完這一關，先別打開：自己判斷過，再對照才有用。`));
  const b = el('button', 'isl-btn2 is-primary', '我做完這一關了，打開');
  b.type = 'button';
  b.addEventListener('click', () => { setOpened(t.stem); renderCmp(); $('cmpBody').querySelector('button')?.focus(); });
  const a = el('a', '', `還沒做，先去 ${lab.title} →`);
  a.href = lab.href;
  box.append(b, a);
  return box;
}

function renderPurpose(c) {
  const i = useIdx[c.key] ?? 0, use = c.uses[i];
  const cols = el('div', 'cmp-cols');
  const left = el('section', 'cmp-col');
  left.append(el('h3', '', c.default.h), el('p', '', c.default.text));
  const right = el('section', 'cmp-col');
  right.appendChild(el('h3', '', '講清楚用途之後'));
  const chips = el('div', 'cmp-uses');
  chips.setAttribute('role', 'group'); chips.setAttribute('aria-label', '選一個用途');
  c.uses.forEach((u, k) => {
    const b = el('button', 'cmp-chip', u.label);
    b.type = 'button'; b.setAttribute('aria-pressed', String(k === i));
    b.addEventListener('click', () => { useIdx[c.key] = k; renderCmp(); $('cmpBody').querySelectorAll('.cmp-chip')[k]?.focus(); });
    chips.appendChild(b);
  });
  const table = el('table', 'cmp-table');
  const tr = el('tr'); c.table.head.forEach(h => tr.appendChild(el('th', '', h)));
  const thead = el('thead'); thead.appendChild(tr); table.appendChild(thead);
  const tbody = el('tbody');
  c.table.rows.forEach((row, r) => {
    const t = el('tr');
    if (use.hi === r) t.className = 'is-hi';
    if (use.cap !== undefined && Number(row[c.cap_col]) > use.cap) t.className = 'is-over';
    row.forEach(v => t.appendChild(el('td', '', v)));
    tbody.appendChild(t);
  });
  table.appendChild(tbody);
  right.append(chips, table, el('p', '', use.text));
  cols.append(left, right);
  return cols;
}

function renderChecks(c) {
  const wrap = el('div');
  const table = el('table', 'cmp-board');
  const head = el('tr');
  head.appendChild(el('th', '', '故意放的錯誤'));
  c.checks.forEach((name, j) => {
    const th = el('th');
    const b = el('button', 'cmp-switch');
    b.type = 'button'; b.setAttribute('aria-pressed', String(board.on[j]));
    b.setAttribute('aria-label', `${name}檢查：${board.on[j] ? '開著' : '關掉'}`);
    b.append(name, el('small', '', board.on[j] ? '開著' : '關掉'));
    b.addEventListener('click', () => { board.on[j] = !board.on[j]; renderCmp(); $('cmpBody').querySelectorAll('.cmp-switch')[j]?.focus(); });
    th.appendChild(b); head.appendChild(th);
  });
  head.appendChild(el('th', '', '結果'));
  const thead = el('thead'); thead.appendChild(head); table.appendChild(thead);
  const tbody = el('tbody');
  c.bugs.forEach(([name, row]) => {
    const t = el('tr');
    t.appendChild(el('td', '', name));
    row.forEach((fail, j) => {
      const td = el('td');
      const cell = !board.on[j] ? el('span', 'cmp-cell is-off', '—')
        : !board.ran ? el('span', 'cmp-cell is-hidden', '？')
        : el('span', 'cmp-cell ' + (fail ? 'is-fail' : 'is-pass'), fail ? 'FAIL' : 'PASS');
      td.appendChild(cell); t.appendChild(td);
    });
    const caught = row.some((fail, j) => fail && board.on[j]);
    const v = el('td');
    if (board.ran) v.appendChild(el('span', 'cmp-verdict ' + (caught ? 'is-hit' : 'is-miss'), caught ? '抓到了' : '溜過去'));
    t.appendChild(v); tbody.appendChild(t);
  });
  table.appendChild(tbody);
  const actions = el('div', 'cmp-actions');
  const run = el('button', 'isl-btn2 is-primary', board.ran ? '已放進四個錯誤' : '放進四個錯誤，跑一次');
  run.type = 'button'; run.disabled = board.ran;
  run.addEventListener('click', () => { board.ran = true; renderCmp(); });
  const reset = el('button', 'isl-btn2', '重來');
  reset.type = 'button';
  reset.addEventListener('click', () => { board.ran = false; board.on = c.checks.map(() => true); renderCmp(); });
  actions.append(run, reset);
  const tw = el('div'); tw.style.overflowX = 'auto'; tw.appendChild(table);
  wrap.append(tw, actions, el('p', 'cmp-after', board.ran ? c.after : ''));
  return wrap;
}

function renderCmp() {
  const t = cmpTab[cmpKey];
  $('cmpTitle').textContent = t.kind === 'checks' ? '檢查漏網燈板' : '同一份資料、兩種用途';
  $('cmpOp').textContent = t.c.ask;
  $('cmpTabs').querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.key === cmpKey)));
  const body = $('cmpBody');
  const isOpen = !!opened[t.stem];
  body.replaceChildren(!isOpen ? gate(t) : t.kind === 'checks' ? renderChecks(t.c) : renderPurpose(t.c));
  $('cmpNote').textContent = isOpen ? CMPD.note : '';
}
CMP_TABS.forEach(t => {
  const b = el('button', 'cmp-tab', t.label);
  b.type = 'button'; b.dataset.key = t.key;
  b.addEventListener('click', () => { cmpKey = t.key; renderCmp(); });
  $('cmpTabs').appendChild(b);
});
function openCompare(key) {
  if (key && cmpTab[key]) cmpKey = key;
  else if (current) { const t = CMP_TABS.find(x => x.stem === current); if (t) cmpKey = t.key; }
  renderCmp();
  if (!cmpDlg.open) cmpDlg.showModal();
}
$('islCompare').addEventListener('click', () => openCompare());
$('cmpClose').addEventListener('click', () => cmpDlg.close());
cmpDlg.addEventListener('click', e => {                 // 只有點在對話框外面（backdrop）才關閉；內距空白的 target 也是 dialog
  if (e.target !== cmpDlg) return;
  const r = cmpDlg.getBoundingClientRect();
  if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) cmpDlg.close();
});
window.addEventListener('storage', e => { if (e.key === OPEN_KEY) { opened = loadOpened(); if (cmpDlg.open) renderCmp(); } });
window.__cmp = { tabs: () => CMP_TABS.map(t => t.key), opened: () => ({ ...opened }) };   // 給 check_island_browser.js 用

// 面板上：這一頁相關的對照
function renderPanelCompare(stem) {
  const host = $('islPanelCmp');
  const list = CMP_TABS.filter(t => t.stem === stem);
  host.hidden = !list.length;
  host.replaceChildren(...list.map(t => {
    const b = el('button', 'isl-cmp-link', `做完再對照：${t.kind === 'checks' ? '檢查漏網燈板' : '同一份資料、兩種用途'} →`);
    b.type = 'button';
    b.addEventListener('click', () => openCompare(t.key));
    return b;
  }));
}
