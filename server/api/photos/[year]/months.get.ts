import { requireAdmin } from "~/server/utils/auth-helper";
import { countMonth, listMonths } from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const year = getRouterParam(event, "year") || "";
  const months = await listMonths(year);
  const out: { month: string; count: number }[] = [];
  for (const m of months) out.push({ month: m, count: await countMonth(year, m) });
  return { year, months: out };
});
