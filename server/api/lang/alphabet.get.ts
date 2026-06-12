/**
 * GET /api/lang/alphabet?language=de
 * 回傳該語言的「字母教學 + 測驗」策展資料（純策展、無 AI）。
 * 英文不提供（使用者已熟英文字母）→ available:false。
 */
import { alphabetForClient } from "~/server/data/alphabets";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const language = (getQuery(event).language as string) || "";
  const alphabet = alphabetForClient(language);
  return { language, available: !!alphabet, alphabet: alphabet ?? null };
});
