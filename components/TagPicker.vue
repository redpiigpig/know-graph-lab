<template>
  <div class="flex flex-wrap items-center gap-1.5">
    <!-- selected tag chips -->
    <span v-for="t in selectedTags" :key="t.id"
      class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs bg-blue-50 text-blue-700 border border-blue-200">
      <span>{{ t.name }}</span>
      <button v-if="!readonly" @click="remove(t.id)" type="button"
        class="hover:text-red-600 transition leading-none">×</button>
    </span>

    <!-- add button + popover -->
    <div v-if="!readonly" class="relative" ref="rootEl">
      <button @click="open = !open" type="button"
        class="px-2 py-0.5 rounded-md text-xs text-gray-500 border border-dashed border-gray-300 hover:border-blue-400 hover:text-blue-600 transition">
        + 標籤
      </button>

      <div v-if="open"
        class="absolute z-30 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg p-2 left-0">
        <input v-model="query" @keyup.enter="onEnter" type="text"
          placeholder="搜尋或新增 tag (按 Enter 新增)"
          class="w-full px-2 py-1.5 text-sm border border-gray-200 rounded mb-1 focus:outline-none focus:border-blue-500"
          ref="inputEl" />
        <div class="max-h-56 overflow-y-auto">
          <button v-for="t in suggestions" :key="t.id" @click="add(t)" type="button"
            :class="['w-full text-left px-2 py-1 text-xs rounded transition flex items-center justify-between',
              modelValue.includes(t.id) ? 'opacity-40 cursor-default'
                : 'hover:bg-blue-50 text-gray-700']">
            <span>{{ t.name }}</span>
            <span class="text-gray-400">{{ t.book_count + t.excerpt_count }}</span>
          </button>
          <p v-if="!suggestions.length && query.trim()" class="text-xs text-gray-400 px-2 py-1.5">
            沒有現成標籤 — 按 Enter 新增「{{ query.trim() }}」
          </p>
          <p v-if="!suggestions.length && !query.trim() && !allTags.length" class="text-xs text-gray-400 px-2 py-1.5">
            還沒任何標籤，輸入文字 + Enter 建立第一個
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Tag { id: string; name: string; color: string | null; book_count: number; excerpt_count: number }

const props = defineProps<{
  modelValue: string[];   // tag ids
  readonly?: boolean;
}>();
const emit = defineEmits<{
  (e: "update:modelValue", v: string[]): void;
}>();

const supabase = useSupabaseClient();
const router = useRouter();
async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

const allTags = ref<Tag[]>([]);
const open = ref(false);
const query = ref("");
const rootEl = ref<HTMLElement | null>(null);
const inputEl = ref<HTMLInputElement | null>(null);

const tagById = computed(() => {
  const m = new Map<string, Tag>();
  for (const t of allTags.value) m.set(t.id, t);
  return m;
});
const selectedTags = computed<Tag[]>(() =>
  props.modelValue.map(id => tagById.value.get(id)).filter(Boolean) as Tag[]
);
const suggestions = computed(() => {
  const q = query.value.trim().toLowerCase();
  let list = allTags.value;
  if (q) list = list.filter(t => t.name.toLowerCase().includes(q));
  return list.slice(0, 30);
});

async function loadTags() {
  const token = await getToken(); if (!token) return;
  allTags.value = await $fetch<Tag[]>("/api/tags", {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
}

function add(t: Tag) {
  if (props.modelValue.includes(t.id)) return;
  emit("update:modelValue", [...props.modelValue, t.id]);
}
function remove(id: string) {
  emit("update:modelValue", props.modelValue.filter(x => x !== id));
}

async function onEnter() {
  const name = query.value.trim();
  if (!name) return;
  // If a tag with the same name (case-insensitive) already exists, add it
  // instead of creating a duplicate.
  const existing = allTags.value.find(t => t.name.toLowerCase() === name.toLowerCase());
  if (existing) { add(existing); query.value = ""; return; }

  const token = await getToken(); if (!token) return;
  const created = await $fetch<Tag>("/api/tags", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: { name },
  }).catch(() => null);
  if (created) {
    // Server may have returned an existing row (idempotent). Either way,
    // make sure it's in our local list before adding.
    if (!allTags.value.find(t => t.id === created.id)) {
      allTags.value = [...allTags.value, { ...created, book_count: 0, excerpt_count: 0 }];
    }
    add(created);
    query.value = "";
  }
}

// Click-outside to close popover
function onDocClick(e: MouseEvent) {
  if (!open.value || !rootEl.value) return;
  if (!rootEl.value.contains(e.target as Node)) open.value = false;
}

watch(open, async (v) => {
  if (v) await nextTick(() => inputEl.value?.focus());
});

onMounted(() => {
  loadTags();
  document.addEventListener("mousedown", onDocClick);
});
onBeforeUnmount(() => {
  document.removeEventListener("mousedown", onDocClick);
});
</script>
