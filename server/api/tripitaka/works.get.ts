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
        "term_count,term_langs,equiv_count,parallel_langs,pali_ref,sanskrit_ref,tibetan_toh," +
        // 藏文大藏經（canon='DK'）：title_zh 是漢譯對照本的書名，661 部是空的，
        // 列表顯示與搜尋都要退到這幾欄，否則會列出一整排沒有標題的經。
        "toh,title_bo,title_bo_short,title_sa,title_en,translator_en,folio_start,folio_end",
      { count: "exact" },
    )
    .order("display_order", { ascending: true })
    .range(offset, offset + limit - 1);

  if (division) sel = sel.eq("division_key", division);
  if (canon) sel = sel.eq("canon", canon);
  if (search) {
    // 經名／譯者／作者模糊；經號（T0262 / 262 / Toh 113）另走精確比對。
    // 藏文與英譯題名一併納入，否則甘珠爾那 677 部只有藏文的經永遠搜不到。
    const num = search.match(/^(?:[TtNnXx]|[Tt]oh\s*)?0*(\d{1,4})[A-Za-z]?$/);
    sel = num
      ? sel.or(`work_no.eq.${num[1]},id.ilike.%${search}%`)
      : sel.or(
          `title_zh.ilike.%${search}%,series.ilike.%${search}%,` +
            `translator.ilike.%${search}%,author.ilike.%${search}%,` +
            `title_bo.ilike.%${search}%,title_en.ilike.%${search}%,` +
            `title_sa.ilike.%${search}%`,
        );
  }

  const { data, error, count } = await sel;
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { works: data ?? [], total: count ?? 0, limit, offset };
});
