<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/scripture-canon" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">信條對照</span>
      <span class="text-xs text-gray-400 ml-1">{{ ALL_CREEDS.length }} 份</span>
    </nav>

    <div class="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">⛪ 信條對照</h1>
        <p class="text-sm text-gray-500">大公會議信條 / 宗派信條 / 普世合一對話文件 — 多語言版本平行列表</p>
      </div>

      <!-- Filter bar -->
      <div class="flex flex-wrap items-center gap-2 mb-6">
        <button
          @click="activeCategory = null"
          class="text-xs px-3 py-1.5 rounded-full border transition"
          :class="activeCategory === null
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >全部 ({{ ALL_CREEDS.length }})</button>
        <button
          v-for="cat in categories"
          :key="cat.key"
          @click="activeCategory = cat.key"
          class="text-xs px-3 py-1.5 rounded-full border transition"
          :class="activeCategory === cat.key
            ? 'bg-stone-900 text-white border-stone-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
        >{{ cat.label }} ({{ cat.count }})</button>
      </div>

      <!-- Grouped list -->
      <div v-for="group in groupedCreeds" :key="group.key" class="mb-8">
        <h2 class="text-sm font-semibold text-gray-700 mb-3 border-b border-gray-200 pb-1">
          {{ group.label }}
          <span class="text-xs text-gray-400 font-normal">{{ group.items.length }} 份</span>
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <NuxtLink
            v-for="creed in group.items"
            :key="creed.slug"
            :to="`/creeds/${creed.slug}`"
            class="block bg-white border border-gray-200 rounded-lg p-4 hover:border-stone-300 hover:shadow-sm transition"
          >
            <div class="flex items-baseline gap-2 mb-1">
              <span v-if="creed.councilNo" class="text-xs font-mono text-stone-500">#{{ creed.councilNo }}</span>
              <span class="text-xs text-gray-400">{{ creed.year }}</span>
            </div>
            <div class="font-semibold text-gray-900 text-sm">{{ creed.nameZh }}</div>
            <div class="text-xs text-gray-500 mt-0.5">{{ creed.nameEn }}</div>
            <div class="text-xs text-gray-600 mt-2 line-clamp-2 leading-relaxed">{{ creed.topic }}</div>
            <div class="flex flex-wrap gap-1 mt-2">
              <span
                v-for="t in creed.acceptedBy.slice(0, 4)"
                :key="t"
                class="text-[10px] px-1.5 py-0.5 rounded bg-stone-50 text-stone-600 border border-stone-100"
              >{{ TRADITION_LABEL_ZH[t] }}</span>
              <span
                v-if="creed.acceptedBy.length > 4"
                class="text-[10px] px-1.5 py-0.5 rounded bg-gray-50 text-gray-500"
              >+{{ creed.acceptedBy.length - 4 }}</span>
            </div>
          </NuxtLink>
        </div>
      </div>

      <div v-if="filteredCreeds.length === 0" class="text-center text-gray-400 py-12 text-sm">
        此分類目前尚無資料
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ALL_CREEDS, CATEGORY_LABEL_ZH, TRADITION_LABEL_ZH, type CreedCategory } from '~/data/creeds'

definePageMeta({ middleware: 'auth' })
useHead({ title: '信條對照 — Know Graph Lab' })

const activeCategory = ref<CreedCategory | null>(null)

const categories = computed(() =>
  (Object.keys(CATEGORY_LABEL_ZH) as CreedCategory[]).map(key => ({
    key,
    label: CATEGORY_LABEL_ZH[key],
    count: ALL_CREEDS.filter(c => c.category === key).length,
  })).filter(c => c.count > 0)
)

const filteredCreeds = computed(() =>
  activeCategory.value === null
    ? ALL_CREEDS
    : ALL_CREEDS.filter(c => c.category === activeCategory.value)
)

const groupedCreeds = computed(() => {
  const groups: { key: CreedCategory; label: string; items: typeof ALL_CREEDS }[] = []
  ;(Object.keys(CATEGORY_LABEL_ZH) as CreedCategory[]).forEach(key => {
    const items = filteredCreeds.value.filter(c => c.category === key)
    if (items.length > 0) {
      groups.push({ key, label: CATEGORY_LABEL_ZH[key], items })
    }
  })
  return groups
})
</script>
