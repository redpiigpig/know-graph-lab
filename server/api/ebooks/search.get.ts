/**
 * GET /api/ebooks/search?q=...&ebookId=...
 * Full-text + semantic search within ebook pages
 */
import { ollamaEmbed, ollamaStatus } from "~/server/utils/ollama";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { q, ebookId } = getQuery(event) as { q?: string; ebookId?: string };

  if (!q?.trim()) throw createError({ statusCode: 400, message: "Missing query" });

  const results: any[] = [];

  // Try semantic search first
  const status = await ollamaStatus();
  if (status.ok && status.models.some(m => m.includes("nomic-embed"))) {
    const embedding = await ollamaEmbed(q);
    const { data: matches } = await supabase.rpc("match_pages", {
      query_embedding: `[${embedding.join(",")}]`,
      match_count: 10,
      threshold: 0.25,
    });

    if (matches?.length) {
      let pageQuery = supabase
        .from("book_pages")
        .select("id, ebook_id, page_number, content, ebooks(title, author)")
        .in("id", matches.map((m: any) => m.page_id));

      if (ebookId) pageQuery = pageQuery.eq("ebook_id", ebookId);

      const { data: pages } = await pageQuery;
      results.push(...(pages ?? []).map((p: any) => ({
        ...p,
        similarity: matches.find((m: any) => m.page_id === p.id)?.similarity ?? 0,
        matchType: "semantic",
      })));
    }
  }

  // Full-text fallback or supplement
  if (results.length < 5) {
    let ftQuery = supabase
      .from("book_pages")
      .select("id, ebook_id, page_number, content, ebooks(title, author)")
      .ilike("content", `%${q}%`)
      .order("page_number")
      .limit(10);

    if (ebookId) ftQuery = ftQuery.eq("ebook_id", ebookId);

    const { data: pages } = await ftQuery;
    const existing = new Set(results.map(r => r.id));
    (pages ?? []).forEach((p: any) => {
      if (!existing.has(p.id)) results.push({ ...p, matchType: "fulltext" });
    });
  }

  return results.sort((a, b) => (b.similarity ?? 0) - (a.similarity ?? 0)).slice(0, 10);
});
