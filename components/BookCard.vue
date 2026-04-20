<template>
  <div class="flex items-start gap-3">
    <div class="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0 text-lg select-none">📚</div>
    <div class="flex-1 min-w-0">
      <h3 class="font-semibold text-gray-900 text-sm leading-tight mb-1 group-hover:text-blue-700 transition line-clamp-2">
        {{ book.title }}
      </h3>
      <p class="text-xs text-gray-500 truncate">{{ book.author }}</p>
      <div class="flex items-center gap-2 mt-1.5">
        <span class="text-xs text-blue-600 font-medium">{{ book.excerpt_count }} 筆摘文</span>
        <span v-if="book.book_categories?.name" class="text-xs text-gray-400 bg-gray-50 rounded px-1.5 py-0.5">
          {{ book.book_categories.name }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ book: any }>();
</script>
