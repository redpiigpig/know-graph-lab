// 稽核 /fathers 的三欄呈現 —— 直接跑 reader 用的那一支 buildParallelColumns，
// 量「使用者實際看到的列」，不另外寫一套判準。
//
// 🚨 為什麼不在 Python 端重寫一套：三欄對齊的真正邏輯在 lib/multilang-sources.ts
// 的 alignByAnchors（章節號／{{p:NNN}} 頁碼錨點 → 最長遞增鏈 → 區間填充），對不上
// 才退回逐位配對。在外面用「兩欄段落數相不相等」近似它，會把十九本全判成壞掉
// ——我第一版就是這樣，全紅，而那是判準錯不是資料錯。凡是要問「頁面呈現對不對」，
// 就跑呈現頁面的那支函式，不要複寫一份。
//
// 量三個數字，全部取自 buildParallelColumns 的真實輸出：
//   zhOnly     繁中有字、原典欄空白的列（原典沒補到這一列）
//   srcOnly    原典有字、繁中空白的列（溢出）
//   dup        同一塊原典文字被掛在好幾段上 —— 這是實際查到的病因：整卷原典
//              沒有切片，原封不動塞進該卷每一段。希拉里《論三位一體》一塊
//              48,823 字的拉丁文掛在連續 36 段上，讀者翻到卷六任何一頁，
//              原典欄都是整卷。
//              🚨 比長度要設下限，否則兩封信引同一句經文（23–42 字）也會被算成
//              重複 —— 巴西流《書信集》就是這樣誤報過 5 組。
//
//   npx vite-node -c scripts/audit.vite.config.mjs scripts/audit_fathers_columns.mjs
//   npx vite-node -c scripts/audit.vite.config.mjs scripts/audit_fathers_columns.mjs <uuid>
//
// 走 vite-node 並自帶 vite 設定，是為了解析 `~/lib` 別名（vitest 那邊的別名由
// @nuxt/test-utils 提供，vite-node 直接跑腳本時沒有那一層）。
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { resolve } from "node:path";
import { buildParallelColumns } from "~/lib/ebook-render";
import { normalizeSources } from "~/lib/multilang-sources";

const ROOT = resolve(import.meta.dirname, "..");
const DUP_MIN_CHARS = 500; // 低於此的重複多半是共用的引經短句，不是整塊沒切

function loadEnv() {
  for (const line of readFileSync(resolve(ROOT, ".env"), "utf-8").split(/\r?\n/)) {
    const t = line.trim();
    if (!t || t.startsWith("#") || !t.includes("=")) continue;
    const i = t.indexOf("=");
    const k = t.slice(0, i).trim();
    if (!process.env[k]) process.env[k] = t.slice(i + 1).trim().replace(/^["']|["']$/g, "");
  }
}

// 取源順序與 server/utils/ebook-chunks.ts 一致：**先本機 Drive，再 R2**。
// 🚨 只讀 R2 會量到過期的東西。修完本機 JSONL、還沒同步 R2 時跑稽核，數字會
//    一動也不動，看起來像「修了沒用」——實際上是量錯了地方。
async function loadChunks(id) {
  const dir = process.env.EBOOK_CHUNKS_DIR;
  if (dir) {
    const local = resolve(dir, `${id}.jsonl`);
    try {
      return readFileSync(local, "utf-8").split(/\r?\n/)
        .filter((l) => l.trim()).map((l) => JSON.parse(l));
    } catch { /* 本機沒有就走 R2 */ }
  }
  const { S3Client, GetObjectCommand } = await import("@aws-sdk/client-s3");
  const cli = new S3Client({
    region: "auto",
    endpoint: process.env.R2_ENDPOINT,
    credentials: {
      accessKeyId: process.env.R2_ACCESS_KEY,
      secretAccessKey: process.env.R2_SECRET_KEY,
    },
  });
  const res = await cli.send(new GetObjectCommand({
    Bucket: process.env.R2_BUCKET,
    Key: `ebook-chunks/${id}.jsonl.gz`,
  }));
  const buf = Buffer.from(await res.Body.transformToByteArray());
  return gunzipSync(buf).toString("utf-8").split("\n")
    .filter((l) => l.trim()).map((l) => JSON.parse(l));
}

function originalIds() {
  const vue = readFileSync(resolve(ROOT, "pages/fathers/index.vue"), "utf-8");
  const m = vue.match(/ORIGINAL_IDS\s*=\s*new Set\(\[([\s\S]*?)\]\)/);
  if (!m) return [];
  return [...m[1].matchAll(/['"]([0-9a-f-]{36})['"]/g)].map((x) => x[1]);
}

async function auditBook(id) {
  const chunks = await loadChunks(id);
  let withOrig = 0, zhOnly = 0, srcOnly = 0, rows = 0;
  const seen = new Map();
  chunks.forEach((c, i) => {
    const norm = normalizeSources(c);
    const langs = (norm.source_order ?? []).filter((l) => l !== "en" && norm.sources?.[l]?.trim());
    if (!langs.length) return;
    withOrig++;
    // en 也要查。🚨 希拉里那本英文欄同樣是整卷重複（359/401 段），而且早於
    // 原典欄就存在——只修原典欄，對照頁的英文欄照樣整卷。
    for (const lang of [...langs, "en"]) {
      const txt = norm.sources[lang] ?? "";
      if (txt.length < DUP_MIN_CHARS) continue;
      const key = `${lang}|${txt.length}|${txt.slice(0, 120)}`;
      if (!seen.has(key)) {
        seen.set(key, { lang, len: txt.length, at: [], path: c.chapter_path ?? "" });
      }
      seen.get(key).at.push(i);
    }
    const cols = buildParallelColumns(c.content ?? "", norm.sources, langs, i);
    for (const r of cols.rows) {
      rows++;
      const src = langs.map((l) => r.cols[l] ?? "").join("").trim();
      const zh = (r.zh ?? "").trim();
      if (zh && !src) zhOnly++;
      if (!zh && src) srcOnly++;
    }
  });
  const dupGroups = [...seen.values()].filter((g) => g.at.length > 1);
  const dupChunks = dupGroups.reduce((a, g) => a + g.at.length - 1, 0);
  return { chunks: chunks.length, withOrig, rows, zhOnly, srcOnly, dupGroups, dupChunks };
}

loadEnv();
const only = process.argv[2];
const ids = only ? [only] : originalIds();
const srcLabel = process.env.EBOOK_CHUNKS_DIR ? "本機 Drive（讀不到才退 R2）" : "R2";
console.log(`ORIGINAL_IDS ${ids.length} 本；取源＝${srcLabel}\n`);
let bad = 0;
for (const id of ids) {
  try {
    const r = await auditBook(id);
    const pct = (n) => (r.rows ? ((n / r.rows) * 100).toFixed(1) : "0.0");
    const flag = r.dupChunks
      ? `  ⚠ 整塊原典沒切片：${r.dupGroups.length} 組害到 ${r.dupChunks} 段`
      : "";
    if (r.dupChunks) bad++;
    console.log(
      `${flag ? "!" : "✓"} ${id.slice(0, 8)}  有原典段=${String(r.withOrig).padStart(3)}` +
      `  列=${String(r.rows).padStart(5)}` +
      `  中有原典空=${pct(r.zhOnly)}%  原典溢出=${pct(r.srcOnly)}%${flag}`
    );
    for (const g of r.dupGroups.sort((a, b) => b.at.length - a.at.length).slice(0, 3)) {
      console.log(
        `      同一塊 ${g.lang}（${g.len} 字）掛在 ${g.at.length} 段 ` +
        `#${g.at.slice(0, 6).join(",#")}${g.at.length > 6 ? "…" : ""}  ${g.path.slice(0, 50)}`
      );
    }
  } catch (e) {
    console.log(`✗ ${id.slice(0, 8)}  ${String(e.message).slice(0, 80)}`);
  }
}
console.log(`\n整塊原典沒切片的書：${bad}/${ids.length}`);
