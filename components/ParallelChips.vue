<template>
  <div class="flex items-center gap-1 flex-shrink-0">
    <span
      v-for="c in chips"
      :key="c.k"
      :title="c.title"
      class="px-1.5 py-0.5 rounded border text-[10px] leading-none"
      :class="c.cls"
    >{{ c.label }}</span>
  </div>
</template>

<script setup lang="ts">
/**
 * 一部經有哪些原文對照可用。顏色即來源分級（見 data/tripitaka/divisions.ts
 * 的 PARALLEL_SOURCES）—— 大正藏原註／CBETA 詞條／本站對齊不可混色，
 * 讀者要能一眼看出哪些是權威編者所加、哪些是本站自行判斷的。
 */
const props = defineProps<{ w: any }>()

const chips = computed(() => {
  const w = props.w ?? {}
  const out: { k: string; label: string; title: string; cls: string }[] = []
  if (w.equiv_count > 0) {
    out.push({
      k: 'equiv', label: `巴 ${w.equiv_count}`,
      title: `大正藏原註標出的巴利對應 ${w.equiv_count} 條`,
      cls: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    })
  }
  const langs: string[] = w.term_langs ?? []
  if (w.term_count > 0) {
    const names = langs
      .map(l => ({ sa: '梵', pi: '巴', 'sa-Sidd': '悉曇' } as Record<string, string>)[l] ?? l)
      .filter(Boolean)
    out.push({
      k: 'term', label: `${names.join('·') || '詞'} ${w.term_count}`,
      title: `CBETA 詞條對照 ${w.term_count} 組（${langs.join(', ')}）`,
      cls: 'bg-sky-50 text-sky-700 border-sky-200',
    })
  }
  for (const l of (w.parallel_langs ?? [])) {
    out.push({
      k: `p-${l}`, label: ({ pi: 'Pāli', sa: 'Skt', bo: 'Tib' } as Record<string, string>)[l] ?? l,
      title: '逐段原文對照', cls: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    })
  }
  return out
})
</script>
