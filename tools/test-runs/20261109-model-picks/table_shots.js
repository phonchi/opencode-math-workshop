// Screenshot the "依記憶體挑起點" table of local-models.html at desktop and phone widths.
const path = require('path'), fs = require('fs');
const puppeteer = require(path.join(process.env.HOME, '.cache/selfstudy-node/node_modules/puppeteer-core'));
const chromeRoot = path.join(process.env.HOME, '.cache/puppeteer/chrome');
const versions = fs.readdirSync(chromeRoot).sort();
const CHROME = path.join(chromeRoot, versions[versions.length - 1], 'chrome-linux64', 'chrome');
const ROOT = path.resolve(__dirname, '../../..');
const OUT = path.join(__dirname, 'shots');

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  for (const width of [1280, 390]) {
    const tab = await browser.newPage();
    await tab.setViewport({ width, height: 900, deviceScaleFactor: 2 });
    await tab.goto('file://' + path.join(ROOT, 'local-models.html'), { waitUntil: 'load' });
    const handle = await tab.evaluateHandle(() => {
      const table = [...document.querySelectorAll('table')].find((t) => t.textContent.includes('候選模型'));
      const wrap = table.closest('.tw') || table;
      wrap.scrollIntoView({ block: 'center' });
      return wrap;
    });
    const box = await handle.boundingBox();
    const scroll = await tab.evaluate((el) => ({ scrollWidth: el.scrollWidth, clientWidth: el.clientWidth }), handle);
    await handle.screenshot({ path: path.join(OUT, `picks-table-${width}.png`) });
    console.log(width, 'table box', Math.round(box.width), 'x', Math.round(box.height), 'scroll', scroll);
    await tab.close();
  }
  await browser.close();
})();
