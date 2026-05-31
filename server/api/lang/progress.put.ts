/** PUT /api/lang/progress — 設定某語言的「目前程度」（lang_progress.level） */
import { getCoach } from "~/server/utils/lang-coaches";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, level } = (await readBody(event)) as { language: string; level: string };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  if (!coach.levelScale.includes(level)) throw createError({ statusCode: 400, message: "程度不在量表內" });

  const { data, error } = await supabase
    .from("lang_progress")
    .upsert(
      { user_id: user.id, language, level, updated_at: new Date().toISOString() },
      { onConflict: "user_id,language" }
    )
    .select("language, level")
    .single();
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { progress: data };
});
