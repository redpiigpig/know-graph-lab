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

    const csv = decodeCsv(full);
    const rows = parseCsv(csv);
    const categoryId = await findOrCreateCategory(item.category);
    const bookId = await findBookId(item.title);
    if (!bookId) {
      throw new Error(`Book not found: ${item.title}`);
    }

    await updateBookCategory(bookId, categoryId);
    const excerpts = toExcerptsWithChapter(rows, bookId);
    await deleteAllExcerptsByBook(bookId);
    const inserted = await insertExcerpts(excerpts);
    console.log(`✓ ${item.title}: rebuilt ${inserted} excerpts`);
  }
}

function decodeCsv(fullPath) {
  const buf = fs.readFileSync(fullPath);
  return new TextDecoder("big5").decode(buf);
}

function toExcerptsWithChapter(rows, book_id) {
  const dataRows = rows.slice(1); // skip bibliography row
  const out = [];
  let currentChapter = null;

  for (const r of dataRows) {
    const c0 = (r[0] || "").trim();
    const c1 = (r[1] || "").trim();
    const c2 = (r[2] || "").trim();

    const chapter = detectChapterRow(c0, c1, c2);
    if (chapter) {
      currentChapter = chapter;
      continue;
    }

    const title = c0 || null;
    const content = c1;
    const page = c2 || null;
    if (!content) continue;

    out.push({
      title,
      content,
      page_number: page,
      chapter: currentChapter,
      book_id,
    });
  }

  return out;
}

function detectChapterRow(c0, c1, c2) {
  const candidate = c1 || c0;
  if (!candidate) return null;
  if (candidate.length > 100) return null;
  if (c2) return null; // has page => probably excerpt row

  const shortHeadingPatterns = [
    /^第[一二三四五六七八九十百零〇\d]+章[、：:].*$/,
    /^第[一二三四五六七八九十百零〇\d]+章$/,
    /^前言$/,
    /^序$/,
    /^結語$/,
    /^後記$/,
    /^附錄/,
  ];

  if (shortHeadingPatterns.some((re) => re.test(candidate))) return candidate;

  // "第一部 xxx" 這類
  if (/^第[一二三四五六七八九十百零〇\d]+部/.test(candidate)) return candidate;

  return null;
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

async function findBookId(title) {
  const q = `${SUPABASE_URL}/rest/v1/books?select=id,title&title=eq.${encodeURIComponent(title)}&limit=1`;
  const res = await fetch(q, { headers });
  const list = await res.json();
  return list?.[0]?.id || null;
}

async function updateBookCategory(bookId, categoryId) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/books?id=eq.${bookId}`, {
    method: "PATCH",
    headers,
    body: JSON.stringify({ category_id: categoryId }),
  });
  if (!res.ok) {
    throw new Error(`Update category failed: ${bookId} ${res.status} ${await res.text()}`);
  }
}

async function deleteAllExcerptsByBook(bookId) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/excerpts?book_id=eq.${bookId}`, {
    method: "DELETE",
    headers,
  });
  if (!res.ok) {
    throw new Error(`Delete excerpts failed: ${bookId} ${res.status} ${await res.text()}`);
  }
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
    if (!res.ok) {
      throw new Error(`Insert chunk failed: ${res.status} ${await res.text()}`);
    }
    inserted += chunk.length;
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
      if (q && text[i + 1] === '"') {
        cur += '"';
        i++;
      } else {
        q = !q;
      }
    } else if (c === "," && !q) {
      row.push(cur);
      cur = "";
    } else if ((c === "\n" || c === "\r") && !q) {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(cur);
      cur = "";
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
