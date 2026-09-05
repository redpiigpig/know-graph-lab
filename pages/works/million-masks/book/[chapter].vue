<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader :title="meta?.title ?? '書稿'" :back="{ to: '/works/million-masks', label: '千面上帝' }" container-class="max-w-5xl" />

    <div class="max-w-3xl mx-auto px-6 py-10">
      <div v-if="loading" class="flex items-center justify-center h-40 text-gray-400 text-sm">載入中⋯</div>

      <div v-else-if="error" class="text-center text-gray-400 py-20">
        <div class="text-3xl mb-3">⚠️</div>
        <p>{{ error }}</p>
      </div>

      <div v-else>
        <div class="mb-8">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-100 text-amber-700 mb-3 inline-block">
            {{ meta?.volume ?? '書稿' }}
          </span>
          <h1 class="text-xl font-bold text-gray-900 leading-snug">第{{ no }}章　{{ meta?.title }}</h1>
          <p v-if="meta" class="text-sm text-gray-400 mt-1">{{ meta.span }}（{{ meta.period }}）</p>
        </div>

        <article class="book-page">
          <div class="book-body" v-html="rendered"></div>

          <div v-if="notes.length" class="notes">
            <div class="notes-rule"></div>
            <p v-for="n in notes" :key="n.no" :id="`note-${no}-${n.no}`" class="note">
              <a :href="`#ref-${no}-${n.no}`" class="note-no">{{ n.no }}</a>
              <span>{{ n.text }}</span>
            </p>
          </div>
        </article>

        <div class="flex justify-between items-center mt-8 text-sm">
          <NuxtLink v-if="prev" :to="`/works/million-masks/book/${prev.no}`" class="text-amber-600 no-underline hover:text-amber-700">
            ← 第{{ prev.no }}章　{{ prev.title }}
          </NuxtLink>
          <span v-else></span>
          <NuxtLink v-if="next" :to="`/works/million-masks/book/${next.no}`" class="text-amber-600 no-underline hover:text-amber-700">
            第{{ next.no }}章　{{ next.title }} →
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ChapterMeta {
  no: number; volume: string; title: string; span: string; period: string
  chars: number; notes: number
}

const route = useRoute()
const no = computed(() => Number(route.params.chapter))

const loading = ref(true)
const error = ref('')
const raw = ref('')
const index = ref<ChapterMeta[]>([])

const meta = computed(() => index.value.find(c => c.no === no.value) ?? null)
const prev = computed(() => index.value.find(c => c.no === no.value - 1) ?? null)
const next = computed(() => index.value.find(c => c.no === no.value + 1) ?? null)

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

/** 註釋定義收在檔尾的 `[^1]: 註文`，正文裡是 `[^1]`。 */
const notes = computed(() => {
  const out: { no: number; text: string }[] = []
  for (const line of raw.value.split('\n')) {
    const m = /^\[\^(\d+)\]:\s*(.+)$/.exec(line.trim())
    if (m) out.push({ no: Number(m[1]), text: m[2] })
  }
  return out
})

const rendered = computed(() => {
  const out: string[] = []
  for (const line of raw.value.split('\n')) {
    const t = line.trim()
    // 檔尾的註釋定義、標題行與 HTML 註解都不進正文
    if (!t || t === '---' || t.startsWith('<!--') || /^\[\^\d+\]:/.test(t)) continue
    if (t.startsWith('# ')) continue
    if (t.startsWith('### ')) continue
    if (t.startsWith('## ')) {
      out.push(`<h2 class="b-sec">${esc(t.slice(3))}</h2>`)
      continue
    }
    const body = esc(t).replace(
      /\[\^(\d+)\]/g,
      (_, n) => `<sup class="b-ref"><a id="ref-${no.value}-${n}" href="#note-${no.value}-${n}">${n}</a></sup>`
    )
    out.push(`<p class="b-para">${body}</p>`)
  }
  return out.join('')
})

useHead(() => ({ title: `${meta.value?.title ?? '書稿'} — 千面上帝 — Know Graph Lab` }))

async function load() {
  loading.value = true
  error.value = ''
  try {
    index.value = await $fetch<ChapterMeta[]>('/content/million-masks-book/index.json')
    raw.value = await $fetch<string>(
      `/content/million-masks-book/ch${String(no.value).padStart(2, '0')}.md`
    ) as string
  } catch {
    error.value = '這一章還沒上架'
  }
  loading.value = false
}

onMounted(load)
watch(no, load)
</script>

<style scoped>
.book-page {
  background: white;
  border-radius: 1rem;
  border: 1px solid #f0f0f0;
  padding: 2.5rem 3rem;
  font-family: 'Georgia', 'Noto Serif TC', serif;
}
:deep(.b-sec) {
  font-size: 1.05rem;
  font-weight: 700;
  color: #92400e;
  margin: 2.25rem 0 1rem;
}
:deep(.b-sec:first-child) { margin-top: 0; }
:deep(.b-para) {
  font-size: 0.95rem;
  line-height: 2.1;
  text-indent: 2em;
  margin-bottom: 0.85rem;
  color: #1f2937;
  text-align: justify;
}
:deep(.b-ref) { font-size: 0.7em; }
:deep(.b-ref a) {
  color: #b45309;
  text-decoration: none;
  padding: 0 0.1em;
}
.notes { margin-top: 2.5rem; }
.notes-rule {
  width: 33%;
  border-top: 1px solid #d1d5db;
  margin-bottom: 1rem;
}
.note {
  font-size: 0.78rem;
  line-height: 1.75;
  color: #4b5563;
  margin-bottom: 0.35rem;
  padding-left: 1.6em;
  text-indent: -1.6em;
}
.note-no {
  color: #b45309;
  text-decoration: none;
  margin-right: 0.4em;
}
</style>
