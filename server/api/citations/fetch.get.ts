// GET /api/citations/fetch?doi=...    → CrossRef metadata
// GET /api/citations/fetch?isbn=...   → Open Library + Google Books fallback
//
// Returns a partial CitationItem-shaped object the UI can splice into a
// books / journal_articles edit form.

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const { doi, isbn } = getQuery(event) as { doi?: string; isbn?: string };

  if (doi) return await fetchDoi(doi.trim());
  if (isbn) return await fetchIsbn(isbn.replace(/[-\s]/g, "").trim());
  throw createError({ statusCode: 400, message: "doi or isbn required" });
});

async function fetchDoi(doi: string) {
  const url = `https://api.crossref.org/works/${encodeURIComponent(doi)}`;
  let res: Response;
  try {
    res = await fetch(url, { headers: { Accept: "application/json" } });
  } catch (e: any) {
    throw createError({ statusCode: 502, message: `CrossRef fetch failed: ${e.message}` });
  }
  if (!res.ok) throw createError({ statusCode: res.status, message: `CrossRef: ${res.statusText}` });

  const json: any = await res.json();
  const w = json.message || {};
  const authors = (w.author || [])
    .map((a: any) => {
      if (a.family && a.given) return `${a.family}, ${a.given}`;
      return a.name || a.family || a.given || "";
    })
    .filter(Boolean)
    .join("; ");

  const issued = w.issued?.["date-parts"]?.[0]?.[0];
  const type = w.type === "journal-article" ? "article" : (w["container-title"]?.length ? "chapter" : "book");

  return {
    source: "crossref",
    type,
    doi,
    title: Array.isArray(w.title) ? w.title[0] : w.title,
    author: authors,
    publisher: w.publisher,
    publish_year: issued,
    venue: Array.isArray(w["container-title"]) ? w["container-title"][0] : w["container-title"],
    volume: w.volume,
    issue: w.issue,
    pages: w.page,
    language: w.language,
    url: w.URL,
  };
}

async function fetchIsbn(isbn: string) {
  // Try Open Library first
  try {
    const olUrl = `https://openlibrary.org/api/books?bibkeys=ISBN:${isbn}&jscmd=data&format=json`;
    const res = await fetch(olUrl);
    if (res.ok) {
      const data: any = await res.json();
      const book = data[`ISBN:${isbn}`];
      if (book) {
        return {
          source: "openlibrary",
          type: "book",
          isbn,
          title: book.title,
          author: (book.authors || []).map((a: any) => a.name).join("; "),
          publisher: (book.publishers || [])[0]?.name,
          publish_place: (book.publish_places || [])[0]?.name,
          publish_year: book.publish_date ? parseInt(book.publish_date.match(/\d{4}/)?.[0] ?? "") || undefined : undefined,
          pages: book.number_of_pages ? String(book.number_of_pages) : undefined,
          url: book.url,
        };
      }
    }
  } catch { /* fall through */ }

  // Google Books fallback
  try {
    const gbUrl = `https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`;
    const res = await fetch(gbUrl);
    if (res.ok) {
      const data: any = await res.json();
      const v = data.items?.[0]?.volumeInfo;
      if (v) {
        return {
          source: "googlebooks",
          type: "book",
          isbn,
          title: v.title + (v.subtitle ? `: ${v.subtitle}` : ""),
          author: (v.authors || []).join("; "),
          publisher: v.publisher,
          publish_year: v.publishedDate ? parseInt(v.publishedDate.match(/\d{4}/)?.[0] ?? "") || undefined : undefined,
          pages: v.pageCount ? String(v.pageCount) : undefined,
          language: v.language,
          url: v.infoLink,
        };
      }
    }
  } catch { /* fall through */ }

  throw createError({ statusCode: 404, message: `No metadata found for ISBN ${isbn}` });
}
