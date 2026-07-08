/**
 * GET /api/ebooks/search?q=...&mode=title|author|fulltext|all
 *
 * - title    → ilike on ebooks.title           (returns book rows)
 * - author   → ilike on ebooks.author          (returns book rows)
 * - fulltext → ilike on ebook_chunks.content   (returns chunk hits with snippet)
 * - all (default) → run all three, label each
 *
 * Note: fulltext only covers books whose preview rows are in `ebook_chunks`
 * (standardized or OCR'd books). Run scripts/repopulate_chunk_previews.py to
 * back-fill the rest.
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { q, mode = "all", ebookId } = getQuery(event) as {
    q?: string;
    mode?: string;
    ebookId?: string;
  };
  const query = q?.trim();
  if (!query) throw createError({ statusCode: 400, message: "Missing query" });
  // Escape ilike wildcards so user-typed % and _ are treated literally.
  const safe = query.replace(/[%_]/g, (c) => "\\" + c);

  const wantTitle = mode === "title" || mode === "all";
  const wantAuthor = mode === "author" || mode === "all";
  const wantFulltext = mode === "fulltext" || mode === "all";

  const [titleHits, authorHits, fulltextHits] = await Promise.all([
    wantTitle
      ? supabase
          .from("ebooks")
          .select("id, title, author, file_type, total_pages, chunk_count, category, subcategory")
          .is("collection", null)
          .ilike("title", `%${safe}%`)
          .order("title")
          .limit(50)
      : Promise.resolve({ data: [] as any[], error: null }),
    wantAuthor
      ? supabase
          .from("ebooks")
          .select("id, title, author, file_type, total_pages, chunk_count, category, subcategory")
          .is("collection", null)
          .ilike("author", `%${safe}%`)
          .order("title")
          .limit(50)
      : Promise.resolve({ data: [] as any[], error: null }),
    wantFulltext
      ? (() => {
          let req = supabase
            .from("ebook_chunks")
            .select(
              "id, ebook_id, chunk_index, page_number, chapter_path, content, ebooks!inner(title, author, collection)"
            )
            .ilike("content", `%${safe}%`)
            .limit(40);
          // 書內搜尋（指定 ebookId）不做 collection 過濾；跨館全文搜尋才排除全集
          if (ebookId) req = req.eq("ebook_id", ebookId);
          else req = req.is("ebooks.collection", null);
          return req;
        })()
      : Promise.resolve({ data: [] as any[], error: null }),
  ]);

  return {
    query,
    mode,
    titleMatches: (titleHits.data ?? []).map((b: any) => ({ ...b, matchType: "title" })),
    authorMatches: (authorHits.data ?? []).map((b: any) => ({ ...b, matchType: "author" })),
    fulltextMatches: (fulltextHits.data ?? []).map((c: any) => ({
      ...c,
      matchType: "fulltext",
    })),
  };
});
