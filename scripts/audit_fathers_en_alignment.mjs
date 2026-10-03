// 稽核 /fathers 中英對照欄（中｜英）——直接跑 reader 用的 buildParallelColumns，量使用者實際看到的列。
// 與 audit_fathers_columns.mjs（三欄：原典欄）分工：這支只看英文欄。
//
//   zhOnly    中有字、英空的列（英文沒配到）
//   enOnly    英有字、中空的列（缺譯）
//   leadBad   兩邊段首節號都有、卻不一樣的列（錯位的最直接指標）
//   dupChunks 同一份英文整塊掛在好幾塊（舊病灶：每塊都掛整檔）
//
//   npx vite-node -c scripts/audit.vite.config.mjs scripts/audit_fathers_en_alignment.mjs [<uuid>]
//   EBOOK_CHUNKS_DIR="C:/nonexistent" … 強制驗 R2（兩邊都要驗）
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { resolve } from "node:path";
import { buildParallelColumns } from "~/lib/ebook-render";
import { normalizeSources } from "~/lib/multilang-sources";

const ROOT = resolve(import.meta.dirname, "..");
const DUP_MIN_CHARS = 500;
const LEAD = /^\s*(\d{1,3})\.\s/;

function loadEnv() {
  for (const line of readFileSync(resolve(ROOT, ".env"), "utf-8").split(/\r?\n/)) {
    const t = line.trim();
    if (!t || t.startsWith("#") || !t.includes("=")) continue;
    const i = t.indexOf("=");
    const k = t.slice(0, i).trim();
    if (!process.env[k]) process.env[k] = t.slice(i + 1).trim().replace(/^["']|["']$/g, "");
  }
}

async function loadChunks(id) {
  const dir = process.env.EBOOK_CHUNKS_DIR;
  if (dir) {
    try {
      return readFileSync(resolve(dir, `${id}.jsonl`), "utf-8").split(/\r?\n/)
        .filter((l) => l.trim()).map((l) => JSON.parse(l));
    } catch { /* 本機沒有就走 R2 */ }
  }
  const { S3Client, GetObjectCommand } = await import("@aws-sdk/client-s3");
  const cli = new S3Client({
    region: "auto", endpoint: process.env.R2_ENDPOINT,
    credentials: { accessKeyId: process.env.R2_ACCESS_KEY, secretAccessKey: process.env.R2_SECRET_KEY },
  });
  const res = await cli.send(new GetObjectCommand({ Bucket: process.env.R2_BUCKET, Key: `ebook-chunks/${id}.jsonl.gz` }));
  const buf = Buffer.from(await res.Body.transformToByteArray());
  return gunzipSync(buf).toString("utf-8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
}

const text = (h) => (h ?? "").replace(/<[^>]+>/g, "").replace(/&nbsp;|\u200b/g, " ").replace(/\{\{[ps]:[^}]*\}\}/g, "").trim();

async function auditBook(id) {
  const chunks = await loadChunks(id);
  let rows = 0, zhOnly = 0, enOnly = 0, both = 0, leadBad = 0, leadOk = 0;
  const seen = new Map();
  chunks.forEach((c, i) => {
    const norm = normalizeSources(c);
    const en = norm.sources.en ?? c.source_text ?? "";
    if (!en.trim()) return;
    if (en.length >= DUP_MIN_CHARS) {
      const key = `${en.length}|${en.slice(0, 120)}`;
      seen.set(key, (seen.get(key) ?? 0) + 1);
    }
    const cols = buildParallelColumns(c.content ?? "", { en }, ["en"], i);
    for (const r of cols.rows) {
      rows++;
      const z = text(r.zh), e = text(r.cols.en);
      if (z && !e) zhOnly++;
      else if (!z && e) enOnly++;
      else if (z && e) {
        both++;
        const a = z.match(LEAD), b = e.match(LEAD);
        if (a && b) { if (a[1] === b[1]) leadOk++; else leadBad++; }
      }
    }
  });
  const dupChunks = [...seen.values()].filter((n) => n > 1).reduce((a, n) => a + n - 1, 0);
  return { chunks: chunks.length, rows, zhOnly, enOnly, both, leadBad, leadOk, dupChunks };
}

loadEnv();
const ids = process.argv[2] ? [process.argv[2]]
  : readFileSync(resolve(ROOT, "output/fathers_gap/ids37.txt"), "utf-8").split(/\s+/).filter(Boolean);
console.log(`取源＝${process.env.EBOOK_CHUNKS_DIR ? "本機 Drive（讀不到才退 R2）" : "R2"}；${ids.length} 卷\n`);
const tot = { rows: 0, zhOnly: 0, enOnly: 0, leadBad: 0, leadOk: 0, dupChunks: 0 };
for (const id of ids) {
  try {
    const r = await auditBook(id);
    for (const k of Object.keys(tot)) tot[k] += r[k];
    const p = (n) => (r.rows ? ((n / r.rows) * 100).toFixed(1) : "0.0");
    const lead = r.leadOk + r.leadBad;
    console.log(`${id.slice(0, 8)}  列=${String(r.rows).padStart(6)}  中有英空=${p(r.zhOnly).padStart(5)}%  英有中空=${p(r.enOnly).padStart(5)}%` +
      `  節號一致=${lead ? ((r.leadOk / lead) * 100).toFixed(1) : "—"}%（${lead}）  整塊重複掛=${r.dupChunks}`);
  } catch (e) {
    console.log(`✗ ${id.slice(0, 8)}  ${String(e.message).slice(0, 80)}`);
  }
}
const lead = tot.leadOk + tot.leadBad;
console.log(`\n合計 列=${tot.rows}  中有英空=${((tot.zhOnly / tot.rows) * 100).toFixed(1)}%  英有中空=${((tot.enOnly / tot.rows) * 100).toFixed(1)}%` +
  `  節號一致=${((tot.leadOk / lead) * 100).toFixed(1)}%（${lead} 列）  整塊重複掛=${tot.dupChunks}`);
