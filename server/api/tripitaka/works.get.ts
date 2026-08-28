// GET /api/tripitaka/works?division=agama&canon=T&q=法華&page=1
//
// 目錄查詢。只碰 tripitaka_works（2,554 列），不碰正文檔案。
// 南傳一部書常被切成數冊（長部經典 ×3），列表按 series 歸群、冊次為子項。
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const q = getQuery(event);
  const division = String(q.division || "").trim();
  const canon = String(q.canon || "").trim();
  const search = String(q.q || "").trim();
  const limit = Math.min(Number(q.limit) || 400, 1000);
  const offset = Math.max(Number(q.offset) || 0, 0);

  const supabase = getAdminClient();
  let sel = supabase
    .from("tripitaka_works")
    .select(
      "id,canon,vol,work_no,work_suffix,title_zh,series,byline,dynasty,translator,author," +
        "lost_translator,extent,juan_count,division_key,japanese,seg_count,char_count," +
        "term_count,term_langs,equiv_count,parallel_langs,pali_ref,sanskrit_ref,tibetan_toh",
      { count: "exact" },
    )
    .order("display_order", { ascending: true })
    .range(offset, offset + limit - 1);

  if (division) sel = sel.eq("division_key", division);
  if (canon) sel = sel.eq("canon", canon);
  if (search) {
    // 經名／譯者／作者三欄模糊；經號（T0262 / 262）另走精確比對
    const num = search.match(/^[TtNn]?0*(\d{1,4})[A-Za-z]?$/);
    sel = num
      ? sel.or(`work_no.eq.${num[1]},id.ilike.%${search}%`)
      : sel.or(
          `title_zh.ilike.%${search}%,series.ilike.%${search}%,` +
            `translator.ilike.%${search}%,author.ilike.%${search}%`,
        );
  }

  const { data, error, count } = await sel;
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { works: data ?? [], total: count ?? 0, limit, offset };
});
