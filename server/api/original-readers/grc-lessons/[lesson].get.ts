import { getGreekLesson, parseGreekLessonKey } from "~/data/originalReaders/greek-full-reader";

export default defineEventHandler(async (event) => {
  setHeader(event, "X-Robots-Tag", "noindex, nofollow, noarchive");
  setHeader(event, "Cache-Control", "private, no-store");
  setHeader(event, "Vary", "Authorization");
  await requireAuth(event);

  // The reader is two volumes, so the key carries both numbers ("v2-37").  A
  // bare number still works and means the first volume, which is what every
  // link written before the second volume existed meant.
  const parsed = parseGreekLessonKey(getRouterParam(event, "lesson") || "");
  if (!parsed) {
    throw createError({ statusCode: 404, message: "找不到這一課" });
  }
  const lesson = getGreekLesson(parsed.volume, parsed.lesson);
  if (!lesson) {
    throw createError({ statusCode: 404, message: "課次必須是第 1–2 冊的第 1–50 課" });
  }
  return lesson;
});
