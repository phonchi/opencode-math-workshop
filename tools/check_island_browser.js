#!/usr/bin/env node
/* 3D 課程島 island/index.html 的瀏覽器驗收。
 *   - WebGL 正常／CDN 被攔／getContext 回傳 null 三種狀態 × 桌面與 390×844
 *   - 比喻與防劇透約束（island_meta.py 開頭列的那幾條）：杯子不動、門檻桿有人手、告示牌與柵欄分開、
 *     「我推導」永遠空白、輪播只用 idle、一進來看不到參考數字
 *   - 點地標開面板、鍵盤、足跡、15 題猜題、做完再對照（閘門＋與本檔獨立計算的燈板結果比對）
 *   - 四條導覽路線、續走、走完；代表圖
 *   - 繪製呼叫上限、拖曳時繪製不重複排程、閒置暫停
 *   - 三個代表圖深連結的落點
 * 用法：SHOT_DIR=tools/test-runs/<日期>-island/shots node tools/check_island_browser.js
 * puppeteer-core 裝在 ~/.cache/selfstudy-node（見 build_island_figs.js）。 */
const path = require('path');
const fs = require('fs');

const PPT_HOME = process.env.PPT_HOME || path.join(process.env.HOME, '.cache/selfstudy-node');
const puppeteer = require(path.join(PPT_HOME, 'node_modules', 'puppeteer-core'));
const ROOT = path.resolve(__dirname, '..');
const SHOT_DIR = process.env.SHOT_DIR || path.join(PPT_HOME, 'shots-island');
const CHROME = process.env.CHROME_PATH || (() => {
  const base = path.join(process.env.HOME, '.cache/puppeteer/chrome');
  const dirs = fs.readdirSync(base).sort();
  return path.join(base, dirs[dirs.length - 1], 'chrome-linux64', 'chrome');
})();
const URL_ = 'file://' + path.join(ROOT, 'island', 'index.html');
const IGNORE = [/software WebGL/i, /GL Driver Message/i, /GPU stall/i, /fonts\.g/i, /net::ERR/i, /Failed to load resource/i];
const LABS = ['lab1-cluster', 'lab2-pca', 'lab3-notes'];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const problems = [];
const note = m => { problems.push(m); console.log('  ✗ ' + m); };
const ok = m => console.log('  ✓ ' + m);
const info = m => console.log('  · ' + m);
const KEY = k => 'aimath-island:' + k;

(async () => {
  fs.mkdirSync(SHOT_DIR, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });

  async function open(mode) {
    const page = await browser.newPage();
    const errors = [];
    page.on('console', m => { if (['error', 'warning'].includes(m.type()) && !IGNORE.some(r => r.test(m.text()))) errors.push(m.text()); });
    page.on('pageerror', e => errors.push('pageerror: ' + e.message));
    if (mode === 'cdn') {
      await page.setRequestInterception(true);
      page.on('request', r => (/cdn\.jsdelivr\.net/.test(r.url()) ? r.abort() : r.continue()).catch(() => {}));
    }
    if (mode === 'nogl') {
      await page.evaluateOnNewDocument(() => {
        const o = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function (t, ...r) { return /webgl/i.test(t) ? null : o.call(this, t, ...r); };
      });
    }
    return { page, errors };
  }
  async function layout(page, label) {
    const r = await page.evaluate(() => {
      const de = document.documentElement, links = [...document.querySelectorAll('.isl-link')];
      return { over: de.scrollWidth - de.clientWidth, visible: links.filter(a => a.offsetParent !== null).length, total: links.length, webgl: document.body.classList.contains('webgl-ready') };
    });
    if (r.over > 1) note(`${label}：橫向溢出 ${r.over}px`);
    if (r.visible !== r.total) note(`${label}：只有 ${r.visible}/${r.total} 個入口可見`);
    return r;
  }
  async function canvasColors(page) {
    const el = await page.$('#islCanvas'), b64 = await el.screenshot({ encoding: 'base64' });
    return page.evaluate(async src => {
      const img = new Image(); img.src = 'data:image/png;base64,' + src; await img.decode();
      const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
      const g = c.getContext('2d'); g.drawImage(img, 0, 0);
      const d = g.getImageData(0, 0, c.width, c.height).data, seen = new Set();
      for (let i = 0; i < d.length; i += 4 * 97) seen.add((d[i] >> 3) << 10 | (d[i + 1] >> 3) << 5 | d[i + 2] >> 3);
      return seen.size;
    }, b64);
  }
  const visibleText = page => page.evaluate(() => {
    const t = []; const walk = n => { if (n.nodeType === 3) { if (n.parentElement && n.parentElement.offsetParent !== null) t.push(n.textContent); return; }
      if (n.nodeName === 'SCRIPT' || n.nodeName === 'STYLE') return; n.childNodes.forEach(walk); };
    walk(document.body); return t.join(' ');
  });

  /* ═ (a) WebGL 正常 ═ */
  console.log('(a) WebGL');
  {
    const { page, errors } = await open('gl');
    await page.setViewport({ width: 1280, height: 900 });
    await page.goto(URL_, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith('aimath-island:')).forEach(k => localStorage.removeItem(k)));
    await page.reload({ waitUntil: 'domcontentloaded' });
    const ready = await page.waitForSelector('body.webgl-ready', { timeout: 40000 }).then(() => true, () => false);
    if (!ready) note('WebGL 可用時沒有進入 3D');
    await page.waitForFunction(() => !document.documentElement.classList.contains('gl-pending'), { timeout: 40000 }).catch(() => {});
    await sleep(1500);
    const colors = await canvasColors(page);
    if (colors < 30) note(`3D 畫布幾乎是空的（${colors} 種顏色）`); else ok(`3D 畫出 ${colors} 種顏色`);
    await page.screenshot({ path: path.join(SHOT_DIR, '3d_day.png') });

    /* 一進來看得到的文字裡沒有 Lab 的參考數字 */
    {
      const data = await page.evaluate(() => JSON.parse(document.getElementById('island-data').textContent));
      const nums = data.compare.purpose.flatMap(c => c.nums).filter(n => n.includes('.'));
      const text = await visibleText(page);
      const leak = nums.filter(n => text.includes(n));
      if (leak.length) note(`一進來就看得到參考數字：${leak}`); else ok('一進來看不到任何 Lab 的參考數字');
    }

    /* 比喻與防劇透約束 */
    const inv = await page.evaluate(() => window.__island.invariants());
    {
      const r = await page.evaluate(() => {
        const I = window.__island, snap = () => JSON.stringify(I.probe('lab1-cluster').cups), base = snap(), flags0 = JSON.stringify(I.probe('lab1-cluster').flags);
        let moved = 0, flagsMoved = false;
        for (const mode of ['pose', 'idle']) for (let u = 0; u <= 1; u += .05) { I.pose('lab1-cluster', u, mode); if (snap() !== base) moved++; if (mode === 'pose' && JSON.stringify(I.probe('lab1-cluster').flags) !== flags0) flagsMoved = true; }
        I.pose('lab1-cluster', 0);
        return { moved, flagsMoved, back: JSON.stringify(I.probe('lab1-cluster').flags) === flags0 };
      });
      if (r.moved) note(`Lab 1 的杯子（資料點）在動畫中移動了 ${r.moved} 次`); else ok('Lab 1：杯子在 pose 與 idle 中都不動');
      if (!r.flagsMoved) note('Lab 1：旗桿（群中心）在 pose 中沒有移動'); else ok(`Lab 1：旗桿會移動（k-means ${inv['lab1-cluster'].iterations} 輪）`);
      if (!r.back) note('Lab 1：動畫結束沒有回到靜止姿態');
    }
    {
      const r = await page.evaluate(() => {
        const I = window.__island, out = [];
        for (const mode of ['pose', 'idle']) for (let u = 0; u <= 1; u += .05) { I.pose('lab3-notes', u, mode); const p = I.probe('lab3-notes'); out.push([p.t, Math.hypot(p.hand[0] - p.pole[0], p.hand[2] - p.pole[2])]); }
        I.pose('lab3-notes', 0); return { out, rest: I.probe('lab3-notes').t };
      });
      const far = r.out.filter(([, d]) => d > .7);
      if (far.length) note(`Lab 3：門檻桿離開了人手（${far.length} 個時刻）`); else ok('Lab 3：門檻桿一直由人手推著');
      if ([.5, .3, .2, .1, .05].some(t => Math.abs(r.rest - t) < .01)) note(`Lab 3：靜止的門檻 ${r.rest} 停在教材表格的門檻上`); else ok(`Lab 3：靜止門檻 ${r.rest.toFixed(2)} 不是教材表格的任何一個`);
    }
    {
      const r = await page.evaluate(() => {
        const I = window.__island, seen = new Set();
        for (let u = 0; u <= 1; u += .02) { I.pose('research-notes', u); seen.add(I.probe('research-notes').fills[2]); }
        I.pose('research-notes', 0); return [...seen];
      });
      if (r.length !== 1) note(`筆記島：「我推導」那格被填色了 ${r}`); else ok('筆記島：「我推導」那格永遠空白');
    }
    {
      const [sx, sz] = inv['agents-md'].sign, [fx, fz] = inv['agents-md'].fence;
      if (Math.hypot(sx - fx, sz - fz) < 1.5) note('AGENTS.md：告示牌和柵欄靠得太近，看起來像同一個物件'); else ok('AGENTS.md：告示牌（提示）與柵欄（permission）是兩個物件');
      if (Math.abs(inv['lab2-pca'].principal - inv['lab2-pca'].rest) < .3) note('Lab 2：靜止的軸已經是第一主成分方向'); else ok('Lab 2：靜止的軸不是答案方向');
    }
    /* 每個地標的兩段時間軸都跑得完 */
    {
      const stems = await page.evaluate(() => [...document.querySelectorAll('.isl-item')].map(l => l.dataset.stem));
      const bad = await page.evaluate(stems => stems.filter(s => { try { for (const m of ['pose', 'idle']) { for (let u = 0; u <= 1; u += .02) window.__island.pose(s, u, m); } window.__island.pose(s, 0); return false; } catch (e) { return true; } }), stems);
      if (bad.length) note(`時間軸出錯：${bad}`); else ok(`${stems.length} 個地標的 pose／idle 時間軸都跑得完`);
      const br = await page.evaluate(() => window.__island.bridges());
      if (br.length !== 3) note(`拱橋應有 3 座，得到 ${br.length}`); else ok('三座拱橋從主島接到三座小島');
    }
    /* 輪播只用 idle：等幾輪看實際播了什麼 */
    {
      let modes = new Set();
      for (let i = 0; i < 16; i++) { (await page.evaluate(() => window.__island.plays())).forEach(([, m]) => modes.add(m)); await sleep(600); }
      const log = await page.evaluate(() => window.__island.attract());
      if (modes.has('pose')) note('沒有答題時，輪播播了完整動畫（pose）');
      else if (!log.length) info('沒有觀察到輪播（軟體算圖可能進入低效能模式）');
      else ok(`輪播只用 idle（播過 ${log.length} 個地標）`);
    }

    /* 拾取：15 個地標都點得到自己 */
    {
      await page.click('#islReset'); await sleep(1100);
      const r = await page.evaluate(() => {
        const I = window.__island, st = I.stops();
        return Object.keys(st).filter(s => { const p = I.screenPos(s); return I.pickAt(p.x, p.y) !== s; }).map(s => { const p = I.screenPos(s); return `${s}→${I.pickAt(p.x, p.y)}`; });
      });
      if (r.length) note(`全景時點錯或點不到：${r}`); else ok('全景時 15 個地標都點得到自己');
    }
    /* 點地標 → 面板 */
    const pos = await page.evaluate(() => window.__island.screenPos('lab2-pca'));
    await page.mouse.click(pos.x, pos.y); await sleep(300);
    const t1 = await page.$eval('#islPanelTitle', e => e.textContent);
    if (t1 !== 'Lab 2 · PCA') note(`點 Lab 2 開成「${t1}」`); else ok('點地標開對面板');
    const refs = await page.$$eval('.isl-item.is-ref', e => e.map(x => x.dataset.stem));
    if (refs.sort().join() !== 'cheatsheet,first-run') note(`Lab 2 的「需要時可查閱」應高亮 first-run、cheatsheet，得到 ${refs}`); else ok('需要時可查閱的頁有高亮');
    const pcmp = await page.$$eval('#islPanelCmp .isl-cmp-link', e => e.length);
    if (pcmp !== 2) note(`Lab 2 面板應有 2 個「做完再對照」，得到 ${pcmp}`);
    /* 列表鍵盤 → 焦點；Esc 還原 */
    await page.focus('.isl-item[data-stem="herdr"] .isl-link');
    await page.keyboard.press('Enter'); await sleep(900);
    const k = await page.evaluate(() => ({ t: document.getElementById('islPanelTitle').textContent, f: document.activeElement.id, h: document.getElementById('islPanelGo').getAttribute('href'), c: document.getElementById('islPanelCmp').hidden }));
    if (!k.t.includes('Herdr') || k.f !== 'islPanelGo' || k.h !== '../herdr.html') note(`鍵盤選取失敗：${JSON.stringify(k)}`); else ok('鍵盤選取');
    if (!k.c) note('非 Lab 頁不該有「做完再對照」');
    await page.keyboard.press('Escape');
    const back = await page.evaluate(() => ({ h: document.getElementById('islPanel').hidden, f: document.activeElement.dataset.stem }));
    if (!back.h || back.f !== 'herdr') note(`Esc 沒有關閉或還原焦點：${JSON.stringify(back)}`); else ok('Esc 關閉並還原焦點');
    /* 足跡 */
    await page.click('.isl-item[data-stem="lab1-cluster"] .isl-mark');
    const done = await page.evaluate(k => ({ c: document.querySelector('.isl-item[data-stem="lab1-cluster"]').classList.contains('is-done'), s: (localStorage.getItem(k) || '').includes('lab1-cluster') }), KEY('trail:v1'));
    if (!done.c || !done.s) note('標記完成沒有生效'); else ok('標記完成寫入 localStorage');
    /* 標籤：回到全景再數 */
    await page.click('#islReset'); await sleep(1100);
    const tagInfo = await page.$$eval('.isl-tag-stop', e => ({ total: e.length, shown: e.filter(x => !x.classList.contains('is-off')).length }));
    if (tagInfo.shown < tagInfo.total) note(`全景時單元標籤只顯示 ${tagInfo.shown}/${tagInfo.total}`); else ok(`全景時 ${tagInfo.total} 個單元標籤都在`);

    /* 15 題猜題：答對與答錯都要有回饋；答完才播完整動畫 */
    const quizzes = await page.evaluate(() => JSON.parse(document.getElementById('island-data').textContent).pages.map(p => ({ stem: p.stem, a: p.quiz.answer })));
    if (quizzes.length !== 15) note(`猜題應有 15 題，得到 ${quizzes.length}`);
    for (let i = 0; i < quizzes.length; i++) {
      const q = quizzes[i];
      await page.evaluate(s => document.querySelector(`.isl-item[data-stem="${s}"] .isl-link`).click(), q.stem); await sleep(120);
      const pre = await page.evaluate(s => window.__island.plays().some(([x, m]) => x === s && m === 'pose'), q.stem);
      if (pre) note(`${q.stem}：還沒答題就在播完整動畫`);
      await page.click('#islTabQuiz');
      if (!(await page.$eval('#islQuizWhy', e => e.hidden))) note(`${q.stem}：答題前就看到解答`);
      const pick = i % 2 ? q.a : (q.a + 1) % 4;
      await (await page.$$('.isl-opt'))[pick].click(); await sleep(60);
      const r = await page.evaluate(s => ({ why: document.getElementById('islQuizWhy').textContent, right: document.querySelectorAll('.isl-opt.is-right').length, wrong: document.querySelectorAll('.isl-opt.is-wrong').length, plays: window.__island.plays().filter(([x]) => x === s) }), q.stem);
      if (!r.why || r.right !== 1 || r.wrong !== (pick === q.a ? 0 : 1)) note(`${q.stem}：猜題回饋不對 ${JSON.stringify(r)}`);
      if (!r.plays.some(([, m]) => m === 'pose')) note(`${q.stem}：答完沒有播放完整動畫`);
    }
    ok('15 題猜題的回饋與播放');
    await page.keyboard.press('Escape');

    /* 做完再對照：閘門、用途切換、燈板（與獨立計算比對） */
    {
      const data = await page.evaluate(() => JSON.parse(document.getElementById('island-data').textContent).compare);
      await page.evaluate(() => document.querySelector('.isl-item[data-stem="lab1-cluster"] .isl-link').click()); await sleep(150);
      await page.click('#islCompare'); await sleep(150);
      const g = await page.evaluate(() => ({ open: document.getElementById('cmpDialog').open, gate: !!document.querySelector('#cmpBody .cmp-gate'), table: !!document.querySelector('#cmpBody table'), note: document.getElementById('cmpNote').textContent, body: document.getElementById('cmpBody').textContent }));
      const leak = data.purpose[0].nums.filter(n => n.includes('.') && g.body.includes(n));
      if (!g.open || !g.gate || g.table || g.note || leak.length) note(`對照閘門不對：${JSON.stringify({ ...g, leak })}`); else ok('對照：沒按「我做完了」之前只看到閘門');
      await page.click('#cmpBody .cmp-gate button'); await sleep(80);
      const opened = await page.evaluate(() => ({ rows: [...document.querySelectorAll('#cmpBody .cmp-table tbody tr')].map(r => r.className), note: document.getElementById('cmpNote').textContent }));
      if (opened.rows.join() !== 'is-hi,' || !opened.note) note(`Lab 1 打開後的表格不對：${JSON.stringify(opened)}`);
      await (await page.$$('#cmpBody .cmp-chip'))[1].click(); await sleep(50);
      const r2 = await page.$$eval('#cmpBody .cmp-table tbody tr', e => e.map(r => r.className));
      if (r2.join() !== ',is-hi') note(`切到客訴回查後高亮不對：${r2}`); else ok('對照：打開後可切換用途，高亮跟著變');
      // Lab 3：上限 40／20 劃掉的列，與教材表格獨立比對
      await page.evaluate(() => [...document.querySelectorAll('.cmp-tab')].find(b => b.dataset.key === 'lab3').click());
      if (await page.$('#cmpBody .cmp-gate')) await page.click('#cmpBody .cmp-gate button');
      const lab3 = data.purpose.find(c => c.key === 'lab3');
      for (const [i, u] of lab3.uses.entries()) {
        await (await page.$$('#cmpBody .cmp-chip'))[i].click(); await sleep(40);
        const over = await page.$$eval('#cmpBody .cmp-table tbody tr', e => e.map(r => r.classList.contains('is-over')));
        const want = lab3.table.rows.map(row => Number(row[1]) > u.cap);
        if (over.join() !== want.join()) note(`Lab 3 上限 ${u.cap}：劃掉的列不對 ${over}`);
      }
      ok('對照：Lab 3 依提醒上限劃掉的門檻正確');
      // 檢查漏網燈板：獨立計算哪些錯誤溜過去
      await page.evaluate(() => [...document.querySelectorAll('.cmp-tab')].find(b => b.dataset.key === 'checks').click());
      if (await page.$('#cmpBody .cmp-gate')) await page.click('#cmpBody .cmp-gate button');
      const hidden = await page.$$eval('#cmpBody .cmp-cell', e => e.filter(x => x.textContent === 'FAIL' || x.textContent === 'PASS').length);
      if (hidden) note('燈板還沒「放進錯誤」就露出結果');
      const ch = data.checks, trials = [[], [4], [0, 4], [1, 2]];
      for (const off of trials) {
        await page.evaluate(() => [...document.querySelectorAll('#cmpBody .isl-btn2')].find(b => b.textContent === '重來').click());
        for (const j of off) await (await page.$$('#cmpBody .cmp-switch'))[j].click();
        await page.evaluate(() => [...document.querySelectorAll('#cmpBody .isl-btn2')].find(b => b.textContent.startsWith('放進')).click());
        const got = await page.$$eval('#cmpBody .cmp-verdict', e => e.map(x => x.textContent));
        const want = ch.bugs.map(([, row]) => row.some((f, j) => f && !off.includes(j)) ? '抓到了' : '溜過去');
        if (got.join() !== want.join()) note(`燈板關掉 ${off.map(j => ch.checks[j])}：${got} ≠ ${want}`);
      }
      ok('燈板：四種開關組合的「抓到／溜過去」與獨立計算相符');
      await page.screenshot({ path: path.join(SHOT_DIR, 'cmp.png') });
      // 點對話框內距的空白不能關閉；點外面才關
      { const bb = await page.$eval('#cmpDialog', d => { const r = d.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
        await page.mouse.click(bb.x + 6, bb.y + bb.h / 2); await sleep(80);
        if (!(await page.$eval('#cmpDialog', e => e.open))) { note('點對照面板內緣就關閉了'); await page.click('#islCompare'); await sleep(100); } else ok('點面板內緣不會關閉'); }
      await page.keyboard.press('Escape'); await sleep(100);
      if (await page.$eval('#cmpDialog', e => e.open)) note('Esc 沒有關閉對照');
      const st = await page.evaluate(k => JSON.parse(localStorage.getItem(k) || '{}'), KEY('opened:v1'));
      if (!st['lab1-cluster'] || !st['lab2-pca'] || !st['lab3-notes']) note(`「我做完了」沒有記住：${JSON.stringify(st)}`);
      await page.keyboard.press('Escape');
      // 清除足跡：閘門要重新出現（講師在同一台電腦給下一班看）
      page.once('dialog', d => d.accept());
      await page.click('#islClear'); await sleep(150);
      await page.click('#islCompare'); await sleep(150);
      const g2 = await page.evaluate(k => ({ gate: !!document.querySelector('#cmpBody .cmp-gate'), ls: localStorage.getItem(k) }), KEY('opened:v1'));
      if (!g2.gate || g2.ls) note(`清除足跡後閘門沒有回來：${JSON.stringify(g2)}`); else ok('清除足跡後，對照面板的閘門重新出現');
      await page.keyboard.press('Escape'); await sleep(80);
    }

    /* 入夜 */
    await page.click('#islNight');
    await page.waitForFunction(() => window.__island.stats().night === 1, { timeout: 15000 }).catch(() => {});
    const m = await page.evaluate(k => ({ p: document.getElementById('islNight').getAttribute('aria-pressed'), c: document.getElementById('islStage').classList.contains('is-night'), k: window.__island.stats().night, s: localStorage.getItem(k) }), KEY('night'));
    if (m.p !== 'true' || !m.c || m.k !== 1 || m.s !== '1') note(`入夜切換無效：${JSON.stringify(m)}`); else ok('切到入夜');
    await page.screenshot({ path: path.join(SHOT_DIR, '3d_night.png') });
    await page.click('#islNight');
    await page.waitForFunction(() => window.__island.stats().night === 0, { timeout: 15000 }).catch(() => {});

    /* 拖曳時不重複排程 */
    {
      const cv = await page.$('#islCanvas'), bb = await cv.boundingBox();
      await page.evaluate(() => { window.__rafN = 0; const f = () => { window.__rafN++; requestAnimationFrame(f); }; requestAnimationFrame(f); });
      const s0 = await page.evaluate(() => ({ d: window.__island.stats().draws, f: window.__rafN }));
      await page.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2); await page.mouse.down();
      for (let i = 0; i < 25; i++) await page.mouse.move(bb.x + bb.width / 2 + i * 8, bb.y + bb.height / 2, { steps: 2 });
      await page.mouse.up(); await sleep(600);
      const s1 = await page.evaluate(() => ({ d: window.__island.stats().draws, f: window.__rafN }));
      if (s1.d - s0.d > s1.f - s0.f + 3) note(`拖曳時繪製（${s1.d - s0.d}）多於畫面幀（${s1.f - s0.f}）`); else ok(`拖曳：繪製 ${s1.d - s0.d}、畫面幀 ${s1.f - s0.f}`);
    }
    await page.click('#islReset'); await sleep(1100);

    /* 導覽 */
    {
      await page.evaluate(() => document.getElementById('islBubble').hidden = false);
      await page.click('#islBubble'); await sleep(250);
      const routes = await page.$$('#islGuideChoices .isl-choice');
      if (routes.length !== 4) note(`路線應有 4 條，得到 ${routes.length}`);
      await routes[1].click(); await sleep(900);
      const a = await page.evaluate(() => ({ step: document.getElementById('islGuideStep').textContent, title: document.getElementById('islPanelTitle').textContent, text: document.getElementById('islGuideText').textContent }));
      if (!a.step.startsWith('第 1／4 站') || a.title !== '第一次對話') note(`導覽第 1 站不對：${JSON.stringify(a)}`);
      if (!a.text.includes('我替你做的決定：')) note('阿卡的台詞少了「我替你做的決定」');
      const g0 = await page.evaluate(() => window.__island.guidePos());
      await page.click('#islGuideNext'); await sleep(1600);
      await page.waitForFunction(() => document.getElementById('islFigImg').complete, { timeout: 5000 }).catch(() => {});
      const b = await page.evaluate(() => ({ t: document.getElementById('islPanelTitle').textContent, g: window.__island.guidePos(), img: document.getElementById('islFigImg').naturalWidth, href: document.getElementById('islFigGo').getAttribute('href') }));
      if (b.t !== 'Lab 1 · 分群') note(`下一站不對：${b.t}`);
      if (!b.img) note('代表圖沒有載入');
      if (b.href !== '../lab1-cluster.html#kmeans-title') note(`代表圖連結錯誤：${b.href}`);
      if (Math.hypot(b.g.x - g0.x, b.g.z - g0.z) < 1) note('下一站後阿卡沒有移動'); else ok('導覽：阿卡沿路線移動，代表圖載入');
      await page.screenshot({ path: path.join(SHOT_DIR, 'tour.png') });
      await page.click('#islGuideEnd'); await sleep(150);
      await page.click('#islBubble'); await sleep(250);
      const r = await page.$$eval('#islGuideChoices .isl-choice b', e => e.map(x => x.textContent));
      if (r[0] !== '接著走') note(`沒有問要不要接著走：${r}`); else ok('導覽可續走');
      await page.click('.isl-choice'); await sleep(500);
      await page.evaluate(() => document.querySelector('.isl-item[data-stem="git-safety"] .isl-link').click()); await sleep(200);
      const e = await page.evaluate(() => ({ g: document.getElementById('islGuide').hidden, n: document.getElementById('islGuideNav').hidden }));
      if (!e.g || !e.n) note('導覽中改選別頁後對話列沒有收起');
      await page.keyboard.press('Escape');
      await page.evaluate(k => localStorage.setItem(k, JSON.stringify({ route: 'math', i: 1 })), KEY('tour:v1'));
      await page.click('#islBubble'); await sleep(200); await page.click('.isl-choice'); await sleep(400);
      await page.click('#islGuideNext'); await sleep(200);
      const bye = await page.$eval('#islGuideText', x => x.textContent);
      if (!bye.includes('走完了')) note(`走完路線的台詞不對：${bye}`); else ok('走完路線');
      await page.click('.isl-choice'); await sleep(100);
    }

    /* 繪製呼叫、閒置 */
    const calls = await page.evaluate(() => window.__island.stats().calls);
    if (calls > 50) note(`每幀繪製呼叫過多：${calls}（目標 ≤ 50）`); else ok(`繪製呼叫 ${calls}`);
    await page.evaluate(() => { window.__islandIdleMs = 1200; });
    let d0 = 0, d1 = -1;
    for (let i = 0; i < 12 && d1 !== d0; i++) { d0 = await page.evaluate(() => window.__island.stats().draws); await sleep(1000); d1 = await page.evaluate(() => window.__island.stats().draws); }
    if (d1 !== d0) note('閒置後仍在繪製'); else ok('閒置時停止繪製');
    await page.mouse.move(400, 400); await page.mouse.move(420, 410); await sleep(1000);
    if ((await page.evaluate(() => window.__island.stats().draws)) <= d1) note('有操作後沒有恢復繪製'); else ok('有操作就恢復');
    await page.evaluate(() => { window.__islandIdleMs = 0; localStorage.clear(); });

    await layout(page, '桌面 3D');
    await page.setViewport({ width: 390, height: 844 }); await sleep(1000);
    await page.click('#islReset'); await sleep(1100);
    await layout(page, '手機 3D');
    await page.screenshot({ path: path.join(SHOT_DIR, '3d_mobile.png') });
    const mpos = await page.evaluate(() => window.__island.screenPos('lab3-notes'));
    await page.mouse.click(mpos.x, mpos.y); await sleep(1100);
    if ((await page.$eval('#islPanel', e => e.hidden))) note('手機點地標沒有開面板');
    await page.screenshot({ path: path.join(SHOT_DIR, '3d_mobile_panel.png') });
    await page.click('#islPanelClose');
    await page.click('#islCompare'); await sleep(200);
    if (await page.$('#cmpBody .cmp-gate')) { await page.click('#cmpBody .cmp-gate button'); await sleep(100); }
    await page.screenshot({ path: path.join(SHOT_DIR, 'cmp_mobile.png') });
    const mo = await page.evaluate(() => { const d = document.getElementById('cmpDialog'); return d.scrollWidth - d.clientWidth; });
    if (mo > 1) note(`手機對照面板橫向溢出 ${mo}px`);
    errors.forEach(e => note('console：' + e));
    await page.close();
  }

  /* ═ (b)(c) 退回 2D ═ */
  for (const [mode, label] of [['cdn', 'CDN 失效'], ['nogl', '無 WebGL']]) {
    console.log(`(${mode}) ${label}`);
    const { page, errors } = await open(mode);
    await page.setViewport({ width: 1280, height: 900 });
    await page.goto(URL_, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
    await sleep(2500);
    const r = await layout(page, label + '桌面');
    if (r.webgl) note(`${label}時仍進入 3D`);
    if (!(await page.$eval('#islStage', e => e.hidden))) note(`${label}時畫布沒有隱藏`);
    if (await page.evaluate(() => document.documentElement.classList.contains('gl-pending'))) note(`${label}時 gl-pending 沒有移除`);
    await page.screenshot({ path: path.join(SHOT_DIR, `2d_${mode}.png`), fullPage: true });
    // 2D 也能用對照面板
    await page.click('#islCompare'); await sleep(150);
    if (!(await page.$eval('#cmpDialog', e => e.open)) || !(await page.$('#cmpBody .cmp-gate'))) note(`${label}時對照面板開不起來`);
    await page.keyboard.press('Escape'); await sleep(80);
    // 2D 也能猜題：卡片上的「先猜一題」
    const nq = await page.$$eval('.isl-quizbtn', e => e.filter(x => x.offsetParent !== null).length);
    if (nq !== 15) note(`${label}時「先猜一題」按鈕只有 ${nq} 個可見`);
    await page.click('.isl-item[data-stem="git-safety"] .isl-quizbtn'); await sleep(150);
    const q2 = await page.evaluate(() => ({ panel: !document.getElementById('islPanel').hidden, quiz: !document.getElementById('islQuiz').hidden, t: document.getElementById('islPanelTitle').textContent }));
    if (q2.panel && q2.quiz) { await (await page.$$('.isl-opt'))[0].click(); await sleep(60); }
    const why = await page.$eval('#islQuizWhy', e => !e.hidden);
    if (!q2.panel || !q2.quiz || !why) note(`${label}時猜題無法使用：${JSON.stringify(q2)}`); else ok(`${label}：卡片上的「先猜一題」可以作答`);
    await page.keyboard.press('Escape');
    await page.setViewport({ width: 390, height: 844 }); await sleep(300);
    await layout(page, label + '手機');
    errors.forEach(e => note(`${label} console：` + e));
    ok(`${label}：退回 2D`);
    await page.close();
  }

  /* ═ (show) 會場投影版：?show ═ */
  console.log('(show) 會場投影版');
  {
    const { page, errors } = await open('gl');
    await page.setViewport({ width: 1920, height: 1080 });
    await page.evaluateOnNewDocument(() => { window.__islandIdleMs = 1500; });   // 閒置門檻調短：投影版要照樣一直轉
    await page.goto(URL_ + '?show', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForSelector('body.webgl-ready', { timeout: 40000 }).catch(() => note('投影版沒有進入 3D'));
    await page.waitForFunction(() => !document.documentElement.classList.contains('gl-pending'), { timeout: 40000 }).catch(() => {});
    await sleep(2500);
    const v = await page.evaluate(() => {
      const vis = s => { const e = document.querySelector(s); return !!e && getComputedStyle(e).display !== 'none' && e.getBoundingClientRect().width > 0; };
      const st = document.getElementById('islStage').getBoundingClientRect();
      return { bar: vis('.isl-bar'), list: vis('.isl-list'), bubble: vis('#islBubble'), night: vis('#islNight'), title: vis('.show-title'), card: vis('.show-card'),
        qr: document.querySelector('.show-card img').naturalWidth, full: Math.round(st.width) === innerWidth && Math.round(st.height) === innerHeight };
    });
    if (v.bar || v.list || v.bubble || v.night) note(`投影版還看得到操作介面：${JSON.stringify(v)}`);
    if (!v.title || !v.card || !v.qr || !v.full) note(`投影版的標題卡、QR 或全螢幕舞台不對：${JSON.stringify(v)}`);
    else ok('投影版：只留全螢幕的島、標題卡和 QR code');
    const p0 = await page.evaluate(() => window.__island.screenPos('index'));
    await sleep(3000);                                   // 已超過調短的閒置門檻
    const p1 = await page.evaluate(() => window.__island.screenPos('index'));
    if (Math.hypot(p1.x - p0.x, p1.y - p0.y) < 15) note('投影版沒有自己慢慢轉，或閒置後停了'); else ok(`投影版：沒人操作也一直慢慢轉（3 秒移動 ${Math.round(Math.hypot(p1.x - p0.x, p1.y - p0.y))} px）`);
    await page.screenshot({ path: path.join(SHOT_DIR, 'show_1920.png') });
    errors.forEach(e => note('投影版 console：' + e));
    await page.close();
  }
  {
    const { page, errors } = await open('nogl');
    await page.setViewport({ width: 1920, height: 1080 });
    await page.goto(URL_ + '?show', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await sleep(1500);
    const r = await page.evaluate(() => {
      const b = document.querySelector('.show-card').getBoundingClientRect();
      return { nogl: document.documentElement.classList.contains('show-nogl'), cx: (b.left + b.right) / 2 / innerWidth, w: b.width / innerWidth };
    });
    if (!r.nogl || Math.abs(r.cx - .5) > .05 || r.w < .25) note(`投影版跑不動 3D 時，QR 沒有放大置中：${JSON.stringify(r)}`); else ok('投影版跑不動 3D 時，QR code 放大置中');
    await page.screenshot({ path: path.join(SHOT_DIR, 'show_nogl.png') });
    errors.forEach(e => note('投影版（無 WebGL）console：' + e));
    await page.close();
  }

  /* ═ 代表圖深連結的落點 ═ */
  console.log('(deep links)');
  {
    const figs = await (async () => { const p = await browser.newPage(); await p.goto(URL_, { waitUntil: 'domcontentloaded' }); const d = await p.evaluate(() => JSON.parse(document.getElementById('island-data').textContent).pages.filter(x => x.fig).map(x => x.fig.href)); await p.close(); return d; })();
    if (figs.length !== LABS.length) note(`代表圖應有 ${LABS.length} 張，得到 ${figs.length}`);
    for (const href of figs) {
      const p = await browser.newPage();
      await p.setViewport({ width: 1280, height: 900 });
      await p.goto('file://' + path.resolve(ROOT, 'island', href), { waitUntil: 'networkidle2', timeout: 60000 }).catch(() => {});
      await sleep(2500);
      const r = await p.evaluate(id => { const e = document.getElementById(id), d = e.closest('details:not([open])'); return { top: Math.round(e.getBoundingClientRect().top), hidden: !!d }; }, href.split('#')[1]);
      const good = !r.hidden && r.top > -40 && r.top < 400;
      console.log(`  ${good ? '✓' : '✗'} ${href.replace('../', '')}  top=${r.top}${r.hidden ? ' 在收合區塊' : ''}`);
      if (!good) note(`${href} 落點偏移（top=${r.top}）`);
      await p.close();
    }
  }

  await browser.close();
  console.log(problems.length ? `\n${problems.length} 個問題` : '\n全部通過');
  process.exit(problems.length ? 1 : 0);
})();
