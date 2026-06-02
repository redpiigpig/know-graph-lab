/**
 * PATCH /api/devices/:id  Body: { status: approved|revoked }
 * 核准 / 撤銷一台裝置。只有「已核准」的裝置能操作（依本機 deviceId 驗證）。
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const targetId = getRouterParam(event, "id");
  const { status, actingDeviceId } = (await readBody(event)) as { status: string; actingDeviceId: string };
  if (!["approved", "revoked"].includes(status)) throw createError({ statusCode: 400, message: "status 不正確" });

  // 操作者必須是已核准裝置
  const { data: acting } = await supabase
    .from("trusted_devices")
    .select("status")
    .eq("user_id", user.id)
    .eq("device_id", actingDeviceId)
    .single();
  if (acting?.status !== "approved") throw createError({ statusCode: 403, message: "只有已核准的管理裝置能操作" });

  const { data, error } = await supabase
    .from("trusted_devices")
    .update({ status })
    .eq("user_id", user.id)
    .eq("device_id", targetId)
    .select("device_id, status")
    .single();
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { device: data };
});
