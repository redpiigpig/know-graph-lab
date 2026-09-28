<template>
  <!-- 🔊 朗讀本頁（2026-09-27）：預設 Gemini 語音，額度用盡自動改裝置語音。
       selector：要念的元素（每個 article 只取第一個符合的，避免多個中文譯本重複念）；
       resetKey 一變就停（換頁／換章）。 -->
  <span class="inline-flex items-center gap-1 flex-wrap">
    <button @click="toggle" :disabled="!tts.supported.value"
      :class="['flex items-center gap-1 px-2 py-0.5 rounded-md text-xs border transition',
        tts.playing.value ? 'bg-red-100 text-red-800 border-red-300'
          : 'bg-white text-stone-600 border-stone-200 hover:border-blue-400 hover:text-blue-700']">
      <span>{{ tts.loading.value ? '⏳' : tts.playing.value ? '⏹' : '🔊' }}</span>
      <span>{{ tts.playing.value ? '停止' : '朗讀' }}</span>
    </button>
    <select v-model="choice" title="朗讀語音"
      class="px-1 py-0.5 rounded-md text-xs border border-stone-200 bg-white text-stone-600 max-w-[7.5rem]">
      <option v-for="v in voices" :key="v" :value="`gemini:${v}`">Gemini・{{ v }}</option>
      <option v-if="tts.deviceSupported.value" value="device">裝置語音</option>
    </select>
    <span v-if="tts.notice.value" class="text-[11px] text-amber-700">{{ tts.notice.value }}</span>
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{ selector: string; resetKey?: unknown }>()
const tts = useReaderTts()
const voices = GEMINI_VOICES
const HL = 'bg-amber-50'
let els: HTMLElement[] = []

const choice = computed({
  get: () => tts.engine.value === 'gemini' ? `gemini:${tts.geminiVoice.value}` : 'device',
  set: (v: string) => {
    if (tts.playing.value) stop()
    if (v === 'device') { tts.engine.value = 'device'; return }
    tts.engine.value = 'gemini'
    tts.geminiVoice.value = v.slice('gemini:'.length)
  },
})

function stop() {
  tts.stop()
  for (const el of els) el.classList.remove(HL)
}

function toggle() {
  if (tts.playing.value) { stop(); return }
  els = []
  const texts: string[] = []
  for (const art of Array.from(document.querySelectorAll('article')) as HTMLElement[]) {
    const el = art.querySelector(props.selector) as HTMLElement | null
    const t = (el?.innerText || '').trim()
    if (!el || !t || t === '—') continue
    els.push(el)
    texts.push(t)
  }
  tts.speakQueue(texts)
}

watch(tts.currentIdx, (i, prev) => {
  if (prev !== undefined && prev >= 0 && els[prev]) els[prev].classList.remove(HL)
  if (i >= 0 && els[i]) {
    els[i].classList.add(HL)
    els[i].scrollIntoView({ block: 'center', behavior: 'smooth' })
  }
})
watch(() => props.resetKey, () => { if (tts.playing.value) stop() })
</script>
