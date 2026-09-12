#!/usr/bin/env node
/* 逐頁量每個 pre / table 是否被裁切（scrollWidth > clientWidth）。
 * 這是「截圖歪掉」那類問題的自動化把關。
 *
 * 用法：node tools/check_overflow.js [頁名...]
 *       BASE=https://... node tools/check_overflow.js   # 檢查線上版
 */
const path = require('path'), fs = require('fs');
const PPT = process.env.PPT_HOME || path.join(process.env.HOME, '.cache/selfstudy-node');
const puppeteer = require(path.join(PPT, 'node_modules', 'puppeteer-core'));
const ROOT = path.resolve(__dirname, '..');
const CHROME = process.env.CHROME_PATH || (() => {
  const b = path.join(process.env.HOME, '.cache/puppeteer/chrome');
  const d = fs.readdirSync(b).sort();
  return path.join(b, d[d.length - 1], 'chrome-linux64', 'chrome');
})();
const BASE = process.env.BASE || ('file://' + ROOT + '/');
const pages = process.argv.slice(2).length
  ? process.argv.slice(2)
  : fs.readdirSync(ROOT).filter(f => f.endsWith('.html')).map(f => f.replace(/\.html$/, ''));

// 桌機寬度才是重點：手機本來就得捲，但桌機被裁掉是設計問題
const VIEWS = [['desktop', 1440], ['laptop', 1280]];

(async () => {
  const br = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  const bad = [];
  for (const name of pages) {
    for (const [tag, w] of VIEWS) {
      const p = await br.newPage();
      await p.setViewport({ width: w, height: 1000 });
      await p.goto(BASE + (name === 'index' ? 'index.html' : name + '.html'),
        { waitUntil: 'networkidle0', timeout: 60000 });
      await new Promise(r => setTimeout(r, 1200));
      const hits = await p.evaluate(() => {
        const out = [];
        document.querySelectorAll('pre, .tw').forEach(el => {
          const over = el.scrollWidth - el.clientWidth;
          if (over > 1) {
            const t = (el.innerText || '').trim().split('\n')[0].slice(0, 46);
            out.push({ kind: el.tagName === 'PRE' ? (el.className || 'pre') : 'table',
                       over, txt: t });
          }
        });
        return out;
      });
      hits.forEach(h => bad.push(`[${name}/${tag}] ${h.kind} 超出 ${h.over}px — ${h.txt}`));
      await p.close();
    }
    process.stdout.write('.');
  }
  await br.close();
  console.log('\n');
  if (bad.length) {
    console.log('被裁切的區塊：');
    bad.forEach(b => console.log('  ' + b));
    process.exit(1);
  }
  console.log('  PASS — 桌機寬度下沒有任何 pre 或表格被裁切');
})().catch(e => { console.error(e); process.exit(2); });
