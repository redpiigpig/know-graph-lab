// POST /api/citations/render-document
// Body: { html: string, style?: CitationStyle }
//
// Scans the HTML for `[cite:UUID]` markers, replaces them with sequential
// superscript footnote anchors, and returns:
//   - html_with_footnotes : the rewritten document
//   - footnotes_html      : ordered footnote list
//   - bibliography_html   : sorted bibliography (Chicago Notes-Bibliography by default)
//   - bibliography_markdown
//   - missing             : UUIDs that didn't resolve
//
// The current persona uses Chicago Notes-Bibliography by default — most
// religious-studies departments accept either Chicago NB or SBL.
import {
  bookRowToCitationItem,
  journalRowToCitationItem,
  formatChicagoNotesFootnote,
  formatChicagoNotesBibliography,
  formatChicagoAuthorDate,
  formatSBL,
  formatAPA,
  type CitationStyle,
} from "../../utils/citation";

const CITE_RE = /\[cite:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\]/gi;

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event) as { html?: string; style?: CitationStyle };
  const html = body.html ?? "";
  const style = body.style || "chicago-notes-bibliography";

  // 1. Collect unique excerpt IDs in document order
  const order: string[] = [];
  const seen = new Set<string>();
  let m: RegExpExecArray | null;
  const re = new RegExp(CITE_RE.source, "gi");
  while ((m = re.exec(html)) !== null) {
    const id = m[1].toLowerCase();
    if (!seen.has(id)) {
      seen.add(id);
      order.push(id);
    }
  }

  if (!order.length) {
    return {
      html_with_footnotes: html,
      footnotes_html: "",
      bibliography_html: "",
      bibliography_markdown: "",
      missing: [],
      style,
      footnote_count: 0,
    };
  }

  // 2. Resolve excerpts → bring books / journal_articles in one go
  const { data: excerpts } = await supabase
    .from("excerpts")
    .select(`
      id, page_number, content,
      books(id, title, author, translator, editor, publish_place, publisher, publish_year,
            edition_number, original_title, original_author, original_publish_year,
            isbn, doi, series_title, series_number, container_title, container_editor,
            pages, url, accessed_date, language, citation_key),
      journal_articles(id, title, venue, author, publish_year, issue_label,
            doi, volume, issue, pages, url, accessed_date, publisher, language, citation_key)
    `)
    .in("id", order);

  const byId = new Map<string, any>();
  (excerpts ?? []).forEach((e: any) => byId.set(e.id, e));

  // 3. For each marker (in order), build footnote text + bibliography entry.
  // Multiple markers can point to the same excerpt → reuse number.
  const idToNum = new Map<string, number>();
  const footnotes: Array<{ num: number; text: string; sortKey: string; bibText: string; sourceKey: string }> = [];
  const missing: string[] = [];

  order.forEach((id, i) => {
    const num = i + 1;
    idToNum.set(id, num);
    const ex = byId.get(id);
    if (!ex) { missing.push(id); return; }

    const book = ex.books;
    const ja = ex.journal_articles;
    const pageOverride = (ex.page_number || "").trim();

    let item: any;
    let sourceKey: string;
    if (book) {
      item = bookRowToCitationItem({ ...book, pages: pageOverride || book.pages });
      sourceKey = `book:${book.id}`;
    } else if (ja) {
      item = journalRowToCitationItem({ ...ja, pages: pageOverride || ja.pages });
      sourceKey = `journal:${ja.id}`;
    } else {
      missing.push(id);
      return;
    }

    let footnoteText: string;
    let bibText: string;
    switch (style) {
      case "chicago-author-date":
        footnoteText = formatChicagoAuthorDate(item);
        bibText = formatChicagoAuthorDate(item);
        break;
      case "sbl":
        footnoteText = formatSBL(item);
        bibText = formatSBL(item);
        break;
      case "apa":
        footnoteText = formatAPA(item);
        bibText = formatAPA(item);
        break;
      case "chicago-notes-bibliography":
      case "chicago-notes-footnote":
      default:
        footnoteText = formatChicagoNotesFootnote(item);
        bibText = formatChicagoNotesBibliography(item);
        break;
    }

    footnotes.push({
      num,
      text: footnoteText,
      bibText,
      sourceKey,
      sortKey: (item.author || item.title || "").toString(),
    });
  });

  // 4. Bibliography: dedupe by source (book/journal), sort alphabetically.
  const bibMap = new Map<string, { sortKey: string; text: string }>();
  for (const f of footnotes) {
    if (!bibMap.has(f.sourceKey)) {
      bibMap.set(f.sourceKey, { sortKey: f.sortKey, text: f.bibText });
    }
  }
  const bibSorted = Array.from(bibMap.values()).sort((a, b) =>
    a.sortKey.localeCompare(b.sortKey, "zh-Hant"));

  // 5. Rewrite HTML — replace [cite:UUID] with <sup>n</sup>.
  // Multiple occurrences of the same UUID reuse the same n.
  const html_with_footnotes = html.replace(CITE_RE, (_, id) => {
    const num = idToNum.get(id.toLowerCase());
    if (!num) return `<sup class="text-red-500" title="未對應的引用">?</sup>`;
    return `<sup class="text-blue-700"><a href="#fn-${num}">${num}</a></sup>`;
  });

  const renderInline = (text: string) => text.replace(/\*([^*\n]+?)\*/g, '<em>$1</em>');

  const footnotes_html = footnotes.length
    ? `<ol class="text-sm text-gray-700 space-y-1.5 list-decimal pl-6">`
      + footnotes.map((f) => `<li id="fn-${f.num}">${renderInline(escapeHtml(f.text))}</li>`).join("")
      + `</ol>`
    : "";

  const bibliography_html = bibSorted.length
    ? `<ul class="text-sm text-gray-700 space-y-2 pl-0 list-none">`
      + bibSorted.map((b) => `<li class="pl-6 -indent-6">${renderInline(escapeHtml(b.text))}</li>`).join("")
      + `</ul>`
    : "";

  const bibliography_markdown = bibSorted
    .map((b) => `- ${b.text}`)
    .join("\n");

  return {
    html_with_footnotes,
    footnotes_html,
    bibliography_html,
    bibliography_markdown,
    missing: Array.from(new Set(missing)),
    style,
    footnote_count: footnotes.length,
  };
});

function escapeHtml(s: string): string {
  return s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c] as string));
}
