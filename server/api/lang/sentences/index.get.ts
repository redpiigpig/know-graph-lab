/**
 * GET /api/lang/sentences?language=en
 * 回傳「情境實用句」策展庫（情境分類 + 句子）。目前只有英文。
 */
import { scenariosForClient } from "~/server/data/enSentences";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const language = (getQuery(event).language as string) || "en";
  if (language !== "en") return { language, available: false, scenarios: [] };
  return { language, available: true, scenarios: scenariosForClient() };
});
