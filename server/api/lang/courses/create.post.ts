/**
 * POST /api/lang/courses/create
 * Body: { language, theme, usePaid? }
 * 依主題用 Gemini 生成一套循序課表（每課含預估分鐘），建立一門主題課程。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, theme, usePaid } = (await readBody(event)) as { language: string; theme: string; usePaid?: boolean };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  if (!theme?.trim()) throw createError({ statusCode: 400, message: "請提供主題" });

  const { data: prog } = await supabase
    .from("lang_progress").select("level").eq("user_id", user.id).eq("language", language).single();
  const lv = prog?.level || coach.defaultLevel || coach.levelScale[0];

  const raw = await coachGemini(
    {
      system: `你是${coach.langLabel}課程設計師。為「${lv}」程度、做宗教研究的學生，依主題「${theme}」設計一套**循序漸進**的主題課程大綱。
只輸出 JSON：{
  "title": "課程名稱（繁中）",
  "syllabus": [ { "id": "c1", "title": "這一課的標題（繁中，可附目標語術語）", "summary": "一句話內容（繁中）", "minutes": 每課預估分鐘數（10–30 整數） } ]
}
由淺到深排序，出 8–14 課，難度貼合 ${lv}。id 用 c1, c2…。繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: `主題：${theme}` }] }],
      json: true,
      temperature: 0.5,
      maxOutputTokens: 2048,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let g: any;
  try { g = parseJsonLoose(raw); } catch { throw createError({ statusCode: 502, message: "課程生成失敗，請重試" }); }
  const syllabus = (g.syllabus || []).map((x: any, i: number) => ({
    id: x.id || `c${i + 1}`,
    title: x.title || "",
    summary: x.summary || "",
    minutes: Math.min(30, Math.max(5, Number(x.minutes) || 15)),
    content: null,
    done: false,
  }));
  if (!syllabus.length) throw createError({ statusCode: 502, message: "未生成課程內容" });

  const { data: course } = await supabase
    .from("lang_courses")
    .insert({ user_id: user.id, language, title: g.title || theme, theme, level: lv, syllabus })
    .select("id, title, theme, level, syllabus, created_at")
    .single();

  return { course };
});
