<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader title="學術活動紀錄" :back="{ to: '/', label: '返回主頁' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-12">
      <div class="mb-10">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">學術活動紀錄</h1>
        <p class="text-sm text-gray-500">張辰瑋 — 學位論文、期刊／研討會論文、社論、演講</p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink to="/cv" class="project-card border-amber-100 hover:border-amber-300 hover:shadow-amber-100">
          <div class="project-icon bg-amber-50 text-amber-600">📋</div>
          <div>
            <h2 class="project-title">學術履歷</h2>
            <p class="project-desc">學歷、學會職務、獎項、研究計畫等個人學術簡歷</p>
            <p class="text-xs text-amber-500 mt-2">Academic CV</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/writing/degrees" class="project-card border-purple-100 hover:border-purple-300 hover:shadow-purple-100">
          <div class="project-icon bg-purple-50 text-purple-600">🎓</div>
          <div>
            <h2 class="project-title">學位論文</h2>
            <p class="project-desc">博士研究計畫、碩士論文與學士論文線上閱讀</p>
            <p class="text-xs text-purple-500 mt-2">博士計畫 · 碩士 · 學士</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/papers?type=journal" class="project-card border-teal-100 hover:border-teal-300 hover:shadow-teal-100">
          <div class="project-icon bg-teal-50 text-teal-600">📄</div>
          <div>
            <h2 class="project-title">期刊論文</h2>
            <p class="project-desc">學術期刊投稿與發表紀錄</p>
            <p class="text-xs text-teal-500 mt-2">3 篇期刊論文</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/papers?type=conference" class="project-card border-indigo-100 hover:border-indigo-300 hover:shadow-indigo-100">
          <div class="project-icon bg-indigo-50 text-indigo-600">🗂️</div>
          <div>
            <h2 class="project-title">研討會論文</h2>
            <p class="project-desc">國內外學術研討會發表論文紀錄</p>
            <p class="text-xs text-indigo-500 mt-2">11 篇會議論文</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/papers?type=editorial" class="project-card border-orange-100 hover:border-orange-300 hover:shadow-orange-100">
          <div class="project-icon bg-orange-50 text-orange-600">📰</div>
          <div>
            <h2 class="project-title">報紙社論</h2>
            <p class="project-desc">報紙專欄、社論與短評</p>
            <p class="text-xs text-orange-500 mt-2">3 篇台灣教會公報</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/speech" class="project-card border-rose-100 hover:border-rose-300 hover:shadow-rose-100">
          <div class="project-icon bg-rose-50 text-rose-600">🎤</div>
          <div>
            <h2 class="project-title">演講活動</h2>
            <p class="project-desc">受邀演講、公開講座、講課與專題分享</p>
            <p class="text-xs text-rose-500 mt-2">{{ talksCount }} 場演講</p>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSpeechStore } from '~/stores/speech'

useHead({ title: '學術活動紀錄 — Know Graph Lab' })

const speechStore = useSpeechStore()
const talksCount = computed(() => speechStore.talks.length)
</script>

<style scoped>
.project-card {
  @apply flex items-start gap-4 p-6 rounded-2xl bg-white border-2 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer no-underline;
}
.project-icon {
  @apply w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0;
}
.project-title {
  @apply text-sm font-semibold text-gray-900 mb-1;
}
.project-desc {
  @apply text-xs text-gray-500 leading-relaxed;
}
</style>
