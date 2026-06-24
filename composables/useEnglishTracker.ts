// ============================================================================
// Happy English 學習時間追蹤：頁面掛載期間累計「使用中」秒數，定時送 /api/english/activity。
// 分頁隱藏/失焦暫停計時；activeSeconds 單調遞增（顯示用），只送尚未送出的增量（不重複計）。
// 用法：const t = useEnglishTracker(); t.start('lesson'); ... 卸載自動 stop()。
// ============================================================================
import { ref, onUnmounted } from "vue";
import { authedFetch } from "~/composables/useAuthedFetch";

export function useEnglishTracker() {
  const activeSeconds = ref(0);
  let sentSeconds = 0;
  let source = "lesson";
  let timer: ReturnType<typeof setInterval> | null = null;
  let flushTimer: ReturnType<typeof setInterval> | null = null;
  let running = false;
  let token = "";

  function tick() {
    if (typeof document !== "undefined" && document.hidden) return;
    if (running) activeSeconds.value += 1;
  }

  async function refreshToken() {
    try {
      const supabase = useSupabaseClient();
      const { data } = await supabase.auth.getSession();
      token = data?.session?.access_token ?? "";
    } catch { /* ignore */ }
  }

  async function flush(force = false) {
    const delta = activeSeconds.value - sentSeconds;
    if (delta < (force ? 3 : 30)) return;
    const minutes = Math.round((delta / 60) * 100) / 100;
    const target = activeSeconds.value;
    try {
      await authedFetch("/api/english/activity", { method: "POST", body: { minutes, source } });
      sentSeconds = target;
    } catch { /* 失敗下次重送 */ }
  }

  function flushBeacon() {
    const delta = activeSeconds.value - sentSeconds;
    if (delta < 3 || !token) return;
    const minutes = Math.round((delta / 60) * 100) / 100;
    sentSeconds = activeSeconds.value;
    try {
      fetch("/api/english/activity", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ minutes, source }),
        keepalive: true,
      }).catch(() => {});
    } catch { /* ignore */ }
  }

  function onVisibility() {
    if (typeof document !== "undefined" && document.hidden) flushBeacon();
  }

  function start(src = "lesson") {
    source = src;
    running = true;
    refreshToken();
    if (!timer) timer = setInterval(tick, 1000);
    if (!flushTimer) flushTimer = setInterval(() => { flush(); refreshToken(); }, 30000);
    if (typeof window !== "undefined") {
      window.addEventListener("pagehide", flushBeacon);
      document.addEventListener("visibilitychange", onVisibility);
    }
  }

  async function stop() {
    running = false;
    if (timer) { clearInterval(timer); timer = null; }
    if (flushTimer) { clearInterval(flushTimer); flushTimer = null; }
    if (typeof window !== "undefined") {
      window.removeEventListener("pagehide", flushBeacon);
      document.removeEventListener("visibilitychange", onVisibility);
    }
    await flush(true);
  }

  onUnmounted(() => { stop(); });

  return { activeSeconds, start, stop, flush };
}
