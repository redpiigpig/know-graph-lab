/** GET /api/lang/coaches — 公開的教練人設清單（給語言選擇頁） */
import { publicCoaches } from "~/server/utils/lang-coaches";

export default defineEventHandler(() => {
  return { coaches: publicCoaches() };
});
