// ============================================================================
// 練習時間追蹤：在某個練習頁面掛載期間累計「使用中」秒數，定時 flush 到後端。
// 分頁隱藏 / 失焦時暫停計時，避免把掛機時間算進去。
// 用法：const tracker = useActivityTracker(); tracker.start('en','speaking','chat');
//      ...頁面卸載時 tracker.stop()（composable 會自動在 unmount flush）
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

  function tick() {
    if (typeof document !== "undefined" && document.hidden) return; // 分頁隱藏不計
    if (!running) return;
    activeSeconds.value += 1;
  }

  async function flush() {
    const secs = activeSeconds.value;
    if (secs < 30) return; // 不足 30 秒不送，避免碎片
    activeSeconds.value = 0;
    const minutes = Math.round((secs / 60) * 100) / 100;
    try {
      await authedFetch("/api/lang/activity", {
        method: "POST",
        body: { language, skill, minutes, source },
      });
    } catch {
      // 失敗就把秒數加回去，下次再試
      activeSeconds.value += secs;
    }
  }

  function start(lang: string, sk: string, src = "chat") {
    language = lang;
    skill = sk;
    source = src;
    running = true;
    if (!timer) timer = setInterval(tick, 1000);
    if (!flushTimer) flushTimer = setInterval(flush, 60000); // 每分鐘 flush
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
    await flush();
  }

  onUnmounted(() => {
    stop();
  });

  return { activeSeconds, start, pause, resume, stop, flush };
}
