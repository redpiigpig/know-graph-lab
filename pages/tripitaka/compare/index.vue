<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="異譯對讀" :back="{ to: '/tripitaka', label: '佛教大藏經' }" :editable="false" />
    <main class="flex-1 px-4 sm:px-6 py-8">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-xl font-bold text-gray-900">異譯對讀</h1>
        <p class="mt-1 text-xs text-gray-500 leading-relaxed">
          同一部經的多個漢譯本，與梵、巴利、藏原典按義段並排——像聖經的多譯本對照。
          佛典沒有跨語言共通的「節」，義段由本站編訂，各格文字逐字取自原典。
        </p>
        <div v-for="f in families" :key="f.key" class="mt-6">
          <h2 class="text-sm font-semibold text-gray-700 mb-2">{{ f.label }}</h2>
          <div v-if="!f.items.length" class="text-xs text-gray-300">（尚無）</div>
          <NuxtLink
            v-for="s in f.items" :key="s.slug" :to="`/tripitaka/compare/${s.slug}`"
            class="block rounded-xl border border-gray-200 bg-white px-4 py-3 mb-2 hover:border-amber-300 transition"
          >
            <div class="text-sm font-medium text-gray-800">{{ s.title }}</div>
            <div class="text-[11px] text-gray-400 truncate">{{ s.versions }} 個本子・{{ s.works.join('、') }}</div>
          </NuxtLink>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '異譯對讀 — 佛教大藏經' })
interface Item { slug: string; title: string; family: string; works: string[]; versions: number }
const { data } = await useFetch<Item[]>('/content/tripitaka/compare/index.json', { server: false })
const FAM = [
  { key: 'sa', label: '梵本系' },
  { key: 'pi', label: '巴利系' },
  { key: 'bo', label: '藏譯系（梵本已佚）' },
]
const families = computed(() => FAM.map(f => ({ ...f, items: (data.value ?? []).filter(s => s.family === f.key) })))
</script>
