/**
 * Import three store CSV books into library (books + excerpts).
 * - 中年之路 -> 心理學
 * - 反穀, 儀式的科學 -> 人類學
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
};

const plan = [
  { file: "中年之路.csv", title: "中年之路", category: "心理學" },
  { file: "反穀.csv", title: "反穀", category: "人類學" },
  { file: "儀式的科學.csv", title: "儀式的科學", category: "人類學" },
];

async function main() {
  for (const item of plan) {
    const full = path.join(process.cwd(), "stores", item.file);
    if (!fs.existsSync(full)) {
      console.warn("Skip missing file:", item.file);
      continue;
    }

    const csv = fs.readFileSync(full, "utf8");
    const rows = parseCsv(csv);
    const meta = rows[0]?.[1] || "";
    const parsed = parseBibliography(meta);

    const categoryId = await findOrCreateCategory(item.category);
    const bookId = await findOrCreateBook(item.title, categoryId, parsed);
    const excerpts = toExcerpts(rows, bookId);
    const inserted = await insertExcerpts(excerpts);

    console.log(`✓ ${item.title}: parsed ${excerpts.length}, inserted ${inserted}`);
  }
}

async function findOrCreateCategory(name) {
  const q = `${SUPABASE_URL}/rest/v1/book_categories?select=id,name&name=eq.${encodeURIComponent(name)}`;
  const res = await fetch(q, { headers });
  const list = await res.json();
  if (list?.[0]?.id) return list[0].id;

  const create = await fetch(`${SUPABASE_URL}/rest/v1/book_categories`, {
    method: "POST",
    headers: { ...headers, Prefer: "return=representation" },
    body: JSON.stringify([{ name, parent_id: null, display_order: 999 }]),
  });
  const created = await create.json();
  return created[0].id;
}

async function findOrCreateBook(title, category_id, parsedMeta = {}) {
  const q = `${SUPABASE_URL}/rest/v1/books?select=id,title&title=eq.${encodeURIComponent(title)}&limit=1`;
  const res = await fetch(q, { headers });
  const list = await res.json();
  if (list?.[0]?.id) {
    // ensure category updated
    await fetch(`${SUPABASE_URL}/rest/v1/books?id=eq.${list[0].id}`, {
      method: "PATCH",
      headers,
      body: JSON.stringify({ category_id }),
    });
    return list[0].id;
  }

  const create = await fetch(`${SUPABASE_URL}/rest/v1/books`, {
    method: "POST",
    headers: { ...headers, Prefer: "return=representation" },
    body: JSON.stringify([{
      title,
      author: parsedMeta.author || "未知作者",
      translator: parsedMeta.translator || null,
      publisher: parsedMeta.publisher || null,
      publish_year: parsedMeta.year || null,
      category_id,
    }]),
  });
  if (!create.ok) {
    throw new Error(`Create book failed (${title}): ${create.status} ${await create.text()}`);
  }
  const created = await create.json();
  if (!created?.[0]?.id) {
    // fallback query
    const verify = await fetch(
      `${SUPABASE_URL}/rest/v1/books?select=id,title&title=eq.${encodeURIComponent(title)}&limit=1`,
      { headers }
    );
    const v = await verify.json();
    if (v?.[0]?.id) return v[0].id;
    throw new Error(`Create book returned empty for ${title}`);
  }
  return created[0].id;
}

function parseBibliography(metaRaw) {
  const meta = (metaRaw || "").trim();
  const out = {};
  // ...某某著
  const mAuthor = meta.match(/[》)）]\s*([^，,。]+?)著/);
  if (mAuthor) out.author = mAuthor[1].trim();
  // ...某某譯
  const mTranslator = meta.match(/著，\s*([^，,。]+?)譯/);
  if (mTranslator) out.translator = mTranslator[1].trim();
  // 出版社：一般在地名：出版社，年份
  const mPub = meta.match(/[：:]\s*([^，,。]+?)[，,]\s*(\d{4})/);
  if (mPub) {
    out.publisher = mPub[1].trim();
    out.year = Number(mPub[2]);
  }
  return out;
}

function toExcerpts(rows, book_id) {
  // row0 is bibliographic line, not excerpt
  const dataRows = rows.slice(1);
  const out = [];
  for (const r of dataRows) {
    const title = (r[0] || "").trim();
    const content = (r[1] || "").trim();
    const page = (r[2] || "").trim();
    if (!content) continue;
    out.push({
      title: title || null,
      content,
      page_number: page || null,
      chapter: null,
      book_id,
    });
  }
  return out;
}

async function insertExcerpts(items) {
  if (!items.length) return 0;
  let inserted = 0;
  const step = 100;
  for (let i = 0; i < items.length; i += step) {
    const chunk = items.slice(i, i + step);
    const res = await fetch(`${SUPABASE_URL}/rest/v1/excerpts`, {
      method: "POST",
      headers,
      body: JSON.stringify(chunk),
    });
    if (res.ok) inserted += chunk.length;
    else {
      const txt = await res.text();
      console.warn("Insert chunk failed:", txt.slice(0, 200));
    }
  }
  return inserted;
}

function parseCsv(text) {
  const out = [];
  let row = [];
  let cur = "";
  let q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (q && text[i + 1] === '"') { cur += '"'; i++; }
      else q = !q;
    } else if (c === "," && !q) {
      row.push(cur); cur = "";
    } else if ((c === "\n" || c === "\r") && !q) {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(cur); cur = "";
      if (row.some((v) => v !== "")) out.push(row);
      row = [];
    } else {
      cur += c;
    }
  }
  if (cur.length || row.length) {
    row.push(cur);
    if (row.some((v) => v !== "")) out.push(row);
  }
  return out;
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

