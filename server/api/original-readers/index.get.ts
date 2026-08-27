import { ORIGINAL_READER_VOLUMES } from "~/data/originalReaders";

export default defineEventHandler(async (event) => {
  setHeader(event, "X-Robots-Tag", "noindex, nofollow, noarchive");
  setHeader(event, "Cache-Control", "private, no-store");
  setHeader(event, "Vary", "Authorization");
  await requireAuth(event);

  return ORIGINAL_READER_VOLUMES.map((volume) => ({
    id: volume.id,
    slug: volume.slug,
    language: volume.language,
    title: volume.title,
    subtitle: volume.subtitle,
    rtl: volume.rtl,
    print: volume.print,
    pronunciationProfiles: volume.pronunciationProfiles,
    parts: volume.parts,
    selectionCount: volume.selections.length,
    readyCount: volume.selections.filter((item) =>
      ["sample_ready", "edited", "audio_ready", "complete"].includes(item.status),
    ).length,
    estimatedPages: volume.selections.reduce(
      (total, item) => total + item.estimatedPages,
      0,
    ),
  }));
});
