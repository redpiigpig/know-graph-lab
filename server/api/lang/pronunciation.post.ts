/**
 * POST /api/lang/pronunciation
 * Body: { language, target, heard, usePaid? }
 * 發音點評：把「目標句」與「語音辨識聽到的」交給 AI（NVIDIA 主→Gemini），
 * 推斷可能的發音問題（哪些詞/音被聽錯=可能發不準）、給繁中建議與要練的音。
 * 註：Web Speech 無音素級資料，故用「目標 vs 轉錄」的差異反推發音弱點（可落地、零額外 API）。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, target, heard, usePaid } = (await readBody(event)) as {
    language: string; target: string; heard: string; usePaid?: boolean;
  };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  if (!target?.trim()) throw createError({ statusCode: 400, message: "缺少目標句" });

  const raw = await coachGemini(
    {
      system: `你是${coach.langLabel}發音教練。學生朗讀了一個目標句，下面是語音辨識「聽到」的結果。
辨識聽錯的地方，通常代表那個詞/音發得不夠準。請據此給發音回饋。
只輸出 JSON：{
  "score": 0–100 的發音評分（依吻合度與可能誤讀估計）,
  "comment": "繁體中文整體點評（1–2 句）",
  "issues": [ { "word": "可能發不準的詞", "tip": "繁中具體建議（要注意哪個音/重音）" } ]
}
issues 最多 4 個；若幾乎完全吻合就給高分、issues 可空。繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: `目標句：${target}\n辨識聽到：${heard || "（沒聽到/空）"}` }] }],
      json: true,
      temperature: 0.3,
      maxOutputTokens: 600,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let d: any;
  try { d = parseJsonLoose(raw); } catch { d = { score: null, comment: raw.slice(0, 100), issues: [] }; }
  return {
    score: typeof d.score === "number" ? Math.round(d.score) : null,
    comment: d.comment || "",
    issues: Array.isArray(d.issues) ? d.issues.slice(0, 4) : [],
  };
});
