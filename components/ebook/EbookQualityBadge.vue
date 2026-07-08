<script setup lang="ts">
/**
 * 轉錄品質 badge（資料來自夜間 quality_sweep：ebooks.quality_score / quality_flags）。
 * 三色：≥80 綠（不顯示，免視覺噪音）/ 60-79 黃 / <60 紅；有 NEEDS_OCR 顯示「待轉錄」。
 * compact＝書卡用小圓點；完整模式給 reader 頂部（含 tier 文案）。
 */
const props = defineProps<{
  score?: number | null
  flags?: string[] | null
  compact?: boolean
}>()

const flagList = computed<string[]>(() =>
  Array.isArray(props.flags) ? props.flags : [])

const info = computed(() => {
  const s = props.score
  if (s === null || s === undefined) return null
  if (flagList.value.includes('NEEDS_OCR'))
    return { label: '待轉錄', cls: 'bg-red-950 text-red-400 border-red-900' }
  if (s >= 80) return null // 好書不掛牌
  if (s >= 60)
    return { label: `品質 ${s}`, cls: 'bg-amber-950 text-amber-400 border-amber-900' }
  return { label: `品質 ${s}`, cls: 'bg-red-950 text-red-400 border-red-900' }
})

const detail = computed(() => {
  const zh: Record<string, string> = {
    NEEDS_OCR: '掃描檔尚未轉錄',
    BLANK_BODY: '部分頁面內容空白',
    NO_TOC: '目錄未抓到',
    PARTIAL_TOC: '目錄不完整',
    OVER_FRAGMENTED: '分段碎裂',
    UNDER_SEGMENTED: '有超大段落未切分',
    STRUCTURE_MESS: '結構有頁眉/頁碼污染',
    PER_PAGE_ONLY: '逐頁呈現（無章節結構）',
    NOT_STANDARDIZED: '尚未標準化',
    PATH_BROKEN: '原始檔案路徑失效',
  }
  return flagList.value.map((f) => zh[f] ?? f).join('、')
})
</script>

<template>
  <span v-if="info" :title="detail"
    :class="['inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-xs whitespace-nowrap', info.cls]">
    <span v-if="!compact">⚠</span>{{ info.label }}
  </span>
</template>
