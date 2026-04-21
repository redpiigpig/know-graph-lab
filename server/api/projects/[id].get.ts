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

  // Fetch all excerpts for this project via inner join
  const { data: excerpts, error: ee } = await supabase
    .from("excerpts")
    .select(`
      id, title, content, chapter, page_number, created_at,
      books(id, title, author),
      excerpt_book_projects!inner(book_project_id)
    `)
    .eq("excerpt_book_projects.book_project_id", id)
    .order("chapter", { nullsFirst: false })
    .order("created_at");

  if (ee) throw createError({ statusCode: 500, message: ee.message });

  const all = (excerpts ?? []).map((e: any) => ({
    id: e.id,
    title: e.title,
    content: e.content,
    chapter: e.chapter,
    page_number: e.page_number,
    created_at: e.created_at,
    book: e.books ?? null,
  }));

  // If a chapter is requested, return filtered excerpts
  if (chapter) {
    return {
      project: { id: proj.id, name: proj.name, type: proj.type },
      excerpts: all.filter((e) => e.chapter === chapter),
    };
  }

  // Otherwise return overview: chapters with counts + total
  const chapterMap: Record<string, number> = {};
  for (const e of all) {
    const key = e.chapter ?? "（未分章）";
    chapterMap[key] = (chapterMap[key] ?? 0) + 1;
  }

  const chapterOrder = Array.from({ length: 30 }, (_, i) => {
    const nums = ["一","二","三","四","五","六","七","八","九","十","十一","十二","十三","十四","十五","十六","十七","十八","十九","二十","二十一","二十二","二十三","二十四","二十五","二十六","二十七","二十八","二十九","三十"];
    return `第${nums[i]}章`;
  });

  const chapters = Object.entries(chapterMap)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => {
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
