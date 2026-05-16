import { requireAdmin } from "~/server/utils/auth-helper";
import { listYears, countMonth, listMonths } from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const years = await listYears();
  const out: { year: string; total: number }[] = [];
  for (const year of years) {
    const months = await listMonths(year);
    let total = 0;
    for (const m of months) total += await countMonth(year, m);
    out.push({ year, total });
  }
  return { years: out };
});
