<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader
      :title="loc ? loc.text.title_zh : '古近東大藏經'"
      :back="loc ? { to: `/near-east/${loc.canon.key}/${loc.volume.key}#${loc.text.slug}`, label: `${loc.volume.sigil} ${loc.volume.name}` } : { to: '/near-east', label: '古近東大藏經' }"
      container-class="max-w-6xl"
    >
      <template #actions>
        <span v-if="doc" class="text-xs text-gray-400">{{ segCount }} 段</span>
      </template>
    </AppHeader>

    <div v-if="!loc" class="flex-1 flex items-center justify-center text-gray-400 text-sm">找不到此篇。</div>

    <div v-else class="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8">
      <div class="mb-6">
        <h1 class="text-xl font-bold text-gray-900 break-words">{{ loc.text.title_zh }}</h1>
        <div class="text-[11px] text-gray-400 break-words mt-0.5">
          <span v-if="loc.text.title_orig" class="italic">{{ loc.text.title_orig }}</span>
          <span v-if="loc.text.siglum"> · <span class="font-mono">{{ loc.text.siglum }}</span></span>
        </div>
        <p v-if="loc.text.note" class="text-sm text-gray-600 leading-relaxed mt-2 break-words">{{ loc.text.note }}</p>
        <p v-if="doc" class="text-[11px] text-gray-400 mt-2 break-words">
          來源：<a v-if="doc.source_url" :href="doc.source_url" target="_blank" rel="noopener" class="text-teal-700 hover:underline">{{ doc.source }}</a><span v-else>{{ doc.source }}</span>
          <span v-if="doc.license">（{{ doc.license }}）</span>。段號照抄來源的行號範圍。
        </p>

        <div class="flex flex-wrap gap-1.5 mt-3">
          <button
            v-for="c in availableCols"
            :key="c"
            class="text-[11px] px-2 py-0.5 rounded border transition"
            :class="shown[c] ? 'bg-slate-900 text-teal-200 border-slate-900' : 'bg-white text-gray-500 border-gray-200'"
            @click="shown[c] = !shown[c]"
          >{{ COL_LABEL[c] }}</button>
        </div>
        <p v-if="!hasZh" class="mt-2 text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1 inline-block">繁體中文尚未翻譯，目前只有原文轉寫與英譯。</p>
      </div>

      <div v-if="loading" class="text-sm text-gray-400 py-10 text-center">載入中⋯</div>
      <div v-else-if="!doc" class="text-sm text-gray-400 py-10 text-center bg-white border border-gray-200 rounded-xl">此篇正文尚未上架。</div>

      <template v-else>
        <nav v-if="doc.compositions.length > 1" class="flex flex-wrap gap-1 mb-5">
          <a v-for="c in doc.compositions" :key="c.num" :href="`#c-${c.num}`" class="text-[11px] px-2 py-0.5 rounded bg-white border border-gray-200 hover:border-teal-400 text-gray-600 break-words">{{ c.num }} {{ c.title_zh || c.title_en }}</a>
        </nav>

        <section v-for="comp in doc.compositions" :id="`c-${comp.num}`" :key="comp.num" class="mb-10 scroll-mt-20">
          <h2 v-if="doc.compositions.length > 1" class="text-sm font-bold text-teal-900 border-b border-teal-200 pb-1.5 mb-3 break-words">
            <span class="font-mono text-gray-400 mr-1">{{ comp.num }}</span>{{ comp.title_zh || comp.title_en }}
          </h2>
          <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
            <div v-for="(s, i) in comp.segments" :key="i" class="px-4 py-3 grid gap-x-6 gap-y-2" :class="gridCls">
              <div class="text-[11px] font-mono text-gray-400 tabular-nums md:col-span-full -mb-1">{{ s.ref }}</div>
              <div v-if="shown.orig" class="text-[13px] text-gray-700 leading-relaxed whitespace-pre-line break-words font-serif italic">{{ s.orig }}</div>
              <div v-if="shown.en" class="text-[13px] text-gray-700 leading-relaxed break-words">{{ s.en }}</div>
              <div v-if="shown.zh && hasZh" class="text-[14px] text-gray-900 leading-relaxed break-words">{{ s.zh }}</div>
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { findText } from '~/data/near-east'
import { loadText } from '~/data/near-east/sources'
import type { NeSourceDoc } from '~/data/near-east/sources'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const slug = computed(() => String(route.params.slug))
const loc = computed(() => findText(slug.value))

useHead(() => ({ title: loc.value ? `${loc.value.text.title_zh} — 古近東大藏經` : '古近東大藏經' }))

const doc = ref<NeSourceDoc | null>(null)
const loading = ref(true)

const COL_LABEL = { orig: '原文轉寫', en: '英譯', zh: '繁體中文' } as const
const shown = reactive({ orig: true, en: true, zh: true })

const hasZh = computed(() => !!doc.value?.compositions.some(c => c.segments.some(s => s.zh)))
const availableCols = computed(() => (hasZh.value ? ['orig', 'en', 'zh'] : ['orig', 'en']) as Array<keyof typeof COL_LABEL>)
const segCount = computed(() => doc.value?.compositions.reduce((n, c) => n + c.segments.length, 0) ?? 0)
const gridCls = computed(() => {
  const n = (shown.orig ? 1 : 0) + (shown.en ? 1 : 0) + (shown.zh && hasZh.value ? 1 : 0)
  return n >= 3 ? 'grid-cols-1 md:grid-cols-3' : n === 2 ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1'
})

watch(slug, async (s) => {
  loading.value = true
  doc.value = await loadText(s)
  loading.value = false
}, { immediate: true })
</script>
