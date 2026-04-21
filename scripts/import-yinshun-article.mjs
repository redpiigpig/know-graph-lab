/**
 * Create article project「印順導師人間佛教思想的傳承與實踐」+ project chapters,
 * import stores/印順學與人間佛教.csv: attach excerpts to project, books→圖書館, journals→期刊書摘.
 *
 * Run: node --env-file=.env scripts/import-yinshun-article.mjs
 */
import fs from "node:fs";
import path from "node:path";

const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!SUPABASE_URL || !SERVICE_KEY) {
  console.error("Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY");
  process.exit(1);
}

const headers = {
  apikey: SERVICE_KEY,
  Authorization: `Bearer ${SERVICE_KEY}`,
  "Content-Type": "application/json",
  Prefer: "return=representation",
};

const PROJECT_NAME = "印順導師人間佛教思想的傳承與實踐";
const CHAPTERS = [
  { code: "人間佛教", sort: 1 },
  { code: "印順學", sort: 2 },
  { code: "星雲法師與佛光山", sort: 3 },
  { code: "聖嚴法師與法鼓山", sort: 4 },
  { code: "證嚴法師與慈濟", sort: 5 },
  { code: "趙樸初居士", sort: 6 },
];

function parseCsv(text) {
  const out = [];
  let row = [];
  let cur = "";
  let q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (q && text[i + 1] === '"') {
        cur += '"';
        i++;
      } else q = !q;
    } else if (c === "," && !q) {
      row.push(cur);
      cur = "";
    } else if ((c === "\n" || c === "\r") && !q) {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(cur);
      cur = "";
      if (row.some((v) => v !== "")) out.push(row);
      row = [];
    } else cur += c;
  }
  if (cur.length || row.length) {
    row.push(cur);
    if (row.some((v) => v !== "")) out.push(row);
  }
  return out;
}

function findCsvPath() {
  const dir = path.join(process.cwd(), "stores");
  if (!fs.existsSync(dir)) {
    throw new Error("缺少 stores/ 資料夾，請將 印順學與人間佛教.csv 放在專案根目錄的 stores/ 下");
  }
  const skip = new Set(["中年之路.csv", "反穀.csv", "儀式的科學.csv"]);
  const preferredNames = ["印順學與人間佛教.csv", "\u5370\u9806\u5b78\u8207\u4eba\u9593\u4f5b\u6559.csv"];
  for (const name of preferredNames) {
    const p = path.join(dir, name);
    if (fs.existsSync(p)) return p;
  }
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith(".csv") || skip.has(f)) continue;
    const b = fs.readFileSync(path.join(dir, f));
    const head = new TextDecoder("big5").decode(b.slice(0, 500));
    if (head.includes("人間佛教") && head.includes("印順")) return path.join(dir, f);
  }
  throw new Error("stores/ 內找不到 印順學與人間佛教.csv（請確認檔名與編碼為 Big5）");
}

function isJournalCitation(cite) {
  if (!cite?.trim()) return false;
  if (/第\s*\d+\s*期/.test(cite)) return true;
  if (/《[^》]*學報[^》]*》/.test(cite)) return true;
  if (/碩士論文|博士論文/.test(cite)) return true;
  if (/《弘誓》/.test(cite)) return true;
  if (/《普門學報》/.test(cite)) return true;
  if (/《人間佛教研究》/.test(cite)) return true;
  if (/《人間佛教》學報/.test(cite)) return true;
  if (/《臺灣師大歷史學報》/.test(cite)) return true;
  if (/s英文原作|中文摘譯/.test(cite) && /《弘誓》/.test(cite)) return true;
  return false;
}

function assignTopic(title, content, cite) {
  const t = `${title}\n${content}\n${cite}`;
  if (/證嚴|慈濟/.test(t)) return "證嚴法師與慈濟";
  if (/聖嚴|法鼓/.test(t)) return "聖嚴法師與法鼓山";
  if (/星雲|佛光山/.test(t)) return "星雲法師與佛光山";
  if (/趙樸初/.test(t)) return "趙樸初居士";
  if (/印順|釋印順/.test(t)) return "印順學";
  return "人間佛教";
}

function extractPage(cite) {
  const m = cite.match(/頁\s*(\d+(?:[-–]\d+)?)/);
  return m ? m[1].replace("–", "-") : null;
}

function parseBookFromCitation(cite) {
  const matches = [...cite.matchAll(/《([^》]+)》[（(]([^）)]+)[）)]/g)];
  if (!matches.length) return null;
  const [, title, inner] = matches[matches.length - 1];
  const yearM = inner.match(/(\d{4})/);
  const publish_year = yearM ? Number(yearM[1]) : null;
  const authorM = cite.match(/^([^，,、]+?)[，,]/);
  const author = authorM ? authorM[1].trim() : "佚名";
  const parts = inner.split("：");
  const publisher = parts.length >= 2 ? parts[parts.length - 1].replace(/\d{4}.*$/, "").trim() : inner;
  return { title: title.trim(), author, publisher: publisher || "未知出版社", publish_year };
}

function parseJournalFromCitation(cite, rowTitle) {
  const venueM = cite.match(/《([^》]+)》\s*第\s*(\d+)\s*期/);
  const yearM = cite.match(/（(\d{4})[^）]*）/);
  const authorM = cite.match(/^([^，,、]+?)[，,]/);
  const angleM = cite.match(/〈([^〉]+)〉/);
  const title = (angleM?.[1] || rowTitle || "篇目").trim();
  return {
    title,
    venue: venueM ? venueM[1].trim() : null,
    issue_label: venueM ? `第${venueM[2]}期` : null,
    author: authorM ? authorM[1].trim() : null,
    publish_year: yearM ? Number(yearM[1]) : null,
  };
}

function journalDedupeKey(cite) {
  return cite.replace(/\s+/g, " ").trim().slice(0, 400);
}

async function fetchJson(url, opts = {}) {
  const res = await fetch(url, { headers, ...opts });
  const t = await res.text();
  if (!res.ok) throw new Error(`${res.status} ${t}`);
  try {
    return JSON.parse(t);
  } catch {
    return t;
  }
}

async function main() {
  const csvPath = findCsvPath();
  const buf = fs.readFileSync(csvPath);
  const text = new TextDecoder("big5").decode(buf);
  const rows = parseCsv(text).filter((r) => r.length >= 2);

  let projectId = null;
  const existing = await fetchJson(
    `${SUPABASE_URL}/rest/v1/book_projects?select=id,name&type=eq.${encodeURIComponent("待寫文章")}&name=eq.${encodeURIComponent(PROJECT_NAME)}`
  );
  if (existing?.[0]?.id) {
    projectId = existing[0].id;
    console.log("Use existing project:", projectId);
  } else {
    const created = await fetchJson(`${SUPABASE_URL}/rest/v1/book_projects`, {
      method: "POST",
      headers,
      body: JSON.stringify([
        { name: PROJECT_NAME, type: "待寫文章", description: "印順學與人間佛教資料匯入" },
      ]),
    });
    projectId = created[0].id;
    console.log("Created project:", projectId);
  }

  for (const ch of CHAPTERS) {
    try {
      await fetchJson(`${SUPABASE_URL}/rest/v1/project_chapters`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          project_id: projectId,
          chapter_code: ch.code,
          chapter_name: "",
          sort_order: ch.sort,
        }),
      });
    } catch {
      await fetchJson(
        `${SUPABASE_URL}/rest/v1/project_chapters?project_id=eq.${projectId}&chapter_code=eq.${encodeURIComponent(ch.code)}`,
        {
          method: "PATCH",
          headers,
          body: JSON.stringify({ sort_order: ch.sort }),
        }
      );
    }
  }

  const bookCache = new Map();
  const journalCache = new Map();

  let nEx = 0;
  for (const r of rows) {
    const title = (r[0] || "").trim();
    const content = (r[1] || "").trim();
    const cite = (r[2] || "").trim();
    if (!title || !content || !cite) continue;

    const topic = assignTopic(title, content, cite);
    const page = extractPage(cite);
    const fullContent = cite ? `${content}\n\n出處：${cite}` : content;
    const isJ = isJournalCitation(cite);

    let book_id = null;
    let journal_article_id = null;

    if (isJ) {
      const jk = journalDedupeKey(cite);
      if (journalCache.has(jk)) {
        journal_article_id = journalCache.get(jk);
      } else {
        const meta = parseJournalFromCitation(cite, title);
        const ins = await fetchJson(`${SUPABASE_URL}/rest/v1/journal_articles`, {
          method: "POST",
          headers,
          body: JSON.stringify([
            {
              title: meta.title,
              venue: meta.venue || "期刊",
              author: meta.author,
              publish_year: meta.publish_year,
              issue_label: meta.issue_label,
            },
          ]),
        });
        journal_article_id = ins[0].id;
        journalCache.set(jk, journal_article_id);
      }
    } else {
      const meta = parseBookFromCitation(cite);
      if (!meta) continue;
      const bk = `${meta.title}|${meta.author}|${meta.publish_year ?? ""}`;
      if (bookCache.has(bk)) {
        book_id = bookCache.get(bk);
      } else {
        const found = await fetchJson(
          `${SUPABASE_URL}/rest/v1/books?select=id&title=eq.${encodeURIComponent(meta.title)}&limit=1`
        );
        if (found?.[0]?.id) {
          book_id = found[0].id;
        } else {
          const ins = await fetchJson(`${SUPABASE_URL}/rest/v1/books`, {
            method: "POST",
            headers,
            body: JSON.stringify([
              {
                title: meta.title,
                author: meta.author,
                publisher: meta.publisher,
                publish_year: meta.publish_year,
              },
            ]),
          });
          book_id = ins[0].id;
        }
        bookCache.set(bk, book_id);
      }
    }

    const exIns = await fetchJson(`${SUPABASE_URL}/rest/v1/excerpts`, {
      method: "POST",
      headers,
      body: JSON.stringify([
        {
          title,
          content: fullContent,
          chapter: topic,
          page_number: page,
          book_id,
          journal_article_id,
        },
      ]),
    });
    const exId = exIns[0].id;

    await fetchJson(`${SUPABASE_URL}/rest/v1/excerpt_book_projects`, {
      method: "POST",
      headers,
      body: JSON.stringify([{ excerpt_id: exId, book_project_id: projectId }]),
    });

    nEx++;
  }

  console.log(`Done. Imported ${nEx} excerpts into project ${projectId}`);
  console.log("Books touched:", bookCache.size, "Journals touched:", journalCache.size);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
