// GET /api/tripitaka/stats
// 各部類的部數／字數／有原文對照的部數，供 /tripitaka 首頁卡片。
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  // 2,554 列全撈會撞 PostgREST 的 1000 列上限，且只需要彙總 —— 走 DB 端聚合。
  const { data, error } = await supabase.rpc("tripitaka_division_stats");
  if (!error && data) return { divisions: data };

  // rpc 尚未建立時的退路：分頁把目錄撈完再在 node 端彙總。
  const rows: any[] = [];
  for (let off = 0; ; off += 1000) {
    const { data: page, error: e } = await supabase
      .from("tripitaka_works")
      .select("division_key,canon,char_count,seg_count,term_count,equiv_count")
      .range(off, off + 999);
    if (e) throw createError({ statusCode: 500, message: e.message });
    rows.push(...(page ?? []));
    if (!page || page.length < 1000) break;
  }
  const tally = new Map<string, any>();
  for (const r of rows) {
    const t = tally.get(r.division_key) ?? {
      division_key: r.division_key,
      canon: r.canon,
      works: 0,
      chars: 0,
      segs: 0,
      with_parallel: 0,
    };
    t.works += 1;
    t.chars += r.char_count ?? 0;
    t.segs += r.seg_count ?? 0;
    if ((r.term_count ?? 0) > 0 || (r.equiv_count ?? 0) > 0) t.with_parallel += 1;
    tally.set(r.division_key, t);
  }
  return { divisions: [...tally.values()] };
});
