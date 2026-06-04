<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 sticky top-0">
      <NuxtLink :to="`/works/${slug}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">{{ monthLabel }}</span>
      <span v-if="monthDays.length" class="text-xs text-gray-400">{{ monthDays.length }} 天 · {{ monthTurns }} 則</span>
    </nav>

    <div class="flex-1 max-w-4xl w-full mx-auto px-6 py-10">
      <div v-if="pending" class="text-center text-gray-400 py-16 text-sm">載入中…</div>
      <div v-else-if="!user" class="text-center text-gray-400 py-24 text-sm">
        <div class="text-3xl mb-3">🔒</div>
        此為私人對話，請先登入後查閱。
      </div>
      <div v-else-if="monthDays.length === 0" class="text-center text-gray-400 py-24 text-sm">這個月沒有對話。</div>

      <template v-else>
        <div class="mb-6">
          <h1 class="text-2xl font-bold text-gray-900">{{ monthLabel }}</h1>
          <p class="text-sm text-gray-500 mt-0.5">選一天查閱當天的對話</p>
        </div>
        <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2.5">
          <NuxtLink v-for="d in monthDays" :key="d.day_date"
            :to="`/works/${slug}/day/${d.day_date}`"
            class="no-underline flex flex-col items-center justify-center py-4 rounded-xl bg-white border border-gray-200 hover:border-violet-400 hover:shadow-sm transition">
            <div class="text-xl font-bold text-violet-600 leading-none">{{ dayNum(d.day_date) }}</div>
            <div class="text-[10px] text-gray-400 mt-1">{{ d.weekday?.replace('星期', '週') }}</div>
            <div class="text-[10px] text-gray-400 mt-0.5">{{ d.n_turns }} 則</div>
          </NuxtLink>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const supabase = useSupabaseClient()
const user = useSupabaseUser()
const slug = computed(() => String(route.params.slug))
const ym = computed(() => String(route.params.ym))   // e.g. 2026-01

interface DialogueDay { day_date: string; weekday: string; day_title: string; n_turns: number }

const days = ref<DialogueDay[]>([])
const pending = ref(true)

const MONTH_ZH = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
const monthLabel = computed(() => {
  const [y, m] = ym.value.split('-')
  return m ? `${y}年${MONTH_ZH[Number(m) - 1]}` : ym.value
})
const monthDays = computed(() => days.value.filter(d => d.day_date.startsWith(ym.value + '-')))
const monthTurns = computed(() => monthDays.value.reduce((s, d) => s + (d.n_turns || 0), 0))
function dayNum(date: string) { return Number(date.split('-')[2]) }

useHead(() => ({ title: `${monthLabel.value} — 與克里希那對話` }))

async function load() {
  pending.value = true
  try {
    let token = ''
    if (user.value) {
      const { data: { session } } = await supabase.auth.getSession()
      token = session?.access_token ?? ''
    }
    const res = await $fetch<{ days: DialogueDay[] }>('/api/works/dialogue-days', {
      query: { slug: slug.value },
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    days.value = res.days ?? []
  } catch { days.value = [] } finally { pending.value = false }
}
onMounted(load)
watch(() => user.value, load)
</script>
