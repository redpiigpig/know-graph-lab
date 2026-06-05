// ============================================================================
// 練習時間追蹤：在某個練習頁面掛載期間累計「使用中」秒數，定時 flush 到後端。
// 分頁隱藏 / 失焦時暫停計時，避免把掛機時間算進去。
// 用法：const tracker = useActivityTracker(); tracker.start('en','speaking','chat');
//      ...頁面卸載時 tracker.stop()（composable 會自動在 unmount flush）
//
// ⚠️ 連續計時（2026-06-05 修）：以前 flush 會把 activeSeconds 歸零，導致畫面計時器
//   每 30–60 秒就跳回 0、看似「一直重新計」。現在把「顯示用累計秒數」與「送 server 的
//   增量」分開：activeSeconds 單調遞增、永不歸零（連續顯示）；flush 只送「尚未送出的
//   增量」(activeSeconds - sentSeconds)，送成功才推進 sentSeconds（失敗不推進、下次重送，
//   不會重複計）。離開頁面/切分頁用 keepalive beacon 送殘餘增量。
// ============================================================================
import { ref, onUnmounted } from "vue";
import { authedFetch } from "~/composables/useAuthedFetch";

export function useActivityTracker() {
  const activeSeconds = ref(0); // 顯示用：本頁累計使用秒數，單調遞增、永不歸零
  let sentSeconds = 0;          // 已 flush 到 server 的秒數（避免重複計）
  let language = "";
  let skill = "";
  let source = "chat";
  let timer: ReturnType<typeof setInterval> | null = null;
  let flushTimer: ReturnType<typeof setInterval> | null = null;
  let running = false;
  let token = ""; // 快取 access token，給關頁時的 keepalive beacon 同步使用

  function tick() {
    if (typeof document !== "undefined" && document.hidden) return; // 分頁隱藏不計
    if (!running) return;
    activeSeconds.value += 1;
  }

  async function refreshToken() {
    try {
      const supabase = useSupabaseClient();
      const { data } = await supabase.auth.getSession();
      token = data?.session?.access_token ?? "";
    } catch { /* ignore */ }
  }

  // flush「尚未送出的增量」。force=true（離開頁面）時降低門檻。送成功才推進 sentSeconds。
  async function flush(force = false) {
    const delta = activeSeconds.value - sentSeconds;
    const floor = force ? 3 : 30;
    if (delta < floor) return;
    const minutes = Math.round((delta / 60) * 100) / 100;
    const target = activeSeconds.value;
    try {
      await authedFetch("/api/lang/activity", {
        method: "POST",
        body: { language, skill, minutes, source },
      });
      sentSeconds = target; // 成功才推進；失敗不動 → 下次補送同段增量
    } catch { /* 失敗：sentSeconds 不變，下次重送 */ }
  }

  // 關分頁 / 切走分頁：keepalive 讓請求在頁面卸載後仍送達（await 來不及）。
  function flushBeacon() {
    const delta = activeSeconds.value - sentSeconds;
    if (delta < 3 || !token) return;
    const minutes = Math.round((delta / 60) * 100) / 100;
    sentSeconds = activeSeconds.value; // beacon 無法確認結果 → 樂觀推進，避免重複送
    try {
      fetch("/api/lang/activity", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ language, skill, minutes, source }),
        keepalive: true,
      }).catch(() => {});
    } catch { /* ignore */ }
  }

  function onVisibility() {
    if (typeof document !== "undefined" && document.hidden) flushBeacon();
  }

  function start(lang: string, sk: string, src = "chat") {
    language = lang;
    skill = sk;
    source = src;
    running = true;
    refreshToken();
    if (!timer) timer = setInterval(tick, 1000);
    // 每 30 秒：把累積增量送 server + 刷新 token（顯示計時不受影響、不歸零）
    if (!flushTimer) flushTimer = setInterval(() => { flush(); refreshToken(); }, 30000);
    if (typeof window !== "undefined") {
      window.addEventListener("pagehide", flushBeacon);
      document.addEventListener("visibilitychange", onVisibility);
    }
  }

  function pause() { running = false; }
  function resume() { running = true; }

  async function stop() {
    running = false;
    if (timer) { clearInterval(timer); timer = null; }
    if (flushTimer) { clearInterval(flushTimer); flushTimer = null; }
    if (typeof window !== "undefined") {
      window.removeEventListener("pagehide", flushBeacon);
      document.removeEventListener("visibilitychange", onVisibility);
    }
    await flush(true); // 離開頁面：連不足 30 秒的殘餘增量也送
  }

  onUnmounted(() => { stop(); });

  return { activeSeconds, start, pause, resume, stop, flush };
}
