<template>
  <div class="flex flex-col bg-stone-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 sticky top-0">
      <NuxtLink :to="`/works/${slug}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900 truncate">{{ day?.day_title || '每日對話' }}</span>
      <span v-if="day" class="text-xs text-gray-400 hidden md:inline">{{ day.n_turns }} 則</span>
      <div class="ml-auto flex items-center gap-2 text-xs">
        <button @click="go(prev)" :disabled="!prev"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-violet-400 disabled:opacity-30">‹ 前一天</button>
        <button @click="go(next)" :disabled="!next"
          class="px-2 py-1 rounded border border-gray-200 text-gray-600 hover:border-violet-400 disabled:opacity-30">後一天 ›</button>
      </div>
    </nav>

    <div class="flex-1 overflow-y-auto">
      <div class="max-w-3xl w-full mx-auto px-5 py-8">
        <div v-if="pending" class="text-center text-gray-400 py-16 text-sm">載入中…</div>
        <div v-else-if="unauth" class="text-center text-gray-400 py-24 text-sm">
          <div class="text-3xl mb-3">🔒</div>
          此為私人對話，請先登入後查閱。
        </div>
        <div v-else-if="error || !day" class="text-center text-red-400 py-24 text-sm">找不到這一天的對話。</div>

        <article v-else class="dialogue-day" v-html="day.html"></article>

        <div v-if="day" class="mt-12 flex items-center justify-between border-t border-gray-100 pt-5">
          <button @click="go(prev)" :disabled="!prev"
            class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-violet-400 disabled:opacity-30">← 前一天</button>
          <NuxtLink :to="`/works/${slug}`" class="text-sm text-gray-400 hover:text-gray-700">回每日列表</NuxtLink>
          <button @click="go(next)" :disabled="!next"
            class="px-3 py-1.5 rounded border border-gray-200 text-sm text-gray-700 hover:border-violet-400 disabled:opacity-30">後一天 →</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const supabase = useSupabaseClient()
const user = useSupabaseUser()
const slug = computed(() => String(route.params.slug))
const date = computed(() => String(route.params.date))

interface Day { day_date: string; weekday: string; day_title: string; html: string; n_turns: number }

const day = ref<Day | null>(null)
const prev = ref<string | null>(null)
const next = ref<string | null>(null)
const pending = ref(true)
const error = ref(false)
const unauth = ref(false)

useHead(() => ({ title: day.value ? `${day.value.day_title} — 與克里希那對話` : '每日對話' }))

async function load() {
  pending.value = true; error.value = false; unauth.value = false
  try {
    let token = ''
    if (user.value) {
      const { data: { session } } = await supabase.auth.getSession()
      token = session?.access_token ?? ''
    }
    const res = await $fetch<{ day: Day; prev: string | null; next: string | null }>(
      `/api/works/dialogue-days/${date.value}`,
      { query: { slug: slug.value }, headers: token ? { Authorization: `Bearer ${token}` } : {} }
    )
    day.value = res.day; prev.value = res.prev; next.value = res.next
  } catch (err: any) {
    if (err?.statusCode === 401) unauth.value = true
    else error.value = true
  } finally {
    pending.value = false
  }
}

function go(d: string | null) {
  if (!d) return
  router.push(`/works/${slug.value}/day/${d}`)
  if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'instant' })
}

onMounted(load)
watch([date, () => user.value], load)
</script>

<style scoped>
.dialogue-day :deep(h1) { display: none; }
/* 日期標題（h3） */
.dialogue-day :deep(h3) {
  font-size: 1.15rem; font-weight: 700; color: #111827;
  margin: 0 0 1.1em; padding-bottom: 0.45em; border-bottom: 2px solid #ede9fe;
}
/* 主題小標（h4） */
.dialogue-day :deep(h4) {
  font-size: 0.8rem; font-weight: 600; color: #7c3aed; letter-spacing: 0.05em;
  margin: 1.8em 0 0.8em; padding-left: 0.6em; border-left: 3px solid #c4b5fd;
}
/* 段落：預設整段縮排兩字（接續發言的第二段以後） */
.dialogue-day :deep(p) {
  margin: 0 0 0.9em; line-height: 1.9; color: #374151; font-size: 15.5px;
  margin-left: 2em;
}
/* 講者起首那段：第一行頂格（接著講者名），折行縮排兩字 */
.dialogue-day :deep(p:has(strong.speaker)) {
  margin-left: 0; padding-left: 2em; text-indent: -2em;
}
.dialogue-day :deep(strong.speaker) { color: #6d28d9; font-weight: 700; }
/* 段內強調（原 markdown **）維持深色，不誤判成講者 */
.dialogue-day :deep(p strong:not(.speaker)) { color: #4b5563; font-weight: 600; }
</style>
