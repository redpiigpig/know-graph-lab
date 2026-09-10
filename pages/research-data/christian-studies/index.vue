<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="基督教研究" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">基督教研究</h1>
        <p class="text-gray-500 text-sm leading-relaxed">
          基督宗教研究的四個材料區。前兩區是電子圖書館既有的館藏，後兩區是為
          <NuxtLink to="/works/christian-genealogy" class="text-sky-700 hover:underline">《基督宗教譜系學》</NuxtLink>
          第六章另外蒐集的一手文獻語料。
        </p>
        <p class="mt-2 text-xs text-gray-400 leading-relaxed">
          ⚠️ 語料區只存純文字、不進電子圖書館：那批是拿來檢索與引用的會議紀錄與研究報告，
          數量大且多數不是「書」。檢索走 <code>scripts/genealogy_research.py</code>。
        </p>
      </div>

      <div v-if="pending" class="text-sm text-gray-400 py-10 text-center">載入中⋯</div>
      <div v-else-if="!areas.length" class="text-sm text-gray-400 py-10 text-center">尚無資料</div>

      <div v-else class="space-y-5">
        <section v-for="a in areas" :key="a.slug" class="bg-white rounded-2xl border border-gray-100 p-6">
          <div class="flex items-start gap-4 mb-3">
            <div class="text-2xl leading-none mt-0.5">{{ a.icon }}</div>
            <div class="flex-1 min-w-0">
              <div class="flex items-baseline gap-2 flex-wrap">
                <h2 class="text-lg font-bold text-gray-900">{{ a.name }}</h2>
                <span class="text-xs px-2 py-0.5 rounded-full"
                      :class="a.source === 'library' ? 'bg-amber-50 text-amber-700' : 'bg-sky-50 text-sky-700'">
                  {{ a.source === 'library' ? '電子圖書館館藏' : '一手文獻語料' }}
                </span>
              </div>
              <p class="text-sm text-gray-500 leading-relaxed mt-1 break-words">{{ a.desc }}</p>
            </div>
            <div class="text-right flex-shrink-0 text-xs text-gray-400 leading-relaxed">
              <template v-if="a.source === 'library'">
                <div class="text-base font-semibold text-gray-700">{{ a.books.toLocaleString() }} 本</div>
                <div>{{ a.chunks.toLocaleString() }} 段</div>
              </template>
              <template v-else>
                <div class="text-base font-semibold text-gray-700">{{ (a.docs || 0).toLocaleString() }} 份</div>
                <div>{{ ((a.chars || 0) / 10000).toFixed(0) }} 萬字</div>
              </template>
            </div>
          </div>

          <!-- 館藏區：分類明細 -->
          <div v-if="a.source === 'library' && a.parts?.length" class="mt-4 flex flex-wrap gap-2">
            <span v-for="p in a.parts" :key="p.name"
                  class="text-xs px-2.5 py-1 rounded-lg bg-gray-50 text-gray-600 border border-gray-100">
              {{ p.name }}
              <span class="text-gray-400">{{ p.books }} 本</span>
            </span>
          </div>

          <!-- 語料區：份量最大的幾份 -->
          <div v-else-if="a.items?.length" class="mt-4">
            <button @click="open = open === a.slug ? '' : a.slug"
                    class="text-xs text-sky-700 hover:underline">
              {{ open === a.slug ? '收合' : `列出份量最大的 ${a.items.length} 份` }}
            </button>
            <ul v-if="open === a.slug" class="mt-3 space-y-1.5">
              <li v-for="it in a.items" :key="it.id" class="text-xs text-gray-600 flex gap-3">
                <span class="text-gray-400 flex-shrink-0 w-16 text-right">{{ Math.round(it.chars / 1000) }}k</span>
                <span class="break-words">{{ it.title }}</span>
              </li>
            </ul>
          </div>

          <p v-if="a.note" class="mt-3 text-xs text-amber-600">{{ a.note }}</p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Part { name: string; books: number; chunks: number }
interface Item { id: string; title: string; chars: number }
interface Area {
  slug: string; name: string; icon: string; desc: string
  source: 'library' | 'corpus'
  books?: number; chunks?: number; parts?: Part[]
  docs?: number; chars?: number; items?: Item[]; note?: string
}

const areas = ref<Area[]>([])
const pending = ref(true)
const open = ref('')

onMounted(async () => {
  try {
    const d = await $fetch<{ areas: Area[] }>(
      '/content/research-data/christian-studies/index.json', { responseType: 'json' })
    areas.value = d?.areas ?? []
  } catch { areas.value = [] } finally { pending.value = false }
})

useHead({ title: '基督教研究 — Know Graph Lab' })
</script>
