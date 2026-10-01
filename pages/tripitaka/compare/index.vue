<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="多譯本對照目錄" :back="{ to: '/tripitaka', label: '佛教大藏經' }" :editable="false" />
    <main class="flex-1 px-4 sm:px-6 py-8">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-xl font-bold text-gray-900">多譯本對照目錄</h1>
        <p class="mt-1 text-xs text-gray-500 leading-relaxed">
          下列經文在閱讀器裡可以多欄並排（同一部經的多個漢譯本，與梵、巴利、藏原典），點進去即是該經的閱讀頁。
          佛典沒有跨語言共通的「節」，義段由本站編訂，各格文字逐字取自原典。
          <span class="text-amber-700">「自動」</span>表示義段由模型提出、腳本逐字切分把關，未經人工校讀。
        </p>

        <div class="mt-4 flex gap-2">
          <input v-model="q" type="search" placeholder="搜尋經名、經號（如 SN 56、雜阿含、心經）"
                 class="flex-1 min-w-0 px-3 py-2 text-sm rounded-lg border border-gray-200 bg-white focus:outline-none focus:border-amber-400" />
          <label class="flex items-center gap-1 text-xs text-gray-500 whitespace-nowrap">
            <input v-model="manualOnly" type="checkbox" /> 只看人工
          </label>
        </div>

        <div v-for="f in families" :key="f.key" class="mt-6">
          <h2 class="text-sm font-semibold text-gray-700 mb-2">{{ f.label }}
            <span class="font-normal text-gray-400">{{ f.items.length }} 組</span></h2>
          <div v-if="!f.items.length" class="text-xs text-gray-300">（無）</div>
          <NuxtLink
            v-for="s in f.items.slice(0, f.limit)" :key="s.slug" :to="`/tripitaka/compare/${s.slug}`"
            class="block rounded-xl border border-gray-200 bg-white px-4 py-2.5 mb-2 hover:border-amber-300 transition"
          >
            <div class="flex items-center gap-2 min-w-0">
              <span class="text-sm font-medium text-gray-800 truncate">{{ s.title }}</span>
              <span v-if="s.auto" class="flex-shrink-0 px-1.5 text-[10px] rounded bg-amber-50 text-amber-700 border border-amber-200">自動</span>
              <span v-else class="flex-shrink-0 px-1.5 text-[10px] rounded bg-emerald-50 text-emerald-700 border border-emerald-200">人工</span>
            </div>
            <div class="text-[11px] text-gray-400 truncate">{{ s.versions }} 本・{{ (s.labels || []).join('、') }}</div>
          </NuxtLink>
          <button v-if="f.items.length > f.limit" class="text-xs text-amber-700 hover:underline"
                  @click="more[f.key] = (more[f.key] || 30) + 100">再顯示 {{ Math.min(100, f.items.length - f.limit) }} 組</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: "多譯本對照目錄 — 佛教大藏經" })
interface Item { slug: string; title: string; family: string; auto?: boolean; works: string[]; versions: number; labels?: string[] }
const { data } = await useFetch<Item[]>('/content/tripitaka/compare/index.json', { server: false })
const q = ref('')
const manualOnly = ref(false)
const more = reactive<Record<string, number>>({})
const FAM = [
  { key: 'sa', label: '梵本系' },
  { key: 'pi', label: '巴利系' },
  { key: 'bo', label: '藏譯系' },
]
const families = computed(() => {
  const k = q.value.trim().toLowerCase().replace(/\s+/g, '')
  const hit = (s: Item) => !k || [s.title, s.slug, ...(s.labels || []), ...s.works]
    .some(t => String(t).toLowerCase().replace(/\s+/g, '').includes(k))
  return FAM.map(f => {
    const items = (data.value ?? [])
      .filter(s => s.family === f.key && hit(s) && (!manualOnly.value || !s.auto))
      .sort((a, b) => Number(!!a.auto) - Number(!!b.auto) || a.slug.localeCompare(b.slug, undefined, { numeric: true }))
    return { ...f, items, limit: more[f.key] || 30 }
  })
})
</script>
