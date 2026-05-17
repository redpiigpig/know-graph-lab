import { requireAdmin } from "~/server/utils/auth-helper";
import { LIBRARIES, summarizeLibrary, type LibrarySlug } from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const out: {
    slug: LibrarySlug;
    name: string;
    layout: string;
    totalFiles: number;
    topFolders: number;
  }[] = [];
  for (const meta of Object.values(LIBRARIES)) {
    const s = await summarizeLibrary(meta.slug).catch(() => ({ totalFiles: 0, topFolders: 0 }));
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
