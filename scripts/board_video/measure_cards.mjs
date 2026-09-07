import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1600, height: 900 } });
await p.goto(pathToFileURL('G:/我的雲端硬碟/創作/影片創作/人魚島解說/人魚島黑板_全景.html').href);
await p.waitForTimeout(1200);
const sizes = await p.evaluate(() => {
  const out = {};
  document.querySelectorAll('.node').forEach((el, i) => {
    const id = Object.keys(window).length && el.querySelector('.ttl') ? el.querySelector('.ttl').textContent : i;
    out[id] = [el.offsetWidth, el.offsetHeight];
  });
  return out;
});
console.log(JSON.stringify(sizes, null, 0));
await b.close();
