/**
 * 通用閱讀器朗讀 composable：兩個引擎。
 *   - gemini（預設）：POST /api/works/tts 逐段生成 WAV 播放、預抓下一段（音色自然）。
 *     🚨 免費層額度小（見 [[project_works_reader_tts]]）：撞 429／額度用盡時**自動改用裝置引擎**，
 *     從當前段接著念，不中斷。2026-09-27 使用者：「現行的 gemini 語音還不錯」，要加進電子書閱讀器。
 *   - device：瀏覽器 SpeechSynthesis，免費不限量；Edge 有 HsiaoChen 等神經語音；語音挑選沿用 works reader 評分法。
 */
export type TtsEngine = 'gemini' | 'device'
export const GEMINI_VOICES = ['Kore', 'Aoede', 'Leda', 'Charon', 'Zephyr', 'Puck', 'Orus', 'Sulafat'] as const

export function useReaderTts() {
  const supported = ref(false)
  const deviceSupported = ref(false)
  const playing = ref(false)
  const paused = ref(false)
  const loading = ref(false)
  const currentIdx = ref(-1)
  const rate = ref(1)
  const zhVoices = ref<SpeechSynthesisVoice[]>([])
  const voiceURI = ref('')
  const engine = ref<TtsEngine>('gemini')
  const geminiVoice = ref<string>('Kore')
  const notice = ref('')          // 例：額度用盡已改用裝置語音

  const VOICE_KEY = 'reader-tts-voice'
  const RATE_KEY = 'reader-tts-rate'
  const ENGINE_KEY = 'reader-tts-engine'
  const GVOICE_KEY = 'reader-tts-gvoice'

  let queue: string[] = []
  let qi = 0
  let keepAlive: ReturnType<typeof setInterval> | null = null
  let audio: HTMLAudioElement | null = null
  let token = 0
  const cache = new Map<number, string>()

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

  // ── 引擎 A：裝置 ─────────────────────────────────────────────
  function speakNextDevice() {
    const synth = window.speechSynthesis
    if (!synth || !playing.value || qi >= queue.length) { stop(); return }
    currentIdx.value = qi
    const u = new SpeechSynthesisUtterance(queue[qi])
    u.lang = currentVoice.value?.lang || 'zh-TW'
    if (currentVoice.value) u.voice = currentVoice.value
    u.rate = rate.value
    u.onend = () => { if (playing.value && !paused.value && engine.value === 'device') { qi++; speakNextDevice() } }
    u.onerror = () => { if (playing.value && engine.value === 'device') { qi++; speakNextDevice() } }
    synth.speak(u)
  }

  // Chrome 長播自動暫停 → 定時 pause/resume 續命
  function armKeepAlive() {
    if (keepAlive) clearInterval(keepAlive)
    keepAlive = setInterval(() => {
      const s = window.speechSynthesis
      if (s && playing.value && !paused.value && engine.value === 'device') { s.pause(); s.resume() }
    }, 9000)
  }

  // ── 引擎 B：Gemini 雲端 ──────────────────────────────────────
  async function fetchSeg(i: number, t: number, retries: number): Promise<string> {
    if (cache.has(i)) return cache.get(i)!
    let last: any
    for (let a = 0; a <= retries; a++) {
      if (t !== token) throw new Error('stale')
      try {
        const blob = await $fetch<Blob>('/api/works/tts', {
          method: 'POST', responseType: 'blob',
          body: { text: queue[i].slice(0, 4000), voice: geminiVoice.value },
        })
        if (t !== token) throw new Error('stale')
        const url = URL.createObjectURL(blob)
        cache.set(i, url)
        return url
      } catch (e: any) {
        last = e
        if (e?.message === 'stale' || t !== token) throw e
        const quota = e?.statusCode === 429 || e?.data?.data?.code === 'quota_exhausted'
        if (quota) throw e                       // 額度用盡不重試，直接退回裝置
        if (a < retries) await new Promise(r => setTimeout(r, 2500 + a * 2500))
      }
    }
    throw last
  }

  function fallbackToDevice(reason: string) {
    if (!deviceSupported.value) { notice.value = reason; stop(); return }
    notice.value = `${reason}，已改用裝置語音接著念。`
    engine.value = 'device'
    loading.value = false
    qi = Math.max(0, currentIdx.value)          // 從剛才那段接著念
    armKeepAlive()
    speakNextDevice()
  }

  async function playGeminiAt(i: number, t: number) {
    if (t !== token || !playing.value) return
    if (i >= queue.length) { stop(); return }
    currentIdx.value = i
    let url: string
    try {
      if (!cache.has(i)) loading.value = true
      url = await fetchSeg(i, t, 3)
    } catch (e: any) {
      if (t !== token || e?.message === 'stale') return
      const quota = e?.statusCode === 429 || e?.data?.data?.code === 'quota_exhausted'
      fallbackToDevice(quota ? 'Gemini 免費語音額度暫時用盡' : 'Gemini 語音暫時無法生成')
      return
    }
    if (t !== token || !playing.value || !audio) return
    loading.value = false
    audio.src = url
    audio.playbackRate = rate.value
    audio.play().catch(() => {})
    if (i + 1 < queue.length && !cache.has(i + 1)) fetchSeg(i + 1, t, 0).catch(() => {})
  }

  // ── 共用控制 ─────────────────────────────────────────────────
  /** 從 startIdx 開始逐段朗讀（空白段自動跳過）。 */
  function speakQueue(paragraphs: string[], startIdx = 0) {
    stop()
    queue = paragraphs.map(p => p.trim()).filter(Boolean)
    if (!queue.length || !supported.value) return
    qi = Math.min(Math.max(0, startIdx), queue.length - 1)
    playing.value = true
    paused.value = false
    notice.value = ''
    if (engine.value === 'gemini') {
      token++
      playGeminiAt(qi, token)
    } else {
      armKeepAlive()
      speakNextDevice()
    }
  }

  function stop() {
    playing.value = false
    paused.value = false
    loading.value = false
    currentIdx.value = -1
    qi = 0
    token++
    if (keepAlive) { clearInterval(keepAlive); keepAlive = null }
    try { window.speechSynthesis?.cancel() } catch { /* unsupported */ }
    if (audio) { audio.pause(); audio.removeAttribute('src') }
    for (const u of cache.values()) URL.revokeObjectURL(u)
    cache.clear()
  }

  function togglePause() {
    if (!playing.value) return
    if (engine.value === 'gemini') {
      if (!audio) return
      if (paused.value) { audio.play().catch(() => {}); paused.value = false }
      else { audio.pause(); paused.value = true }
      return
    }
    const s = window.speechSynthesis
    if (!s) return
    if (paused.value) { s.resume(); paused.value = false }
    else { s.pause(); paused.value = true }
  }

  watch(rate, (r) => {
    try { localStorage.setItem(RATE_KEY, String(r)) } catch { /* private mode */ }
    if (audio) audio.playbackRate = r
  })
  watch(voiceURI, (u) => { try { localStorage.setItem(VOICE_KEY, u) } catch { /* private mode */ } })
  watch(geminiVoice, (v) => { try { localStorage.setItem(GVOICE_KEY, v) } catch { /* private mode */ } })
  watch(engine, (e) => { try { localStorage.setItem(ENGINE_KEY, e) } catch { /* private mode */ } })

  onMounted(() => {
    deviceSupported.value = typeof window !== 'undefined' && 'speechSynthesis' in window
    supported.value = typeof window !== 'undefined'   // gemini 只需 fetch + <audio>
    try {
      rate.value = Number(localStorage.getItem(RATE_KEY)) || 1
      const e = localStorage.getItem(ENGINE_KEY)
      if (e === 'device' || e === 'gemini') engine.value = e
      const gv = localStorage.getItem(GVOICE_KEY)
      if (gv && (GEMINI_VOICES as readonly string[]).includes(gv)) geminiVoice.value = gv
    } catch { /* private mode */ }
    if (engine.value === 'device' && !deviceSupported.value) engine.value = 'gemini'
    audio = new Audio()
    audio.addEventListener('ended', () => {
      if (engine.value !== 'gemini' || !playing.value || paused.value) return
      qi = currentIdx.value + 1
      playGeminiAt(qi, token)
    })
    if (deviceSupported.value) {
      loadVoices()
      window.speechSynthesis.onvoiceschanged = loadVoices
    }
  })
  onBeforeUnmount(stop)

  return {
    supported, deviceSupported, playing, paused, loading, currentIdx, rate, zhVoices, voiceURI,
    currentVoice, engine, geminiVoice, notice, speakQueue, stop, togglePause,
  }
}
