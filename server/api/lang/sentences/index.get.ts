/**
 * GET /api/lang/sentences?language=en
 * 回傳「情境實用句」策展庫 + 「短文/長文」範例庫。目前只有英文。
 */
import { scenariosForClient } from "~/server/data/enSentences";
import { passagesForClient } from "~/server/data/enPassages";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const language = (getQuery(event).language as string) || "en";
  if (language !== "en") return { language, available: false, scenarios: [], passages: [] };
  return { language, available: true, scenarios: scenariosForClient(), passages: passagesForClient() };
});
