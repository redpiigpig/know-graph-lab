// GET /api/citations/bibtex
//   ?source=book|journal&id=<uuid>          → single .bib entry
//   ?source=all                              → dump entire library
//   (no params → defaults to all)
//
// Always returns text/plain so browsers offer Save As.
import {
  bookRowToCitationItem,
  journalRowToCitationItem,
  formatBibTeX,
} from "../../utils/citation";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { source, id } = getQuery(event) as { source?: string; id?: string };

  setHeader(event, "Content-Type", "text/plain; charset=utf-8");

  if ((source === "book" || source === "journal") && id) {
    const table = source === "book" ? "books" : "journal_articles";
    const { data, error } = await supabase.from(table).select("*").eq("id", id).single();
    if (error) throw createError({ statusCode: 404, message: error.message });
    const item = source === "book" ? bookRowToCitationItem(data) : journalRowToCitationItem(data);
    setHeader(event, "Content-Disposition", `attachment; filename="${(item.citation_key || id)}.bib"`);
    return formatBibTeX(item);
  }

  // Dump all
  const [{ data: books }, { data: journals }] = await Promise.all([
    supabase.from("books").select("*"),
    supabase.from("journal_articles").select("*"),
  ]);

  const entries: string[] = [];
  (books ?? []).forEach((b) => entries.push(formatBibTeX(bookRowToCitationItem(b))));
  (journals ?? []).forEach((j) => entries.push(formatBibTeX(journalRowToCitationItem(j))));

  setHeader(event, "Content-Disposition", 'attachment; filename="know-graph-lab.bib"');
  return entries.join("\n\n") + "\n";
});
