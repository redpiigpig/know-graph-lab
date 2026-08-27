import { toEcclesiasticalSpeech } from "~/utils/ecclesiasticalLatin";
import type {
  OriginalReaderAudioTrack,
  OriginalReaderLanguage,
  OriginalReaderSegment,
} from "~/data/originalReaders/types";

const DEVICE_LANG: Record<OriginalReaderLanguage, string> = {
  hbo: "he-IL",
  grc: "el-GR",
  la: "it-IT",
};

// 希伯來文與希臘文只能借現代語音，念出來不是本讀本教的發音；拉丁文不一樣——
// 羅馬式教會發音本來就是照義大利語音韻讀的，只要先把拼寫改成義大利文的寫法，
// 義大利語聲線念出來就是對的。所以只有拉丁文有這層改寫。
const SPEECH_TEXT: Partial<Record<OriginalReaderLanguage, (text: string) => string>> = {
  la: toEcclesiasticalSpeech,
};

const DEVICE_NOTE: Record<OriginalReaderLanguage, string> = {
  hbo: "現代以色列語音，僅供聽出斷句與節奏；發音以 BBH2 課本音標為準。",
  grc: "裝置試聽只供定位，不代表本讀本採用的歷史發音。",
  la: "以義大利語聲線朗讀，拼寫已依羅馬式教會發音改寫（ae/oe→e、gratia→grazia、ch→[k]）。裝置沒有義大利語音時會退回預設聲線，發音就不準了。",
};

/** Audio controller for aligned recordings plus a clearly provisional device preview. */
export function useOriginalReaderAudio() {
  const recordedSupported = ref(false);
  const deviceSupported = ref(false);
  const playing = ref(false);
  const paused = ref(false);
  const currentSegmentId = ref("");
  const currentTokenId = ref("");
  const currentTrackId = ref("");
  const warning = ref("");
  // 原文讀本要跟著唸，預設就比說話慢一截；使用者可再調。
  const rate = ref(0.78);
  let audio: HTMLAudioElement | null = null;
  let deviceQueue: OriginalReaderSegment[] = [];
  let deviceIndex = 0;

  function clearPosition() {
    currentSegmentId.value = "";
    currentTokenId.value = "";
    currentTrackId.value = "";
  }

  function stop() {
    if (audio) {
      audio.pause();
      audio.src = "";
      audio = null;
    }
    if (typeof window !== "undefined") window.speechSynthesis?.cancel();
    playing.value = false;
    paused.value = false;
    deviceQueue = [];
    deviceIndex = 0;
    clearPosition();
  }

  function playRecorded(track: OriginalReaderAudioTrack) {
    stop();
    warning.value = "";
    if (!track.src) {
      warning.value = "這條校訂音軌尚待匯入。";
      return;
    }
    audio = new Audio(track.src);
    currentTrackId.value = track.id;
    audio.ontimeupdate = () => {
      if (!audio || !track.cues?.length) return;
      const now = audio.currentTime * 1000;
      const cue = track.cues.find((item) => now >= item.startMs && now < item.endMs);
      currentSegmentId.value = cue?.segmentId || "";
      currentTokenId.value = cue?.tokenId || "";
    };
    audio.onended = () => stop();
    audio.onerror = () => {
      warning.value = "音軌無法載入，請檢查私人音訊檔。";
      stop();
    };
    playing.value = true;
    void audio.play();
  }

  function speakDeviceSegment(language: OriginalReaderLanguage) {
    if (!playing.value || deviceIndex >= deviceQueue.length) {
      stop();
      return;
    }
    const segment = deviceQueue[deviceIndex];
    currentSegmentId.value = segment.id;
    const spoken = (SPEECH_TEXT[language] || ((text: string) => text))(segment.sourceText);
    if (!spoken.trim()) {
      deviceIndex += 1;
      speakDeviceSegment(language);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(spoken);
    utterance.lang = DEVICE_LANG[language];
    const voice = preferredVoice(DEVICE_LANG[language]);
    if (voice) utterance.voice = voice;
    utterance.rate = rate.value;
    utterance.onend = () => {
      deviceIndex += 1;
      speakDeviceSegment(language);
    };
    utterance.onerror = () => {
      deviceIndex += 1;
      speakDeviceSegment(language);
    };
    window.speechSynthesis.speak(utterance);
  }

  function playDevice(
    language: OriginalReaderLanguage,
    segments: OriginalReaderSegment[],
  ) {
    stop();
    if (!deviceSupported.value) {
      warning.value = "此裝置沒有可用的語音試聽功能。";
      return;
    }
    // The only Hebrew voice any device ships is modern Israeli, which merges ח
    // with ḵ, drops ע and reads ק as k — exactly the contrasts BBH2 teaches.
    // It is offered for phrasing and rhythm only, never as a pronunciation model.
    warning.value = missingVoice(language)
      ? `${DEVICE_NOTE[language]}（本裝置找不到對應語音）`
      : DEVICE_NOTE[language];
    deviceQueue = segments.filter((item) => item.sourceText.trim());
    if (!deviceQueue.length) return;
    playing.value = true;
    deviceIndex = 0;
    speakDeviceSegment(language);
  }

  /** 同一語系可能同時裝著舊聲線與 Natural 聲線，挑到後者差別很大。 */
  function preferredVoice(lang: string) {
    if (typeof window === "undefined") return undefined;
    const base = lang.toLowerCase().split("-")[0];
    const candidates = window.speechSynthesis
      .getVoices()
      .filter((voice) => voice.lang.toLowerCase().split(/[-_]/)[0] === base);
    const score = (voice: SpeechSynthesisVoice) => {
      const name = voice.name.toLowerCase();
      let value = voice.lang.toLowerCase().replace("_", "-") === lang.toLowerCase() ? 20 : 0;
      if (name.includes("natural")) value += 8;
      if (name.includes("premium") || name.includes("enhanced")) value += 6;
      if (name.includes("google")) value += 4;
      return value;
    };
    return candidates.sort((a, b) => score(b) - score(a))[0];
  }

  function missingVoice(language: OriginalReaderLanguage) {
    return !preferredVoice(DEVICE_LANG[language]);
  }

  /** 唸一行（或一個詞）。點哪一行就唸哪一行，不必從頭播。 */
  function speakOne(language: OriginalReaderLanguage, text: string) {
    stop();
    if (!deviceSupported.value) {
      warning.value = "此裝置沒有可用的語音試聽功能。";
      return;
    }
    const spoken = (SPEECH_TEXT[language] || ((value: string) => value))(text);
    if (!spoken.trim()) return;
    warning.value = missingVoice(language)
      ? `${DEVICE_NOTE[language]}（本裝置找不到對應語音）`
      : "";
    const utterance = new SpeechSynthesisUtterance(spoken);
    utterance.lang = DEVICE_LANG[language];
    const voice = preferredVoice(DEVICE_LANG[language]);
    if (voice) utterance.voice = voice;
    utterance.rate = rate.value;
    utterance.onend = () => stop();
    utterance.onerror = () => stop();
    playing.value = true;
    window.speechSynthesis.speak(utterance);
  }

  function togglePause() {
    if (!playing.value) return;
    if (audio) {
      if (paused.value) void audio.play();
      else audio.pause();
    } else if (typeof window !== "undefined") {
      if (paused.value) window.speechSynthesis.resume();
      else window.speechSynthesis.pause();
    }
    paused.value = !paused.value;
  }

  onMounted(() => {
    recordedSupported.value = typeof Audio !== "undefined";
    deviceSupported.value =
      typeof window !== "undefined" && "speechSynthesis" in window;
    // Chrome 第一次 getVoices() 常常回空陣列，聲線是非同步載入的。不先暖機的話
    // 第一次點朗讀會誤報「本裝置找不到對應語音」，而其實裝著。
    if (deviceSupported.value) {
      window.speechSynthesis.getVoices();
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
      };
    }
  });
  onBeforeUnmount(stop);

  return {
    recordedSupported,
    deviceSupported,
    playing,
    paused,
    currentSegmentId,
    currentTokenId,
    currentTrackId,
    warning,
    rate,
    playRecorded,
    playDevice,
    speakOne,
    togglePause,
    stop,
  };
}
