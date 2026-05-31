// ============================================================================
// 語言教練 AI 呼叫包裝（前端）
//  - 每次 AI 請求自動帶上 usePaid（免費優先）
//  - 免費額度用完（429 code=free_exhausted）→ 跳確認 → 改用付費 key → 自動重試
//  - usePaid 偏好同步 lang_profile.use_paid_key，跨頁共用
// ============================================================================
import { useState } from "#app";
import { authedFetch } from "~/composables/useAuthedFetch";

export function useCoachAi() {
  // 跨頁共用的偏好狀態
  const usePaid = useState<boolean>("coachUsePaid", () => false);
  const loaded = useState<boolean>("coachUsePaidLoaded", () => false);

  async function ensureLoaded() {
    if (loaded.value) return;
    try {
      const { profile } = await authedFetch<any>("/api/lang/profile");
      usePaid.value = !!profile?.use_paid_key;
    } catch {
      /* ignore */
    } finally {
      loaded.value = true;
    }
  }

  async function setUsePaid(v: boolean) {
    usePaid.value = v;
    try {
      await authedFetch("/api/lang/profile", { method: "PUT", body: { use_paid_key: v } });
    } catch {
      /* ignore */
    }
  }

  /**
   * 呼叫 AI 端點。自動帶 usePaid；遇 free_exhausted 跳確認後切付費重試。
   * @returns 後端回應；若使用者拒絕切換則 throw 原錯誤。
   */
  async function aiFetch<T = any>(url: string, opts: Record<string, any> = {}): Promise<T> {
    await ensureLoaded();
    const bodyBase = (opts.body as Record<string, any>) || {};
    try {
      return await authedFetch<T>(url, { ...opts, body: { ...bodyBase, usePaid: usePaid.value } });
    } catch (e: any) {
      const code = e?.data?.code;
      if (code === "free_exhausted") {
        const ok = typeof window !== "undefined" && window.confirm(
          "今日免費 Gemini 額度已用完。\n要改用「付費 key」繼續嗎？（之後的請求都會走付費，可在儀表板切回免費）"
        );
        if (ok) {
          await setUsePaid(true);
          return await authedFetch<T>(url, { ...opts, body: { ...bodyBase, usePaid: true } });
        }
      } else if (code === "no_paid_key") {
        if (typeof window !== "undefined") window.alert("尚未設定付費 Gemini key，請先在 .env 填入 GEMINI_COACH_PAID_KEY。");
      } else if (code === "paid_exhausted") {
        if (typeof window !== "undefined") window.alert("付費 Gemini 額度也用完了，請檢查帳戶配額。");
      }
      throw e;
    }
  }

  return { usePaid, ensureLoaded, setUsePaid, aiFetch };
}
