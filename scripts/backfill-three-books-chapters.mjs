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

const TARGET_BOOKS = ["中年之路", "反穀", "儀式的科學"];

async function main() {
  const books = await fetchJson(
    `${SUPABASE_URL}/rest/v1/books?select=id,title&title=in.(${TARGET_BOOKS.join(",")})`
  );

  for (const book of books) {
    const excerpts = await fetchJson(
      `${SUPABASE_URL}/rest/v1/excerpts?select=id,title,content,chapter,page_number,created_at&book_id=eq.${book.id}&order=created_at.asc`
    );

    let currentChapter = null;
    let updated = 0;

    for (const e of excerpts) {
      const maybeHeading = detectChapterHeading(e.title, e.content);
      if (maybeHeading) {
        currentChapter = maybeHeading;
      }
      if (!e.chapter && currentChapter) {
        await patchExcerptChapter(e.id, currentChapter);
        updated += 1;
      }
    }

    console.log(`✓ ${book.title}: chapter backfilled ${updated} excerpts`);
  }
}

function detectChapterHeading(title, content) {
  const cand = [title, content]
    .map((x) => (x || "").trim())
    .find((x) => x.length > 0);
  if (!cand) return null;
  if (cand.length > 80) return null;

  const patterns = [
    /^第[一二三四五六七八九十百零〇\d]+章(?:[:：].*)?$/,
    /^第[一二三四五六七八九十百零〇\d]+部(?:[:：].*)?$/,
    /^Chapter\s+\d+(?:[:：].*)?$/i,
    /^Part\s+\d+(?:[:：].*)?$/i,
  ];
  return patterns.some((re) => re.test(cand)) ? cand : null;
}

async function patchExcerptChapter(id, chapter) {
  const url = `${SUPABASE_URL}/rest/v1/excerpts?id=eq.${id}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers,
    body: JSON.stringify({ chapter }),
  });
  if (!res.ok) {
    throw new Error(`PATCH excerpt failed: ${id} ${res.status} ${await res.text()}`);
  }
}

async function fetchJson(url) {
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
