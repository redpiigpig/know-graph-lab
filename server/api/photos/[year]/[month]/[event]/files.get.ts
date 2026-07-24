import { requireAdmin } from "~/server/utils/auth-helper";
import { getPhotoIndex, listFiles, listFilesFromIndex } from "~/server/utils/photos";

// 月內事件夾檔案清單：/api/photos/{year}/{MM}/{event}/files
// segment 傳給 utils 為 "{MM}/{event}"（bucketDir / listFilesFromIndex 已支援單層巢狀）。
export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const year = getRouterParam(event, "year") || "";
  const month = getRouterParam(event, "month") || "";
  const rawEvent = getRouterParam(event, "event") || "";
  let eventName = rawEvent;
  if (rawEvent.includes("%")) {
    try { eventName = decodeURIComponent(rawEvent); } catch { eventName = rawEvent; }
  }
  const segment = `${month}/${eventName}`;

  const idx = await getPhotoIndex();
  if (idx) {
    const fromIdx = listFilesFromIndex(idx, year, segment);
    if (fromIdx !== null) return { year, month, event: eventName, files: fromIdx };
  }
  // fs fallback
  const files = await listFiles(year, segment);
  return { year, month, event: eventName, files };
});
