// POST /api/citations/bulk-import
// Body: { items: string[], category_id?: string }
//   each string is either an ISBN (10/13 digits, dashes ok) or a DOI.
// Returns per-row result: { input, status, book_id?|journal_article_id?, title?, error? }
//
// Routes to:
//   ISBN → books table   (via Open Library + Google Books fallback)
//   DOI  → if CrossRef says "journal-article" → journal_articles
//          otherwise                          → books
//
// Idempotent: if a row with same ISBN / DOI already exists, returns "exists"
// instead of duplicating.

function isDoi(s: string): boolean {
  return /^10\.\d{4,9}\/\S+/.test(s.trim());
}

function normIsbn(s: string): string {
  return s.replace(/[-\s]/g, "").trim();
}

async function fetchDoi(doi: string) {
  const res = await fetch(`https://api.crossref.org/works/${encodeURIComponent(doi)}`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`CrossRef ${res.status}`);
  const j: any = await res.json();
  const w = j.message || {};
  const authors = (w.author || []).map((a: any) =>
    a.family && a.given ? `${a.family}, ${a.given}` : (a.name || a.family || a.given || "")
  ).filter(Boolean).join("; ");
  const year = w.issued?.["date-parts"]?.[0]?.[0];
  return {
    crossref_type: w.type,
    title: Array.isArray(w.title) ? w.title[0] : w.title,
    author: authors,
    publisher: w.publisher,
    publish_year: year,
    venue: Array.isArray(w["container-title"]) ? w["container-title"][0] : w["container-title"],
    volume: w.volume,
    issue: w.issue,
    pages: w.page,
    language: w.language,
    url: w.URL,
    doi,
  };
}

async function fetchIsbn(isbn: string) {
  // Open Library
  try {
    const r = await fetch(`https://openlibrary.org/api/books?bibkeys=ISBN:${isbn}&jscmd=data&format=json`);
    if (r.ok) {
      const d: any = await r.json();
      const b = d[`ISBN:${isbn}`];
      if (b) return {
        title: b.title,
        author: (b.authors || []).map((a: any) => a.name).join("; "),
        publisher: (b.publishers || [])[0]?.name,
        publish_place: (b.publish_places || [])[0]?.name,
        publish_year: b.publish_date ? parseInt(b.publish_date.match(/\d{4}/)?.[0] ?? "") || undefined : undefined,
        pages: b.number_of_pages ? String(b.number_of_pages) : undefined,
        url: b.url,
        isbn,
      };
    }
  } catch { /* fall through */ }
  // Google Books fallback
  try {
    const r = await fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`);
    if (r.ok) {
      const d: any = await r.json();
      const v = d.items?.[0]?.volumeInfo;
      if (v) return {
        title: v.title + (v.subtitle ? `: ${v.subtitle}` : ""),
        author: (v.authors || []).join("; "),
        publisher: v.publisher,
        publish_year: v.publishedDate ? parseInt(v.publishedDate.match(/\d{4}/)?.[0] ?? "") || undefined : undefined,
        pages: v.pageCount ? String(v.pageCount) : undefined,
        language: v.language,
        url: v.infoLink,
        isbn,
      };
    }
  } catch { /* fall through */ }
  throw new Error(`No metadata for ISBN ${isbn}`);
}

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event) as { items?: string[]; category_id?: string };
  const items = (body.items ?? []).map((s) => s.trim()).filter(Boolean);
  if (!items.length) throw createError({ statusCode: 400, message: "items required" });

  const results: Array<{
    input: string;
    status: "created" | "exists" | "error";
    kind?: "book" | "journal";
    id?: string;
    title?: string;
    error?: string;
  }> = [];

  for (const raw of items) {
    try {
      if (isDoi(raw)) {
        const meta = await fetchDoi(raw);
        const isJournal = meta.crossref_type === "journal-article";

        if (isJournal) {
          const { data: dup } = await supabase
            .from("journal_articles").select("id, title").eq("doi", meta.doi).maybeSingle();
          if (dup) {
            results.push({ input: raw, status: "exists", kind: "journal", id: (dup as any).id, title: (dup as any).title });
            continue;
          }
          const { data, error } = await supabase
            .from("journal_articles").insert({
              title: meta.title, author: meta.author, venue: meta.venue,
              publish_year: meta.publish_year, doi: meta.doi,
              volume: meta.volume, issue: meta.issue, pages: meta.pages,
              url: meta.url, language: meta.language, publisher: meta.publisher,
            }).select("id, title").single();
          if (error) throw new Error(error.message);
          results.push({ input: raw, status: "created", kind: "journal", id: (data as any).id, title: (data as any).title });
        } else {
          const { data: dup } = await supabase
            .from("books").select("id, title").eq("doi", meta.doi).maybeSingle();
          if (dup) {
            results.push({ input: raw, status: "exists", kind: "book", id: (dup as any).id, title: (dup as any).title });
            continue;
          }
          const insert: any = {
            title: meta.title, author: meta.author, publisher: meta.publisher,
            publish_year: meta.publish_year, doi: meta.doi, pages: meta.pages,
            url: meta.url, language: meta.language,
          };
          if (body.category_id) insert.category_id = body.category_id;
          const { data, error } = await supabase
            .from("books").insert(insert).select("id, title").single();
          if (error) throw new Error(error.message);
          results.push({ input: raw, status: "created", kind: "book", id: (data as any).id, title: (data as any).title });
        }
      } else {
        const isbn = normIsbn(raw);
        if (!/^\d{9}[\dXx]$|^\d{13}$/.test(isbn)) {
          throw new Error(`不是合法 ISBN 也不是 DOI`);
        }
        const meta = await fetchIsbn(isbn);
        const { data: dup } = await supabase
          .from("books").select("id, title").eq("isbn", meta.isbn).maybeSingle();
        if (dup) {
          results.push({ input: raw, status: "exists", kind: "book", id: (dup as any).id, title: (dup as any).title });
          continue;
        }
        const insert: any = {
          title: meta.title, author: meta.author, publisher: meta.publisher,
          publish_place: meta.publish_place, publish_year: meta.publish_year,
          isbn: meta.isbn, pages: meta.pages, url: meta.url, language: meta.language,
        };
        if (body.category_id) insert.category_id = body.category_id;
        const { data, error } = await supabase
          .from("books").insert(insert).select("id, title").single();
        if (error) throw new Error(error.message);
        results.push({ input: raw, status: "created", kind: "book", id: (data as any).id, title: (data as any).title });
      }
    } catch (e: any) {
      results.push({ input: raw, status: "error", error: e?.message || String(e) });
    }
  }

  return {
    total: items.length,
    created: results.filter((r) => r.status === "created").length,
    exists: results.filter((r) => r.status === "exists").length,
    errors: results.filter((r) => r.status === "error").length,
    results,
  };
});
