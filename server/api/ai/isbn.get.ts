/**
 * GET /api/ai/isbn?q=<isbn or title>
 * Looks up book metadata from Open Library + Google Books APIs
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const { q } = getQuery(event) as { q?: string };
  if (!q?.trim()) throw createError({ statusCode: 400, message: "Missing search query" });

  const query = q.trim();

  // Try Open Library first
  const olResult = await fetchOpenLibrary(query);
  if (olResult) return olResult;

  // Fallback to Google Books
  const gbResult = await fetchGoogleBooks(query);
  if (gbResult) return gbResult;

  throw createError({ statusCode: 404, message: "找不到書目資訊" });
});

async function fetchOpenLibrary(query: string) {
  // Detect if it's an ISBN (all digits, possibly with dashes)
  const isISBN = /^[\d\-X]{10,17}$/.test(query.replace(/\s/g, ""));
  let url: string;

  if (isISBN) {
    const isbn = query.replace(/[\s\-]/g, "");
    url = `https://openlibrary.org/api/books?bibkeys=ISBN:${isbn}&format=json&jscmd=data`;
  } else {
    url = `https://openlibrary.org/search.json?q=${encodeURIComponent(query)}&limit=1`;
  }

  try {
    const res = await fetch(url, { headers: { "User-Agent": "KnowGraphLab/1.0" } });
    if (!res.ok) return null;
    const data = await res.json() as any;

    if (isISBN) {
      const key = Object.keys(data)[0];
      if (!key) return null;
      const book = data[key];
      return {
        title: book.title ?? "",
        author: (book.authors ?? []).map((a: any) => a.name).join("、") || "",
        publisher: book.publishers?.[0]?.name ?? "",
        publish_year: book.publish_date ? parseInt(book.publish_date) || null : null,
        publish_place: book.publish_places?.[0]?.name ?? "",
        isbn: query.replace(/[\s\-]/g, ""),
        cover: book.cover?.medium ?? null,
        source: "Open Library",
      };
    } else {
      const doc = data.docs?.[0];
      if (!doc) return null;
      return {
        title: doc.title ?? "",
        author: (doc.author_name ?? []).join("、"),
        publisher: doc.publisher?.[0] ?? "",
        publish_year: doc.first_publish_year ?? null,
        publish_place: "",
        isbn: doc.isbn?.[0] ?? "",
        cover: doc.cover_i ? `https://covers.openlibrary.org/b/id/${doc.cover_i}-M.jpg` : null,
        source: "Open Library",
      };
    }
  } catch {
    return null;
  }
}

async function fetchGoogleBooks(query: string) {
  const isISBN = /^[\d\-X]{10,17}$/.test(query.replace(/\s/g, ""));
  const searchQ = isISBN ? `isbn:${query.replace(/[\s\-]/g, "")}` : query;
  const url = `https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(searchQ)}&maxResults=1`;

  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const data = await res.json() as any;
    const item = data.items?.[0]?.volumeInfo;
    if (!item) return null;

    return {
      title: item.title ?? "",
      author: (item.authors ?? []).join("、"),
      publisher: item.publisher ?? "",
      publish_year: item.publishedDate ? parseInt(item.publishedDate) || null : null,
      publish_place: "",
      isbn: item.industryIdentifiers?.find((i: any) => i.type === "ISBN_13")?.identifier
        ?? item.industryIdentifiers?.[0]?.identifier ?? "",
      cover: item.imageLinks?.thumbnail ?? null,
      source: "Google Books",
    };
  } catch {
    return null;
  }
}
