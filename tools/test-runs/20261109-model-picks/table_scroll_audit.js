// For every page, at 390 px wide: how many tables scroll horizontally, and how many inline
// <code> elements inside table cells are split across lines (rendered on more than one line box).
const path = require('path'), fs = require('fs');
const puppeteer = require(path.join(process.env.HOME, '.cache/selfstudy-node/node_modules/puppeteer-core'));
const chromeRoot = path.join(process.env.HOME, '.cache/puppeteer/chrome');
const versions = fs.readdirSync(chromeRoot).sort();
const CHROME = path.join(chromeRoot, versions[versions.length - 1], 'chrome-linux64', 'chrome');
const ROOT = path.resolve(__dirname, '../../..');

(async () => {
  const pages = fs.readdirSync(ROOT).filter((f) => f.endsWith('.html'));
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  const totals = { tables: 0, scrolling: 0, codes: 0, splitCodes: 0 };
  const rows = [];
  for (const file of pages) {
    const tab = await browser.newPage();
    await tab.setViewport({ width: 390, height: 900 });
    await tab.goto('file://' + path.join(ROOT, file), { waitUntil: 'load' });
    const r = await tab.evaluate(() => {
      const wraps = [...document.querySelectorAll('.tw')];
      const scrolling = wraps.filter((w) => w.scrollWidth > w.clientWidth + 1).length;
      const codes = [...document.querySelectorAll('td code, th code')];
      const split = codes.filter((c) => c.getClientRects().length > 1 && !/\s/.test(c.textContent.trim()));
      return { tables: wraps.length, scrolling, codes: codes.length, splitCodes: split.length,
               examples: split.slice(0, 3).map((c) => c.textContent) };
    });
    for (const k of Object.keys(totals)) totals[k] += r[k];
    if (r.scrolling || r.splitCodes) rows.push(`${file}: tables=${r.tables} scrolling=${r.scrolling} split-codes=${r.splitCodes} ${JSON.stringify(r.examples)}`);
    await tab.close();
  }
  await browser.close();
  console.log(rows.join('\n'));
  console.log('TOTAL', JSON.stringify(totals));
})();
