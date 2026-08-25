import { getLatinLesson, parseLatinLessonKey } from "~/data/originalReaders/latin-full-reader";

export default defineEventHandler(async (event) => {
  setHeader(event, "X-Robots-Tag", "noindex, nofollow, noarchive");
  setHeader(event, "Cache-Control", "private, no-store");
  setHeader(event, "Vary", "Authorization");
  await requireAuth(event);

  // Two volumes, so the key carries both numbers ("v2-37"); a bare number means
  // the first volume.
  const parsed = parseLatinLessonKey(getRouterParam(event, "lesson") || "");
  if (!parsed) {
    throw createError({ statusCode: 404, message: "找不到這一課" });
  }
  const lesson = getLatinLesson(parsed.volume, parsed.lesson);
  if (!lesson) {
    throw createError({ statusCode: 404, message: "課次必須是第 1–2 冊的第 1–50 課" });
  }
  return { ...lesson, volume: parsed.volume };
});
