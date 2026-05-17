import { requireAdmin } from "~/server/utils/auth-helper";
import { isLibrarySlug, listLibraryFolder } from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const lib = getRouterParam(event, "lib") || "";
  if (!isLibrarySlug(lib)) {
    throw createError({ statusCode: 404, message: `Unknown library: ${lib}` });
  }
  const q = getQuery(event);
  const subpath = String(q.path || "");
  const { folders, files } = await listLibraryFolder(lib, subpath);
  return { lib, path: subpath, folders, files };
});
