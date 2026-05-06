/**
 * POST /api/annotations
 * Create an annotation. Body: { ebook_id, chunk_index, selected_text,
 *                                context_before?, context_after?, note?, color?,
 *                                save_as_excerpt? }
 *
 * If `save_as_excerpt: true`, also inserts an excerpts row and links via excerpt_id.
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event) as {
    ebook_id?: string;
    chunk_index?: number;
    selected_text?: string;
    context_before?: string;
    context_after?: string;
    note?: string;
    color?: string;
    save_as_excerpt?: boolean;
    excerpt_title?: string;
    page_label?: string;
    chapter?: string;
  };

  if (!body.ebook_id) throw createError({ statusCode: 400, message: "ebook_id required" });
  if (body.chunk_index === undefined || body.chunk_index === null)
    throw createError({ statusCode: 400, message: "chunk_index required" });
  if (!body.selected_text?.trim()) throw createError({ statusCode: 400, message: "selected_text required" });

  let excerpt_id: string | null = null;

  if (body.save_as_excerpt) {
    const { data: ebookRow } = await supabase
      .from("ebooks")
      .select("book_id, title, author")
      .eq("id", body.ebook_id)
      .single();

    // If this ebook has no linked books row yet, auto-create one and persist
    // the link — so the resulting excerpt actually shows up in 書摘圖書館.
    let bookId = (ebookRow as any)?.book_id ?? null;
    if (!bookId && ebookRow) {
      const { data: book, error: bookErr } = await supabase
        .from("books")
        .insert({ title: (ebookRow as any).title, author: (ebookRow as any).author })
        .select("id")
        .single();
      if (bookErr) throw createError({ statusCode: 500, message: `book auto-create: ${bookErr.message}` });
      bookId = (book as any).id;
      await supabase.from("ebooks").update({ book_id: bookId }).eq("id", body.ebook_id);
    }

    const { data: ex, error: exErr } = await supabase
      .from("excerpts")
      .insert({
        content: body.selected_text,
        title: body.excerpt_title || null,
        book_id: bookId,
        chapter: body.chapter || null,
        page_number: body.page_label ?? null,
      })
      .select("id")
      .single();
    if (exErr) throw createError({ statusCode: 500, message: `excerpt insert: ${exErr.message}` });
    excerpt_id = (ex as any).id;
  }

  const { data, error } = await supabase
    .from("annotations")
    .insert({
      ebook_id: body.ebook_id,
      chunk_index: body.chunk_index,
      selected_text: body.selected_text,
      context_before: body.context_before ?? null,
      context_after: body.context_after ?? null,
      note: body.note ?? null,
      color: body.color ?? "yellow",
      excerpt_id,
    })
    .select()
    .single();

  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
