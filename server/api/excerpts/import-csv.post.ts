// POST /api/excerpts/import-csv
// multipart/form-data: file, projectId?, bookId?
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const form = await readMultipartFormData(event);
  if (!form) throw createError({ statusCode: 400, message: "No form data" });

  const fileField = form.find((f) => f.name === "file");
  const projectId = form.find((f) => f.name === "projectId")?.data.toString() || null;
  const fallbackBookId = form.find((f) => f.name === "bookId")?.data.toString() || null;
  const fallbackJournalId = form.find((f) => f.name === "journalArticleId")?.data.toString() || null;
  if (!fileField?.data) throw createError({ statusCode: 400, message: "CSV file is required" });

  const csv = fileField.data.toString("utf8");
  const rows = parseCsv(csv);
  if (!rows.length) throw createError({ statusCode: 400, message: "CSV has no rows" });

  const headers = rows[0].map((h) => normalize(h));
  const dataRows = rows.slice(1);
  const createdIds: string[] = [];

  for (const row of dataRows) {
    const rec = toRecord(headers, row);
    const content = rec.content || rec.內文 || "";
    if (!content.trim()) continue;

    const title = rec.title || rec.標題 || null;
    const chapter = rec.chapter || rec.章節 || null;
    const page = rec.page || rec.page_number || rec.頁碼 || null;
    let bookId = fallbackBookId;
    let journalArticleId = fallbackJournalId;

    if (!bookId && !journalArticleId && (rec.book || rec.book_title || rec.書名)) {
      const bookTitle = (rec.book || rec.book_title || rec.書名 || "").trim();
      const author = (rec.author || rec.作者 || "").trim();
      const { data: matches } = await supabase
        .from("books")
        .select("id, title, author")
        .ilike("title", `%${bookTitle}%`)
        .limit(5);
      const picked = (matches ?? []).find((b) =>
        !author || (b.author || "").toLowerCase().includes(author.toLowerCase())
      ) || (matches ?? [])[0];
      bookId = picked?.id || null;
    }

    if (bookId && journalArticleId) journalArticleId = null;

    const { data, error } = await supabase
      .from("excerpts")
      .insert({
        title,
        content,
        chapter,
        page_number: page ? String(page) : null,
        book_id: bookId || null,
        journal_article_id: journalArticleId || null,
      })
      .select("id")
      .single();
    if (!error && data?.id) createdIds.push(data.id);
  }

  if (projectId && createdIds.length) {
    const links = createdIds.map((id) => ({ excerpt_id: id, book_project_id: projectId }));
    await supabase.from("excerpt_book_projects").upsert(links, {
      onConflict: "excerpt_id,book_project_id",
    });
  }

  return { created: createdIds.length, excerptIds: createdIds };
});

function normalize(s: string) {
  return s.trim().toLowerCase().replace(/\s+/g, "_");
}

function toRecord(headers: string[], row: string[]) {
  const r: Record<string, string> = {};
  headers.forEach((h, i) => { r[h] = row[i] ?? ""; });
  return r;
}

function parseCsv(text: string): string[][] {
  const out: string[][] = [];
  let row: string[] = [];
  let cur = "";
  let q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === "\"") {
      if (q && text[i + 1] === "\"") { cur += "\""; i++; }
      else q = !q;
    } else if (c === "," && !q) {
      row.push(cur); cur = "";
    } else if ((c === "\n" || c === "\r") && !q) {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(cur); cur = "";
      if (row.some((v) => v.trim() !== "")) out.push(row);
      row = [];
    } else cur += c;
  }
  if (cur.length || row.length) {
    row.push(cur);
    if (row.some((v) => v.trim() !== "")) out.push(row);
  }
  return out;
}
