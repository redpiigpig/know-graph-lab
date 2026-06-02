// 全站裝置守門：已登入但裝置未核准 → 導到 /device-pending
// 只在 client 執行（device_id 存在 localStorage）。核准後快取，不重複打 API。
import { authedFetch } from "~/composables/useAuthedFetch";
import { getDeviceId, getDeviceName } from "~/composables/useDevice";

const EXEMPT = ["/login", "/device-pending", "/forgot-password", "/reset-password", "/signup", "/privacy", "/terms", "/confirm", "/auth"];

export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return;
  const user = useSupabaseUser();
  if (!user.value) return; // 未登入交給各頁 auth/coach-auth 處理
  if (EXEMPT.some((p) => to.path.startsWith(p))) return;

  const status = useState<string>("deviceStatus", () => "");
  if (status.value === "approved") return;

  try {
    const r = await authedFetch<{ status: string }>("/api/devices/check", {
      method: "POST",
      body: { deviceId: getDeviceId(), name: getDeviceName(), userAgent: navigator.userAgent },
    });
    status.value = r.status;
  } catch {
    return; // API 失敗時不鎖死，放行
  }

  if (status.value !== "approved") {
    return navigateTo("/device-pending");
  }
});
