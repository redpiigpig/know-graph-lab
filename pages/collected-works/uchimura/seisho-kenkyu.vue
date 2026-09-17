<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader
      title="聖書之研究"
      :back="{ to: '/collected-works/uchimura', label: '內村鑑三' }"
      container-class="max-w-5xl"
      :editable="false"
    />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <!-- 標題與說明 -->
      <header class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900">《聖書之研究》分號目次</h1>
        <p class="text-sm text-gray-500 mt-1">
          內村鑑三個人傳道誌．1900 年 9 月創刊至 1930 年 4 月終刊，全 357 號
        </p>

        <div class="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div v-for="s in stats" :key="s.label" class="rounded-xl bg-white ring-1 ring-gray-200 px-3 py-2">
            <div class="text-lg font-bold text-gray-900 tabular-nums">{{ s.value }}</div>
            <div class="text-[11px] text-gray-500 break-words">{{ s.label }}</div>
          </div>
        </div>

        <div v-if="data" class="mt-4 rounded-xl bg-amber-50 ring-1 ring-amber-200 px-4 py-3">
          <p class="text-xs text-amber-900 leading-relaxed break-words">
            <span class="font-semibold">這份目次是反推出來的。</span>
            原刊沒有可取得的整套掃描，篇目取自{{ data.source }}。
            {{ data.caveat }}
          </p>
        </div>
      </header>

      <!-- 搜尋 -->
      <div class="mb-6 flex flex-col sm:flex-row gap-3">
        <input
          v-model="q"
          type="search"
          placeholder="搜尋篇名⋯⋯"
          class="flex-1 min-w-0 rounded-lg ring-1 ring-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
        />
        <label class="flex items-center gap-2 text-xs text-gray-600 whitespace-nowrap">
          <input v-model="onlyWithItems" type="checkbox" class="rounded" />
          只看有篇目的號
        </label>
      </div>

      <p v-if="q" class="text-xs text-gray-500 mb-4">
        找到 {{ matchCount }} 篇，分布在 {{ shownYears.length }} 個年份
      </p>

      <!-- 逐年 → 逐號 -->
      <section v-for="y in shownYears" :key="y.year" class="mb-8">
        <h2 class="text-sm font-semibold text-gray-700 mb-3 pb-1 border-b border-gray-200 flex items-baseline gap-2">
          <span class="tabular-nums">{{ y.year }}</span>
          <span class="text-xs font-normal text-gray-400">{{ y.issues.length }} 號</span>
        </h2>

        <div class="grid gap-3 sm:grid-cols-2">
          <article
            v-for="iss in y.issues"
            :key="iss.issue"
            class="rounded-xl bg-white ring-1 ring-gray-200 p-3"
            :class="{ 'opacity-60': !iss.count }"
          >
            <div class="flex items-baseline gap-2 mb-2">
              <span class="text-sm font-bold text-gray-900 tabular-nums">第 {{ iss.issue }} 號</span>
              <span class="text-[11px] font-mono text-gray-400">{{ iss.year }}.{{ String(iss.month).padStart(2, '0') }}</span>
              <span class="ml-auto text-[11px] text-gray-400">{{ iss.count }} 篇</span>
            </div>

            <p v-if="!iss.count" class="text-[11px] text-gray-400">
              全集未收，或年譜這一條沒被辨識出來
            </p>

            <ul v-else class="space-y-1">
              <li
                v-for="(it, i) in visibleItems(iss)"
                :key="i"
                class="flex items-start gap-2 text-xs"
              >
                <component
                  :is="linkFor(it) ? RowLink : 'span'"
                  v-bind="linkFor(it) ? { to: linkFor(it) } : {}"
                  class="flex-1 min-w-0 break-words"
                  :class="linkFor(it) ? 'text-sky-700 hover:underline' : 'text-gray-700'"
                >
                  <span class="line-clamp-2">{{ it.title }}</span>
                </component>
                <span
                  class="flex-shrink-0 text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500 tabular-nums"
                  :title="it.volName ? `第${it.vol}卷：${it.volName}` : `第${it.vol}卷`"
                >卷{{ it.vol }}</span>
                <span v-if="it.suspect" class="flex-shrink-0 text-amber-500" title="號數與年月對不上，可能是 OCR 咬壞">⚠</span>
              </li>
            </ul>
          </article>
        </div>
      </section>

      <p v-if="!shownYears.length" class="text-center text-sm text-gray-400 py-16">
        沒有符合的篇名。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

type Item = {
  title: string; vol: number; volName: string; ebookId: string
  year: number; month: number; dateEstimated: boolean; suspect: boolean
}
type Issue = { issue: number; year: number; month: number; count: number; items: Item[] }
type Data = {
  source: string; caveat: string; totalIssues: number; totalItems: number
  issuesWithItems: number; missingIssues: number[]; issues: Issue[]
}

const data = ref<Data | null>(null)
const liveChunks = ref<Record<string, number>>({})
const q = ref('')
const onlyWithItems = ref(false)
const RowLink = resolveComponent('NuxtLink')

onMounted(async () => {
  try {
    data.value = await $fetch<Data>('/content/collected-works/seisho-kenkyu.json')
  } catch {
    data.value = null
  }
  // 哪一卷已經轉錄出內容，篇名才連得過去；沒轉的就只是條目。
  try {
    const res = await $fetch<any>('/api/ebooks?collection=collected-works')
    const list = Array.isArray(res) ? res : res?.ebooks ?? []
    const m: Record<string, number> = {}
    for (const e of list) if (e?.id) m[e.id] = e.chunk_count ?? 0
    liveChunks.value = m
  } catch {
    /* 連不到就全部當成還沒轉錄 */
  }
})

const stats = computed(() => [
  { label: '全刊號數', value: data.value?.totalIssues ?? '—' },
  { label: '已還原篇目', value: data.value?.totalItems ?? '—' },
  { label: '有篇目的號', value: data.value ? `${data.value.issuesWithItems}/${data.value.totalIssues}` : '—' },
  { label: '原刊頁碼', value: '從缺' },
])

function matches(it: Item): boolean {
  const k = q.value.trim()
  return !k || it.title.includes(k)
}
const matchCount = computed(() => {
  if (!data.value) return 0
  return data.value.issues.reduce((n, i) => n + i.items.filter(matches).length, 0)
})
function visibleItems(iss: Issue): Item[] {
  return q.value.trim() ? iss.items.filter(matches) : iss.items
}
function linkFor(it: Item): string | undefined {
  return (liveChunks.value[it.ebookId] ?? 0) > 1
    ? `/collected-works/uchimura/${it.ebookId}`
    : undefined
}

const shownYears = computed(() => {
  if (!data.value) return [] as { year: number; issues: Issue[] }[]
  const keep = data.value.issues.filter((i) => {
    if (q.value.trim()) return i.items.some(matches)
    if (onlyWithItems.value) return i.count > 0
    return true
  })
  const byYear = new Map<number, Issue[]>()
  for (const i of keep) {
    if (!byYear.has(i.year)) byYear.set(i.year, [])
    byYear.get(i.year)!.push(i)
  }
  return [...byYear.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([year, issues]) => ({ year, issues: issues.sort((a, b) => a.issue - b.issue) }))
})

useHead({ title: '聖書之研究 分號目次 — 內村鑑三全集' })
</script>
