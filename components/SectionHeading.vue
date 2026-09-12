<template>
  <div class="mb-3">
    <h2 class="flex items-baseline gap-2.5 text-lg font-bold text-gray-900">
      <span class="flex-shrink-0 text-[11px] font-mono text-red-800 border border-red-800 rounded px-1.5 leading-relaxed">
        {{ num }}
      </span>
      <span class="break-words">{{ title }}</span>
    </h2>
    <p v-if="lede" class="mt-1 text-xs text-gray-500 leading-relaxed break-words">{{ lede }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  num: string
  title: string
  lede?: string
}>()
</script>
