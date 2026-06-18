/**
 * GET /api/lang/dictionary
 *   ?language=grc&sort=alpha|level|category&level=&category=&q=&page=0&limit=60
 * 翻閱該語言「共用預備字庫」(lang_vocab_bank) — 字典瀏覽頁。
 * 純讀 DB（零 AI）：依字母／分級／分類排序，可加分級‧分類過濾與關鍵字搜尋，分頁回。
 * 另回 levels / categories 兩組 facet（含數量）供前端做分頁 chip。
 */
import { getCoach } from "~/server/utils/lang-coaches";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const q = getQuery(event);
  const language = (q.language as string) || "en";
  if (!getCoach(language)) throw createError({ statusCode: 400, message: "不支援的語言" });

  const sort = ["alpha", "level", "category"].includes(q.sort as string) ? (q.sort as string) : "alpha";
  const level = (q.level as string) || "";
  const category = (q.category as string) || "";
  // 去除會破壞 PostgREST or() / ilike 萬用字元的字元
  const search = ((q.q as string) || "").trim().replace(/[,()*:%]/g, "").slice(0, 60);
  const page = Math.max(0, parseInt((q.page as string) || "0", 10) || 0);
  const limit = Math.min(120, Math.max(20, parseInt((q.limit as string) || "60", 10) || 60));

  let query = supabase
    .from("lang_vocab_bank")
    .select("word,reading,meaning,example,part_of_speech,category,level,freq_rank", { count: "exact" })
    .eq("language", language)
    .eq("glossed", true);
  if (level) query = query.eq("level", level);
  if (category) query = query.eq("category", category);
  if (search) query = query.or(`word.ilike.*${search}*,meaning.ilike.*${search}*`);

  if (sort === "alpha") {
    query = query.order("word", { ascending: true });
  } else if (sort === "level") {
    query = query.order("freq_rank", { ascending: true, nullsFirst: false }).order("word", { ascending: true });
  } else {
    // category：以頻率排序（同類字頻近，閱讀順）
    query = query.order("freq_rank", { ascending: true, nullsFirst: false }).order("word", { ascending: true });
  }
  query = query.range(page * limit, page * limit + limit - 1);

  const { data, count, error } = await query;
  if (error) throw createError({ statusCode: 500, message: error.message });

  // facet 只在第一頁取（之後分頁不重抓，省往返）
  let levels: any[] = [];
  let categories: any[] = [];
  if (page === 0) {
    const [{ data: lvls }, { data: cats }] = await Promise.all([
      supabase.rpc("vocab_bank_levels", { p_language: language }),
      supabase.rpc("vocab_bank_categories", { p_language: language }),
    ]);
    levels = (lvls ?? []).map((r: any) => ({ level: r.level, count: Number(r.n) }));
    categories = (cats ?? []).map((r: any) => ({ category: r.category, count: Number(r.n) }));
  }

  return { rows: data ?? [], total: count ?? 0, page, limit, sort, levels, categories };
});
