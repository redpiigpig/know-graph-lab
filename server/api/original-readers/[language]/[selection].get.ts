import { getOriginalReaderSelection } from "~/data/originalReaders";
import { materializeOriginalReaderSelection } from "~/server/utils/original-reader-materialize";

export default defineEventHandler(async (event) => {
  setHeader(event, "X-Robots-Tag", "noindex, nofollow, noarchive");
  setHeader(event, "Cache-Control", "private, no-store");
  setHeader(event, "Vary", "Authorization");
  await requireAuth(event);

  const language = getRouterParam(event, "language") || "";
  const selectionId = getRouterParam(event, "selection") || "";
  const result = getOriginalReaderSelection(language, selectionId);
  if (!result) {
    throw createError({ statusCode: 404, message: "找不到這一篇選文" });
  }

  const materialized = await materializeOriginalReaderSelection(
    language,
    result.selection,
  );

  return {
    volume: {
      ...result.volume,
      selections: result.volume.selections.map((selection) => ({
        ...selection,
        segments: undefined,
      })),
    },
    selection: materialized.selection,
    materialization: {
      source: materialized.source,
      warning: materialized.warning,
    },
  };
});
