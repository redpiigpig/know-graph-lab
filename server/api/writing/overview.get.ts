// Returns writing project overview: chapters with excerpt counts
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  // Get all excerpts for 待寫著作 (by joining book_projects)
  const { data, error } = await supabase
    .from("excerpts")
    .select(
      `id, chapter,
       excerpt_book_projects!inner(book_projects!inner(type))`
    )
    .not("chapter", "is", null);

  if (error) throw createError({ statusCode: 500, message: error.message });

  // Filter to 待寫著作 and group by chapter
  const chapterMap: Record<string, number> = {};
  let total = 0;

  (data ?? []).forEach((e: any) => {
    const isWriting = e.excerpt_book_projects?.some(
      (ep: any) => ep.book_projects?.type === "待寫著作"
    );
    if (isWriting && e.chapter) {
      chapterMap[e.chapter] = (chapterMap[e.chapter] ?? 0) + 1;
      total++;
    }
  });

  // Sort chapters by Chinese numeral order
  const chapterOrder = [
    "第一章", "第二章", "第三章", "第四章", "第五章",
    "第六章", "第七章", "第八章", "第九章", "第十章",
    "第十一章", "第十二章", "第十三章", "第十四章", "第十五章",
    "第十六章", "第十七章", "第十八章", "第十九章", "第二十章",
    "第二十一章", "第二十二章", "第二十三章", "第二十四章", "第二十五章",
    "第二十六章", "第二十七章", "第二十八章",
  ];
  const chapters = Object.entries(chapterMap)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => {
      const ai = chapterOrder.indexOf(a.name);
      const bi = chapterOrder.indexOf(b.name);
      return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
    });

  return {
    title: "千面上帝",
    total,
    chapters,
  };
});
