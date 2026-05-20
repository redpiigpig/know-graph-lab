// Citation formatters — Chicago Notes-Bibliography, Chicago Author-Date,
// SBL Handbook of Style, APA 7, plus BibTeX export.
//
// Inputs come from either `books` or `journal_articles` rows. We normalize
// them into one CitationItem shape so each formatter stays small.

export type CitationItemType = "book" | "chapter" | "article" | "web";

export interface CitationItem {
  type: CitationItemType;
  // primary work
  title: string;
  author?: string;       // already formatted as "Last, First; Last, First"-ish or "張三、李四"
  translator?: string;
  editor?: string;
  // book-specific
  publish_place?: string;
  publisher?: string;
  publish_year?: number | string;
  edition_number?: string;
  series_title?: string;
  series_number?: string;
  isbn?: string;
  // chapter within edited volume
  container_title?: string;
  container_editor?: string;
  pages?: string;
  // journal article
  venue?: string;
  volume?: string;
  issue?: string;
  // original work (for translated 二手書)
  original_title?: string;
  original_author?: string;
  original_publisher?: string;
  original_publish_year?: number | string;
  // online
  url?: string;
  doi?: string;
  accessed_date?: string;   // ISO date
  language?: string;
  citation_key?: string;
}

// ── helpers ─────────────────────────────────────────────────

const isChinese = (s?: string) => !!s && /[一-鿿㐀-䶿]/.test(s);

function fmtYear(y?: number | string): string {
  if (y === undefined || y === null || y === "") return "n.d.";
  return String(y);
}

function joinNonEmpty(parts: (string | undefined | null | false)[], sep = " "): string {
  return parts.filter((p): p is string => !!p && String(p).trim() !== "").join(sep);
}

function ensurePeriod(s: string): string {
  const t = s.trimEnd();
  if (!t) return "";
  if (/[.!?。．！？]$/.test(t)) return t;
  return t + ".";
}

// Split an author field like "張三、李四、王五" or "Smith, John; Doe, Jane"
// into individual names while being tolerant of mixed scripts.
function splitAuthors(raw?: string): string[] {
  if (!raw) return [];
  return raw
    .split(/、|；|;|,\s+and\s+| and /i)
    .map((s) => s.trim())
    .filter(Boolean);
}

// Western surname-first ("Smith, John") for first author, given-first for
// subsequent — Chicago / APA style. Chinese names already lead with surname,
// so we leave them as-is.
function formatAuthorsWestern(raw: string | undefined, style: "chicago" | "apa" | "sbl"): string {
  const list = splitAuthors(raw);
  if (!list.length) return "";
  const formatted = list.map((name, i) => {
    if (isChinese(name)) return name;
    // If user already wrote "Last, First" keep it.
    if (name.includes(",")) {
      if (i === 0) return name;
      // subsequent: flip back to "First Last"
      const [last, first] = name.split(",").map((s) => s.trim());
      return `${first} ${last}`;
    }
    // "First Middle Last" — split, last token is surname.
    const parts = name.split(/\s+/);
    if (parts.length < 2) return name;
    const last = parts.pop()!;
    const first = parts.join(" ");
    if (i === 0) {
      if (style === "apa") {
        const initials = first.split(/\s+/).map((p) => p[0]?.toUpperCase() + ".").join(" ");
        return `${last}, ${initials}`;
      }
      return `${last}, ${first}`;
    }
    if (style === "apa") {
      const initials = first.split(/\s+/).map((p) => p[0]?.toUpperCase() + ".").join(" ");
      return `${initials} ${last}`;
    }
    return `${first} ${last}`;
  });

  if (formatted.length === 1) return formatted[0];
  if (formatted.length === 2) {
    const sep = isChinese(list[0]) ? "、" : (style === "apa" ? ", & " : ", and ");
    return formatted.join(sep);
  }
  const last = formatted.pop()!;
  const sep = isChinese(list[0]) ? "、" : ", ";
  const tail = isChinese(list[0]) ? "、" : (style === "apa" ? ", & " : ", and ");
  return formatted.join(sep) + tail + last;
}

// Author-date in-text year, prefers Chinese surname-only.
function authorShort(raw?: string): string {
  const list = splitAuthors(raw);
  if (!list.length) return "";
  const first = list[0];
  if (isChinese(first)) return first.length <= 4 ? first : first.slice(0, 4);
  // Western: surname
  if (first.includes(",")) return first.split(",")[0].trim();
  const parts = first.split(/\s+/);
  return parts[parts.length - 1];
}

// Italics — markdown style so we can render in UI. BibTeX escapes separately.
const it = (s: string) => `*${s}*`;

// ── Chicago Notes-Bibliography (NB) ──────────────────────────
// Footnote form for first citation. (Bibliography form differs slightly —
// we provide it via formatChicagoNotesBibliography for the bib list.)

export function formatChicagoNotesFootnote(item: CitationItem): string {
  const authors = formatAuthorsWestern(item.author, "chicago");
  const out: string[] = [];

  if (item.type === "article") {
    if (authors) out.push(`${authors},`);
    if (item.title) out.push(`"${item.title},"`);
    if (item.venue) out.push(`${it(item.venue)}`);
    const volIssue = joinNonEmpty([item.volume, item.issue ? `no. ${item.issue}` : undefined], ", ");
    const yearPart = item.publish_year ? `(${fmtYear(item.publish_year)})` : "";
    const tail = joinNonEmpty([volIssue, yearPart], " ");
    if (tail) out.push(tail + (item.pages ? ":" : "."));
    if (item.pages) out.push(`${item.pages}.`);
    if (item.doi) out.push(`https://doi.org/${item.doi}.`);
    return joinNonEmpty(out, " ");
  }

  if (item.type === "chapter") {
    if (authors) out.push(`${authors},`);
    if (item.title) out.push(`"${item.title},"`);
    if (item.container_title) {
      const editorPart = item.container_editor ? `ed. ${item.container_editor}` : "";
      out.push(`in ${it(item.container_title)}${editorPart ? ", " + editorPart : ""},`);
    }
    if (item.pages) out.push(`${item.pages},`);
    const pub = joinNonEmpty([item.publish_place, item.publisher], ": ");
    const yearPart = fmtYear(item.publish_year);
    if (pub || yearPart) out.push(`(${joinNonEmpty([pub, yearPart], ", ")}).`);
    return joinNonEmpty(out, " ");
  }

  if (item.type === "web") {
    if (authors) out.push(`${authors},`);
    if (item.title) out.push(`"${item.title},"`);
    if (item.publisher) out.push(`${item.publisher},`);
    if (item.publish_year) out.push(`${fmtYear(item.publish_year)},`);
    if (item.url) out.push(`${item.url}.`);
    return joinNonEmpty(out, " ");
  }

  // book — Chicago Notes footnote format:
  // Author, *Title*, trans. X, ed. Y (Place: Publisher, Year), pp.
  let s = "";
  if (authors) s += `${authors}, `;
  if (item.title) s += it(item.title);
  if (item.translator) s += `, trans. ${item.translator}`;
  if (item.editor) s += `, ed. ${item.editor}`;
  if (item.edition_number) s += `, ${item.edition_number} ed.`;
  const pub = joinNonEmpty([item.publish_place, item.publisher], ": ");
  const yearPart = fmtYear(item.publish_year);
  if (pub || yearPart) s += ` (${joinNonEmpty([pub, yearPart], ", ")})`;
  if (item.pages) s += `, ${item.pages}`;
  return ensurePeriod(s);
}

export function formatChicagoNotesBibliography(item: CitationItem): string {
  // Bib form: author block first, then title block ending in periods.
  const authors = formatAuthorsWestern(item.author, "chicago");
  const out: string[] = [];

  if (item.type === "article") {
    if (authors) out.push(ensurePeriod(authors));
    if (item.title) out.push(`"${item.title}."`);
    if (item.venue) out.push(`${it(item.venue)}`);
    const volIssue = joinNonEmpty([item.volume, item.issue ? `no. ${item.issue}` : undefined], ", ");
    const yearPart = item.publish_year ? `(${fmtYear(item.publish_year)})` : "";
    const tail = joinNonEmpty([volIssue, yearPart], " ");
    if (tail) out.push(tail + (item.pages ? ":" : "."));
    if (item.pages) out.push(`${item.pages}.`);
    if (item.doi) out.push(`https://doi.org/${item.doi}.`);
    return joinNonEmpty(out, " ");
  }

  if (item.type === "chapter") {
    if (authors) out.push(ensurePeriod(authors));
    if (item.title) out.push(`"${item.title}."`);
    if (item.container_title) {
      const editorPart = item.container_editor ? `Edited by ${item.container_editor}` : "";
      out.push(`In ${it(item.container_title)}${editorPart ? ", " + editorPart : ""},`);
    }
    if (item.pages) out.push(`${item.pages}.`);
    const pub = joinNonEmpty([item.publish_place, item.publisher], ": ");
    const yearPart = fmtYear(item.publish_year);
    if (pub || yearPart) out.push(`${joinNonEmpty([pub, yearPart], ", ")}.`);
    return joinNonEmpty(out, " ");
  }

  // book / web fall back to book-ish shape
  if (authors) out.push(ensurePeriod(authors));
  if (item.title) out.push(ensurePeriod(it(item.title)));
  if (item.translator) out.push(`Translated by ${item.translator}.`);
  if (item.editor) out.push(`Edited by ${item.editor}.`);
  if (item.edition_number) out.push(`${item.edition_number} ed.`);
  const pub = joinNonEmpty([item.publish_place, item.publisher], ": ");
  const yearPart = fmtYear(item.publish_year);
  if (pub || yearPart) out.push(`${joinNonEmpty([pub, yearPart], ", ")}.`);
  if (item.url && item.type === "web") out.push(`${item.url}.`);
  return joinNonEmpty(out, " ");
}

// ── Chicago Author-Date ──────────────────────────────────────

export function formatChicagoAuthorDate(item: CitationItem): string {
  const authors = formatAuthorsWestern(item.author, "chicago");
  const year = fmtYear(item.publish_year);
  const out: string[] = [];

  if (authors) out.push(`${ensurePeriod(authors)} ${year}.`);
  else if (year) out.push(`${year}.`);

  if (item.type === "article") {
    if (item.title) out.push(`"${item.title}."`);
    if (item.venue) out.push(it(item.venue));
    const volIssue = joinNonEmpty([item.volume, item.issue ? `no. ${item.issue}` : undefined], ", ");
    if (volIssue) out.push(volIssue + (item.pages ? ":" : "."));
    if (item.pages) out.push(`${item.pages}.`);
    if (item.doi) out.push(`https://doi.org/${item.doi}.`);
    return joinNonEmpty(out, " ");
  }

  if (item.title) out.push(ensurePeriod(it(item.title)));
  if (item.translator) out.push(`Translated by ${item.translator}.`);
  if (item.editor) out.push(`Edited by ${item.editor}.`);
  const pub = joinNonEmpty([item.publish_place, item.publisher], ": ");
  if (pub) out.push(`${pub}.`);
  if (item.url && item.type === "web") out.push(`${item.url}.`);
  return joinNonEmpty(out, " ");
}

export function formatChicagoAuthorDateInText(item: CitationItem): string {
  const a = authorShort(item.author);
  const y = fmtYear(item.publish_year);
  const p = item.pages ? `, ${item.pages}` : "";
  if (a && y) return `(${a} ${y}${p})`;
  if (y) return `(${y}${p})`;
  return "";
}

// ── SBL Handbook of Style ────────────────────────────────────
// SBL is close to Chicago NB but with abbreviated journal names and
// distinct ordering. We approximate the canonical form.

export function formatSBL(item: CitationItem): string {
  const authors = formatAuthorsWestern(item.author, "sbl");

  if (item.type === "article") {
    const out: string[] = [];
    if (authors) out.push(ensurePeriod(authors));
    if (item.title) out.push(`"${item.title}."`);
    if (item.venue) out.push(`${it(item.venue)}`);
    if (item.volume) out.push(`${item.volume}`);
    const yearPart = item.publish_year ? `(${fmtYear(item.publish_year)})` : "";
    if (yearPart) out.push(yearPart + (item.pages ? ":" : "."));
    if (item.pages) out.push(`${item.pages}.`);
    if (item.doi) out.push(`doi:${item.doi}.`);
    return joinNonEmpty(out, " ");
  }

  // book / chapter
  const out: string[] = [];
  if (authors) out.push(ensurePeriod(authors));
  if (item.title) out.push(ensurePeriod(it(item.title)));
  if (item.translator) out.push(`Translated by ${item.translator}.`);
  if (item.editor) out.push(`Edited by ${item.editor}.`);
  if (item.series_title) out.push(`${item.series_title}${item.series_number ? " " + item.series_number : ""}.`);
  const pub = joinNonEmpty([item.publish_place, item.publisher], ": ");
  const yearPart = fmtYear(item.publish_year);
  if (pub || yearPart) out.push(`${joinNonEmpty([pub, yearPart], ", ")}.`);
  return joinNonEmpty(out, " ");
}

// ── APA 7 ────────────────────────────────────────────────────

export function formatAPA(item: CitationItem): string {
  const authors = formatAuthorsWestern(item.author, "apa");
  const year = item.publish_year ? `(${fmtYear(item.publish_year)})` : "(n.d.)";
  const out: string[] = [];
  if (authors) out.push(`${authors} ${year}.`);
  else out.push(`${year}.`);

  if (item.type === "article") {
    if (item.title) out.push(`${ensurePeriod(item.title)}`);
    if (item.venue) {
      const volIssue = joinNonEmpty([item.volume, item.issue ? `(${item.issue})` : undefined], "");
      out.push(`${it(item.venue)}${volIssue ? ", " + volIssue : ""}${item.pages ? ", " + item.pages : ""}.`);
    }
    if (item.doi) out.push(`https://doi.org/${item.doi}`);
    return joinNonEmpty(out, " ");
  }

  if (item.title) out.push(ensurePeriod(it(item.title)));
  if (item.edition_number) out.push(`(${item.edition_number} ed.).`);
  if (item.publisher) out.push(`${ensurePeriod(item.publisher)}`);
  if (item.url && item.type === "web") out.push(`${item.url}`);
  return joinNonEmpty(out, " ");
}

// ── BibTeX ───────────────────────────────────────────────────

function bibtexEscape(s: string): string {
  return s.replace(/[{}\\]/g, "\\$&").replace(/&/g, "\\&");
}

function bibtexKey(item: CitationItem): string {
  if (item.citation_key) return item.citation_key;
  const a = authorShort(item.author).replace(/\s+/g, "").toLowerCase() || "anon";
  const y = item.publish_year ? String(item.publish_year) : "nd";
  const t = (item.title || "")
    .toLowerCase()
    .replace(/[^a-z0-9一-鿿]+/g, "")
    .slice(0, 8) || "ref";
  return `${a}${y}${t}`;
}

export function formatBibTeX(item: CitationItem): string {
  const key = bibtexKey(item);
  let type: string;
  if (item.type === "article") type = "article";
  else if (item.type === "chapter") type = "incollection";
  else if (item.type === "web") type = "misc";
  else type = "book";

  const fields: Record<string, string | undefined> = {
    author: item.author,
    title: item.title,
    translator: item.translator,
    editor: item.editor,
    publisher: item.publisher,
    address: item.publish_place,
    year: item.publish_year ? String(item.publish_year) : undefined,
    edition: item.edition_number,
    series: item.series_title,
    number: item.series_number,
    journal: item.venue,
    volume: item.volume,
    issue: item.issue,
    pages: item.pages,
    booktitle: item.container_title,
    isbn: item.isbn,
    doi: item.doi,
    url: item.url,
    urldate: item.accessed_date,
    language: item.language,
    note: item.original_title
      ? `Originally: ${joinNonEmpty([item.original_author, item.original_title, item.original_publish_year && String(item.original_publish_year)], ", ")}`
      : undefined,
  };

  const lines = Object.entries(fields)
    .filter(([, v]) => v !== undefined && v !== null && v !== "")
    .map(([k, v]) => `  ${k} = {${bibtexEscape(String(v))}}`);

  return `@${type}{${key},\n${lines.join(",\n")}\n}`;
}

// ── master dispatcher ────────────────────────────────────────

export type CitationStyle =
  | "chicago-notes-footnote"
  | "chicago-notes-bibliography"
  | "chicago-author-date"
  | "chicago-author-date-intext"
  | "sbl"
  | "apa"
  | "bibtex";

export function formatCitation(item: CitationItem, style: CitationStyle): string {
  switch (style) {
    case "chicago-notes-footnote":     return formatChicagoNotesFootnote(item);
    case "chicago-notes-bibliography": return formatChicagoNotesBibliography(item);
    case "chicago-author-date":        return formatChicagoAuthorDate(item);
    case "chicago-author-date-intext": return formatChicagoAuthorDateInText(item);
    case "sbl":                        return formatSBL(item);
    case "apa":                        return formatAPA(item);
    case "bibtex":                     return formatBibTeX(item);
  }
}

// ── normalizers — DB row → CitationItem ──────────────────────

export function bookRowToCitationItem(row: any): CitationItem {
  const isChapter = !!row.container_title;
  return {
    type: isChapter ? "chapter" : "book",
    title: row.title || "",
    author: row.author,
    translator: row.translator,
    editor: row.editor,
    publish_place: row.publish_place,
    publisher: row.publisher,
    publish_year: row.publish_year,
    edition_number: row.edition_number,
    series_title: row.series_title,
    series_number: row.series_number,
    isbn: row.isbn,
    doi: row.doi,
    container_title: row.container_title,
    container_editor: row.container_editor,
    pages: row.pages,
    url: row.url,
    accessed_date: row.accessed_date,
    language: row.language,
    original_title: row.original_title,
    original_author: row.original_author,
    original_publisher: row.original_publisher,
    original_publish_year: row.original_publish_year,
    citation_key: row.citation_key,
  };
}

export function journalRowToCitationItem(row: any): CitationItem {
  return {
    type: "article",
    title: row.title || "",
    author: row.author,
    venue: row.venue,
    volume: row.volume,
    issue: row.issue,
    publish_year: row.publish_year,
    pages: row.pages,
    publisher: row.publisher,
    doi: row.doi,
    url: row.url,
    accessed_date: row.accessed_date,
    language: row.language,
    citation_key: row.citation_key,
  };
}
