<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader :title="div?.label || '部類'" :back="{ to: '/tripitaka', label: '佛教大藏經' }" :editable="false" />

    <div class="flex-1 flex items-start justify-center px-6 py-10">
      <div class="w-full max-w-5xl">
        <div v-if="div" class="mb-6">
          <div class="flex items-baseline gap-3">
            <h1 class="text-2xl font-bold text-gray-900">{{ div.label }}</h1>
            <span v-if="div.label_alt" class="text-sm text-gray-400 italic">{{ div.label_alt }}</span>
            <span class="text-xs text-gray-400 font-mono">{{ div.vols }}</span>
          </div>
          <p class="text-sm text-gray-500 mt-1.5 max-w-3xl leading-relaxed">{{ div.desc }}</p>
        </div>

        <div class="mb-4 flex items-center gap-3 text-xs text-gray-400">
          <span>{{ total }} 部</span>
          <span v-if="charTotal">· {{ charTotal.toLocaleString('en-US') }} 字</span>
          <label class="ml-auto flex items-center gap-1.5 cursor-pointer">
            <input v-model="onlyParallel" type="checkbox" class="rounded border-gray-300" />
            <span>只看有原文對照的</span>
          </label>
        </div>

        <div v-if="pending" class="text-sm text-gray-400 py-12 text-center">載入中…</div>
        <p v-else-if="err" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl p-4">{{ err }}</p>

        <div v-else class="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <ul class="divide-y divide-gray-50">
            <li v-for="g in grouped" :key="g.series">
              <!-- 單冊本：直接一列 -->
              <NuxtLink
                v-if="g.items.length === 1"
                :to="`/tripitaka/w/${g.items[0].id}`"
                class="flex items-baseline gap-3 px-5 py-3 hover:bg-amber-50/50 transition"
              >
                <span class="font-mono text-[11px] text-gray-400 w-24 flex-shrink-0">{{ g.items[0].id }}</span>
                <div class="min-w-0 flex-1">
                  <div class="text-sm text-gray-900 truncate">{{ g.series }}</div>
                  <div class="text-xs text-gray-400 mt-0.5 truncate">
                    <span v-if="g.items[0].byline">{{ g.items[0].byline }}</span>
                    <span v-if="g.items[0].extent"> · {{ g.items[0].extent }}</span>
                    <span v-if="g.items[0].char_count"> · {{ g.items[0].char_count.toLocaleString('en-US') }} 字</span>
                  </div>
                </div>
                <ParallelChips :w="g.items[0]" />
              </NuxtLink>

              <!-- 多冊本（長部經典 ×3、大般若 ×3）：歸群後列冊 -->
              <div v-else class="px-5 py-3">
                <div class="flex items-baseline gap-3">
                  <span class="font-mono text-[11px] text-gray-400 w-24 flex-shrink-0">{{ g.items[0].id }}…</span>
                  <div class="min-w-0 flex-1">
                    <div class="text-sm text-gray-900 truncate">{{ g.series }}</div>
                    <div class="text-xs text-gray-400 mt-0.5 truncate">
                      <span v-if="g.items[0].byline">{{ g.items[0].byline }}</span>
                      <span> · 分 {{ g.items.length }} 冊</span>
                      <span> · {{ g.items.reduce((a, b) => a + (b.char_count || 0), 0).toLocaleString('en-US') }} 字</span>
                    </div>
                  </div>
                </div>
                <div class="mt-2 ml-24 flex flex-wrap gap-1.5">
                  <NuxtLink
                    v-for="it in g.items"
                    :key="it.id"
                    :to="`/tripitaka/w/${it.id}`"
                    class="px-2 py-1 text-[11px] rounded-lg border border-gray-200 text-gray-600 hover:border-amber-300 hover:bg-amber-50 transition"
                  >{{ volLabel(it) }}</NuxtLink>
                </div>
              </div>
            </li>
          </ul>
          <p v-if="!grouped.length" class="px-5 py-10 text-sm text-gray-400 text-center">這一部類沒有符合條件的經。</p>
        </div>

        <p v-if="loadedAll === false" class="mt-4 text-center">
          <button class="text-xs text-amber-700 hover:underline" @click="loadMore">載入更多（已顯示 {{ works.length }} / {{ total }}）</button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { divisionByKey } from '~/data/tripitaka/divisions'

definePageMeta({ middleware: 'auth' })
const route = useRoute()
const key = computed(() => String(route.params.division))
const div = computed(() => divisionByKey(key.value))
useHead(() => ({ title: `${div.value?.label ?? '部類'} — 佛教大藏經` }))

const supabase = useSupabaseClient()
const works = ref<any[]>([])
const total = ref(0)
const pending = ref(true)
const err = ref<string | null>(null)
const onlyParallel = ref(false)
const loadedAll = ref<boolean | null>(null)

const charTotal = computed(() => works.value.reduce((a, b) => a + (b.char_count || 0), 0))

const filtered = computed(() =>
  onlyParallel.value
    ? works.value.filter(w => (w.term_count || 0) > 0 || (w.equiv_count || 0) > 0)
    : works.value,
)

/** 南傳「長部經典(第1卷-第14卷)」×3 冊、大正藏 T0220a/b/c —— 同一部書歸一群。 */
const grouped = computed(() => {
  const out: { series: string; items: any[] }[] = []
  for (const w of filtered.value) {
    const s = w.series || w.title_zh
    const last = out[out.length - 1]
    if (last && last.series === s) last.items.push(w)
    else out.push({ series: s, items: [w] })
  }
  return out
})

function volLabel(w: any) {
  const m = String(w.title_zh).match(/[（(](第.*?)[)）]\s*$/)
  return m ? m[1] : (w.canon === 'N' ? `第 ${w.vol} 冊` : w.id)
}

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}

async function load(offset = 0) {
  try {
    const headers = await authHeaders()
    const r: any = await $fetch('/api/tripitaka/works', {
      headers, query: { division: key.value, limit: 400, offset },
    })
    works.value = offset ? [...works.value, ...r.works] : r.works
    total.value = r.total
    loadedAll.value = works.value.length >= r.total
  } catch (e: any) {
    err.value = e?.data?.message || e?.message || '載入失敗'
  } finally {
    pending.value = false
  }
}
function loadMore() { load(works.value.length) }
onMounted(() => load())
watch(key, () => { works.value = []; pending.value = true; load() })
</script>
