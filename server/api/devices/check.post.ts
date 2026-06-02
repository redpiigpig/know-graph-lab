/**
 * POST /api/devices/check
 * Body: { deviceId, name, userAgent }
 * 登入後檢查/註冊本機裝置。第一台（尚無任何已核准裝置）自動核准=管理機；
 * 之後的新裝置為 pending，需由已核准裝置核准才能使用。
 * 回傳 { status: approved|pending|revoked }
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { deviceId, name, userAgent } = (await readBody(event)) as { deviceId: string; name?: string; userAgent?: string };
  if (!deviceId) throw createError({ statusCode: 400, message: "缺少 deviceId" });

  const now = new Date().toISOString();
  const { data: existing } = await supabase
    .from("trusted_devices")
    .select("status")
    .eq("user_id", user.id)
    .eq("device_id", deviceId)
    .single();

  if (existing) {
    await supabase
      .from("trusted_devices")
      .update({ last_seen: now, name: name ?? null, user_agent: userAgent ?? null })
      .eq("user_id", user.id)
      .eq("device_id", deviceId);
    return { status: existing.status };
  }

  // 新裝置：若目前沒有任何「已核准」裝置 → 自動核准（首台/防鎖死）；否則 pending
  const { count } = await supabase
    .from("trusted_devices")
    .select("device_id", { count: "exact", head: true })
    .eq("user_id", user.id)
    .eq("status", "approved");
  const status = (count ?? 0) === 0 ? "approved" : "pending";

  await supabase.from("trusted_devices").insert({
    user_id: user.id,
    device_id: deviceId,
    name: name ?? null,
    user_agent: userAgent ?? null,
    status,
    last_seen: now,
  });

  return { status };
});
