// GET /api/citations/format?source=book&id=<uuid>&style=chicago-notes-footnote
// Returns formatted citation strings for one source in all common styles.
import {
  bookRowToCitationItem,
  journalRowToCitationItem,
  formatCitation,
  type CitationStyle,
} from "../../utils/citation";

const ALL_STYLES: CitationStyle[] = [
  "chicago-notes-footnote",
  "chicago-notes-bibliography",
  "chicago-author-date",
  "chicago-author-date-intext",
  "sbl",
  "apa",
  "bibtex",
];

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { source, id, style } = getQuery(event) as {
    source?: "book" | "journal";
    id?: string;
    style?: CitationStyle;
  };
  if (!source || !id) throw createError({ statusCode: 400, message: "source and id required" });

  let item;
  if (source === "book") {
    const { data, error } = await supabase
      .from("books")
      .select("*")
      .eq("id", id)
      .single();
    if (error) throw createError({ statusCode: 404, message: error.message });
    item = bookRowToCitationItem(data);
  } else if (source === "journal") {
    const { data, error } = await supabase
      .from("journal_articles")
      .select("*")
      .eq("id", id)
      .single();
    if (error) throw createError({ statusCode: 404, message: error.message });
    item = journalRowToCitationItem(data);
  } else {
    throw createError({ statusCode: 400, message: "source must be 'book' or 'journal'" });
  }

  if (style) {
    return { style, formatted: formatCitation(item, style) };
  }

  // No style → return all
  const all: Record<string, string> = {};
  for (const s of ALL_STYLES) {
    all[s] = formatCitation(item, s);
  }
  return { item, styles: all };
});
