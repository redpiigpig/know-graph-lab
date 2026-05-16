import { requireAdmin } from "~/server/utils/auth-helper";
import { countMonth, listMonths, listYears } from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const years = await listYears();
  const out: { year: string; total: number; monthsWithPhotos: number }[] = [];
  for (const year of years) {
    const months = await listMonths(year);
    let total = 0;
    let monthsWithPhotos = 0;
    for (const m of months) {
      const c = await countMonth(year, m);
      total += c;
      if (c > 0) monthsWithPhotos++;
    }
    out.push({ year, total, monthsWithPhotos });
  }
  return { years: out };
});
