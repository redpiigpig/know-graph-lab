/** GET /api/lang/courses?language=en — 列出已建課程 + 建議主題 */
import { getCoach } from "~/server/utils/lang-coaches";

const PRESETS: Record<string, string[]> = {
  en: [
    "宗教文獻英文精讀",
    "學術寫作（論文段落）",
    "TOEFL 口說衝刺",
    "TOEFL 獨立寫作",
    "神學・宗教學英語術語",
    "批判思考與論辯英文",
    "學術聽力（大學講座）",
    "聖經英文（KJV/NRSV）導讀",
  ],
  ja: [
    "五十音と発音の復習",
    "N5 基礎文法コース",
    "敬語入門",
    "宗教・神話の日本語",
    "日常会話",
    "旅行で使う日本語",
  ],
};

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const language = (getQuery(event).language as string) || "en";
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });

  const { data } = await supabase
    .from("lang_courses")
    .select("id, title, theme, level, syllabus, created_at")
    .eq("user_id", user.id)
    .eq("language", language)
    .order("created_at", { ascending: false });

  const courses = (data ?? []).map((c: any) => ({
    id: c.id,
    title: c.title,
    theme: c.theme,
    level: c.level,
    total: (c.syllabus || []).length,
    done: (c.syllabus || []).filter((s: any) => s.done).length,
    minutes: (c.syllabus || []).reduce((s: number, x: any) => s + (Number(x.minutes) || 0), 0),
  }));

  return { courses, presets: PRESETS[language] || [] };
});
