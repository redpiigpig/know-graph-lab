// GET /api/journal-articles — list journal / magazine sources with excerpt counts
import { journalArticleMergeKey } from "../../utils/journal-merge";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const [{ data: rows, error }, { data: excerpts }] = await Promise.all([
    supabase
      .from("journal_articles")
      .select("id, title, venue, author, publish_year, issue_label, created_at")
      .order("created_at", { ascending: false }),
    supabase.from("excerpts").select("journal_article_id").not("journal_article_id", "is", null),
  ]);

  if (error) throw createError({ statusCode: 500, message: error.message });

  const countMap: Record<string, number> = {};
  excerpts?.forEach((e) => {
    if (e.journal_article_id) countMap[e.journal_article_id] = (countMap[e.journal_article_id] ?? 0) + 1;
  });

  const withCounts = (rows ?? []).map((r) => ({
    ...r,
    excerpt_count: countMap[r.id] ?? 0,
  }));

  const groups = new Map<string, typeof withCounts>();
  for (const r of withCounts) {
    const k = journalArticleMergeKey(r);
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k)!.push(r);
  }

  const merged: typeof withCounts = [];
  for (const arr of groups.values()) {
    arr.sort((a, b) => b.excerpt_count - a.excerpt_count || a.id.localeCompare(b.id));
    const primary = arr[0];
    const excerpt_count = arr.reduce((s, x) => s + x.excerpt_count, 0);
    merged.push({ ...primary, excerpt_count });
  }

  merged.sort((a, b) => (b.created_at ?? "").localeCompare(a.created_at ?? ""));
  return merged;
});
