/**
 * GET /api/lang/grammar?language=en
 * 取得該語言的文法課大綱（依「目前程度」循序）。若無、或程度已改變 → 用 Gemini 生成一次。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const q = getQuery(event);
  const language = (q.language as string) || "en";
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });

  const { data: prog } = await supabase
    .from("lang_progress")
    .select("level")
    .eq("user_id", user.id)
    .eq("language", language)
    .single();
  const currentLevel = prog?.level || coach.defaultLevel || coach.levelScale[0];
  // 可指定要看哪個程度的課（B2/C1/C2、N5–N1…），預設目前程度
  const lv = coach.levelScale.includes(q.level as string) ? (q.level as string) : currentLevel;

  const { data: existing } = await supabase
    .from("lang_grammar")
    .select("level, syllabus, updated_at")
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("level", lv)
    .single();

  // 已有 → 直接回
  if (existing?.syllabus?.length) {
    return { level: lv, currentLevel, levelScale: coach.levelScale, syllabus: existing.syllabus };
  }

  // 生成循序大綱（一次）
  const beginner = ["A1", "A2", "N5", "N4", "入門", "初級"].includes(lv);
  const raw = await coachGemini(
    {
      system: `你是${coach.langLabel}文法課程設計師。為「${lv}」程度的學生（母語繁體中文${coach.language === "ja" || beginner ? "、初學者" : ""}）設計一套**循序漸進**的文法課大綱。
只輸出 JSON：{ "syllabus": [ { "id": "g1", "title": "這一課的文法重點（繁中，可附目標語術語）", "summary": "一句話說明（繁中）" } ] }
要求：${beginner ? "從最基礎開始（如語序、動詞變化、助詞/冠詞、基本時態…），" : `聚焦 ${lv} → 下一級之間真正會卡關的進階文法（如語氣、從句、慣用結構、語體轉換…），`}由淺到深排序，出 ${beginner ? "16–24" : "12–18"} 課。id 用 g1, g2…。繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: `語言：${coach.langLabel}，程度：${lv}` }] }],
      json: true,
      temperature: 0.4,
      maxOutputTokens: 2048,
    },
    { usePaid: false, userId: user.id, supabase }
  );

  let syllabus: any[] = [];
  try {
    syllabus = (parseJsonLoose<{ syllabus: any[] }>(raw).syllabus || []).map((x: any, i: number) => ({
      id: x.id || `g${i + 1}`,
      title: x.title || "",
      summary: x.summary || "",
      content: null,
      done: false,
    }));
  } catch {
    throw createError({ statusCode: 502, message: "大綱生成失敗，請重試" });
  }

  await supabase
    .from("lang_grammar")
    .upsert(
      { user_id: user.id, language, level: lv, syllabus, updated_at: new Date().toISOString() },
      { onConflict: "user_id,language,level" }
    );

  return { level: lv, currentLevel, levelScale: coach.levelScale, syllabus };
});
