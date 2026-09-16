/**
 * GET /api/ebooks/search?q=...&mode=title|author|fulltext|all[&ebookId=...]
 *
 * - title    → ilike on ebooks.title    (returns book rows)
 * - author   → ilike on ebooks.author   (returns book rows)
 * - fulltext → 掃 JSONL 全文            (returns chunk hits with snippet)
 * - all (default) → run all three, label each
 *
 * 2026-09-16 全文這一路改寫。以前是 `ilike` 打在 `ebook_chunks.content` 上，
 * 那張表 1,005,032 列、在 Supabase 免費層（上限 500 MB）獨自佔掉 503 MB，
 * 而且**那個欄位只存每個 chunk 的前 100 字** —— 全館搜尋從來只搜得到每段開頭
 * 那一小截，中後段寫什麼都搜不到；又沒有支援索引，每查一次就是百萬列全表掃描。
 *
 * 現在改讀 Drive／R2 上的 JSONL（reader 本來就只讀那一份）：
 *   - 指定 ebookId（書內搜尋）→ 掃那本的**全文**，比舊版涵蓋得多。
 *   - 沒指定（跨書搜尋）→ 先用書名／作者／分類選出候選書，再平行掃它們的全文。
 *     覆蓋率不如「真正的全館索引」，但舊版那個也只搜前 100 字；
 *     真正的全館索引（R2 上的 bloom）是下一階段的事，見 SKILL.md Workflow J。
 */
import { searchBookFulltext, type FulltextHit } from "~/server/utils/ebook-chunks";

const CANDIDATE_BOOKS = 24;   // 跨書搜尋時最多掃幾本，免得一次拉爆 Drive／R2
const MAX_HITS = 40;

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
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

  const BOOK_COLS =
    "id, title, author, file_type, total_pages, chunk_count, category, subcategory, collection, quality_score";

  const [titleHits, authorHits] = await Promise.all([
    wantTitle
      ? supabase
          .from("ebooks")
          // 圖書館搜尋涵蓋全集（collected-works）與相關書：不再 .is("collection", null)
          .select(BOOK_COLS)
          .ilike("title", `%${safe}%`)
          .order("title")
          .limit(50)
      : Promise.resolve({ data: [] as any[], error: null }),
    wantAuthor
      ? supabase
          .from("ebooks")
          .select(BOOK_COLS)
          .ilike("author", `%${safe}%`)
          .order("title")
          .limit(50)
      : Promise.resolve({ data: [] as any[], error: null }),
  ]);

  // ── 全文：掃 JSONL ─────────────────────────────────────────────────────
  let fulltextMatches: (FulltextHit & { ebooks: any; matchType: string })[] = [];
  if (wantFulltext) {
    let candidates: any[] = [];
    if (ebookId) {
      const { data } = await supabase.from("ebooks").select(BOOK_COLS).eq("id", ebookId).limit(1);
      candidates = data ?? [];
    } else {
      // 跨書：用便宜的 metadata 把候選收斂到可掃的數量。
      const { data } = await supabase
        .from("ebooks")
        .select(BOOK_COLS)
        .not("chunk_count", "is", null)
        .gt("chunk_count", 0)
        .or(
          `title.ilike.%${safe}%,author.ilike.%${safe}%,` +
            `category.ilike.%${safe}%,subcategory.ilike.%${safe}%`
        )
        .limit(CANDIDATE_BOOKS);
      candidates = data ?? [];
    }

    const per = ebookId ? MAX_HITS : Math.max(2, Math.floor(MAX_HITS / Math.max(1, candidates.length)));
    const results = await Promise.all(
      candidates.map(async (b) => {
        try {
          const hits = await searchBookFulltext(b.id, query, { limit: per });
          return hits.map((h) => ({ ...h, ebooks: b, matchType: "fulltext" }));
        } catch {
          return [];        // 某本讀不到（Drive 沒掛／R2 缺檔）不該讓整個搜尋失敗
        }
      })
    );
    fulltextMatches = results.flat().slice(0, MAX_HITS);
  }

  // 品質閘門，與 /api/ebooks 共用 server/utils/ebook-quality-gate.ts 的規則。
  // 這裡在 JS 端過濾而不寫進查詢：三個查詢各自最多 50 列，成本可以忽略，
  // 而 PostgREST 的 or(...) 巢狀語法容易寫錯又不會報錯，只會靜靜地漏書。
  const showAll = String((getQuery(event) as any).quality || "") === "all";
  const keep = (b: any) => showAll || ebookPassesGate(b);

  return {
    query,
    mode,
    titleMatches: (titleHits.data ?? []).filter(keep).map((b: any) => ({ ...b, matchType: "title" })),
    authorMatches: (authorHits.data ?? []).filter(keep).map((b: any) => ({ ...b, matchType: "author" })),
    fulltextMatches: fulltextMatches.filter((c: any) => keep(c.ebooks)),
  };
});
