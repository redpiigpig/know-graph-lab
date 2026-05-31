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

  if (typeof window !== "undefined") {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    supported.value = !!SR;
    ttsSupported.value = "speechSynthesis" in window;
    if (SR) {
      recognition = new SR();
      recognition.continuous = false;
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
        error.value = e.error || "語音辨識錯誤";
        listening.value = false;
      };
      recognition.onend = () => {
        listening.value = false;
        interim.value = "";
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
    try {
      recognition.start();
      listening.value = true;
    } catch {
      // start() 在已啟動時會丟錯，忽略
    }
  }

  function stopListening() {
    if (recognition && listening.value) recognition.stop();
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
