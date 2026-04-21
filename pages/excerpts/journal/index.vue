<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <NuxtLink to="/excerpts" class="hover:text-amber-600 transition flex items-center gap-1.5">
              <img src="/logo_image.jpg" alt="logo" class="w-5 h-5 rounded object-cover" />
              <span>書摘庫</span>
            </NuxtLink>
            <span>›</span>
            <span class="font-semibold text-amber-700">期刊書摘</span>
          </div>
          <div class="flex items-center gap-2">
            <button
              class="text-xs px-3 py-1.5 rounded-lg bg-amber-600 text-white hover:bg-amber-500 transition"
              @click="showCreate = true"
            >+ 新增篇目</button>
            <button @click="handleLogout" class="text-gray-500 hover:text-red-600 transition text-sm">登出</button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex items-center gap-4 mb-8">
        <div class="w-14 h-14 bg-amber-100 rounded-2xl flex items-center justify-center text-3xl">📰</div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">期刊書摘</h1>
          <p class="text-sm text-gray-500 mt-0.5">期刊、學報、雜誌篇目與摘文（格式比照書摘圖書館）</p>
        </div>
      </div>

      <div class="relative mb-6">
        <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="q"
          type="text"
          placeholder="搜尋篇名、刊名或作者…"
          class="w-full pl-12 pr-10 py-3 bg-white border border-gray-200 rounded-xl shadow-sm focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none transition"
        />
        <button v-if="q" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" @click="q = ''">✕</button>
      </div>

      <p class="text-sm text-gray-500 mb-4">共 {{ filtered.length }} 篇</p>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <NuxtLink
          v-for="j in filtered"
          :key="j.id"
          :to="`/excerpts/journal/${j.id}`"
          class="group bg-white rounded-xl border border-gray-200 p-4 hover:border-amber-300 hover:shadow-md transition-all"
        >
          <p class="font-semibold text-gray-900 line-clamp-2 group-hover:text-amber-800">{{ j.title }}</p>
          <p class="text-xs text-gray-500 mt-1 line-clamp-1">{{ j.venue || "—" }} · {{ j.author || "佚名" }}</p>
          <p class="text-xs text-amber-700 mt-2">{{ j.excerpt_count ?? 0 }} 筆摘文</p>
        </NuxtLink>
      </div>
      <p v-if="!loading && filtered.length === 0" class="text-center py-12 text-gray-400">尚無篇目</p>
    </div>

    <div v-if="showCreate" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-md bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold text-gray-900 mb-3">新增期刊篇目</h3>
        <input v-model="form.title" class="w-full px-3 py-2 border rounded-lg text-sm mb-2" placeholder="篇名（必填）" />
        <input v-model="form.venue" class="w-full px-3 py-2 border rounded-lg text-sm mb-2" placeholder="刊名／學報名" />
        <input v-model="form.author" class="w-full px-3 py-2 border rounded-lg text-sm mb-2" placeholder="作者" />
        <input v-model="form.issue_label" class="w-full px-3 py-2 border rounded-lg text-sm mb-2" placeholder="期別（例：第2期）" />
        <input v-model.number="form.publish_year" type="number" class="w-full px-3 py-2 border rounded-lg text-sm mb-3" placeholder="年份" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showCreate = false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-amber-600 text-white rounded-lg" @click="createOne">建立</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
const supabase = useSupabaseClient();
const router = useRouter();

const loading = ref(true);
const items = ref<any[]>([]);
const q = ref("");
const showCreate = ref(false);
const form = ref({ title: "", venue: "", author: "", issue_label: "", publish_year: null as number | null });

const filtered = computed(() => {
  const s = q.value.trim().toLowerCase();
  if (!s) return items.value;
  return items.value.filter((j) =>
    [j.title, j.venue, j.author].some((x) => (x || "").toLowerCase().includes(s))
  );
});

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

async function load() {
  const token = await getToken(); if (!token) return;
  items.value = await $fetch<any[]>("/api/journal-articles", {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
  loading.value = false;
}

async function createOne() {
  if (!form.value.title.trim()) return;
  const token = await getToken(); if (!token) return;
  await $fetch("/api/journal-articles", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: {
      title: form.value.title.trim(),
      venue: form.value.venue.trim() || undefined,
      author: form.value.author.trim() || undefined,
      issue_label: form.value.issue_label.trim() || undefined,
      publish_year: form.value.publish_year || null,
    },
  }).catch(() => null);
  showCreate.value = false;
  form.value = { title: "", venue: "", author: "", issue_label: "", publish_year: null };
  await load();
}

async function handleLogout() {
  await supabase.auth.signOut();
  router.push("/login");
}

onMounted(load);
useHead({ title: "期刊書摘 — 書摘庫" });
</script>
