/**
 * POST /api/lang/content/ingest
 * Body: { language, sourceType: 'youtube'|'article', url?, text? }
 * YouTube：Gemini 2.5 Flash 原生吃 URL（fileData）；文章：直接吃文字。
 * 回傳並儲存：摘要、理解題、關鍵單字、討論題、大綱。可延伸到對話討論。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { parseJsonLoose } from "~/server/utils/gemini";
import { coachGemini } from "~/server/utils/coach-ai";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, sourceType, url, text, usePaid } = (await readBody(event)) as {
    language: string;
    sourceType: "youtube" | "article";
    url?: string;
    text?: string;
    usePaid?: boolean;
  };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });

  if (sourceType === "youtube" && !url?.trim()) throw createError({ statusCode: 400, message: "請提供 YouTube 網址" });
  if (sourceType === "article" && !text?.trim()) throw createError({ statusCode: 400, message: "請貼上文章內容" });

  const { data: profile } = await supabase
    .from("lang_profile")
    .select("goal_level, interests")
    .eq("user_id", user.id)
    .single();
  const lv = profile?.goal_level || "C1";

  const system = `你是${coach.langLabel}學術內容導讀老師，服務一位 CEFR ${lv}、主修人文的學生。
分析以下${sourceType === "youtube" ? "YouTube 影片" : "文章"}，只輸出 JSON：
{
  "title": "內容標題（${coach.langLabel}）",
  "summary": "繁體中文摘要（150字內）",
  "outline": ["重點1","重點2","重點3"],
  "questions": [ { "q": "${coach.langLabel}理解問題", "answer": "參考答案要點（繁中）" } ],
  "vocab": [ { "word": "", "reading": "", "meaning": "繁中釋義", "example": "" } ],
  "discussion": ["可與教練深入討論/辯論的開放題（${coach.langLabel}）"]${sourceType === "youtube" ? ',\n  "duration_minutes": 影片的實際長度（分鐘，整數，盡量準確）' : ""}
}
要求：questions 3–5 題、vocab 挑 6–10 個該程度學術單字、discussion 2–3 題。繁體中文不可簡體。`;

  const parts: any[] =
    sourceType === "youtube"
      ? [{ fileData: { fileUri: url!.trim(), mimeType: "video/mp4" } }, { text: "請依系統指示分析這部影片。" }]
      : [{ text: `文章內容：\n${text}` }];

  const raw = await coachGemini(
    {
      system,
      contents: [{ role: "user", parts }],
      json: true,
      temperature: 0.5,
      maxOutputTokens: 4096,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let analysis: any;
  try {
    analysis = parseJsonLoose(raw);
  } catch {
    throw createError({ statusCode: 502, message: "分析解析失敗，影片可能過長或無字幕，請改貼文字或換一部" });
  }

  // 把關鍵單字加入單字庫（SRS）
  const vocab = Array.isArray(analysis.vocab) ? analysis.vocab : [];
  if (vocab.length) {
    const rows = vocab
      .filter((v: any) => v?.word)
      .map((v: any) => ({
        user_id: user.id,
        language,
        word: String(v.word).trim(),
        reading: v.reading ?? null,
        meaning: v.meaning ?? "",
        example: v.example ?? null,
        source: sourceType,
        list_key: "immersion",
      }));
    if (rows.length) await supabase.from("lang_vocab").upsert(rows, { onConflict: "user_id,language,word", ignoreDuplicates: true });
  }

  // 建立一個討論 session，把內容摘要塞進長期記憶，之後可直接跟教練深入討論
  const seedSummary = `學生剛看完一則${sourceType === "youtube" ? "YouTube 影片" : "文章"}：「${analysis.title ?? ""}」。摘要：${analysis.summary ?? ""}。重點：${(analysis.outline || []).join("；")}。接下來請以這則內容為基礎，用${coach.langLabel}跟學生討論、追問、辯論。`;
  const { data: sess } = await supabase
    .from("lang_sessions")
    .insert({ user_id: user.id, language, title: analysis.title ?? "內容討論", summary: seedSummary })
    .select("id")
    .single();

  const { data: saved } = await supabase
    .from("lang_content")
    .insert({
      user_id: user.id,
      language,
      source_type: sourceType,
      url: url ?? null,
      title: analysis.title ?? null,
      summary: analysis.summary ?? null,
      analysis,
      session_id: sess?.id ?? null,
    })
    .select("*")
    .single();

  // YouTube：把影片時長算進「聽力」時間（你說「今天看了這個」，整部片長計入）
  let watchedMinutes = 0;
  if (sourceType === "youtube") {
    watchedMinutes = Math.max(0, Math.round(Number(analysis.duration_minutes) || 0));
    if (watchedMinutes > 0) {
      await supabase.from("lang_activity").insert({
        user_id: user.id,
        language,
        skill: "listening",
        minutes: watchedMinutes,
        source: "youtube",
        detail: analysis.title ?? null,
      });
      // 更新最後活躍 + 累計（streak 由 activity 端點/其他流程維護，這裡補時間）
      const today = new Date().toISOString().slice(0, 10);
      const { data: prog } = await supabase
        .from("lang_progress")
        .select("total_minutes")
        .eq("user_id", user.id)
        .eq("language", language)
        .single();
      await supabase.from("lang_progress").upsert(
        { user_id: user.id, language, last_active: today, total_minutes: Math.round(((prog?.total_minutes || 0) + watchedMinutes) * 100) / 100, updated_at: new Date().toISOString() },
        { onConflict: "user_id,language" }
      );
    }
  }

  return { content: saved, watchedMinutes };
});
