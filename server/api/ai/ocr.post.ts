/**
 * POST /api/ai/ocr  (multipart/form-data)
 * Fields: image (file), bookId? (uuid), startPage? (number)
 * Uses Qwen2.5-VL vision model to OCR book pages and split by page breaks
 */
import { ollamaChatWithImage, ollamaStatus } from "~/server/utils/ollama";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  // Parse multipart form
  const formData = await readMultipartFormData(event);
  if (!formData) throw createError({ statusCode: 400, message: "No form data" });

  const imageField = formData.find(f => f.name === "image");
  const bookId = formData.find(f => f.name === "bookId")?.data.toString() ?? null;
  const startPage = parseInt(formData.find(f => f.name === "startPage")?.data.toString() ?? "1");

  if (!imageField?.data) throw createError({ statusCode: 400, message: "No image provided" });

  const imageBase64 = imageField.data.toString("base64");
  const mimeType = imageField.type ?? "image/jpeg";

  // Check Ollama
  const status = await ollamaStatus();
  if (!status.ok) throw createError({ statusCode: 503, message: "Ollama 尚未啟動" });

  const hasVisionModel = status.models.some(m => m.includes("qwen2.5vl") || m.includes("llava") || m.includes("minicpm"));

  let rawText: string;

  if (hasVisionModel) {
    const visionModel = status.models.find(m => m.includes("qwen2.5vl") || m.includes("llava") || m.includes("minicpm"))!;
    const prompt = `請完整轉錄這張書頁圖片中的所有文字。
規則：
1. 保留原文，不要修改或省略任何內容
2. 如果圖片中包含多頁，用「---PAGE---」分隔每一頁
3. 忽略頁碼數字、頁首頁尾、出版資訊等版面元素，只保留正文
4. 直接輸出文字，不要加任何說明`;

    rawText = await ollamaChatWithImage(`data:${mimeType};base64,${imageBase64}`, prompt, visionModel);
  } else {
    throw createError({
      statusCode: 503,
      message: "需要視覺模型（Qwen2.5-VL）才能進行 OCR。請先執行：ollama pull qwen2.5vl:7b",
    });
  }

  // Split by page markers
  const pages = rawText
    .split(/---PAGE---/i)
    .map(p => p.trim())
    .filter(p => p.length > 20); // filter out empty/noise pages

  // Build excerpt objects
  const excerpts = pages.map((content, i) => ({
    content,
    page_number: String(startPage + i),
    book_id: bookId,
    title: null as string | null,
    chapter: null as string | null,
  }));

  // If bookId provided, try to detect chapter from content using Qwen
  if (bookId && excerpts.length > 0) {
    const chatModel = status.models.find(m => m.includes("qwen2.5") && !m.includes("vl")) ?? status.models[0];
    if (chatModel) {
      const sampleText = excerpts[0].content.slice(0, 300);
      const chapterPrompt = `以下是書的一段文字，請判斷這段文字屬於哪個章節（如果有的話）。只回答章節名稱，如「第一章」、「第三章：論神性」等。若無法判斷則回答「無」。\n\n文字：${sampleText}`;
      try {
        const chapter = await ollamaChatWithImage("", chapterPrompt, chatModel).catch(() => "無");
        if (chapter && chapter !== "無" && chapter.length < 30) {
          excerpts.forEach(e => { e.chapter = chapter.trim(); });
        }
      } catch { /* skip chapter detection */ }
    }
  }

  // Insert excerpts into DB
  const inserted: any[] = [];
  for (const ex of excerpts) {
    const { data, error } = await supabase.from("excerpts").insert(ex).select().single();
    if (!error && data) inserted.push(data);
  }

  return {
    pagesDetected: pages.length,
    excerptsSaved: inserted.length,
    excerpts: inserted,
  };
});
