/** GET /api/lang/vocab/categories?language=grc — 該語言共用字庫的分類標籤（含數量），依頻率排序。
 *  複習頁推薦 chip / 每日輪替主題用：有字庫的語言就拿真實分類，沒有就回空（前端 fallback 到內建 presets）。 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const language = (getQuery(event).language as string) || "en";
  const { data, error } = await supabase.rpc("vocab_bank_categories", { p_language: language });
  if (error) return { categories: [] };
  return { categories: (data ?? []).map((r: any) => ({ category: r.category, count: Number(r.n) })) };
});
