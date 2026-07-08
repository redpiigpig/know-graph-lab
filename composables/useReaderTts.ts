/**
 * 通用閱讀器朗讀 composable（裝置 SpeechSynthesis 引擎，免費不限量）。
 * 抽自 /works 書籍閱讀器的段落佇列朗讀；只做裝置引擎，不接 Gemini 雲端
 * （免費層額度小，長讀必撞 429 — 見 [[project_works_reader_tts]]）。
 * Edge 有 HsiaoChen 等神經語音；語音挑選沿用 works reader 的評分法。
 */
export function useReaderTts() {
  const supported = ref(false)
  const playing = ref(false)
  const paused = ref(false)
  const currentIdx = ref(-1)
  const rate = ref(1)
  const zhVoices = ref<SpeechSynthesisVoice[]>([])
  const voiceURI = ref('')

  const VOICE_KEY = 'reader-tts-voice'
  const RATE_KEY = 'reader-tts-rate'

  let queue: string[] = []
  let qi = 0
  let keepAlive: ReturnType<typeof setInterval> | null = null

  // 神經／線上聲線 ＞ Google ＞ 台灣優先（同 works reader）
  function voiceScore(v: SpeechSynthesisVoice): number {
    const n = v.name.toLowerCase(), l = v.lang.toLowerCase()
    let s = 0
    if (/natural|neural|online/.test(n)) s += 40
    if (/premium|enhanced/.test(n)) s += 20
    if (/google/.test(n)) s += 12
    if (/hsiaochen|hsiaoyu|yating|zhiwei|hanhan/.test(n)) s += 4
    if (l.startsWith('zh-tw')) s += 8
    else if (l.startsWith('zh-hk')) s += 4
    return s
  }

  function loadVoices() {
    const vs = window.speechSynthesis?.getVoices?.() ?? []
    zhVoices.value = vs.filter(v => /^zh/i.test(v.lang)).sort((a, b) => voiceScore(b) - voiceScore(a))
    if (!zhVoices.value.length) return
    let saved = ''
    try { saved = localStorage.getItem(VOICE_KEY) || '' } catch { /* private mode */ }
    if (saved && zhVoices.value.some(v => v.voiceURI === saved)) voiceURI.value = saved
    else if (!voiceURI.value || !zhVoices.value.some(v => v.voiceURI === voiceURI.value))
      voiceURI.value = zhVoices.value[0].voiceURI
  }

  const currentVoice = computed(() =>
    zhVoices.value.find(v => v.voiceURI === voiceURI.value) ?? null)

  function speakNext() {
    const synth = window.speechSynthesis
    if (!synth || !playing.value || qi >= queue.length) { stop(); return }
    currentIdx.value = qi
    const u = new SpeechSynthesisUtterance(queue[qi])
    u.lang = currentVoice.value?.lang || 'zh-TW'
    if (currentVoice.value) u.voice = currentVoice.value
    u.rate = rate.value
    u.onend = () => { if (playing.value && !paused.value) { qi++; speakNext() } }
    u.onerror = () => { if (playing.value) { qi++; speakNext() } }
    synth.speak(u)
  }

  // Chrome 長播自動暫停 → 定時 pause/resume 續命
  function armKeepAlive() {
    if (keepAlive) clearInterval(keepAlive)
    keepAlive = setInterval(() => {
      const s = window.speechSynthesis
      if (s && playing.value && !paused.value) { s.pause(); s.resume() }
    }, 9000)
  }

  /** 從 startIdx 開始逐段朗讀（空白段自動跳過）。 */
  function speakQueue(paragraphs: string[], startIdx = 0) {
    stop()
    queue = paragraphs.map(p => p.trim()).filter(Boolean)
    if (!queue.length || !supported.value) return
    qi = Math.min(Math.max(0, startIdx), queue.length - 1)
    playing.value = true
    paused.value = false
    armKeepAlive()
    speakNext()
  }

  function stop() {
    playing.value = false
    paused.value = false
    currentIdx.value = -1
    qi = 0
    if (keepAlive) { clearInterval(keepAlive); keepAlive = null }
    try { window.speechSynthesis?.cancel() } catch { /* unsupported */ }
  }

  function togglePause() {
    const s = window.speechSynthesis
    if (!s || !playing.value) return
    if (paused.value) { s.resume(); paused.value = false }
    else { s.pause(); paused.value = true }
  }

  watch(rate, (r) => { try { localStorage.setItem(RATE_KEY, String(r)) } catch { /* private mode */ } })
  watch(voiceURI, (u) => { try { localStorage.setItem(VOICE_KEY, u) } catch { /* private mode */ } })

  onMounted(() => {
    supported.value = typeof window !== 'undefined' && 'speechSynthesis' in window
    if (!supported.value) return
    try { rate.value = Number(localStorage.getItem(RATE_KEY)) || 1 } catch { /* private mode */ }
    loadVoices()
    window.speechSynthesis.onvoiceschanged = loadVoices
  })
  onBeforeUnmount(stop)

  return { supported, playing, paused, currentIdx, rate, zhVoices, voiceURI, currentVoice, speakQueue, stop, togglePause }
}
