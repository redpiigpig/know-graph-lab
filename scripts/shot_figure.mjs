// 把書稿某一節裡的 <figure> 單獨截圖出來看版面。SVG 一定要眼睛看過——
// 疊字、超出畫布、文字被裁，這些在 XML 層完全看不出來。
//
// 用法：node scripts/_shot_figure.mjs <節檔路徑> <輸出png> [第幾個figure，預設0]
//
// ⚠️ 必須放在 repo 內執行，否則 node 找不到 playwright（同 .airiti_fetch.mjs）。
// ⚠️ 寫這支檔案時不要用 bash heredoc——heredoc 會吃掉一層反斜線，
//    path.replace(/\\/g, '/') 會變成 replace(/\/g, '/') 而語法錯誤。
import { chromium } from 'playwright';
import { readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const [src, out, idxArg] = process.argv.slice(2);
if (!src || !out) {
  console.error('用法：node scripts/_shot_figure.mjs <節檔路徑> <輸出png> [figure 序號]');
  process.exit(1);
}
const idx = Number(idxArg || 0);
const figs = readFileSync(src, 'utf8').match(/<figure[\s\S]*?<\/figure>/g) || [];
if (!figs[idx]) {
  console.error(`找不到第 ${idx} 個 <figure>（該檔共 ${figs.length} 個）`);
  process.exit(1);
}

const html = join(tmpdir(), `_fig_${Date.now()}.html`);
writeFileSync(
  html,
  '<!doctype html><meta charset=utf-8>'
    + '<body style="margin:0;padding:20px;background:#fff;width:920px;'
    + 'font-family:system-ui,\'Noto Sans TC\',sans-serif">'
    + figs[idx] + '</body>',
  'utf8',
);

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 980, height: 900 }, deviceScaleFactor: 1.5 });
await p.goto(pathToFileURL(html).href);
await p.waitForTimeout(350);
await p.locator('figure').screenshot({ path: out });
await b.close();
console.log(`已截圖 → ${out}（該節共 ${figs.length} 個 figure）`);
