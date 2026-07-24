import { requireAdmin } from "~/server/utils/auth-helper";
import {
  getMonthEventsFromIndex,
  getPhotoIndex,
  listFiles,
  listFilesFromIndex,
} from "~/server/utils/photos";

const MONTH_RE = /^(0[1-9]|1[0-2])$/;

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const year = getRouterParam(event, "year") || "";
  const month = getRouterParam(event, "month") || "";
  const idx = await getPhotoIndex();
  if (idx) {
    const fromIdx = listFilesFromIndex(idx, year, month);
    if (fromIdx !== null) {
      // 若是真正的月份，附帶該月底下的事件夾清單給前端渲染
      const events = MONTH_RE.test(month) ? getMonthEventsFromIndex(idx, year, month) : [];
      return { year, month, files: fromIdx, events };
    }
  }
  // fs fallback
  const files = await listFiles(year, month);
  return { year, month, files, events: [] };
});
