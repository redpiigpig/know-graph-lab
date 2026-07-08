<script setup lang="ts">
/**
 * 閱讀設定（Aa）：字級 4 檔 / 行距 3 檔 / 主題 亮‧米色‧暗。
 * 以 CSS 變數作用在閱讀區（--ebook-font-scale / --ebook-line-height /
 * --ebook-bg / --ebook-paper / --ebook-text），存 localStorage `ebook-display`。
 * 預設值＝原本的觀感（scale 1 / 行距原樣 / 亮）。
 */
interface EbookDisplay {
  fontScale: number   // 0.9 | 1 | 1.15 | 1.3
  lineHeight: number  // 1.7 | 2 | 2.3
  theme: 'light' | 'sepia' | 'dark'
}

const DEFAULTS: EbookDisplay = { fontScale: 1, lineHeight: 2, theme: 'light' }
const STORAGE_KEY = 'ebook-display'

const model = defineModel<EbookDisplay>({
  default: () => ({ fontScale: 1, lineHeight: 2, theme: 'light' }),
})
const open = ref(false)

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
    if (saved) model.value = { ...DEFAULTS, ...saved }
  } catch { /* private mode */ }
})

function set(patch: Partial<EbookDisplay>) {
  model.value = { ...model.value, ...patch }
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(model.value)) } catch { /* private mode */ }
}

const FONT_STEPS = [
  { v: 0.9, label: '小' }, { v: 1, label: '標準' },
  { v: 1.15, label: '大' }, { v: 1.3, label: '特大' },
]
const LINE_STEPS = [
  { v: 1.7, label: '緊' }, { v: 2, label: '標準' }, { v: 2.3, label: '鬆' },
]
const THEMES: { v: EbookDisplay['theme']; label: string; swatch: string }[] = [
  { v: 'light', label: '亮', swatch: 'bg-white border-stone-300' },
  { v: 'sepia', label: '米色', swatch: 'bg-amber-50 border-amber-300' },
  { v: 'dark', label: '暗', swatch: 'bg-stone-800 border-stone-600' },
]
</script>

<template>
  <div class="relative flex-shrink-0">
    <button @click="open = !open" title="閱讀設定（字級／行距／主題）"
      :class="['hidden md:flex items-center gap-1 px-2 py-1 rounded-md text-xs transition border',
        open ? 'bg-blue-100 text-blue-800 border-blue-300'
             : 'bg-white text-stone-600 border-stone-200 hover:border-blue-400 hover:text-blue-700']">
      <span class="font-serif">Aa</span>
    </button>

    <div v-if="open" class="absolute right-0 top-full mt-2 z-50 w-64 bg-white border border-stone-200 rounded-xl shadow-lg p-4 space-y-4">
      <div>
        <div class="text-xs text-stone-500 mb-1.5">字級</div>
        <div class="inline-flex bg-stone-100 rounded-lg p-0.5 gap-0.5 w-full">
          <button v-for="s in FONT_STEPS" :key="s.v" @click="set({ fontScale: s.v })"
            :class="['flex-1 px-2 py-1 rounded-md text-xs transition truncate',
              model.fontScale === s.v ? 'bg-white shadow text-stone-900' : 'text-stone-500 hover:text-stone-800']">
            {{ s.label }}
          </button>
        </div>
      </div>
      <div>
        <div class="text-xs text-stone-500 mb-1.5">行距</div>
        <div class="inline-flex bg-stone-100 rounded-lg p-0.5 gap-0.5 w-full">
          <button v-for="s in LINE_STEPS" :key="s.v" @click="set({ lineHeight: s.v })"
            :class="['flex-1 px-2 py-1 rounded-md text-xs transition truncate',
              model.lineHeight === s.v ? 'bg-white shadow text-stone-900' : 'text-stone-500 hover:text-stone-800']">
            {{ s.label }}
          </button>
        </div>
      </div>
      <div>
        <div class="text-xs text-stone-500 mb-1.5">主題</div>
        <div class="flex gap-2">
          <button v-for="t in THEMES" :key="t.v" @click="set({ theme: t.v })"
            :class="['flex-1 flex flex-col items-center gap-1 rounded-lg border px-2 py-2 text-xs transition',
              model.theme === t.v ? 'border-blue-400 ring-1 ring-blue-300' : 'border-stone-200 hover:border-stone-300']">
            <span :class="['w-6 h-6 rounded-full border', t.swatch]"></span>
            <span class="text-stone-600 truncate">{{ t.label }}</span>
          </button>
        </div>
      </div>
    </div>
    <!-- 點外面關閉 -->
    <div v-if="open" @click="open = false" class="fixed inset-0 z-40"></div>
  </div>
</template>
