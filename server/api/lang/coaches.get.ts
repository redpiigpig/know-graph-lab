/** GET /api/lang/coaches — 公開的教練人設清單＋分類（給語言選擇頁） */
import { publicCoaches, CATEGORIES } from "~/server/utils/lang-coaches";

export default defineEventHandler(() => {
  return { coaches: publicCoaches(), categories: CATEGORIES };
});
