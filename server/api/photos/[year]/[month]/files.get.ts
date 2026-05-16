import { requireAdmin } from "~/server/utils/auth-helper";
import { listFiles } from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const year = getRouterParam(event, "year") || "";
  const month = getRouterParam(event, "month") || "";
  const files = await listFiles(year, month);
  return { year, month, files };
});
