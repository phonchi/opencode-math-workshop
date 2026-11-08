// Screenshot specific pre.cmd blocks at desktop and phone widths; report where each line's
// first character starts and how tall each line block is.
const path = require('path'), fs = require('fs');
const puppeteer = require(path.join(process.env.HOME, '.cache/selfstudy-node/node_modules/puppeteer-core'));
const chromeRoot = path.join(process.env.HOME, '.cache/puppeteer/chrome');
const versions = fs.readdirSync(chromeRoot).sort();
const CHROME = path.join(chromeRoot, versions[versions.length - 1], 'chrome-linux64', 'chrome');
const ROOT = path.resolve(__dirname, '../../..');
const OUT = path.join(__dirname, 'element-shots');
// [page, text the block must contain (null = first multi-line block with a wrapped line), viewport width]
const cases = [
  ['local-models', 'ollama --version', 1280],
  ['local-models', 'ollama --version', 390],
  ['git-safety', null, 390],
  ['prep', null, 390],
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  for (const [page, needle, width] of cases) {
    const tab = await browser.newPage();
    await tab.setViewport({ width, height: 900, deviceScaleFactor: 2 });
    await tab.goto('file://' + path.join(ROOT, page + '.html'), { waitUntil: 'load' });
    const index = await tab.evaluate((needle) => {
      const blocks = [...document.querySelectorAll('pre.cmd')];
      if (needle) return blocks.findIndex((b) => b.textContent.includes(needle));
      return blocks.findIndex((b) => {
        const lines = [...b.querySelectorAll('.ln')];
        return lines.length > 1 && lines.some((l) => l.getBoundingClientRect().height > 40);
      });
    }, needle);
    if (index < 0) { console.log(page, width, 'no matching block'); await tab.close(); continue; }
    const info = await tab.evaluate((i) => {
      const block = document.querySelectorAll('pre.cmd')[i];
      block.scrollIntoView({ block: 'center' });
      return [...block.querySelectorAll('.ln')].map((line) => {
        const text = line.firstChild;
        if (!text || !text.textContent.trim()) return 'blank/' + Math.round(line.getBoundingClientRect().height);
        const range = document.createRange();
        range.setStart(text, 0); range.setEnd(text, 1);
        return Math.round(range.getBoundingClientRect().left) + '/' + Math.round(line.getBoundingClientRect().height);
      }).join(' ');
    }, index);
    const element = (await tab.$$('pre.cmd'))[index];
    const file = `${page}-${width}-block${index}.png`;
    await element.screenshot({ path: path.join(OUT, file) });
    console.log(page, width, 'block', index, 'left/height per line:', info, '->', file);
    await tab.close();
  }
  await browser.close();
})();
