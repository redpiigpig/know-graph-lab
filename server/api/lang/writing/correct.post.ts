/**
 * POST /api/lang/writing/correct
 * Body: { language, text, prompt?, usePaid? }
 * 寫作逐句批改：把使用者寫的內容逐句糾錯，每句給「原句／修正後／為何錯」，
 * 並給整體點評與一個潤飾版。走 NVIDIA 主→Gemini。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, text, prompt, usePaid } = (await readBody(event)) as {
    language: string; text: string; prompt?: string; usePaid?: boolean;
  };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  if (!text?.trim()) throw createError({ statusCode: 400, message: "請先寫一些內容" });

  const raw = await coachGemini(
    {
      system: `你是${coach.langLabel}寫作老師，為一位 B2+、做宗教研究的學生逐句批改。
${prompt ? `題目/情境：${prompt}\n` : ""}逐句檢查文法、用字、搭配、語氣、道地度。
只輸出 JSON：{
  "sentences": [ { "original": "原句", "corrected": "修正後的句子（若本句沒問題則與原句相同）", "ok": true/false, "issue": "繁體中文說明哪裡錯、為什麼（沒問題則空字串）" } ],
  "overall": "繁體中文整體點評（2–3 句，講優點與主要可改進方向）",
  "polished": "把整篇潤飾成道地、流暢的版本（${coach.langLabel}）",
  "score": 0–100 整體評分
}
逐句對應使用者原文的每一句；繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text }] }],
      json: true,
      temperature: 0.3,
      maxOutputTokens: 2400,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let d: any;
  try { d = parseJsonLoose(raw); } catch { throw createError({ statusCode: 502, message: "批改解析失敗，請重試" }); }
  return {
    sentences: Array.isArray(d.sentences) ? d.sentences : [],
    overall: d.overall || "",
    polished: d.polished || "",
    score: typeof d.score === "number" ? Math.round(d.score) : null,
  };
});
