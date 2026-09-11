<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="吉福德講座" :back="{ to: '/research-data/contemporary-theology', label: '當代神學研究' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">吉福德講座歷屆名單</h1>
        <p class="text-gray-500 text-sm leading-relaxed">
          一八八八年起依吉福德勳爵遺囑，在亞伯丁、愛丁堡、格拉斯哥、聖安德魯斯四所蘇格蘭大學
          輪流舉辦的自然神學講座，多數講稿後來成書。把歷屆名單當一份書目來讀，
          等於得到一條橫跨一百四十年的神學與宗教哲學主軸。
        </p>
      </div>

      <div class="mb-5 flex flex-wrap gap-2 items-center">
        <input v-model="q" type="search" placeholder="搜講者或講題⋯"
               class="text-sm px-3 py-1.5 rounded-lg border border-gray-200 bg-white w-56" />
        <button v-for="u in unis" :key="u" @click="uni = uni === u ? '' : u"
                class="text-xs px-2.5 py-1 rounded-lg border"
                :class="uni === u ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-gray-600 border-gray-200'">
          {{ u }}
        </button>
        <span class="text-xs text-gray-400">{{ shown.length }} / {{ rows.length }} 場</span>
      </div>

      <div v-if="pending" class="text-sm text-gray-400 py-10 text-center">載入中⋯</div>

      <div v-else class="bg-white rounded-2xl border border-gray-100 overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-xs text-gray-400 border-b border-gray-100">
              <th class="text-left font-medium px-4 py-2.5 whitespace-nowrap">年份</th>
              <th class="text-left font-medium px-4 py-2.5 whitespace-nowrap">大學</th>
              <th class="text-left font-medium px-4 py-2.5">講者</th>
              <th class="text-left font-medium px-4 py-2.5">講題</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in shown" :key="i" class="border-b border-gray-50 last:border-0 align-top">
              <td class="px-4 py-2.5 text-gray-400 tabular-nums whitespace-nowrap">{{ r.year }}</td>
              <td class="px-4 py-2.5 text-gray-500 whitespace-nowrap">{{ r.university_zh }}</td>
              <td class="px-4 py-2.5 text-gray-800 font-medium break-words">{{ r.speaker }}</td>
              <td class="px-4 py-2.5 text-gray-600 break-words">
                <a v-if="r.url" :href="r.url" target="_blank" rel="noopener"
                   class="text-violet-700 hover:underline">{{ r.lecture }}</a>
                <span v-else>{{ r.lecture }}</span>
                <span v-if="r.isbn" class="text-gray-300 ml-2">{{ r.isbn }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p class="mt-6 text-xs text-gray-400 leading-relaxed">
        來源：維基百科英文版〈Gifford Lectures〉。⚠️ 官方網站 giffordlectures.org 有 Cloudflare，
        直接抓一律 403，因此走維基那份表格；重跑見 <code>scripts/gifford_lectures_fetch.py</code>。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Row {
  university: string; university_zh: string; year: string
  speaker: string; lecture: string; isbn: string | null; url: string | null
}

const rows = ref<Row[]>([])
const pending = ref(true)
const q = ref('')
const uni = ref('')
const unis = ['亞伯丁', '愛丁堡', '格拉斯哥', '聖安德魯斯']

const shown = computed(() => rows.value.filter(r => {
  if (uni.value && r.university_zh !== uni.value) return false
  const s = q.value.trim().toLowerCase()
  if (!s) return true
  return r.speaker.toLowerCase().includes(s) || (r.lecture || '').toLowerCase().includes(s)
}))

onMounted(async () => {
  try {
    const d = await $fetch<{ rows: Row[] }>(
      '/content/research-data/contemporary-theology/gifford.json', { responseType: 'json' })
    rows.value = d?.rows ?? []
  } catch { rows.value = [] } finally { pending.value = false }
})

useHead({ title: '吉福德講座 — Know Graph Lab' })
</script>
