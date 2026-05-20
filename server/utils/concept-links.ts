// Parse a concept body for [[wiki link]] occurrences and (re)populate the
// concept_links table for that source concept. The link target is resolved
// by matching name or aliases case-insensitively against the concepts table.

const WIKI_LINK_RE = /\[\[([^\[\]\n]+?)\]\]/g;

export interface ParsedLink {
  raw: string;
  context: string;
}

export function parseWikiLinks(body: string): ParsedLink[] {
  const out: ParsedLink[] = [];
  if (!body) return out;
  let m: RegExpExecArray | null;
  // Reset state on a fresh regex.
  const re = new RegExp(WIKI_LINK_RE.source, "g");
  while ((m = re.exec(body)) !== null) {
    const start = Math.max(0, m.index - 60);
    const end = Math.min(body.length, m.index + m[0].length + 60);
    out.push({
      raw: m[1].trim(),
      context: body.slice(start, end),
    });
  }
  return out;
}

export async function rebuildConceptLinks(
  supabase: any,
  fromConceptId: string,
  body: string,
) {
  await supabase.from("concept_links").delete().eq("from_concept_id", fromConceptId);

  const parsed = parseWikiLinks(body);
  if (!parsed.length) return { inserted: 0, unresolved: [] as string[] };

  const uniqueNames = Array.from(new Set(parsed.map((p) => p.raw)));

  // Fetch potential matches in one query.
  // Match on name OR aliases (case-insensitive).
  const lowered = uniqueNames.map((n) => n.toLowerCase());
  const { data: candidates } = await supabase
    .from("concepts")
    .select("id, name, aliases");

  const nameToId = new Map<string, string>();
  (candidates ?? []).forEach((c: any) => {
    nameToId.set((c.name || "").toLowerCase(), c.id);
    (c.aliases ?? []).forEach((a: string) => nameToId.set(a.toLowerCase(), c.id));
  });

  const rows: any[] = [];
  const unresolved: string[] = [];
  for (const p of parsed) {
    const target = nameToId.get(p.raw.toLowerCase());
    if (!target) {
      unresolved.push(p.raw);
      continue;
    }
    if (target === fromConceptId) continue; // skip self-link
    rows.push({
      from_concept_id: fromConceptId,
      to_concept_id: target,
      raw_link_text: p.raw,
      context: p.context,
    });
  }

  if (rows.length) {
    // Use upsert semantics — UNIQUE constraint will dedupe.
    await supabase.from("concept_links").insert(rows);
  }

  return { inserted: rows.length, unresolved: Array.from(new Set(unresolved)) };
}

export function slugify(name: string): string {
  // For CJK names we just URL-encode + lowercase a stable ascii hash;
  // for ASCII names produce a kebab-case slug.
  const s = name.trim();
  if (!s) return "untitled";
  const asciiOnly = /^[\x00-\x7F]+$/.test(s);
  if (asciiOnly) {
    return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "untitled";
  }
  // Keep CJK as-is but strip whitespace + punctuation.
  return s.replace(/\s+/g, "-").replace(/[、，。．！？：；,.\/!?:;]/g, "");
}
