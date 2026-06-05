// ============================================================================
// 練習時間追蹤：在某個練習頁面掛載期間累計「使用中」秒數，定時 flush 到後端。
// 分頁隱藏 / 失焦時暫停計時，避免把掛機時間算進去。
// 用法：const tracker = useActivityTracker(); tracker.start('en','speaking','chat');
//      ...頁面卸載時 tracker.stop()（composable 會自動在 unmount flush）
//
// ⚠️ 可靠 flush（2026-06-05）：以前「離開頁面」常沒記到，因為
//   (1) flush 不足 30 秒就整包丟掉；(2) onUnmounted 裡 await fetch 在關分頁/SPA
//   導航時來不及送。現在：離開頁面 force-flush（連 <30 秒也送）；切分頁/關頁用
//   `fetch(keepalive:true)` beacon（可帶 Bearer header、請求能在頁面卸載後存活）。
// ============================================================================
import { ref, onUnmounted } from "vue";
import { authedFetch } from "~/composables/useAuthedFetch";

export function useActivityTracker() {
  const activeSeconds = ref(0);
  let language = "";
  let skill = "";
  let source = "chat";
  let timer: ReturnType<typeof setInterval> | null = null;
  let flushTimer: ReturnType<typeof setInterval> | null = null;
  let running = false;
  let token = ""; // 快取 access token，給關頁時的 keepalive beacon 同步使用
  let supabase: any = null;

  function tick() {
    if (typeof document !== "undefined" && document.hidden) return; // 分頁隱藏不計
    if (!running) return;
    activeSeconds.value += 1;
  }

  // 快取最新 token（beacon 在 pagehide 時沒空 await getSession）
  async function refreshToken() {
    try {
      if (!supabase) supabase = useSupabaseClient();
      const { data } = await supabase.auth.getSession();
      token = data?.session?.access_token ?? "";
    } catch { /* ignore */ }
  }

  // 一般 flush（可 await、失敗會把秒數加回去重試）。
  // force=true（離開頁面）時連不足 30 秒也送，避免短停留時間流失。
  async function flush(force = false) {
    const secs = activeSeconds.value;
    const floor = force ? 3 : 30; // 平時 30 秒門檻避免碎片；離開頁面降到 3 秒
    if (secs < floor) return;
    activeSeconds.value = 0;
    const minutes = Math.round((secs / 60) * 100) / 100;
    try {
      await authedFetch("/api/lang/activity", {
        method: "POST",
        body: { language, skill, minutes, source },
      });
    } catch {
      activeSeconds.value += secs; // 失敗加回去，下次再試
    }
  }

  // 關分頁 / 切走分頁時用：keepalive 讓請求在頁面卸載後仍送達（await 來不及）。
  function flushBeacon() {
    const secs = activeSeconds.value;
    if (secs < 3 || !token) return;
    activeSeconds.value = 0;
    const minutes = Math.round((secs / 60) * 100) / 100;
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
    // 每 30 秒：flush 已累積時間 + 刷新 token（讓 beacon 隨時可用）
    if (!flushTimer) flushTimer = setInterval(() => { flush(); refreshToken(); }, 30000);
    if (typeof window !== "undefined") {
      window.addEventListener("pagehide", flushBeacon);
      document.addEventListener("visibilitychange", onVisibility);
    }
  }

  function pause() {
    running = false;
  }
  function resume() {
    running = true;
  }

  async function stop() {
    running = false;
    if (timer) { clearInterval(timer); timer = null; }
    if (flushTimer) { clearInterval(flushTimer); flushTimer = null; }
    if (typeof window !== "undefined") {
      window.removeEventListener("pagehide", flushBeacon);
      document.removeEventListener("visibilitychange", onVisibility);
    }
    await flush(true); // 離開頁面：連不足 30 秒也送
  }

  onUnmounted(() => {
    stop();
  });

  return { activeSeconds, start, pause, resume, stop, flush };
}
