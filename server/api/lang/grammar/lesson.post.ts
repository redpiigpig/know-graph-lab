/**
 * POST /api/lang/grammar/lesson
 * Body: { language, lessonId, usePaid? }
 * 取得某一課的完整內容（解說 + 例句 + 練習）。第一次開啟才用 Gemini 生成，之後快取。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, level, lessonId, usePaid } = (await readBody(event)) as { language: string; level: string; lessonId: string; usePaid?: boolean };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });

  const { data: row } = await supabase
    .from("lang_grammar")
    .select("level, syllabus")
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("level", level)
    .single();
  if (!row?.syllabus?.length) throw createError({ statusCode: 404, message: "尚未建立大綱" });

  const syllabus: any[] = row.syllabus;
  const idx = syllabus.findIndex((s) => s.id === lessonId);
  if (idx < 0) throw createError({ statusCode: 404, message: "找不到這一課" });
  const lesson = syllabus[idx];

  // 已生成 → 直接回
  if (lesson.content) return { lesson };

  const raw = await coachGemini(
    {
      system: `你是${coach.langLabel}文法老師，為「${row.level}」程度的學生上一堂文法課：「${lesson.title}」。
只輸出 JSON：{
  "explanation": "繁體中文清楚解說這個文法點：用法、規則、常見錯誤（可分點，初學者要淺白）",
  "examples": [ { "target": "${coach.langLabel}例句", "translation": "繁中翻譯", "note": "可選的重點提示" } ],
  "practice": [ { "q": "練習題（如填空/改寫/翻譯，繁中說明）", "answer": "參考答案" } ]
}
examples 給 4–6 句、practice 給 3–5 題。繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: `文法課：${lesson.title}（${lesson.summary || ""}）` }] }],
      json: true,
      temperature: 0.4,
      maxOutputTokens: 2048,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let content: any;
  try { content = parseJsonLoose(raw); } catch { content = { explanation: raw, examples: [], practice: [] }; }

  syllabus[idx] = { ...lesson, content };
  await supabase
    .from("lang_grammar")
    .update({ syllabus, updated_at: new Date().toISOString() })
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("level", level);

  return { lesson: syllabus[idx] };
});
