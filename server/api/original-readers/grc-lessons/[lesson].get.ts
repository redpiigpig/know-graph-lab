import { getGreekLesson } from "~/data/originalReaders/greek-full-reader";

export default defineEventHandler(async (event) => {
  setHeader(event, "X-Robots-Tag", "noindex, nofollow, noarchive");
  setHeader(event, "Cache-Control", "private, no-store");
  setHeader(event, "Vary", "Authorization");
  await requireAuth(event);

  const rawLesson = getRouterParam(event, "lesson") || "";
  if (!/^\d{1,2}$/u.test(rawLesson)) {
    throw createError({ statusCode: 404, message: "找不到這一課" });
  }
  const lesson = getGreekLesson(Number(rawLesson));
  if (!lesson) {
    throw createError({ statusCode: 404, message: "課次必須介於 1–50" });
  }
  return lesson;
});
