<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="多譯本對照" :back="{ to: '/tripitaka/compare', label: '多譯本對照目錄' }" :editable="false" />
    <div class="flex-1 flex items-center justify-center text-sm text-gray-400">
      {{ missing ? '找不到這一組對照' : '前往經文…' }}
    </div>
  </div>
</template>

<script setup lang="ts">
// 多譯本對照已併入經文閱讀器（/tripitaka/w/<經號>，聖經對照頁同款的多欄並排）。
// 舊網址照樣能用：轉到該組在閱讀器裡的位置——阿含的一經、長經的一品用錨點，整部的直接開經。
definePageMeta({ middleware: 'auth' })
const route = useRoute()
const missing = ref(false)

onMounted(async () => {
  try {
    const idx = await $fetch<any[]>('/content/tripitaka/compare/index.json')
    const c = idx.find(x => x.slug === String(route.params.slug))
    if (!c) { missing.value = true; return }
    const a = (c.anchors || []).find((x: any) => x.uid)
    const work = a?.work ?? c.works.find((w: string) => /^[TX]\d/.test(w)) ?? c.works[0]
    await navigateTo(`/tripitaka/w/${work}${a ? `#${a.uid}` : ''}`, { replace: true })
  } catch {
    missing.value = true
  }
})
</script>
