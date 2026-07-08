<script setup lang="ts">
/**
 * 轉錄與翻譯進度面板（重轉錄佇列＋全集翻譯，資料源 /api/transcription-progress）。
 * - /ebook 圖書館頁嵌入：dark + collapsible（標題列常駐重點數字，點開看全貌）
 * - /transcription-progress 獨立頁：亮色全開
 */
const props = withDefaults(defineProps<{ dark?: boolean; collapsible?: boolean }>(), {
  dark: false,
  collapsible: false,
})

interface WorkRow { slug: string; title: string; done: boolean; sections: number; paras_total: number; paras_zh: number }
interface Corpus { name: string; works_total: number; works_done: number; works: WorkRow[] }
interface Progress {
  generated_at: string
  reocr: {
    tier_counts: Record<string, number>
    ledger_states: Record<string, number>
    recent: { title: string; state: string; updated_at?: string }[]
  }
  translation: Corpus[]
}

const { data, pending, error } = useFetch<Progress>('/api/transcription-progress')
const open = ref(!props.collapsible)

const tierCards = [
  { key: 'GOOD', label: '良好', cls: 'bg-emerald-50 border-emerald-200 text-emerald-700', darkCls: 'bg-emerald-900/30 border-emerald-800 text-emerald-300' },
  { key: 'FAIR', label: '普通', cls: 'bg-gray-50 border-gray-200 text-gray-600', darkCls: 'bg-gray-800/60 border-gray-700 text-gray-300' },
  { key: 'FIX_TOC', label: '待補目錄', cls: 'bg-sky-50 border-sky-200 text-sky-700', darkCls: 'bg-sky-900/30 border-sky-800 text-sky-300' },
  { key: 'RESTANDARDIZE', label: '待重標準化', cls: 'bg-amber-50 border-amber-200 text-amber-700', darkCls: 'bg-amber-900/30 border-amber-800 text-amber-300' },
  { key: 'REOCR', label: '待重轉錄', cls: 'bg-red-50 border-red-200 text-red-700', darkCls: 'bg-red-900/30 border-red-800 text-red-300' },
]

const STATE_ZH: Record<string, string> = {
  pending: '排隊中', ocr_staged: '已轉錄待驗', validated: '已過品質閘',
  swapped: '已上線', restandardized: '已重排版', done: '完成',
  rejected: '品質未過', ocr_failed: '轉錄失敗',
}
const stateLabel = (s: string) => STATE_ZH[s] ?? s

function pct(w: WorkRow): number {
  if (w.done) return 100
  if (!w.paras_total) return 0
  return Math.round((w.paras_zh / w.paras_total) * 100)
}
function corpusPct(c: Corpus): number {
  const total = c.works.reduce((s, w) => s + w.paras_total, 0)
  const done = c.works.reduce((s, w) => s + (w.done ? w.paras_total : w.paras_zh), 0)
  return total ? Math.round((done / total) * 100) : 0
}
function fmtTime(iso?: string): string {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('zh-TW', { hour12: false, month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch { return iso }
}

// 標題列重點：待重轉數 + 各 corpus 一句話
const headline = computed(() => {
  if (!data.value) return []
  const chips: string[] = []
  const reocr = data.value.reocr.tier_counts?.REOCR
  if (reocr) chips.push(`待重轉 ${reocr} 本`)
  const doneStates = data.value.reocr.ledger_states?.done
  if (doneStates) chips.push(`已重轉 ${doneStates} 本`)
  for (const c of data.value.translation) {
    const p = corpusPct(c)
    chips.push(`${c.name.replace(/（.*?）/, '')} ${c.works_done}/${c.works_total} 部（${p}%）`)
  }
  return chips
})

const t = computed(() => props.dark
  ? {
      card: 'bg-gray-900 border-gray-800',
      title: 'text-gray-100',
      sub: 'text-gray-400',
      muted: 'text-gray-500',
      bar: 'bg-gray-800',
      chip: 'bg-gray-800 text-gray-300 border-gray-700',
      section: 'border-gray-800',
    }
  : {
      card: 'bg-white border-gray-200',
      title: 'text-gray-900',
      sub: 'text-gray-500',
      muted: 'text-gray-400',
      bar: 'bg-gray-100',
      chip: 'bg-gray-50 text-gray-600 border-gray-200',
      section: 'border-gray-100',
    })
</script>

<template>
  <section :class="['border rounded-2xl', t.card]">
    <!-- 標題列（collapsible 時可點開合） -->
    <component :is="collapsible ? 'button' : 'div'"
      :class="['w-full flex items-center gap-3 px-5 py-3.5 text-left flex-wrap', collapsible ? 'cursor-pointer' : '']"
      @click="collapsible && (open = !open)">
      <span :class="['text-sm font-semibold flex-shrink-0', t.title]">🛰 轉錄與翻譯進度</span>
      <span v-for="(c, i) in headline" :key="i"
        :class="['text-xs px-2 py-0.5 rounded-full border truncate', t.chip]">{{ c }}</span>
      <span class="flex-1"></span>
      <span v-if="data" :class="['text-xs flex-shrink-0 hidden sm:inline', t.muted]">{{ fmtTime(data.generated_at) }}</span>
      <span v-if="collapsible" :class="['text-xs flex-shrink-0', t.muted]">{{ open ? '▾' : '▸' }}</span>
    </component>

    <div v-if="open" :class="['px-5 pb-5 space-y-5 border-t pt-4', t.section]">
      <div v-if="pending" class="space-y-2 animate-pulse">
        <div v-for="i in 3" :key="i" :class="['h-10 rounded-lg', t.bar]"></div>
      </div>
      <p v-else-if="error" :class="['text-sm', t.sub]">
        進度資料尚未產生——排程跑過後自動更新，或手動跑
        <code class="text-xs">python scripts/push_transcription_progress.py</code>。
      </p>

      <template v-else-if="data">
        <!-- 重轉錄佇列 -->
        <div>
          <h3 :class="['text-sm font-medium mb-2', t.title]">🔁 電子書重轉錄佇列</h3>
          <div class="grid grid-cols-2 sm:grid-cols-5 gap-2">
            <div v-for="tc in tierCards" :key="tc.key"
              :class="['rounded-lg border p-2 text-center', dark ? tc.darkCls : tc.cls]">
              <div class="text-lg font-bold">{{ data.reocr.tier_counts[tc.key] ?? 0 }}</div>
              <div class="text-[11px] truncate">{{ tc.label }}</div>
            </div>
          </div>
          <div v-if="!Object.keys(data.reocr.ledger_states || {}).length"
            :class="['text-xs mt-2', t.muted]">
            尚未開始重轉——等 Gemini 額度補上後由 02:30 夜間排程自動消化（每晚最多 5 本）。
          </div>
          <div v-else class="flex flex-wrap gap-1.5 mt-2">
            <span v-for="(n, st) in data.reocr.ledger_states" :key="st"
              :class="['text-xs px-2 py-0.5 rounded border', t.chip]">
              {{ stateLabel(st as string) }}：{{ n }}
            </span>
          </div>
          <ul v-if="data.reocr.recent?.length" class="mt-2 space-y-0.5">
            <li v-for="(r, i) in data.reocr.recent.slice(0, 5)" :key="i"
              :class="['text-xs flex items-center gap-2', t.sub]">
              <span :class="['w-1.5 h-1.5 rounded-full flex-shrink-0',
                r.state === 'done' ? 'bg-emerald-500' : r.state === 'rejected' ? 'bg-red-500' : 'bg-blue-400']"></span>
              <span class="truncate">{{ r.title }}</span>
              <span :class="['flex-shrink-0', t.muted]">{{ stateLabel(r.state) }}‧{{ fmtTime(r.updated_at) }}</span>
            </li>
          </ul>
        </div>

        <!-- 全集翻譯 -->
        <div v-for="corpus in data.translation" :key="corpus.name">
          <h3 :class="['text-sm font-medium mb-2', t.title]">
            📚 {{ corpus.name }}
            <span :class="['text-xs font-normal ml-1.5', t.muted]">{{ corpus.works_done }}/{{ corpus.works_total }} 部完成</span>
          </h3>
          <div class="space-y-1.5">
            <div v-for="w in corpus.works" :key="w.slug" class="flex items-center gap-2.5">
              <span :class="['text-xs w-44 sm:w-60 truncate flex-shrink-0', t.sub]" :title="w.title">
                {{ w.done ? '✅' : w.paras_zh > 0 ? '⏳' : '⬜' }} {{ w.title }}
              </span>
              <div :class="['flex-1 h-2 rounded-full overflow-hidden', t.bar]">
                <div :class="['h-full rounded-full transition-all',
                    w.done ? 'bg-emerald-500' : w.paras_zh > 0 ? 'bg-blue-500' : 'bg-transparent']"
                  :style="{ width: pct(w) + '%' }"></div>
              </div>
              <span :class="['text-[11px] w-24 text-right flex-shrink-0', t.muted]">
                {{ w.paras_total ? `${w.paras_zh}/${w.paras_total} 段` : '未開始' }}
              </span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>
