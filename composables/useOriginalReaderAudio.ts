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
    const utterance = new SpeechSynthesisUtterance(segment.sourceText);
    utterance.lang = DEVICE_LANG[language];
    utterance.rate = 0.78;
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
    warning.value =
      language === "hbo"
        ? "現代以色列語音，僅供聽出斷句與節奏；發音以 BBH2 課本音標為準。"
        : "裝置試聽只供定位，不代表本讀本採用的歷史發音。";
    deviceQueue = segments.filter((item) => item.sourceText.trim());
    if (!deviceQueue.length) return;
    playing.value = true;
    deviceIndex = 0;
    speakDeviceSegment(language);
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
    playRecorded,
    playDevice,
    togglePause,
    stop,
  };
}
