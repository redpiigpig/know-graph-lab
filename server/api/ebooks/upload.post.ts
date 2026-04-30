/**
 * POST /api/ebooks/upload  (multipart/form-data)
 * Fields: file (pdf/epub), title?, author?, bookId?
 * Parses the file, stores pages in book_pages, optionally vectorizes
 */
import { ollamaEmbed, ollamaStatus } from "~/server/utils/ollama";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const formData = await readMultipartFormData(event);
  if (!formData) throw createError({ statusCode: 400, message: "No form data" });

  const fileField = formData.find(f => f.name === "file");
  const title    = formData.find(f => f.name === "title")?.data.toString() ?? "未命名電子書";
  const author   = formData.find(f => f.name === "author")?.data.toString() ?? null;
  const bookId   = formData.find(f => f.name === "bookId")?.data.toString() ?? null;
  const category    = formData.find(f => f.name === "category")?.data.toString() ?? null;
  const subcategory = formData.find(f => f.name === "subcategory")?.data.toString() ?? null;

  if (!fileField?.data) throw createError({ statusCode: 400, message: "No file provided" });

  const fileName = fileField.filename ?? "file";
  const ext = fileName.split(".").pop()?.toLowerCase() ?? "";
  if (!["pdf", "epub"].includes(ext)) {
    throw createError({ statusCode: 400, message: "只支援 PDF 和 EPUB 格式" });
  }

  // Parse file into pages
  let pages: { page: number; content: string }[] = [];

  if (ext === "pdf") {
    pages = await parsePDF(fileField.data);
  } else {
    pages = await parseEPUB(fileField.data);
  }

  if (pages.length === 0) throw createError({ statusCode: 422, message: "無法從檔案中提取文字" });

  // Create ebook record
  const { data: ebook, error: ebookErr } = await supabase
    .from("ebooks")
    .insert({ title, author, file_type: ext, total_pages: pages.length, book_id: bookId, category, subcategory })
    .select()
    .single();

  if (ebookErr) throw createError({ statusCode: 500, message: ebookErr.message });

  // Insert pages in batches of 50
  const BATCH = 50;
  let insertedPages = 0;
  for (let i = 0; i < pages.length; i += BATCH) {
    const batch = pages.slice(i, i + BATCH).map(p => ({
      ebook_id: ebook.id,
      page_number: p.page,
      content: p.content,
    }));
    const { error } = await supabase.from("book_pages").insert(batch);
    if (!error) insertedPages += batch.length;
  }

  // Optional: vectorize (only if nomic-embed-text available)
  let vectorized = 0;
  const status = await ollamaStatus();
  if (status.ok && status.models.some(m => m.includes("nomic-embed"))) {
    vectorized = await vectorizePages(supabase, ebook.id, pages.slice(0, 100)); // limit first 100 pages async
  }

  return {
    ebook_id: ebook.id,
    title,
    file_type: ext,
    total_pages: pages.length,
    pages_inserted: insertedPages,
    pages_vectorized: vectorized,
    message: vectorized < pages.length && pages.length > 100
      ? `前 100 頁已向量化，其餘 ${pages.length - 100} 頁可稍後批量處理`
      : undefined,
  };
});

async function parsePDF(buffer: Buffer): Promise<{ page: number; content: string }[]> {
  const pdfParse = (await import("pdf-parse")).default;
  const data = await pdfParse(buffer);

  // pdf-parse gives us full text; split by page using their render_page callback
  // For a better per-page split, we re-parse with page callback
  const pages: { page: number; content: string }[] = [];
  let pageNum = 0;

  await pdfParse(buffer, {
    pagerender: (pageData: any) => {
      pageNum++;
      return pageData.getTextContent().then((tc: any) => {
        const text = tc.items.map((i: any) => i.str).join(" ").trim();
        if (text.length > 10) pages.push({ page: pageNum, content: text });
        return text;
      });
    },
  }).catch(() => {
    // Fallback: split full text into rough page chunks
    if (pages.length === 0 && data.text) {
      const chunkSize = Math.ceil(data.text.length / (data.numpages || 1));
      for (let i = 0; i < data.numpages; i++) {
        const chunk = data.text.slice(i * chunkSize, (i + 1) * chunkSize).trim();
        if (chunk.length > 10) pages.push({ page: i + 1, content: chunk });
      }
    }
  });

  return pages.length > 0 ? pages : [{ page: 1, content: data.text }];
}

async function parseEPUB(buffer: Buffer): Promise<{ page: number; content: string }[]> {
  const { EPub } = await import("epub2");
  const epub = await EPub.createAsync(buffer as any);

  const chapters = epub.flow ?? [];
  const pages: { page: number; content: string }[] = [];

  for (let i = 0; i < chapters.length; i++) {
    try {
      const chapterContent = await new Promise<string>((resolve, reject) => {
        epub.getChapter(chapters[i].id, (err: any, text: any) => {
          if (err) reject(err);
          else resolve(text ?? "");
        });
      });
      // Strip HTML tags
      const text = chapterContent.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
      if (text.length > 20) pages.push({ page: i + 1, content: text });
    } catch { /* skip chapter */ }
  }

  return pages;
}

async function vectorizePages(
  supabase: any,
  ebookId: string,
  pages: { page: number; content: string }[]
): Promise<number> {
  let count = 0;
  for (const p of pages) {
    try {
      const embedding = await ollamaEmbed(p.content.slice(0, 2000));
      if (!embedding.length) continue;

      const { data: pageRow } = await supabase
        .from("book_pages")
        .select("id")
        .eq("ebook_id", ebookId)
        .eq("page_number", p.page)
        .single();

      if (pageRow) {
        await supabase.from("page_embeddings").upsert({
          page_id: pageRow.id,
          embedding: `[${embedding.join(",")}]`,
        });
        count++;
      }
    } catch { /* skip on error */ }
  }
  return count;
}
