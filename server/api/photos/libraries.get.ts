import { requireAdmin } from "~/server/utils/auth-helper";
import {
  LIBRARIES,
  getPhotoIndex,
  summarizeLibrary,
  summarizeLibraryFromIndex,
  type LibrarySlug,
} from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const idx = await getPhotoIndex();
  const out: {
    slug: LibrarySlug;
    name: string;
    layout: string;
    totalFiles: number;
    topFolders: number;
  }[] = [];
  for (const meta of Object.values(LIBRARIES)) {
    // 走 index 優先（瞬間），找不到才掃 fs（最舊版 fallback）
    let s = idx ? summarizeLibraryFromIndex(idx, meta.slug) : null;
    if (!s) {
      s = await summarizeLibrary(meta.slug).catch(() => ({ totalFiles: 0, topFolders: 0 }));
    }
    out.push({
      slug: meta.slug,
      name: meta.name,
      layout: meta.layout,
      totalFiles: s.totalFiles,
      topFolders: s.topFolders,
    });
  }
  return { libraries: out };
});
