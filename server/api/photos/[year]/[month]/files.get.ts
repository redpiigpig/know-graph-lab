import { requireAdmin } from "~/server/utils/auth-helper";
import { getPhotoIndex, listFiles, listFilesFromIndex } from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const year = getRouterParam(event, "year") || "";
  const month = getRouterParam(event, "month") || "";
  const idx = await getPhotoIndex();
  if (idx) {
    const fromIdx = listFilesFromIndex(idx, year, month);
    if (fromIdx !== null) return { year, month, files: fromIdx };
  }
  // fs fallback
  const files = await listFiles(year, month);
  return { year, month, files };
});
