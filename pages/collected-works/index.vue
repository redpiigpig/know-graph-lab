<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader title="全集" :back="{ to: '/', label: '返回主頁' }" container-class="max-w-5xl" :editable="false" />

    <div class="max-w-5xl mx-auto px-6 py-12">
      <!-- hero -->
      <div class="text-center mb-12">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">經典學者全集</h1>
        <p class="text-sm text-gray-500 max-w-2xl mx-auto leading-relaxed">
          收錄宗教學、深層心理學等領域奠基學者的全集，每位學者一份學術小傳、生平年表與按年編排的完整著作目錄；
          各部著作以原文‧（譯本）‧繁中多欄逐段對照閱讀。
        </p>
      </div>

      <!-- 作家卡片 -->
      <div class="grid gap-5 sm:grid-cols-2">
        <NuxtLink
          v-for="a in authors"
          :key="a.slug"
          :to="`/collected-works/${a.slug}`"
          class="author-card no-underline"
          :class="`border-${a.color}-100 hover:border-${a.color}-300 hover:shadow-${a.color}-100`"
        >
          <img
            :src="a.portraitUrl"
            :alt="a.name"
            class="w-20 h-20 rounded-xl object-cover object-top flex-shrink-0 bg-gray-100 ring-1 ring-gray-200"
            loading="lazy"
          />
          <div class="flex-1 min-w-0">
            <div class="flex items-baseline gap-2 flex-wrap">
              <h2 class="text-base font-bold text-gray-900">{{ a.name }}</h2>
              <span class="text-xs text-gray-400 font-mono">{{ a.lifespan }}</span>
            </div>
            <p v-if="a.nameEn" class="text-xs text-gray-400 italic mb-1">{{ a.nameEn }}</p>
            <p class="text-xs text-gray-600 leading-relaxed line-clamp-2">{{ a.discipline }}</p>
            <div class="mt-2 flex items-center gap-1.5 flex-wrap">
              <span
                v-for="f in a.fields.slice(0, 4)"
                :key="f"
                class="text-[11px] px-1.5 py-0.5 rounded-full"
                :class="`bg-${a.color}-50 text-${a.color}-700`"
              >{{ f }}</span>
            </div>
            <div class="mt-2 text-[11px] text-gray-400">
              {{ progress(a).done }}／{{ progress(a).total }} 卷已轉錄
            </div>
          </div>
        </NuxtLink>
      </div>

      <p class="mt-12 text-center text-xs text-gray-400">
        全集原檔皆取自公有領域來源；繁體中譯與多欄對照為本站自製。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CwAuthor } from '~/stores/collectedWorks'

definePageMeta({ middleware: 'auth' })
useHead({ title: '全集 — Know Graph Lab' })

const store = useCollectedWorksStore()
const authors = computed(() => store.authors)

function progress(a: CwAuthor) {
  return {
    done: a.works.filter((w) => w.status === 'done').length,
    total: a.works.length,
  }
}
</script>

<style scoped>
.author-card {
  @apply flex items-start gap-4 p-5 rounded-2xl bg-white border-2 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer;
}
</style>

<!-- Dynamic Tailwind colors (bg-${color}-*, text-${color}-*, border-${color}-*) are safelisted in tailwind.config.ts -->
