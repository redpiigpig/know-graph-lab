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
const mascot = path.join(PROJ, '素材', '多馬豬', '多馬豬.png');
const mascots = [];
if (fs.existsSync(mascot)) { const u = dataUri(mascot); images.N01 = u; images.N73 = u; mascots.push('N01', 'N73'); }

const ff = spawn('ffmpeg', [
  '-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
  '-movflags', '+faststart', path.join(PROJ, 'out', outName),
], { stdio: ['pipe', 'ignore', 'pipe'] });
let ffErr = '';
ff.stderr.on('data', (d) => { ffErr = (ffErr + d.toString()).slice(-2000); });

const browser = await chromium.launch({
  args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text'],
});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.join(HERE, 'board.html')).href);
await page.evaluate(([d, o]) => window.init(d, o), [data, { images, noSub, mascots, theme }]);
await page.waitForTimeout(400);

const total = Math.ceil((to - from) * fps);
const t0 = Date.now();
for (let f = 0; f < total; f++) {
  const t = from + f / fps;
  await page.evaluate((tt) => window.seek(tt), t);
  const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  if (f % (fps * 10) === 0) {
    const done = (f + 1) / total;
    const eta = ((Date.now() - t0) / 1000 / Math.max(done, 1e-6)) * (1 - done);
    process.stdout.write(`\r  ${(done * 100).toFixed(1)}%  影片時間 ${t.toFixed(0)}s  剩約 ${(eta / 60).toFixed(1)} 分   `);
  }
}
ff.stdin.end();
await browser.close();
const code = await new Promise((r) => ff.on('close', r));
console.log(`\n${code === 0 ? '完成' : 'ffmpeg 失敗\n' + ffErr}：${path.join(PROJ, 'out', outName)}`);
