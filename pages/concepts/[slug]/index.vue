<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center gap-2 text-sm text-gray-500 truncate">
            <NuxtLink to="/" class="hover:text-blue-600 transition flex items-center gap-1.5">
              <img src="/logo_image.jpg" alt="logo" class="w-5 h-5 rounded object-cover" />
              <span>知識圖工作室</span>
            </NuxtLink>
            <span>›</span>
            <NuxtLink to="/concepts" class="hover:text-cyan-600 transition">概念筆記</NuxtLink>
            <span>›</span>
            <span class="font-medium text-gray-900 truncate">{{ concept?.name ?? '載入中…' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <button v-if="!editing" class="px-3 py-1.5 text-xs rounded-lg border border-cyan-300 text-cyan-700 hover:bg-cyan-50"
              @click="startEdit">編輯</button>
            <button v-else class="px-3 py-1.5 text-xs rounded-lg bg-cyan-600 text-white hover:bg-cyan-500"
              :disabled="saving" @click="save">{{ saving ? '儲存中…' : '儲存' }}</button>
            <button v-if="editing" class="px-3 py-1.5 text-xs rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-100"
              @click="editing = false; load()">取消</button>
            <button class="px-3 py-1.5 text-xs rounded-lg border border-red-300 text-red-700 hover:bg-red-50"
              @click="del">刪除</button>
          </div>
        </div>
      </div>
    </nav>

    <div v-if="concept" class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 grid lg:grid-cols-[1fr,300px] gap-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-1" :style="concept.color ? { color: concept.color } : undefined">{{ concept.name }}</h1>
        <p v-if="concept.aliases?.length" class="text-xs text-gray-400 mb-1">別名：{{ concept.aliases.join('、') }}</p>
        <p v-if="concept.summary" class="text-gray-600 mb-6">{{ concept.summary }}</p>

        <template v-if="!editing">
          <div class="bg-white border border-gray-200 rounded-2xl p-6 leading-relaxed text-gray-800 whitespace-pre-wrap"
               v-html="renderedBody"></div>
          <p v-if="linkInfo?.unresolved?.length" class="mt-3 text-xs text-amber-600">
            未對應的 [[連結]]：{{ linkInfo.unresolved.join('、') }}（建立同名概念後自動連上）
          </p>
        </template>

        <template v-else>
          <div class="bg-white border border-gray-200 rounded-2xl p-4 space-y-3">
            <input v-model="edit.name" placeholder="概念名稱"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
            <input v-model="edit.aliasesRaw" placeholder="別名，逗號分隔"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
            <input v-model="edit.summary" placeholder="一句話摘要"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
            <textarea v-model="edit.body" rows="20"
              placeholder="markdown 內文，使用 [[其他概念]] 雙向連結"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono leading-relaxed" />
            <div class="flex items-center gap-3 text-xs text-gray-400">
              <span>顏色</span>
              <input type="color" v-model="edit.color" class="w-7 h-7 rounded border border-gray-200" />
              <button class="text-red-500 hover:underline" @click="edit.color = ''">清除</button>
            </div>
          </div>
        </template>
      </div>

      <aside class="space-y-6">
        <section>
          <h3 class="text-sm font-semibold text-gray-700 mb-2">指向其他概念 ({{ concept.outlinks?.length ?? 0 }})</h3>
          <div v-if="!concept.outlinks?.length" class="text-xs text-gray-400">無</div>
          <NuxtLink v-for="l in concept.outlinks" :key="l.id" :to="`/concepts/${l.slug}`"
            class="block bg-white border border-gray-200 rounded-lg px-3 py-2 mb-1.5 hover:border-cyan-300">
            <p class="text-sm text-cyan-700">→ {{ l.name }}</p>
            <p v-if="l.summary" class="text-xs text-gray-500 line-clamp-1">{{ l.summary }}</p>
          </NuxtLink>
        </section>
        <section>
          <h3 class="text-sm font-semibold text-gray-700 mb-2">被引用 (Backlinks · {{ concept.backlinks?.length ?? 0 }})</h3>
          <div v-if="!concept.backlinks?.length" class="text-xs text-gray-400">尚無</div>
          <NuxtLink v-for="b in concept.backlinks" :key="b.id" :to="`/concepts/${b.slug}`"
            class="block bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mb-1.5 hover:border-amber-300">
            <p class="text-sm text-amber-800">← {{ b.name }}</p>
            <p v-if="b.context" class="text-xs text-gray-600 line-clamp-2 mt-0.5">…{{ b.context }}…</p>
          </NuxtLink>
        </section>
        <section v-if="concept.source_books?.length">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">引用書籍 ({{ concept.source_books.length }})</h3>
          <NuxtLink v-for="b in concept.source_books" :key="b.id" :to="`/excerpts/library/${b.id}`"
            class="block bg-blue-50/40 border border-blue-100 rounded-lg px-3 py-2 mb-1.5 hover:border-blue-300">
            <p class="text-sm text-gray-800 line-clamp-1">📚 {{ b.title }}</p>
            <p class="text-[11px] text-gray-500 mt-0.5">
              <span v-if="b.author">{{ b.author }}</span>
              <span v-if="b.publish_year">（{{ b.publish_year }}）</span>
              <span class="ml-1 text-gray-400">· {{ b.excerpt_count }} 筆摘文</span>
            </p>
          </NuxtLink>
        </section>

        <section v-if="concept.source_journals?.length">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">引用期刊 ({{ concept.source_journals.length }})</h3>
          <NuxtLink v-for="j in concept.source_journals" :key="j.id" :to="`/excerpts/journal/${j.id}`"
            class="block bg-amber-50/40 border border-amber-100 rounded-lg px-3 py-2 mb-1.5 hover:border-amber-300">
            <p class="text-sm text-gray-800 line-clamp-1">📰 {{ j.title }}</p>
            <p class="text-[11px] text-gray-500 mt-0.5">
              <span v-if="j.author">{{ j.author }}</span>
              <span v-if="j.venue">·《{{ j.venue }}》</span>
              <span v-if="j.publish_year">（{{ j.publish_year }}）</span>
              <span class="ml-1 text-gray-400">· {{ j.excerpt_count }} 筆摘文</span>
            </p>
          </NuxtLink>
        </section>

        <section v-if="concept.excerpts?.length">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">關聯書摘 ({{ concept.excerpts.length }})</h3>
          <NuxtLink v-for="ex in concept.excerpts" :key="ex.id" :to="`/excerpts/${ex.id}`"
            class="block bg-white border border-gray-200 rounded-lg px-3 py-2 mb-1.5 hover:border-blue-300">
            <p class="text-sm text-gray-800 line-clamp-2">{{ ex.title || ex.content?.slice(0, 80) }}</p>
          </NuxtLink>
        </section>
      </aside>
    </div>

    <div v-else-if="loading" class="text-center text-gray-400 py-20">載入中…</div>
    <div v-else class="text-center text-gray-400 py-20">找不到此概念</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { authedFetch } from '~/composables/useAuthedFetch';

definePageMeta({ middleware: 'auth' });

interface Concept {
  id: string; name: string; slug: string;
  aliases?: string[]; summary?: string | null; body?: string;
  color?: string | null;
  outlinks: any[]; backlinks: any[]; excerpts: any[];
  source_books?: any[]; source_journals?: any[];
}

const route = useRoute();
const router = useRouter();
const slug = computed(() => route.params.slug as string);

const concept = ref<Concept | null>(null);
const loading = ref(true);
const editing = ref(false);
const saving = ref(false);
const linkInfo = ref<any>(null);
const edit = ref({ name: '', aliasesRaw: '', summary: '', body: '', color: '' });

async function load() {
  loading.value = true;
  try {
    concept.value = await authedFetch<Concept>(`/api/concepts/${slug.value}`);
  } catch {
    concept.value = null;
  } finally { loading.value = false; }
}

function startEdit() {
  if (!concept.value) return;
  edit.value.name       = concept.value.name;
  edit.value.aliasesRaw = (concept.value.aliases ?? []).join('、');
  edit.value.summary    = concept.value.summary ?? '';
  edit.value.body       = concept.value.body ?? '';
  edit.value.color      = concept.value.color ?? '';
  editing.value = true;
}

async function save() {
  if (!concept.value) return;
  saving.value = true;
  try {
    const aliases = edit.value.aliasesRaw
      .split(/,|，|、/).map((s) => s.trim()).filter(Boolean);
    const res: any = await authedFetch(`/api/concepts/${concept.value.id}`, {
      method: 'PATCH',
      body: {
        name:    edit.value.name.trim(),
        aliases,
        summary: edit.value.summary.trim() || null,
        body:    edit.value.body,
        color:   edit.value.color || null,
      },
    });
    linkInfo.value = res?.links ?? null;
    editing.value = false;
    await load();
  } finally { saving.value = false; }
}

async function del() {
  if (!concept.value) return;
  if (!confirm(`刪除概念「${concept.value.name}」？所有連結會一併移除。`)) return;
  await authedFetch(`/api/concepts/${concept.value.id}`, { method: 'DELETE' });
  router.push('/concepts');
}

// Render body — minimal: [[wiki]] → link, **bold**, *italic*, ` `code`.
// Resolved outlinks come back keyed by raw_link_text so we map name → slug;
// unresolved links render as a dashed-red placeholder.
const renderedBody = computed(() => {
  const raw = concept.value?.body ?? '';
  const linkBySlug = new Map<string, string>();
  (concept.value?.outlinks ?? []).forEach((l: any) => {
    if (l.raw) linkBySlug.set(l.raw.toLowerCase(), l.slug);
    if (l.name) linkBySlug.set(l.name.toLowerCase(), l.slug);
  });
  const escape = (s: string) => s
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  let html = escape(raw);
  html = html.replace(/\[\[([^\[\]\n]+?)\]\]/g, (_, name) => {
    const target = String(name).trim();
    const slug = linkBySlug.get(target.toLowerCase());
    if (slug) {
      return `<a class="text-cyan-700 underline decoration-dotted hover:text-cyan-900" href="/concepts/${slug}">${escape(target)}</a>`;
    }
    return `<span class="text-red-500 border-b border-dashed border-red-300" title="尚無同名概念，建立後會自動連上">${escape(target)}</span>`;
  });
  html = html.replace(/\*\*([^*\n]+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, '$1<em>$2</em>');
  html = html.replace(/`([^`\n]+?)`/g, '<code class="px-1 bg-gray-100 rounded text-[0.9em]">$1</code>');
  return html;
});

watch(slug, load);
onMounted(load);
</script>
