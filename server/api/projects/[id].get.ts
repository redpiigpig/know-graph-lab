// GET /api/projects/:id?chapter=XXX
// Returns project info + chapter list (overview), or excerpts for one chapter
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id")!;
  const { chapter } = getQuery(event) as { chapter?: string };

  // Fetch project metadata
  const { data: proj, error: pe } = await supabase
    .from("book_projects")
    .select("id, name, type, description")
    .eq("id", id)
    .single();

  if (pe || !proj) throw createError({ statusCode: 404, message: "找不到此項目" });

  // Fetch chapter names
  const { data: chapterRows } = await supabase
    .from("project_chapters")
    .select("chapter_code, chapter_name, sort_order")
    .eq("project_id", id)
    .order("sort_order");

  const chapterNameMap: Record<string, string> = {};
  for (const r of chapterRows ?? []) {
    chapterNameMap[r.chapter_code] = r.chapter_name ?? "";
  }

  // Fetch all excerpts for this project via inner join, including book original year
  const { data: excerpts, error: ee } = await supabase
    .from("excerpts")
    .select(`
      id, title, content, chapter, page_number, created_at,
      books(id, title, author, publish_year, original_publish_year),
      journal_articles(id, title, venue, author, publish_year, issue_label),
      excerpt_book_projects!inner(book_project_id)
    `)
    .eq("excerpt_book_projects.book_project_id", id)
    .order("chapter", { nullsFirst: false })
    .order("created_at");

  if (ee) throw createError({ statusCode: 500, message: ee.message });

  const all = (excerpts ?? []).map((e: any) => {
    const book = e.books
      ? {
          id: e.books.id,
          title: e.books.title,
          author: e.books.author,
          publish_year: e.books.publish_year,
          original_publish_year: e.books.original_publish_year,
          sort_year: e.books.original_publish_year ?? e.books.publish_year ?? 9999,
        }
      : null;
    const ja = e.journal_articles;
    const journalArticle = ja
      ? {
          id: ja.id,
          title: ja.title,
          venue: ja.venue,
          author: ja.author,
          publish_year: ja.publish_year,
          issue_label: ja.issue_label,
          sort_year: ja.publish_year ?? 9999,
        }
      : null;
    return {
      id: e.id,
      title: e.title,
      content: e.content,
      chapter: e.chapter,
      page_number: e.page_number,
      created_at: e.created_at,
      book,
      journalArticle,
    };
  });

  // If a chapter is requested, return filtered excerpts (sorted by book's original year, grouped by book)
  if (chapter) {
    const chExcerpts = all.filter((e) => {
      if (chapter === "（未分章）") {
        return e.chapter == null || String(e.chapter).trim() === "" || e.chapter === "（未分章）";
      }
      return e.chapter === chapter;
    });
    // Group by book, sort groups by sort_year
    const bookMap = new Map<string, { book: any; journalArticle: any; items: typeof chExcerpts }>();
    for (const e of chExcerpts) {
      const key = e.book?.id ?? e.journalArticle?.id ?? "__no_source__";
      if (!bookMap.has(key)) {
        bookMap.set(key, { book: e.book, journalArticle: e.journalArticle, items: [] });
      }
      bookMap.get(key)!.items.push(e);
    }
    const bookGroups = [...bookMap.values()].sort(
      (a, b) =>
        (a.book?.sort_year ?? a.journalArticle?.sort_year ?? 9999) -
        (b.book?.sort_year ?? b.journalArticle?.sort_year ?? 9999)
    );
    function pageSortValue(raw: string | null | undefined): number {
      const s = (raw ?? "").trim().toLowerCase();
      if (!s) return Number.MAX_SAFE_INTEGER;
      const cleaned = s.replace(/^p(?:age)?\.?\s*/i, "").replace(/^頁\s*/i, "");
      const m = cleaned.match(/\d+/);
      return m ? Number(m[0]) : Number.MAX_SAFE_INTEGER;
    }
    function compareExcerptPageOrder(a: (typeof chExcerpts)[0], b: (typeof chExcerpts)[0]): number {
      const pa = pageSortValue(a.page_number);
      const pb = pageSortValue(b.page_number);
      if (pa !== pb) return pa - pb;
      const ta = new Date(a.created_at || 0).getTime();
      const tb = new Date(b.created_at || 0).getTime();
      if (ta !== tb) return ta - tb;
      return String(a.id).localeCompare(String(b.id));
    }
    // Flatten: each來源內依頁碼排序，再依書籍／期刊年代接成一章內連續編號（插入年代居中的書會自然插隊、後方編號遞延）
    let seq = 1;
    const sorted: (typeof chExcerpts[0] & { seq: number })[] = [];
    for (const g of bookGroups) {
      const ordered = [...g.items].sort(compareExcerptPageOrder);
      for (const item of ordered) {
        sorted.push({ ...item, seq: seq++ });
      }
    }
    return {
      project: { id: proj.id, name: proj.name, type: proj.type },
      chapterName: chapterNameMap[chapter] ?? "",
      excerpts: sorted,
    };
  }

  // Otherwise return overview: chapters with counts + chapter names
  const chapterMap: Record<string, number> = {};
  for (const e of all) {
    const key = e.chapter ?? "（未分章）";
    chapterMap[key] = (chapterMap[key] ?? 0) + 1;
  }

  for (const r of chapterRows ?? []) {
    const code = r.chapter_code;
    if (code && chapterMap[code] === undefined) {
      chapterMap[code] = 0;
    }
  }

  const chapterOrder = Array.from({ length: 30 }, (_, i) => {
    const nums = ["一","二","三","四","五","六","七","八","九","十","十一","十二","十三","十四","十五","十六","十七","十八","十九","二十","二十一","二十二","二十三","二十四","二十五","二十六","二十七","二十八","二十九","三十"];
    return `第${nums[i]}章`;
  });

  const sortFromDb = new Map((chapterRows ?? []).map((r: any) => [r.chapter_code, r.sort_order ?? 0]));

  const chapters = Object.entries(chapterMap)
    .map(([name, count]) => ({ name, count, chapterName: chapterNameMap[name] ?? "" }))
    .sort((a, b) => {
      const da = sortFromDb.get(a.name);
      const db = sortFromDb.get(b.name);
      if (da != null || db != null) {
        return (da ?? 999) - (db ?? 999);
      }
      const ai = chapterOrder.indexOf(a.name);
      const bi = chapterOrder.indexOf(b.name);
      if (ai === -1 && bi === -1) return a.name.localeCompare(b.name);
      return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
    });

  return {
    project: { id: proj.id, name: proj.name, type: proj.type, description: proj.description },
    total: all.length,
    chapters,
  };
});
