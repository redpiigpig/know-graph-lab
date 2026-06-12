/**
 * GET /api/lang/parse?language=grc&n=12
 * 古典語「詞形 parsing 自動批改」題庫（零 AI）。回傳隨機 n 題 + 各維度選項。
 * 題庫為 STEPBible 黃金標註離線解碼的靜態 JSON（server/data/parseGreek.json）。
 * 目前只有希臘文（grc）；其他語言 available:false。
 */
import greek from "~/server/data/parseGreek.json";
import hebrew from "~/server/data/parseHebrew.json";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const q = getQuery(event);
  const language = (q.language as string) || "";
  const n = Math.min(Math.max(Number(q.n) || 12, 4), 40);
  const bank: any = language === "grc" ? greek : language === "hbo" ? hebrew : null;
  if (!bank) return { language, available: false, items: [], options: {}, dimLabels: {}, rtl: false };

  // 隨機抽 n 題（Fisher–Yates 取前 n）
  const arr = bank.items.slice();
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return {
    language,
    available: true,
    rtl: !!bank.rtl,
    total: bank.items.length,
    options: bank.options,
    dimLabels: bank.dimLabels,
    items: arr.slice(0, n),
  };
});
