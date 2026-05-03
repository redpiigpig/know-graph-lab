<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/works" class="text-gray-400 hover:text-gray-700 transition text-sm">← 寫作計畫</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">千面上帝</span>
      </div>
    </nav>

    <!-- 封面 -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-5xl mx-auto px-6 py-10">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-100 text-amber-700">寫作計畫</span>
          <span class="text-xs text-gray-400">構思中</span>
        </div>
        <h1 class="text-xl font-bold text-gray-900 leading-snug mb-1">千面上帝</h1>
        <p class="text-sm text-gray-400 italic mb-4">The Many Faces of God: A History of Religion in World Perspective</p>
        <p class="text-sm text-gray-600 leading-relaxed max-w-2xl">
          探討世界各大宗教傳統中神明概念的多元面貌，橫跨印度教、佛教、基督宗教、伊斯蘭教、猶太教等傳統，梳理「上帝」或「神明」概念在不同文化與歷史脈絡中的演變。
        </p>
      </div>
    </div>

    <!-- 分頁 -->
    <div class="bg-white border-b border-gray-100 sticky top-14 z-30">
      <div class="max-w-5xl mx-auto px-6">
        <div class="flex">
          <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
            :class="['px-5 py-3.5 text-sm font-medium border-b-2 transition-colors', activeTab === tab.id ? 'border-amber-600 text-amber-700' : 'border-transparent text-gray-500 hover:text-gray-800']">
            {{ tab.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- 內容 -->
    <div class="max-w-5xl mx-auto px-6 py-8">

      <!-- 宗教史讀書會 -->
      <div v-if="activeTab === 'reading-club'">
        <div class="mb-6">
          <h2 class="text-base font-semibold text-gray-900">宗教史讀書會</h2>
          <p class="text-xs text-gray-500 mt-0.5">YouTube 讀書會影片逐字稿，共 {{ sessions.length }} 集</p>
        </div>

        <div v-if="loading" class="flex items-center justify-center h-32 text-gray-400 text-sm">載入中⋯</div>

        <div v-else-if="sessions.length === 0" class="flex flex-col items-center justify-center h-40 text-gray-400 text-sm gap-2">
          <span class="text-3xl">🎬</span>
          <span>逐字稿轉錄中，請稍後再來</span>
        </div>

        <div v-else class="grid gap-3 sm:grid-cols-2">
          <NuxtLink v-for="s in sessions" :key="s.id"
            :to="`/works/qiangmian/reading-club/${s.id}`"
            class="bg-white rounded-xl border border-gray-100 p-4 hover:border-amber-200 hover:shadow-sm transition-all no-underline">
            <div class="flex items-start gap-3">
              <div class="w-9 h-9 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center text-sm flex-shrink-0 font-bold">
                {{ s.episode }}
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-sm font-semibold text-gray-900 leading-snug mb-0.5">{{ s.title }}</h3>
                <p v-if="s.date" class="text-xs text-gray-400">{{ s.date }}</p>
                <p class="text-xs text-amber-500 mt-1.5">閱讀逐字稿 →</p>
              </div>
            </div>
          </NuxtLink>
        </div>
      </div>

      <!-- 書摘與構思 -->
      <div v-if="activeTab === 'notes'">
        <div class="bg-white rounded-2xl border border-gray-100 p-8 text-center text-gray-400 text-sm">
          <div class="text-3xl mb-3">📝</div>
          <p>書摘與章節構思功能開發中</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
useHead({ title: '千面上帝 — 寫作計畫 — Know Graph Lab' })

const activeTab = ref('reading-club')
const loading = ref(true)
const sessions = ref<{ id: string; episode: number; title: string; date: string | null }[]>([])

const tabs = [
  { id: 'reading-club', label: '宗教史讀書會' },
  { id: 'notes', label: '書摘與構思' },
]

onMounted(async () => {
  try {
    const data = await $fetch<{ sessions: typeof sessions.value }>('/api/works/qiangmian-readings')
    sessions.value = data.sessions ?? []
  } catch {
    sessions.value = []
  }
  loading.value = false
})
</script>
