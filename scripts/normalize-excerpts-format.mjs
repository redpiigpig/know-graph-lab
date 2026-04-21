/**
 * Normalize excerpt content formatting:
 * 1) Auto-bold likely subheadings by wrapping line with **...**
 * 2) In Chinese excerpts, convert half-width parentheses () to full-width （）
 */

const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SERVICE_KEY) {
  console.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in env.");
  process.exit(1);
}

const headers = {
  apikey: SERVICE_KEY,
  Authorization: `Bearer ${SERVICE_KEY}`,
  "Content-Type": "application/json",
};

function isHeadingLine(t) {
  if (!t) return false;
  if (/^\*\*.*\*\*$/.test(t)) return false; // already bold
  if (/^第[一二三四五六七八九十百千0-9]+[章節回部卷篇]/.test(t)) return true;
  if (/^[一二三四五六七八九十]+[、.．]/.test(t)) return true;
  if (/^[（(][一二三四五六七八九十0-9]+[)）]/.test(t)) return true;
  if (/^#{1,6}\s+/.test(t)) return true;
  if ((t.endsWith("：") || t.endsWith(":")) && t.length <= 36) return true;
  return false;
}

function normalizeContent(content) {
  if (!content) return content;
  let changed = false;
  let out = content;

  const hasCJK = /[\u4E00-\u9FFF]/.test(out);
  if (hasCJK) {
    const replaced = out.replaceAll("(", "（").replaceAll(")", "）");
    if (replaced !== out) {
      out = replaced;
      changed = true;
    }
  }

  const lines = out.split(/\r?\n/);
  const normalizedLines = lines.map((line) => {
    const trimmed = line.trim();
    if (!trimmed) return line;
    if (isHeadingLine(trimmed)) {
      const wrapped = `**${trimmed}**`;
      if (wrapped !== trimmed) {
        changed = true;
        // preserve original leading spaces
        const leading = line.match(/^\s*/)?.[0] ?? "";
        return `${leading}${wrapped}`;
      }
    }
    return line;
  });

  return changed ? normalizedLines.join("\n") : content;
}

async function fetchAllExcerpts() {
  const results = [];
  let from = 0;
  const step = 1000;
  while (true) {
    const to = from + step - 1;
    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/excerpts?select=id,content&order=created_at.asc`,
      {
        headers: {
          ...headers,
          Range: `${from}-${to}`,
          Prefer: "count=exact",
        },
      }
    );
    if (!res.ok) throw new Error(`Fetch excerpts failed: ${res.status} ${await res.text()}`);
    const batch = await res.json();
    if (!batch.length) break;
    results.push(...batch);
    if (batch.length < step) break;
    from += step;
  }
  return results;
}

async function updateExcerpt(id, content) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/excerpts?id=eq.${id}`, {
    method: "PATCH",
    headers,
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error(`Update failed for ${id}: ${res.status} ${await res.text()}`);
}

async function main() {
  const all = await fetchAllExcerpts();
  console.log(`Fetched excerpts: ${all.length}`);
  let changed = 0;
  for (const ex of all) {
    const normalized = normalizeContent(ex.content ?? "");
    if (normalized !== (ex.content ?? "")) {
      await updateExcerpt(ex.id, normalized);
      changed++;
      if (changed % 50 === 0) console.log(`Updated: ${changed}`);
    }
  }
  console.log(`Done. Updated excerpts: ${changed}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

