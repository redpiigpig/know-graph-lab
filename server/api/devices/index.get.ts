/** GET /api/devices — 列出本帳號所有裝置（給管理 UI） */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { data } = await supabase
    .from("trusted_devices")
    .select("device_id, name, user_agent, status, created_at, last_seen")
    .eq("user_id", user.id)
    .order("last_seen", { ascending: false });
  return { devices: data ?? [] };
});
