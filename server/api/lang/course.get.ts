/**
 * GET /api/lang/course?language=la
 * 回傳該語言的「課程逐課複習」策展資料（純策展、無 AI、無 DB）。
 * 目前只有教會拉丁文（la）有課程；其他語言 available:false。
 */
import { courseForClient } from "~/server/data/latinCourse";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const language = (getQuery(event).language as string) || "";
  const course = courseForClient(language);
  return { language, available: !!course, course: course ?? null };
});
