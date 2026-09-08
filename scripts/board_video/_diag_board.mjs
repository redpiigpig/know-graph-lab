// 把無限黑板逐格畫出來，直接 pipe 進 ffmpeg 成片（不落地成幾萬張圖）。
//
//   node render.mjs                       # 全片
//   node render.mjs --to 35 --out 樣片.mp4 # 只出前 35 秒
//   node render.mjs --nosub               # 不燒字幕（正式版）
//
import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PROJ = 'G:\\我的雲端硬碟\\創作\\影片創作\\人魚島解說';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i < 0 ? d : argv[i + 1]; };
const flag = (k) => argv.includes('--' + k);

const fps = Number(arg('fps', 30));
const from = Number(arg('from', 0));
const noSub = flag('nosub');
const theme = arg('theme', 'chalk');   // chalk 綠黑板／paper 手帳／neon 知識圖譜
const outName = arg('out', noSub ? '人魚島解說_無字幕.mp4' : '人魚島解說_初版.mp4');

const data = JSON.parse(fs.readFileSync(path.join(PROJ, 'cues.json'), 'utf8'));
const to = Number(arg('to', data.total + 1.5));

// 節點配圖：公有領域圖照前綴配，開場與結語掛多馬豬
const PREFIX = { siren: '賽蓮', minotaur: '米諾陶洛斯', yamata: '八岐大蛇',
                 prometheus: '普羅米修斯', houji: '詩經生民', happyaku: '八百比丘尼' };
const pdDir = path.join(PROJ, '素材', '公有領域');
const dataUri = (p) => {
  const ext = path.extname(p).slice(1).toLowerCase();
  const mime = ext === 'png' ? 'image/png' : ext === 'webp' ? 'image/webp' : 'image/jpeg';
  return `data:${mime};base64,${fs.readFileSync(p).toString('base64')}`;
};
const images = {};
for (const n of data.nodes) {
  const key = PREFIX[n.asset];
  if (!key || !fs.existsSync(pdDir)) continue;
  const hit = fs.readdirSync(pdDir).find((f) => f.startsWith(key + '_'));
  if (hit) images[n.id] = dataUri(path.join(pdDir, hit));
}
// 使用者自備的素材優先：這些比公有領域圖對題得多
const own = {
  N01: path.join(PROJ, '素材', '劇照', '作者被說毫無人性.jpg'),   // 「毫無人性」那句的出處
  N02: path.join(PROJ, '素材', '劇照', '電影劇照.webp'),
  N20: path.join(PROJ, '素材', '劇照', '電影劇照.webp'),
  N73: path.join(PROJ, '素材', '多馬豬', '多馬豬_卡通.png'),
};
const mascots = ['N73'];
for (const [id, f] of Object.entries(own)) if (fs.existsSync(f)) images[id] = dataUri(f);

// 線稿圖示：整段 SVG 直接塞進 DOM，才能一筆一筆描出來
const iconDir = path.join(PROJ, '素材', '線稿');
const icons = {};
for (const n of data.nodes) {
  if (!n.icon) continue;
  const f = path.join(iconDir, n.icon + '.svg');
  if (fs.existsSync(f)) icons[n.id] = fs.readFileSync(f, 'utf8').replace(/<\?xml[^>]*>/, '');
}
const handFile = path.join(iconDir, '手_270D.svg');
const handUrl = fs.existsSync(handFile)
  ? 'data:image/svg+xml;base64,' + fs.readFileSync(handFile).toString('base64') : null;

const avatar = path.join(PROJ, '素材', '多馬豬', '多馬豬_圓形.png');
const mascotUrl = fs.existsSync(avatar) ? dataUri(avatar) : null;
const coverFile = path.join(PROJ, '素材', '封面', '影片封面.png');
const coverHold = Number(arg('cover', from === 0 ? 3.0 : 0));   // 只有從頭開始才放封面卡
const coverUrl = coverHold > 0 && fs.existsSync(coverFile) ? dataUri(coverFile) : null;


const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.join(HERE, 'board.html')).href);
await page.evaluate(([d, o]) => window.init(d, o), [data, { images, noSub: true, mascots, theme: 'paper', mascotUrl, coverUrl: null, coverHold: 0, icons, handUrl }]);
await page.waitForTimeout(500);
const rows = await page.evaluate(() => {
  const out = [];
  const seen = {};
  S.data.cues.forEach(c => { if (seen[c.node] === undefined) seen[c.node] = c; });
  Object.values(seen).forEach(c => {
    const n = S.nodes[c.node];
    window.seek(c.t + c.dur * 0.9);
    const r = S.els[n.id].getBoundingClientRect();
    out.push({ id: n.id, specW: n.w, measW: n._w, specH: n.h, measH: n._h,
               left: Math.round(r.left), right: Math.round(r.right),
               top: Math.round(r.top), bottom: Math.round(r.bottom) });
  });
  return out;
});
console.log(JSON.stringify(rows));
await browser.close();
