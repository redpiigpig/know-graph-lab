/**
 * POST /api/ai/rag
 * Body: { question: string, topK?: number }
 * 1. Embed the question with nomic-embed-text
 * 2. Search similar excerpts via pgvector
 * 3. Send context + question to Qwen2.5 for answer
 */
import { ollamaChat, ollamaEmbed, ollamaStatus } from "~/server/utils/ollama";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { question, topK = 8 } = await readBody(event) as { question: string; topK?: number };

  if (!question?.trim()) throw createError({ statusCode: 400, message: "Missing question" });

  // Check Ollama is running
  const status = await ollamaStatus();
  if (!status.ok) throw createError({ statusCode: 503, message: "Ollama 尚未啟動，請先執行 ollama serve" });

  const hasEmbedModel = status.models.some(m => m.includes("nomic-embed"));
  const hasChatModel  = status.models.some(m => m.includes("qwen2.5") || m.includes("llama"));

  if (!hasChatModel) throw createError({ statusCode: 503, message: "找不到可用的對話模型" });

  // 1. Embed the question (fallback to keyword search if embed model missing)
  let relevantExcerpts: any[] = [];

  if (hasEmbedModel) {
    const embedding = await ollamaEmbed(question);
    const vecStr = `[${embedding.join(",")}]`;

    const { data: matches } = await supabase.rpc("match_excerpts", {
      query_embedding: vecStr,
      match_count: topK,
      threshold: 0.25,
    });

    if (matches?.length) {
      const ids = matches.map((m: any) => m.excerpt_id);
      const { data: excerpts } = await supabase
        .from("excerpts")
        .select("id, title, content, chapter, page_number, books(title, author)")
        .in("id", ids);

      relevantExcerpts = (excerpts ?? []).map((e: any) => ({
        ...e,
        similarity: matches.find((m: any) => m.excerpt_id === e.id)?.similarity ?? 0,
      })).sort((a: any, b: any) => b.similarity - a.similarity);
    }
  }

  // Fallback: keyword search if no embeddings or no results
  if (relevantExcerpts.length === 0) {
    const keywords = question.slice(0, 60);
    const { data: excerpts } = await supabase
      .from("excerpts")
      .select("id, title, content, chapter, page_number, books(title, author)")
      .or(`content.ilike.%${keywords}%,title.ilike.%${keywords}%`)
      .limit(topK);
    relevantExcerpts = excerpts ?? [];
  }

  // 2. Build context for LLM
  const context = relevantExcerpts.map((e: any, i: number) => {
    const book = e.books ? `《${e.books.title}》${e.books.author ? `（${e.books.author}）` : ""}` : "";
    const loc = [e.chapter, e.page_number ? `第${e.page_number}頁` : ""].filter(Boolean).join(" ");
    return `[${i + 1}] ${book}${loc ? ` ${loc}` : ""}\n${e.content}`;
  }).join("\n\n---\n\n");

  // 3. Ask LLM
  const chatModel = status.models.find(m => m.includes("qwen2.5")) ?? status.models[0];
  const systemPrompt = `你是一位學術研究助理。根據以下書摘資料回答問題，務必引用資料來源（書名、章節或頁碼）。若書摘中沒有相關資訊，請明確說明。回答使用繁體中文。`;
  const userPrompt = `【書摘資料】\n${context || "（無相關書摘）"}\n\n【問題】${question}`;

  const answer = await ollamaChat(userPrompt, chatModel, systemPrompt);

  return {
    answer,
    sources: relevantExcerpts.map((e: any) => ({
      id: e.id,
      title: e.title,
      bookTitle: e.books?.title,
      author: e.books?.author,
      chapter: e.chapter,
      page_number: e.page_number,
      snippet: e.content?.slice(0, 150),
    })),
    model: chatModel,
    embeddingUsed: hasEmbedModel,
  };
});
