import { getOriginalReaderVolume } from "~/data/originalReaders";

export default defineEventHandler(async (event) => {
  setHeader(event, "X-Robots-Tag", "noindex, nofollow, noarchive");
  setHeader(event, "Cache-Control", "private, no-store");
  setHeader(event, "Vary", "Authorization");
  await requireAuth(event);

  const language = getRouterParam(event, "language") || "";
  const volume = getOriginalReaderVolume(language);
  if (!volume) {
    throw createError({ statusCode: 404, message: "找不到這本原文讀本" });
  }

  return {
    ...volume,
    selections: volume.selections.map((selection) => ({
      ...selection,
      segments: undefined,
      segmentCount: selection.segments?.length || 0,
    })),
  };
});
