import { requireAdmin } from "~/server/utils/auth-helper";
import { countBucket, listMonths } from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const year = getRouterParam(event, "year") || "";
  const months = await listMonths(year);
  const out: { month: string; count: number }[] = [];
  for (const m of months) out.push({ month: m, count: await countBucket(year, m) });
  const screenshots = await countBucket(year, "screenshots");
  const downloads = await countBucket(year, "downloads");
  return { year, months: out, screenshots, downloads };
});
