import { getLatinReaderOverview } from "~/data/originalReaders/latin-full-reader";

export default defineEventHandler(async (event) => {
  setHeader(event, "X-Robots-Tag", "noindex, nofollow, noarchive");
  setHeader(event, "Cache-Control", "private, no-store");
  setHeader(event, "Vary", "Authorization");
  await requireAuth(event);

  return getLatinReaderOverview();
});
