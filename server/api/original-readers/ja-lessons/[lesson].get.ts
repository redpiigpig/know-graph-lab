import {
  getJapaneseLesson,
  parseJapaneseLessonKey,
} from "~/data/originalReaders/japanese-full-reader";

export default defineEventHandler(async (event) => {
  setHeader(event, "X-Robots-Tag", "noindex, nofollow, noarchive");
  setHeader(event, "Cache-Control", "private, no-store");
  setHeader(event, "Vary", "Authorization");
  await requireAuth(event);

  // The reader is two volumes of fifty, so the key carries both numbers
  // ("v2-37").  A bare number still works and means the first volume.
  const parsed = parseJapaneseLessonKey(getRouterParam(event, "lesson") || "");
  if (!parsed) {
    throw createError({ statusCode: 404, message: "找不到這一課" });
  }
  const lesson = getJapaneseLesson(parsed.volume, parsed.lesson);
  if (!lesson) {
    throw createError({ statusCode: 404, message: "課次必須是第一、二冊的第 1–50 課" });
  }
  return lesson;
});
