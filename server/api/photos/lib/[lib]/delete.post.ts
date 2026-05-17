import fs from "node:fs/promises";
import { requireAdmin } from "~/server/utils/auth-helper";
import { isLibrarySlug, resolveLibFilePath } from "~/server/utils/photos";

interface Item {
  path: string;
  name: string;
}

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const lib = getRouterParam(event, "lib") || "";
  if (!isLibrarySlug(lib)) {
    throw createError({ statusCode: 404, message: `Unknown library: ${lib}` });
  }
  const body = await readBody<{ items?: Item[] }>(event);
  const items = body?.items || [];
  if (!Array.isArray(items) || items.length === 0) {
    throw createError({ statusCode: 400, message: "No items" });
  }
  let deleted = 0;
  const errors: { item: Item; error: string }[] = [];
  for (const it of items) {
    try {
      const fp = resolveLibFilePath(lib, it.path || "", it.name);
      await fs.unlink(fp);
      deleted++;
    } catch (e: unknown) {
      errors.push({ item: it, error: (e as Error).message });
    }
  }
  return { deleted, errors };
});
