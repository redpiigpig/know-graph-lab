// GET /api/glossary/search?q=般若&code=DFB&def=1&limit=60
// 佛學辭典查詢。資料是 file-backed（見 server/utils/glossaries.ts）。
// 🚨 要登入：佛光大辭典授權範圍未確認前不可對外開放，頁面有登入牆不夠，API 也要擋。
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  await ensureGlossaries();
  const q = getQuery(event);
  const term = String(q.q ?? "").trim();
  if (!term) {
    // 沒帶關鍵字時回各部的條數，供頁面初次載入顯示
    return { query: "", total: 0, hits: [], glossaries: glossaryStats() };
  }
  const { total, hits } = searchGlossaries(term, {
    code: q.code ? String(q.code) : undefined,
    limit: q.limit ? Number(q.limit) : undefined,
    inDefinition: q.def === "1" || q.def === "true",
  });
  return { query: term, total, hits, glossaries: glossaryStats() };
});
