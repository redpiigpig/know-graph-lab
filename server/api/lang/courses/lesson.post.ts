/**
 * POST /api/lang/courses/lesson
 * Body: { courseId, lessonId, usePaid? }
 * 生成某一課的內容（解說 + 例句 + 練習），第一次開啟才生成、之後快取。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { courseId, lessonId, usePaid } = (await readBody(event)) as { courseId: string; lessonId: string; usePaid?: boolean };

  const { data: course } = await supabase
    .from("lang_courses")
    .select("language, title, level, syllabus")
    .eq("id", courseId)
    .eq("user_id", user.id)
    .single();
  if (!course?.syllabus?.length) throw createError({ statusCode: 404, message: "找不到課程" });
  const coach = getCoach(course.language);

  const syllabus: any[] = course.syllabus;
  const idx = syllabus.findIndex((s) => s.id === lessonId);
  if (idx < 0) throw createError({ statusCode: 404, message: "找不到這一課" });
  const lesson = syllabus[idx];
  if (lesson.content) return { lesson };

  const raw = await coachGemini(
    {
      system: `你是${coach?.langLabel}老師，課程「${course.title}」（${course.level} 程度）的一課：「${lesson.title}」。
只輸出 JSON：{
  "explanation": "繁體中文清楚解說這一課的重點（可分點；含用法/規則/常見錯誤）",
  "examples": [ { "target": "${coach?.langLabel}例句", "translation": "繁中翻譯", "note": "可選提示" } ],
  "practice": [ { "q": "練習題（繁中說明）", "answer": "參考答案" } ]
}
examples 4–6 句、practice 3–5 題。題材以宗教/宗教學/人文為主。繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: `${lesson.title}（${lesson.summary || ""}）` }] }],
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
    .from("lang_courses")
    .update({ syllabus, updated_at: new Date().toISOString() })
    .eq("id", courseId)
    .eq("user_id", user.id);

  return { lesson: syllabus[idx] };
});
