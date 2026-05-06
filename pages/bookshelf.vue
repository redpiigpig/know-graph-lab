<template>
  <div class="min-h-screen bg-stone-50 text-stone-900">
    <nav class="border-b border-stone-200 bg-white sticky top-0 z-40">
      <div class="px-4 h-14 flex items-center justify-between gap-4 max-w-6xl mx-auto">
        <div class="flex items-center gap-3">
          <NuxtLink to="/ebook" class="text-stone-500 hover:text-stone-900 text-sm transition">← 書庫</NuxtLink>
          <span class="text-stone-300">·</span>
          <h1 class="text-base font-semibold">📚 我的書櫃</h1>
        </div>
        <div class="text-xs text-stone-500">
          共 {{ items.length }} 本
        </div>
      </div>
    </nav>

    <main class="max-w-6xl mx-auto px-4 py-8">
      <div v-if="loading" class="text-stone-400 text-sm">載入中…</div>
      <div v-else-if="!items.length" class="text-center py-20 text-stone-400">
        書櫃是空的。打開任一本書，點工具列右上的「📚 加入書櫃」即可加入。
      </div>

      <template v-else>
        <section>
          <h2 class="text-sm font-semibold text-stone-700 mb-3 px-1 flex items-center gap-2">
            <span>📖 閱讀中</span>
            <span class="text-stone-400 font-normal">({{ reading.length }})</span>
          </h2>
          <div v-if="!reading.length" class="text-stone-400 text-sm px-1 py-4">目前沒有閱讀中的書。</div>
          <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <BookshelfCard v-for="i in reading" :key="i.ebook.id" :item="i" />
          </div>
        </section>

        <section class="mt-10">
          <h2 class="text-sm font-semibold text-stone-700 mb-3 px-1 flex items-center gap-2">
            <span>✅ 已讀</span>
            <span class="text-stone-400 font-normal">({{ read.length }})</span>
          </h2>
          <div v-if="!read.length" class="text-stone-400 text-sm px-1 py-4">尚未標記任何書為已讀。</div>
          <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <BookshelfCard v-for="i in read" :key="i.ebook.id" :item="i" />
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

interface BookshelfItem {
  status: "reading" | "read";
  updated_at: string;
  latest_bookmark_at: string | null;
  ebook: {
    id: string;
    title: string;
    author: string | null;
    category: string | null;
    subcategory: string | null;
    total_pages: number | null;
    chunk_count: number | null;
    file_type: string;
  };
}

const supabase = useSupabaseClient();
const router = useRouter();

const items = ref<BookshelfItem[]>([]);
const loading = ref(true);

const reading = computed(() => items.value.filter(i => i.status === "reading"));
const read = computed(() => items.value.filter(i => i.status === "read"));

async function load() {
  loading.value = true;
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return; }
  items.value = await $fetch<BookshelfItem[]>("/api/me/bookshelf", {
    headers: { Authorization: `Bearer ${session.access_token}` },
  }).catch(() => []);
  loading.value = false;
}

onMounted(load);
useHead({ title: "我的書櫃" });
</script>
