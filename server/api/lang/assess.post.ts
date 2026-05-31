/**
 * POST /api/lang/assess
 * Body: { language }
 * 根據學生近期對話發言，用 Gemini 做 CEFR 評估，寫入 lang_level_history 並更新 lang_progress.level。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { callGemini, parseJsonLoose } from "~/server/utils/gemini";

const CEFR_NUM: Record<string, number> = { A1: 20, A2: 35, B1: 50, B2: 65, C1: 80, C2: 95 };

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language } = (await readBody(event)) as { language: string };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });

  // 取得該語言所有 session
  const { data: sess } = await supabase
    .from("lang_sessions")
    .select("id")
    .eq("user_id", user.id)
    .eq("language", language);
  const sessionIds = (sess ?? []).map((s) => s.id);
  if (!sessionIds.length) throw createError({ statusCode: 400, message: "尚無對話紀錄可評估，先跟教練聊一會兒吧" });

  // 取最近 40 則學生發言
  const { data: msgs } = await supabase
    .from("lang_messages")
    .select("content, created_at")
    .in("session_id", sessionIds)
    .eq("role", "user")
    .order("created_at", { ascending: false })
    .limit(40);
  const samples = (msgs ?? []).map((m) => m.content).reverse();
  if (samples.length < 3) throw createError({ statusCode: 400, message: "對話樣本太少，多聊幾句再評估" });

  const raw = await callGemini({
    model: useRuntimeConfig().geminiGradeModel as string,
    system: `你是 CEFR 語言能力評估專家，評估學生的「${coach.langLabel}」程度。
依據學生的發言樣本，評估其 CEFR 等級與各項分數。只輸出一個 JSON：
{
  "level": "A1|A2|B1|B2|C1|C2",
  "cefr_score": 0到100的數字（A1≈20, A2≈35, B1≈50, B2≈65, C1≈80, C2≈95，可給小數）,
  "scores": { "fluency": 0-100, "grammar": 0-100, "vocabulary": 0-100, "coherence": 0-100 },
  "note": "繁體中文簡短評語：強項、弱項、升級到下一級該加強什麼（80字內）"
}`,
    contents: [{ role: "user", parts: [{ text: `【學生發言樣本】\n${samples.map((s, i) => `${i + 1}. ${s}`).join("\n")}` }] }],
    json: true,
    temperature: 0.3,
    maxOutputTokens: 1024,
  });

  let parsed: any;
  try {
    parsed = parseJsonLoose(raw);
  } catch {
    throw createError({ statusCode: 502, message: "評估解析失敗，請重試" });
  }

  const level = String(parsed.level || "B2").toUpperCase();
  const cefrScore = typeof parsed.cefr_score === "number" ? parsed.cefr_score : CEFR_NUM[level] ?? 65;

  const { data: hist } = await supabase
    .from("lang_level_history")
    .insert({
      user_id: user.id,
      language,
      level,
      cefr_score: cefrScore,
      scores: parsed.scores ?? {},
      method: "ai",
      note: parsed.note ?? null,
    })
    .select("*")
    .single();

  // 更新目前等級
  await supabase
    .from("lang_progress")
    .upsert(
      { user_id: user.id, language, level, updated_at: new Date().toISOString() },
      { onConflict: "user_id,language" }
    );

  return { assessment: hist };
});
