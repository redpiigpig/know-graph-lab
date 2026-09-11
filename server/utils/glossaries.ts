import fs from "node:fs";
import path from "node:path";

/**
 * 佛學辭典的查詢後端。十二部、10.3 萬條、28.6 MB JSONL，正本在 Drive
 * `_corpus/dila-glossaries/`（抓取與解析見 scripts/dila_glossaries_fetch.py）。
 *
 * 為什麼不進 DB：10 萬列帶釋義約 30 MB 文字，而這個專案的 Supabase 曾因大表超量
 * 把整站鎖掉（2026-07-08，bible_verses 已 DROP 搬 Drive）。規矩是新的大內容表一律
 * file-backed，所以這裡照聖經經文那一套：首次查詢才讀進記憶體，之後常駐。
 *
 * ⚠️ 讀不到就回空陣列、不要丟例外。Drive 卡住時 G: 會整個消失（見 CLAUDE.md），
 * 那時該讓頁面顯示「查不到」而不是 500。
 */

export interface GlossaryEntry {
  term: string;
  variants?: string[];
  domain?: string[];
  definition?: string;
  langs?: Record<string, string>;
}
export interface GlossaryHit extends GlossaryEntry {
  code: string;
}

// 代號 → 中文書名。索引 JSON 也有，但那是 repo 裡的檔，這裡只要顯示用的短名。
export const GLOSSARY_NAMES: Record<string, string> = {
  DFB: "丁福保《佛學大辭典》",
  SHH: "蘇慧廉—何樂益《中國佛教術語辭典》",
  JHK: "霍普金斯藏—梵—英辭典",
  PLC: "巴利—漢語辭典",
  MVP: "《翻譯名義大集》",
  NSL: "釋智諭《南山律學辭典》",
  ADV: "辛嶋靜志《比丘威儀法詞典》",
  KDR: "辛嶋靜志《正法華經詞典》",
  KKJ: "辛嶋靜志《妙法蓮華經詞典》",
  KLS: "辛嶋靜志《道行般若經詞典》",
  DAT: "辛嶋靜志《「長阿含経」の原語の研究》",
  PTG: "《五譯合璧集要》",
};

let cache: Map<string, GlossaryEntry[]> | null = null;

function dir(): string {
  const root = useRuntimeConfig().corpusRoot as string;
  return path.join(root, "dila-glossaries");
}

/** 首次呼叫才載入；之後直接用記憶體那一份。 */
export function loadGlossaries(): Map<string, GlossaryEntry[]> {
  if (cache) return cache;
  const out = new Map<string, GlossaryEntry[]>();
  let files: string[] = [];
  try {
    files = fs.readdirSync(dir()).filter((f) => f.endsWith(".jsonl"));
  } catch {
    cache = out; // Drive 不在：記住空的，別每次請求都去戳一次檔案系統
    return out;
  }
  for (const f of files) {
    const code = path.basename(f, ".jsonl");
    try {
      const rows = fs
        .readFileSync(path.join(dir(), f), "utf8")
        .split("\n")
        .filter(Boolean)
        .map((l) => JSON.parse(l) as GlossaryEntry);
      out.set(code, rows);
    } catch {
      /* 單一部壞掉不該讓整批查不了 */
    }
  }
  cache = out;
  return out;
}

export function glossaryStats() {
  const g = loadGlossaries();
  return [...g.entries()]
    .map(([code, rows]) => ({
      code,
      name: GLOSSARY_NAMES[code] ?? code,
      entries: rows.length,
    }))
    .sort((a, b) => b.entries - a.entries);
}

/**
 * 查詞。預設先比詞目、再比釋義——查「般若」時想要的是詞目叫般若的那幾條，
 * 不是釋義裡提過般若的幾千條。所以兩種命中要分開排序，不能混在一起。
 */
export function searchGlossaries(
  q: string,
  opts: { code?: string; limit?: number; inDefinition?: boolean } = {},
): { total: number; hits: GlossaryHit[] } {
  const query = (q ?? "").trim();
  if (!query) return { total: 0, hits: [] };
  const limit = Math.min(Math.max(opts.limit ?? 60, 1), 300);
  const lower = query.toLowerCase();
  const g = loadGlossaries();

  const exact: GlossaryHit[] = [];
  const prefix: GlossaryHit[] = [];
  const inTerm: GlossaryHit[] = [];
  const inDef: GlossaryHit[] = [];

  for (const [code, rows] of g) {
    if (opts.code && code !== opts.code) continue;
    for (const r of rows) {
      const t = (r.term ?? "").toLowerCase();
      if (t === lower) exact.push({ ...r, code });
      else if (t.startsWith(lower)) prefix.push({ ...r, code });
      else if (t.includes(lower)) inTerm.push({ ...r, code });
      else if (
        opts.inDefinition &&
        ((r.definition ?? "").toLowerCase().includes(lower) ||
          (r.variants ?? []).some((v) => v.toLowerCase().includes(lower)))
      ) {
        inDef.push({ ...r, code });
      }
    }
  }
  const all = [...exact, ...prefix, ...inTerm, ...inDef];
  return { total: all.length, hits: all.slice(0, limit) };
}
