/**
 * POST /api/lang/homework/[id]/submit
 * Body: { submission: string }
 * 學生繳交作業 → Gemini 以該語言教練身分批改 → 回傳 feedback / corrections / score
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { callGemini, parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");
  const { submission } = (await readBody(event)) as { submission: string };
  if (!submission?.trim()) throw createError({ statusCode: 400, message: "繳交內容不可為空" });

  const { data: hw } = await supabase
    .from("lang_homework")
    .select("*")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();
  if (!hw) throw createError({ statusCode: 404, message: "找不到作業" });

  const coach = getCoach(hw.language);
  const grader = `${coach?.systemPrompt ?? ""}

你現在要批改學生繳交的作業。請只輸出一個 JSON：
{
  "feedback": "整體回饋（繁體中文，鼓勵 + 具體建議；可夾少量目標語言示範）",
  "corrections": [ { "original": "錯處原句", "fixed": "正確說法", "note": "繁中說明" } ],
  "score": 0到100的整數
}`;

  const raw = await callGemini({
    model: "gemini-2.5-pro", // 批改用 Pro，文法細膩度更高
    system: grader,
    contents: [
      {
        role: "user",
        parts: [
          {
            text: `【作業主題】${hw.topic}\n【題目】${hw.prompt}\n【類型】${hw.hw_type}\n\n【學生繳交】\n${submission}`,
          },
        ],
      },
    ],
    json: true,
    temperature: 0.4,
    maxOutputTokens: 2048,
  });

  let parsed: { feedback?: string; corrections?: any[]; score?: number };
  try {
    parsed = parseJsonLoose(raw);
  } catch {
    parsed = { feedback: raw, corrections: [], score: undefined };
  }

  const { data: updated, error } = await supabase
    .from("lang_homework")
    .update({
      submission,
      feedback: parsed.feedback ?? "",
      corrections: Array.isArray(parsed.corrections) ? parsed.corrections : [],
      score: typeof parsed.score === "number" ? Math.round(parsed.score) : null,
      status: "graded",
      updated_at: new Date().toISOString(),
    })
    .eq("id", id)
    .eq("user_id", user.id)
    .select("*")
    .single();
  if (error) throw createError({ statusCode: 500, message: error.message });

  return { homework: updated };
});
