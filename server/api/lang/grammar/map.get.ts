/**
 * GET /api/lang/grammar/map?language=en
 * 回傳「文法地圖」分類瀏覽資料（手工策展）。目前只有英文。
 */
import { mapForClient } from "~/server/data/enGrammar";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const language = (getQuery(event).language as string) || "en";
  if (language !== "en") {
    return { language, available: false, categories: [] };
  }
  return { language, available: true, categories: mapForClient() };
});
