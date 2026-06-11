/**
 * GET /api/ebooks/{id}/page-map
 * Returns [{ chunk_index, page_number }] for every chunk, ordered by chunk_index.
 *
 * The original-PDF reader (/ebook/pdf/[id]) renders physical PDF pages via
 * pdf.js, but OCR chunk_index ≠ physical page when OCR skipped blank/cover
 * pages (e.g. 979 chunks for a 983-page scan). The chunk's page_number IS the
 * true physical page, so this map lets the client fetch the right OCR text for
 * whatever page pdf.js is showing.
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const id = getRouterParam(event, "id");
  const supabase = getAdminClient();

  const out: { chunk_index: number; page_number: number | null }[] = [];
  const step = 1000;
  for (let from = 0; ; from += step) {
    const { data, error } = await supabase
      .from("ebook_chunks")
      .select("chunk_index,page_number")
      .eq("ebook_id", id!)
      .order("chunk_index")
      .range(from, from + step - 1);
    if (error) throw createError({ statusCode: 500, message: error.message });
    if (!data || data.length === 0) break;
    out.push(...data);
    if (data.length < step) break;
  }
  return out;
});
