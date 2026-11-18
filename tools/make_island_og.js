#!/usr/bin/env node
/* 由實際的 3D 全景產生 LINE 與社群預覽圖 island/og.png（1200×630），全站各頁共用。
 * 畫面只有島、站名和左上角的工作坊名稱。產生後用 pngquant 壓縮：
 *   node tools/make_island_og.js && pngquant --force --skip-if-larger --quality 70-90 --output island/og.png island/og.png
 * 島的構圖或地標改了再重跑，結果要 commit。puppeteer-core 裝在 ~/.cache/selfstudy-node。 */
const path = require('path'), fs = require('fs');
const PPT_HOME = process.env.PPT_HOME || path.join(process.env.HOME, '.cache/selfstudy-node');
const puppeteer = require(path.join(PPT_HOME, 'node_modules', 'puppeteer-core'));
const ROOT = path.resolve(__dirname, '..');
const base = path.join(process.env.HOME, '.cache/puppeteer/chrome');
const dirs = fs.readdirSync(base).sort();
const CHROME = process.env.CHROME_PATH || path.join(base, dirs[dirs.length - 1], 'chrome-linux64', 'chrome');
const OUT = path.join(ROOT, 'island', 'og.png');

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 630 });
  await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);   // 不要自轉、不要輪播：固定在初始全景
  await page.evaluateOnNewDocument(() => {
    document.addEventListener('DOMContentLoaded', () => {
      const s = document.createElement('style');
      s.textContent = `.isl-bar,.isl-list,.isl-jumps,.isl-hint,.isl-bubble,.isl-night{display:none !important;}
        .isl-main{display:block !important;height:630px !important;}
        .isl-stage{height:630px !important;}
        .og-title{position:absolute;z-index:5;left:28px;top:24px;padding:.55rem 1.15rem;color:#fff;border-radius:8px;background:rgba(27,27,43,.88);}
        .og-title b{display:block;font:900 46px/1.25 'Noto Serif TC',serif;letter-spacing:.06em;}
        .og-title span{font:500 22px/1.4 system-ui,'Noto Sans CJK TC',sans-serif;}`;
      document.head.appendChild(s);
      const t = document.createElement('div');
      t.className = 'og-title';
      t.innerHTML = '<b>AI Agent × 數學</b><span>OpenCode 體驗工作坊 · 3D 課程島</span>';
      document.getElementById('islStage').appendChild(t);
    });
  });
  await page.goto('file://' + path.join(ROOT, 'island', 'index.html'), { waitUntil: 'networkidle2', timeout: 60000 });
  await page.waitForFunction(() => !document.documentElement.classList.contains('gl-pending') && document.body.classList.contains('webgl-ready'), { timeout: 60000 });
  await page.evaluate(() => window.dispatchEvent(new Event('resize')));
  await new Promise(r => setTimeout(r, 3000));
  await page.screenshot({ path: OUT });
  await browser.close();
  console.log(`寫入 island/og.png（${(fs.statSync(OUT).size / 1024).toFixed(0)} KB，壓縮前）`);
})().catch(e => { console.error(e); process.exit(1); });
