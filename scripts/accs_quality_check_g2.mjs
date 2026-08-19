import fs from "node:fs";

const env = Object.fromEntries(
  fs
    .readFileSync(".env", "utf8")
    .split(/\r?\n/)
    .filter((line) => line && !line.startsWith("#"))
    .map((line) => {
      const i = line.indexOf("=");
      return [line.slice(0, i), line.slice(i + 1).trim().replace(/^["']|["']$/g, "")];
    })
);

const ref = env.SUPABASE_URL.replace("https://", "").split(".")[0];
const endpoint = `https://api.supabase.com/v1/projects/${ref}/database/query`;

async function query(name, sql) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      Authorization: `Bearer ${env.SUPABASE_ACCESS_TOKEN}`,
    },
    body: JSON.stringify({ query: sql }),
  });
  const text = await res.text();
  console.log(`\n## ${name}`);
  console.log(text);
}

await query(
  "chapter_counts",
  `
  SELECT
    chapter,
    COUNT(*) AS rows,
    COUNT(DISTINCT pericope_order) AS pericopes,
    MIN(verse_start) AS min_v,
    MAX(verse_end) AS max_v
  FROM accs_commentary
  WHERE book_code='gen' AND chapter>=12
  GROUP BY chapter
  ORDER BY chapter;
  `
);

await query(
  "quality_stats",
  `
  SELECT
    COUNT(*) AS rows,
    COUNT(*) FILTER (WHERE section_kind='overview') AS overview_rows,
    COUNT(*) FILTER (WHERE section_kind='comment') AS comment_rows,
    COUNT(*) FILTER (WHERE body_zh IS NULL OR btrim(body_zh)='') AS blank_body,
    COUNT(*) FILTER (
      WHERE section_kind='comment' AND (father_name IS NULL OR btrim(father_name)='')
    ) AS comment_blank_father,
    COUNT(*) FILTER (
      WHERE section_kind='comment' AND (work_title IS NULL OR btrim(work_title)='')
    ) AS comment_blank_work,
    COUNT(*) FILTER (
      WHERE verse_start IS NULL OR verse_end IS NULL OR verse_start<1 OR verse_end<verse_start
    ) AS bad_verse_range,
    COUNT(*) FILTER (WHERE body_zh ~ '[这们为会时过说经圣启]') AS simplified_suspect
  FROM accs_commentary
  WHERE book_code='gen' AND chapter>=12;
  `
);

await query(
  "recent_samples",
  `
  SELECT
    chapter,
    verse_start,
    verse_end,
    pericope_order,
    entry_order,
    section_kind,
    heading,
    father_name,
    work_title,
    LEFT(body_zh, 90) AS body
  FROM accs_commentary
  WHERE book_code='gen' AND chapter IN (48,49)
  ORDER BY chapter, pericope_order, entry_order
  LIMIT 24;
  `
);

await query(
  "verse_range_outliers",
  `
  WITH max_verses AS (
    SELECT book_code, chapter, MAX(verse) AS max_verse
    FROM bible_verses
    WHERE book_code='gen'
    GROUP BY book_code, chapter
  )
  SELECT
    a.chapter,
    a.verse_start,
    a.verse_end,
    m.max_verse,
    a.pericope_order,
    a.entry_order,
    a.section_kind,
    a.heading,
    a.father_name,
    LEFT(a.body_zh, 120) AS body
  FROM accs_commentary a
  LEFT JOIN max_verses m
    ON m.book_code=a.book_code AND m.chapter=a.chapter
  WHERE a.book_code='gen'
    AND a.chapter>=12
    AND (
      m.max_verse IS NULL
      OR a.verse_start > m.max_verse
      OR a.verse_end > m.max_verse
      OR a.verse_start < 1
      OR a.verse_end < a.verse_start
    )
  ORDER BY a.chapter, a.pericope_order, a.entry_order
  LIMIT 50;
  `
);
