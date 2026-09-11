// GET /api/glossary/search?q=般若&code=DFB&def=1&limit=60
// 佛學辭典查詞。資料是 file-backed（見 server/utils/glossaries.ts）。
export default defineEventHandler((event) => {
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
