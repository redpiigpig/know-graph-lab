/** GET /api/lang/profile — 取得學習者檔案；若無則用註冊時的 metadata 自動建立 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();

  const { data: existing } = await supabase
    .from("lang_profile")
    .select("*")
    .eq("user_id", user.id)
    .single();

  if (existing) return { profile: existing };

  // 從 user metadata 帶入註冊時填的資料
  const meta = (user.user_metadata ?? {}) as Record<string, any>;
  const academicFields: string[] = Array.isArray(meta.academic_fields) ? meta.academic_fields : [];
  const { data: created } = await supabase
    .from("lang_profile")
    .insert({
      user_id: user.id,
      display_name: meta.display_name ?? user.email?.split("@")[0] ?? null,
      interests: academicFields,
      onboarded: false,
    })
    .select("*")
    .single();

  return { profile: created };
});
