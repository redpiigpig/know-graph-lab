// ============================================================================
// 瀏覽器原生 Web Speech API 封裝：語音輸入（STT）+ 語音輸出（TTS）
// 零成本、零延遲、免後端。Chrome / Edge 支援最佳。
// ============================================================================
import { ref, onUnmounted } from "vue";

export function useSpeech() {
  const supported = ref(false);
  const ttsSupported = ref(false);
  const listening = ref(false);
  const interim = ref(""); // 即時辨識中的暫定文字
  const speaking = ref(false);
  const error = ref("");

  let recognition: any = null;
  let onFinalCb: ((text: string) => void) | null = null;
  // 連續聆聽控制：使用者按停才真的停；瀏覽器因靜默自動結束時自動重啟，
  // 讓使用者中途停頓思考也不會被關掉麥克風。
  let wantListening = false; // 使用者是否「想」繼續聽（手動按停才設 false）
  let restartTimer: any = null;

  if (typeof window !== "undefined") {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    supported.value = !!SR;
    ttsSupported.value = "speechSynthesis" in window;
    if (SR) {
      recognition = new SR();
      // continuous=true：停頓一兩秒不會結束辨識，可以邊想邊說
      recognition.continuous = true;
      recognition.interimResults = true;

      recognition.onresult = (e: any) => {
        let finalText = "";
        let interimText = "";
        for (let i = e.resultIndex; i < e.results.length; i++) {
          const t = e.results[i][0].transcript;
          if (e.results[i].isFinal) finalText += t;
          else interimText += t;
        }
        interim.value = interimText;
        if (finalText) {
          interim.value = "";
          onFinalCb?.(finalText.trim());
        }
      };
      recognition.onerror = (e: any) => {
        const err = e.error || "";
        // 'no-speech'（沒講話）/'aborted'（手動停）在連續模式下屬正常，交給 onend 處理，不報錯
        if (err === "no-speech" || err === "aborted") return;
        // 權限/裝置類錯誤才中止，避免無限重啟
        if (err === "not-allowed" || err === "service-not-allowed" || err === "audio-capture") {
          wantListening = false;
          listening.value = false;
        }
        error.value = err || "語音辨識錯誤";
      };
      recognition.onend = () => {
        interim.value = "";
        // 使用者還想繼續聽，但瀏覽器（多在長靜默後）自動結束 → 重啟維持麥克風開啟
        if (wantListening) {
          try {
            recognition.start();
            return;
          } catch {
            // start() 太快偶爾會丟錯，稍候再試一次
            if (restartTimer) clearTimeout(restartTimer);
            restartTimer = setTimeout(() => {
              if (!wantListening) return;
              try {
                recognition.start();
              } catch {
                listening.value = false;
                wantListening = false;
              }
            }, 250);
            return;
          }
        }
        listening.value = false;
      };
    }
  }

  // 開始聆聽。lang 為 BCP-47（如 en-US / ja-JP）；onFinal 收到最終文字
  function startListening(lang: string, onFinal: (text: string) => void) {
    if (!recognition) {
      error.value = "此瀏覽器不支援語音辨識，請改用 Chrome / Edge";
      return;
    }
    if (listening.value) return;
    error.value = "";
    onFinalCb = onFinal;
    recognition.lang = lang;
    wantListening = true; // 進入連續聆聽：靜默自動結束時會自動重啟
    try {
      recognition.start();
      listening.value = true;
    } catch {
      // start() 在已啟動時會丟錯，忽略
    }
  }

  function stopListening() {
    wantListening = false; // 手動按停 → onend 不再自動重啟
    if (restartTimer) {
      clearTimeout(restartTimer);
      restartTimer = null;
    }
    if (recognition) {
      try {
        recognition.stop();
      } catch {
        // 已停止時忽略
      }
    }
    listening.value = false;
  }

  // 語音播放教練回覆。lang 為偏好語系；rate 語速
  function speak(text: string, lang: string, rate = 1) {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    if (!text?.trim()) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang;
    u.rate = rate;
    // 盡量挑符合語系的語音
    const voices = window.speechSynthesis.getVoices();
    const match = voices.find((v) => v.lang === lang) || voices.find((v) => v.lang?.startsWith(lang.split("-")[0]));
    if (match) u.voice = match;
    u.onstart = () => (speaking.value = true);
    u.onend = () => (speaking.value = false);
    u.onerror = () => (speaking.value = false);
    window.speechSynthesis.speak(u);
  }

  function stopSpeaking() {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    speaking.value = false;
  }

  onUnmounted(() => {
    stopListening();
    stopSpeaking();
  });

  return {
    supported,
    ttsSupported,
    listening,
    interim,
    speaking,
    error,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
  };
}
