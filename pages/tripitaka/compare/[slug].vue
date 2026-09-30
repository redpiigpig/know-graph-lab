<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader
      :title="data ? `${data.title}・異譯對讀` : '異譯對讀'"
      :back="{ to: '/tripitaka/compare', label: '異譯對讀' }"
      :editable="false"
    />

    <div v-if="pending" class="flex-1 flex items-center justify-center text-sm text-gray-400">載入中…</div>
    <div v-else-if="!data" class="flex-1 flex items-center justify-center text-sm text-gray-400">找不到這一組對讀</div>

    <main v-else class="flex-1 px-4 sm:px-6 py-6">
      <div class="max-w-7xl mx-auto">
        <h1 class="text-xl font-bold text-gray-900">{{ data.title }}</h1>
        <p v-if="data.auto" class="mt-2 text-[11px] text-amber-800 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 max-w-3xl leading-relaxed">
          自動對齊：義段由模型提出，腳本逐字切分並把關（格內文字保證是原文），但分段是否恰當未經人工校讀。
          標 <span class="font-semibold">?</span> 的義段是複核時被標為可能錯位的。
        </p>
        <p class="mt-1 text-xs text-gray-500 leading-relaxed max-w-3xl">{{ data.intro }}</p>
        <p class="mt-1 text-[11px] text-gray-400 leading-relaxed max-w-3xl">
          佛典沒有跨語言的「節」，此處以<strong>義段</strong>為對齊單位（本站編訂）。
          各格文字逐字取自原典，未增刪；某本無此段則留空。
        </p>

        <!-- 本子選擇（像聖經選譯本） -->
        <div class="sticky top-14 z-10 -mx-4 sm:-mx-6 px-4 sm:px-6 py-2 mt-4 bg-slate-50/95 backdrop-blur border-b border-gray-200">
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="v in data.versions" :key="v.id"
              class="px-2 py-1 text-[11px] rounded-lg border transition"
              :class="shown.includes(v.id)
                ? 'bg-amber-600 text-white border-amber-600'
                : 'bg-white text-gray-500 border-gray-200 hover:border-amber-300'"
              :title="v.who"
              @click="toggle(v.id)"
            >{{ v.label }}</button>
          </div>
        </div>

        <div class="mt-4 overflow-x-auto">
          <div class="cmp-wrap" :style="gridStyle">
            <!-- 欄頭 -->
            <div class="cmp-head pb-2 border-b border-gray-200">
              <div v-for="v in cols" :key="v.id" class="min-w-0">
                <div class="text-xs font-semibold text-gray-700 truncate">{{ v.label }}</div>
                <div class="text-[10px] text-gray-400 truncate">{{ v.who }}</div>
                <div v-if="v.reorder" class="text-[10px] text-amber-700" title="此本有義段的先後次第與他本不同，各格照原本次第取文">⇅ 段序依原本</div>
              </div>
            </div>

            <section v-for="(u, ui) in data.units" :key="u.id" :id="u.id" class="py-3 border-b border-gray-100 scroll-mt-28">
              <div class="text-[11px] text-indigo-700 mb-1.5">
                <span class="font-mono text-gray-300 mr-1">{{ ui + 1 }}</span>{{ u.label }}<span
                  v-if="u.doubt" class="ml-1 font-semibold text-amber-600" title="複核時被標為可能錯位">?</span>
              </div>
              <div class="cmp-grid">
                <div v-for="v in cols" :key="v.id" class="min-w-0">
                  <div class="md:hidden text-[10px] text-gray-400 mb-0.5">{{ v.label }}</div>
                  <p
                    v-if="data.cells[u.id]?.[v.id]"
                    class="leading-relaxed text-gray-800 break-words"
                    :class="v.lang === 'lzh' ? 'text-[15px] tracking-wide' : v.lang === 'bo' ? 'text-[16px]' : 'font-serif text-[14px]'"
                  >{{ data.cells[u.id][v.id] }}</p>
                  <p v-else class="text-gray-300 text-sm">—</p>
                </div>
              </div>
            </section>
          </div>
        </div>

        <p class="mt-6 text-[11px] text-gray-400 leading-relaxed">
          漢譯據 CBETA《大正藏》；梵本據 GRETIL；巴利據 SuttaCentral（Mahāsaṅgīti 本）；漢譯南傳據元亨寺版；藏譯與英譯據 84000 翻譯記憶（德格版，CC BY-NC-ND）。
          義段切分由 <code>scripts/tripitaka_compare.py</code> 產生，切完須與原文逐字相符才會發布。
        </p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
const route = useRoute()
const slug = computed(() => String(route.params.slug))

interface Ver { id: string; lang: string; label: string; who: string; reorder?: boolean }
interface Data {
  slug: string; title: string; family: string; intro: string
  auto?: boolean
  units: { id: string; label: string; doubt?: boolean }[]
  versions: Ver[]
  cells: Record<string, Record<string, string>>
}

const { data, pending } = await useFetch<Data>(() => `/content/tripitaka/compare/${slug.value}.json`, {
  server: false,
})
useHead(() => ({ title: `${data.value?.title ?? '異譯對讀'} — 佛教大藏經` }))

// 預設：原典在前、兩個最通行的漢譯在後，最多四欄（再多在窄螢幕上讀不動）
const KEY = computed(() => `tripitaka-compare:${slug.value}`)
const shown = ref<string[]>([])
watch(data, (d) => {
  if (!d) return
  let saved: string[] | null = null
  try { saved = JSON.parse(localStorage.getItem(KEY.value) || 'null') } catch { /* 私密視窗 */ }
  const ids = d.versions.map(v => v.id)
  const valid = saved?.filter(id => ids.includes(id))
  shown.value = valid?.length ? valid : ids.slice(0, 4)
}, { immediate: true })

function toggle(id: string) {
  const s = shown.value.includes(id)
    ? (shown.value.length > 1 ? shown.value.filter(x => x !== id) : shown.value)
    : [...shown.value, id]
  shown.value = s
  try { localStorage.setItem(KEY.value, JSON.stringify(s)) } catch { /* 存不了就算了 */ }
}

// 欄序照資料裡的順序，不照點選順序——原典永遠在左
const cols = computed(() => (data.value?.versions ?? []).filter(v => shown.value.includes(v.id)))
const gridStyle = computed(() => ({
  '--cols': `repeat(${cols.value.length}, minmax(0, 1fr))`,
  '--minw': `${cols.value.length * 200}px`,
}))
</script>

<style scoped>
/* 窄螢幕一本一本往下疊；寬螢幕才並排，欄太多時在框內橫捲而不是整頁橫捲 */
.cmp-grid { display: grid; gap: 0.75rem; grid-template-columns: minmax(0, 1fr); }
.cmp-head { display: none; gap: 0.75rem; }
@media (min-width: 768px) {
  .cmp-wrap { min-width: var(--minw); }
  .cmp-grid, .cmp-head { display: grid; grid-template-columns: var(--cols); }
}
</style>
