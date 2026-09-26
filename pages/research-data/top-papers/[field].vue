<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader :title="data?.title || '最有影響力的研究'" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div v-if="pending" class="text-sm text-gray-400 py-10 text-center">載入中⋯</div>
      <div v-else-if="!data" class="text-sm text-gray-400 py-10 text-center">尚無資料</div>

      <template v-else>
        <div class="mb-8">
          <h1 class="text-2xl font-bold text-gray-900 mb-1">{{ data.icon }} {{ data.title }}</h1>
          <p class="text-gray-500 text-sm leading-relaxed break-words">{{ data.desc }}</p>
          <p v-if="data.method" class="mt-2 text-xs text-gray-400 leading-relaxed break-words">{{ data.method }}</p>
          <div class="mt-3 flex flex-wrap gap-1.5 text-xs">
            <span class="px-2 py-0.5 rounded bg-white border border-gray-200 text-gray-700">
              共 <span class="tabular-nums font-semibold">{{ data.total }}</span> 筆
            </span>
            <span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
              館內已有 <span class="tabular-nums">{{ data.in_library }}</span>
            </span>
            <span class="px-2 py-0.5 rounded bg-sky-50 text-sky-700">
              Crossref 已核對 <span class="tabular-nums">{{ data.verified }}</span>
            </span>
            <span v-for="(n, k) in data.langs" :key="k"
                  class="px-2 py-0.5 rounded bg-white border border-gray-100 text-gray-500">
              {{ langLabel(k) }} <span class="text-gray-400 tabular-nums">{{ n }}</span>
            </span>
          </div>
          <div v-if="data.related?.length" class="mt-3 flex flex-wrap gap-3 text-xs">
            <NuxtLink v-for="r in data.related" :key="r.to" :to="r.to" class="text-sky-700 hover:underline">{{ r.label }} →</NuxtLink>
          </div>
        </div>

        <div class="mb-5 flex flex-wrap gap-2">
          <button v-for="g in data.groups" :key="g.slug" @click="scrollTo(g.slug)"
                  class="text-xs px-3 py-1.5 rounded-full bg-white border border-gray-200 hover:border-gray-400 text-gray-700">
            {{ g.icon }} {{ g.name }} <span class="text-gray-400 tabular-nums">{{ g.count }}</span>
          </button>
          <input v-model="q" type="search" placeholder="篩作者／題名／主題…"
                 class="text-xs px-3 py-1.5 rounded-full border border-gray-200 bg-white min-w-[12rem] flex-1 max-w-xs" />
        </div>

        <div class="space-y-5">
          <section v-for="g in data.groups" :key="g.slug" :id="'g-' + g.slug" class="bg-white rounded-2xl border border-gray-100 p-6 scroll-mt-20">
            <div class="flex items-start gap-4 mb-3">
              <div class="text-2xl leading-none mt-0.5">{{ g.icon }}</div>
              <div class="flex-1 min-w-0">
                <h2 class="text-lg font-bold text-gray-900">{{ g.name }}</h2>
                <p class="text-sm text-gray-500 leading-relaxed mt-1 break-words">{{ g.desc }}</p>
              </div>
              <div class="text-right flex-shrink-0 text-xs text-gray-400 leading-relaxed">
                <div class="text-base font-semibold text-gray-700 tabular-nums">{{ g.count }} 筆</div>
                <div>館內 {{ g.in_library }}・核對 {{ g.verified }}</div>
              </div>
            </div>

            <div v-for="t in filteredThemes(g)" :key="t.name" class="mt-4">
              <h3 class="text-sm font-semibold text-gray-800 border-l-4 pl-2 mb-2" :class="borderClass">
                {{ t.name }} <span class="text-gray-400 font-normal tabular-nums">{{ t.items.length }}</span>
              </h3>
              <ol class="space-y-2.5">
                <li v-for="(b, i) in t.items" :key="i" class="text-xs text-gray-600 leading-relaxed">
                  <div class="flex items-baseline gap-2 flex-wrap">
                    <span class="text-gray-400 tabular-nums">{{ b.year }}</span>
                    <span class="font-semibold text-gray-800 break-words">{{ b.author_zh }}《{{ b.title_zh }}》</span>
                    <span class="px-1.5 rounded bg-gray-50 text-gray-500">{{ typeLabel(b.type) }}</span>
                    <span class="px-1.5 rounded" :class="b.in_library ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-50 text-gray-400'">
                      {{ b.in_library ? '館內已有' : '缺' }}
                    </span>
                    <a v-if="b.crossref?.doi" :href="'https://doi.org/' + b.crossref.doi" target="_blank" rel="noopener"
                       class="px-1.5 rounded bg-sky-50 text-sky-700 hover:underline">DOI</a>
                  </div>
                  <div class="text-gray-500 break-words">
                    {{ b.author }}, <em>{{ b.title }}</em>
                    <span v-if="b.venue">，{{ b.venue }}</span>
                    <span class="text-gray-400">（{{ langLabel(b.lang) }}）</span>
                  </div>
                  <div v-if="b.note" class="text-gray-700 break-words">{{ b.note }}</div>
                </li>
              </ol>
            </div>
          </section>
        </div>

        <p class="mt-8 text-xs text-gray-400">
          資料 <code>data/research-data/{{ data.field }}/</code>，重建 <code>scripts/top_papers_build.py {{ data.field }}</code>；
          產生於 {{ data.built_at?.slice(0, 10) }}。
        </p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Item {
  group: string; theme: string; author: string; author_zh: string; year: number
  title: string; title_zh: string; venue?: string; type: string; lang: string; note?: string
  in_library: boolean; crossref?: { doi?: string } | null
}
interface Theme { name: string; count: number; items: Item[] }
interface Group { slug: string; name: string; icon: string; desc: string; count: number; in_library: number; verified: number; themes: Theme[] }
interface Data {
  field: string; title: string; icon: string; color: string; desc: string; method?: string
  related?: { label: string; to: string }[]; total: number; verified: number; in_library: number
  langs: Record<string, number>; built_at?: string; groups: Group[]
}

const route = useRoute()
const field = computed(() => String(route.params.field))
const data = ref<Data | null>(null)
const pending = ref(true)
const q = ref('')

const LANGS: Record<string, string> = {
  en: '英', de: '德', fr: '法', la: '拉丁', he: '希伯來', nl: '荷', es: '西', pt: '葡', it: '義', ru: '俄', ja: '日', zh: '中',
}
const langLabel = (k: string) => LANGS[k] ?? k
const TYPES: Record<string, string> = { article: '論文', chapter: '專章', monograph: '專著' }
const typeLabel = (k: string) => TYPES[k] ?? k

// tailwind safelist 裡有的色才可用；沒有就退回 slate
const borderClass = computed(() => {
  const c = data.value?.color || 'slate'
  return ({ rose: 'border-rose-300', amber: 'border-amber-300', sky: 'border-sky-300', emerald: 'border-emerald-300', indigo: 'border-indigo-300' } as Record<string, string>)[c] || 'border-slate-300'
})

const filteredThemes = (g: Group) => {
  const s = q.value.trim().toLowerCase()
  if (!s) return g.themes
  return g.themes
    .map(t => ({ ...t, items: t.items.filter(b =>
      [b.author, b.author_zh, b.title, b.title_zh, b.note, t.name].some(x => (x || '').toLowerCase().includes(s))) }))
    .filter(t => t.items.length)
}
const scrollTo = (slug: string) => document.getElementById('g-' + slug)?.scrollIntoView({ behavior: 'smooth' })

onMounted(async () => {
  try {
    data.value = await $fetch<Data>(`/content/research-data/${field.value}/top-papers.json`, { responseType: 'json' })
  } catch { data.value = null }
  pending.value = false
})

useHead(() => ({ title: data.value ? `${data.value.title}｜論文資料整理` : '最有影響力的研究' }))
</script>
