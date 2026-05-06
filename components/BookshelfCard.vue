<template>
  <NuxtLink
    :to="`/ebook/${item.ebook.id}`"
    class="block p-4 bg-white border border-stone-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition"
  >
    <div class="text-sm font-semibold text-stone-900 line-clamp-2 mb-1">{{ item.ebook.title }}</div>
    <div v-if="item.ebook.author" class="text-xs text-stone-500 mb-2">{{ item.ebook.author }}</div>
    <div class="flex items-center justify-between text-xs text-stone-400 gap-2">
      <span class="truncate">
        {{ item.ebook.category }}{{ item.ebook.subcategory ? ` · ${item.ebook.subcategory}` : '' }}
      </span>
      <span v-if="item.latest_bookmark_at" class="text-purple-600 flex-shrink-0">
        📅 {{ fmt(item.latest_bookmark_at) }}
      </span>
      <span v-else class="flex-shrink-0">{{ fmt(item.updated_at) }}</span>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{
  item: {
    status: "reading" | "read";
    updated_at: string;
    latest_bookmark_at: string | null;
    ebook: {
      id: string;
      title: string;
      author: string | null;
      category: string | null;
      subcategory: string | null;
    };
  };
}>();

function fmt(iso: string): string {
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}
</script>
