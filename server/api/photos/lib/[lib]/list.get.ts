import { requireAdmin } from "~/server/utils/auth-helper";
import {
  getPhotoIndex,
  isLibrarySlug,
  listLibraryFolder,
  listLibraryFolderFromIndex,
} from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const lib = getRouterParam(event, "lib") || "";
  if (!isLibrarySlug(lib)) {
    throw createError({ statusCode: 404, message: `Unknown library: ${lib}` });
  }
  if (lib === "chenwei") {
    // 此 endpoint 只給 training/hongshi 用；chenwei 走專屬 year-month 路徑
    throw createError({ statusCode: 400, message: "chenwei uses year-month endpoints" });
  }
  const q = getQuery(event);
  const subpath = String(q.path || "");
  const idx = await getPhotoIndex();
  if (idx) {
    const fromIdx = listLibraryFolderFromIndex(idx, lib, subpath);
    if (fromIdx) return { lib, path: subpath, ...fromIdx };
  }
  // fs fallback
  const { folders, files } = await listLibraryFolder(lib, subpath);
  return { lib, path: subpath, folders, files };
});
