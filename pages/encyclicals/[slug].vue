<template>
  <div v-if="doc" class="flex flex-col bg-stone-50 min-h-dvh">
    <nav class="flex items-center gap-2 px-4 h-12 bg-white/95 backdrop-blur border-b border-stone-200 z-30 sticky top-0 overflow-x-auto">
      <NuxtLink :to="popeBackUrl" class="text-stone-400 hover:text-stone-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-stone-200" />
      <NuxtLink to="/encyclicals" class="text-sm font-semibold text-stone-700 hover:text-stone-900 transition whitespace-nowrap">🕊️</NuxtLink>
      <span class="text-stone-300">/</span>
      <NuxtLink
        :to="`/encyclicals/century/${doc.century}`"
        class="text-sm text-stone-500 hover:text-stone-900 transition whitespace-nowrap"
      >{{ doc.century }} 世紀</NuxtLink>
      <span class="text-stone-300">/</span>
      <NuxtLink
        v-if="pope"
        :to="`/encyclicals/pope/${pope.slug}`"
        class="text-sm text-stone-500 hover:text-stone-900 transition whitespace-nowrap"
      >{{ pope.nameZh }}</NuxtLink>
      <span class="text-stone-300">/</span>
      <span class="text-sm font-semibold text-stone-900 truncate">{{ doc.titleZh }}</span>
      <span class="text-xs text-stone-400 ml-auto whitespace-nowrap font-mono">{{ doc.promulgationDate }}</span>
    </nav>

    <div class="flex-1 max-w-[1400px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <header class="mb-8 pb-6 border-b border-stone-200">
        <div class="flex items-baseline flex-wrap gap-2 mb-3">
          <span class="font-mono text-xs px-2 py-0.5 rounded bg-stone-900 text-white">
            {{ CATEGORY_LABEL_ZH[doc.category] }}
          </span>
          <span class="font-mono text-[11px] px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-200 italic">
            {{ CATEGORY_LABEL_LAT[doc.category] }}
          </span>
          <span class="text-[11px] text-stone-400">{{ doc.century }} 世紀</span>
        </div>
        <h1 class="text-3xl font-bold text-stone-900 leading-tight tracking-tight">{{ doc.titleZh }}</h1>
        <div class="mt-1.5 text-base italic text-stone-600">{{ doc.titleLat }}</div>
        <div class="text-sm text-stone-500 mt-0.5">{{ doc.titleEn }}</div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 mt-6 text-sm">
          <div class="flex gap-2">
            <span class="text-stone-400 shrink-0">頒布：</span>
            <span class="text-stone-800 font-mono">{{ doc.promulgationDate }}</span>
          </div>
          <div v-if="pope" class="flex gap-2">
            <span class="text-stone-400 shrink-0">教宗：</span>
            <span class="text-stone-800">
              {{ pope.nameZh }}
              <span class="italic text-stone-400 text-xs">（{{ pope.nameLat }}，在位 {{ pope.pontificateStart.slice(0, 4) }}–{{ pope.pontificateEnd ? pope.pontificateEnd.slice(0, 4) : '今' }}）</span>
            </span>
          </div>
        </div>

        <div v-if="doc.topics?.length" class="mt-4 flex flex-wrap gap-1.5">
          <span
            v-for="t in doc.topics"
            :key="t"
            class="text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200"
          >{{ t }}</span>
        </div>
      </header>

      <!-- Summary -->
      <section v-if="doc.summaryZh" class="mb-10">
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-base">📌</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">摘要</h2>
        </div>
        <div class="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
          <div class="border-l-[3px] border-amber-400 px-6 py-5 prose-summary">
            <p
              v-for="(part, i) in summaryParagraphs"
              :key="i"
              :class="i === 0 ? 'lead text-[1.02rem] text-stone-900 font-medium leading-loose' : 'text-[0.95rem] text-stone-700 leading-loose mt-3'"
              style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
              v-html="renderRichText(part)"
            ></p>
          </div>
        </div>
      </section>

      <!-- 逐段對照 -->
      <section class="mb-8">
        <div class="flex items-baseline gap-2 mb-3 flex-wrap">
          <span class="text-base">📜</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">逐段對照</h2>
          <span class="text-[11px] text-stone-400">每段一 row × 中／英／拉 三欄並列（vatican.va 段號）</span>
          <span v-if="rows.length > 0" class="text-[11px] text-stone-500 ml-auto">共 {{ paragraphRowCount }} 段</span>
        </div>

        <div v-if="loading" class="text-center text-stone-400 py-12 text-sm">載入中…</div>
        <div v-else-if="loadError" class="text-center text-rose-500 py-12 text-sm">⚠ {{ loadError }}</div>
        <div v-else-if="rows.length === 0" class="text-center text-stone-400 py-12 text-sm">⚠ 無法解析段落</div>

        <div v-else class="space-y-1.5">
          <template v-for="(row, ri) in rows" :key="ri">
            <div
              v-if="row.kind === 'heading'"
              class="bg-gradient-to-r from-amber-50 via-stone-50 to-white border-y border-amber-200 px-4 py-3 mt-5 first:mt-0"
            >
              <div class="text-[11px] font-semibold uppercase tracking-widest text-amber-800 mb-1">section</div>
              <div class="grid gap-4" :style="{ gridTemplateColumns: '1fr 1fr 1fr' }">
                <div
                  class="text-[0.92rem] font-semibold text-stone-900"
                  style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
                >
                  <template v-if="row.byLang.zh">{{ row.byLang.zh }}</template>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
                <div class="text-[0.88rem] font-semibold text-stone-900 font-sans italic">
                  <template v-if="row.byLang.en">{{ row.byLang.en }}</template>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
                <div class="text-[0.9rem] font-semibold text-stone-900 italic">
                  <template v-if="row.byLang.lat">{{ row.byLang.lat }}</template>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
              </div>
            </div>

            <article
              v-else
              :id="`para-${row.num}`"
              class="bg-white border border-stone-200 rounded-md overflow-hidden"
            >
              <div class="grid gap-px bg-stone-100" :style="{ gridTemplateColumns: '3rem 1fr 1fr 1fr' }">
                <div class="bg-stone-50 px-2 py-3 text-xs font-mono font-bold text-stone-700 flex items-start justify-center">
                  {{ row.num }}
                </div>
                <div
                  class="bg-white px-3 py-3 text-[0.92rem] leading-loose text-stone-800 whitespace-pre-wrap"
                  style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
                >
                  <span v-if="row.byLang.zh" v-html="renderBody(row.byLang.zh, 'zh')"></span>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
                <div class="bg-white px-3 py-3 text-[0.875rem] leading-relaxed text-stone-800 font-sans whitespace-pre-wrap">
                  <span v-if="row.byLang.en" v-html="renderBody(row.byLang.en, 'en')"></span>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
                <div class="bg-white px-3 py-3 text-[0.92rem] leading-relaxed text-stone-800 whitespace-pre-wrap italic">
                  <span v-if="row.byLang.lat" v-html="renderBody(row.byLang.lat, 'lat')"></span>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
              </div>
            </article>
          </template>
        </div>

        <!-- Footnotes -->
        <div v-if="hasFootnotes" class="mt-8 border-t-2 border-stone-300 pt-6">
          <div class="text-xs uppercase tracking-widest text-stone-500 font-semibold mb-3">📎 註腳對照</div>
          <div class="grid gap-4" :style="{ gridTemplateColumns: '3rem 1fr 1fr 1fr' }">
            <div></div>
            <div class="text-[10px] uppercase tracking-wider text-stone-400">中文</div>
            <div class="text-[10px] uppercase tracking-wider text-sky-700">English</div>
            <div class="text-[10px] uppercase tracking-wider text-amber-700">Latin</div>

            <template v-for="num in footnoteNumbers" :key="num">
              <div :id="`fn-anchor-${num}`" class="text-xs font-mono font-bold text-stone-600 self-start pt-1 text-center">[{{ num }}]</div>
              <div
                :id="`fn-zh-${num}`"
                class="text-[0.85rem] text-stone-700 leading-relaxed scroll-mt-16"
                style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
              >
                <span v-if="footnoteOf('zh', num)" v-html="renderBody(footnoteOf('zh', num), 'zh')"></span>
                <span v-else class="text-stone-300 italic text-xs">—</span>
              </div>
              <div :id="`fn-en-${num}`" class="text-[0.82rem] text-stone-700 leading-relaxed font-sans scroll-mt-16">
                <span v-if="footnoteOf('en', num)" v-html="renderBody(footnoteOf('en', num), 'en')"></span>
                <span v-else class="text-stone-300 italic text-xs">—</span>
              </div>
              <div :id="`fn-lat-${num}`" class="text-[0.85rem] text-stone-700 leading-relaxed italic scroll-mt-16">
                <span v-if="footnoteOf('lat', num)" v-html="renderBody(footnoteOf('lat', num), 'lat')"></span>
                <span v-else class="text-stone-300 italic text-xs">—</span>
              </div>
            </template>
          </div>
        </div>

        <!-- 來源 footer -->
        <div class="mt-6 grid gap-2 text-[11px] text-stone-500 leading-relaxed" :style="{ gridTemplateColumns: '3rem 1fr 1fr 1fr' }">
          <div></div>
          <div>
            <div v-if="zhVersion?.translator">✍ {{ zhVersion.translator }}</div>
            <div v-if="zhVersion?.source">📖 <a :href="zhVersion.source" target="_blank" class="hover:underline">中文版來源</a></div>
            <div v-if="zhVersion?.placeholder" class="text-amber-700">⏳ 中文版本為 placeholder</div>
          </div>
          <div>
            <div v-if="enVersion?.source">📖 <a :href="enVersion.source" target="_blank" class="hover:underline">English 來源</a></div>
          </div>
          <div>
            <div v-if="latVersion?.source">📖 <a :href="latVersion.source" target="_blank" class="hover:underline">Latin 來源</a></div>
          </div>
        </div>
      </section>

      <!-- Notes -->
      <section v-if="doc.notes" class="mb-10">
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-base">📝</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">歷史 Notes</h2>
        </div>
        <div class="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
          <div class="border-l-[3px] border-stone-400 px-6 py-5">
            <p
              v-for="(part, i) in notesParagraphs"
              :key="i"
              class="text-[0.95rem] text-stone-700 leading-loose mt-3 first:mt-0"
              style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
              v-html="renderRichText(part)"
            ></p>
          </div>
        </div>
      </section>
    </div>
  </div>

  <div v-else class="min-h-dvh flex items-center justify-center text-stone-400">
    找不到此文件：{{ route.params.slug }}
    <NuxtLink to="/encyclicals" class="ml-3 text-blue-500 underline">回列表</NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { findDocument, findPope, CATEGORY_LABEL_ZH, CATEGORY_LABEL_LAT } from '~/data/encyclicals'
import { loadPapalDoc } from '~/data/encyclicals/textLoader'
import { alignDocs, type ParsedDoc, type FootnoteDef } from '~/data/creeds/paragraphParser'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const doc = computed(() => findDocument(route.params.slug as string))
const pope = computed(() => (doc.value ? findPope(doc.value.popeSlug) : undefined))

const popeBackUrl = computed(() => (pope.value ? `/encyclicals/pope/${pope.value.slug}` : '/encyclicals'))

useHead(() => ({
  title: doc.value ? `${doc.value.titleZh} — 教宗訓導文獻` : '找不到文件',
}))

const zhVersion = computed(() => doc.value?.versions.find(v => v.lang === 'zh-Hant'))
const enVersion = computed(() => doc.value?.versions.find(v => v.lang === 'en'))
const latVersion = computed(() => doc.value?.versions.find(v => v.lang === 'lat'))

const loading = ref(true)
const loadError = ref<string | null>(null)
const byLang = ref<Record<string, ParsedDoc>>({})

async function loadAll() {
  if (!doc.value) return
  loading.value = true
  loadError.value = null
  try {
    const popeSlug = doc.value.popeSlug
    const out: Record<string, ParsedDoc> = {}
    for (const v of doc.value.versions) {
      const bucket = v.lang === 'zh-Hant' ? 'zh' : (v.lang === 'en' ? 'en' : 'lat')
      if (out[bucket]) continue // first wins per bucket
      try {
        out[bucket] = await loadPapalDoc(popeSlug, v.textKey)
      } catch (err) {
        // missing text file is ok — placeholder
        out[bucket] = { blocks: [], footnotes: [] }
      }
    }
    byLang.value = out
  } catch (err) {
    loadError.value = String(err)
  } finally {
    loading.value = false
  }
}

watch(() => doc.value?.slug, () => { loadAll() }, { immediate: true })

const aligned = computed(() => alignDocs(byLang.value))
const rows = computed(() => aligned.value.rows)
const paragraphRowCount = computed(() => rows.value.filter(r => r.kind === 'paragraph').length)

const footnotesByLang = computed(() => aligned.value.footnotesByLang)
const footnoteNumbers = computed<string[]>(() => {
  const set = new Set<string>()
  for (const l of Object.keys(footnotesByLang.value)) {
    for (const fn of footnotesByLang.value[l]) set.add(fn.num)
  }
  return [...set].sort((a, b) => parseInt(a) - parseInt(b))
})
const hasFootnotes = computed(() => footnoteNumbers.value.length > 0)

function footnoteOf(lang: string, num: string): string {
  const fns = footnotesByLang.value[lang] || []
  return fns.find((f: FootnoteDef) => f.num === num)?.body || ''
}

// ── Rich-text helpers ─────────────────────────────────────
function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

function renderRichText(text: string): string {
  if (!text) return ''
  let html = escapeHtml(text)
  html = html.replace(/《([^》]+)》/g, '<em class="italic font-medium text-stone-900">《$1》</em>')
  html = html.replace(/（([A-Za-z][A-Za-z\s\-/.,;:]+[A-Za-z])）/g, '<span class="italic text-stone-600">（$1）</span>')
  return html
}

function renderBody(body: string, lang: 'zh' | 'en' | 'lat'): string {
  if (!body) return ''
  let html = escapeHtml(body)
  html = html.replace(/\[\^(\d{1,4})\]/g, (_, n) =>
    `<sup class="ml-0.5"><a class="text-stone-500 hover:text-stone-900 underline decoration-dotted font-semibold" href="#fn-${lang}-${n}">${n}</a></sup>`,
  )
  return html
}

const summaryParagraphs = computed<string[]>(() => {
  const t = doc.value?.summaryZh
  if (!t) return []
  return t.split(/\n{2,}/).map(s => s.trim()).filter(Boolean)
})

const notesParagraphs = computed<string[]>(() => {
  const t = doc.value?.notes
  if (!t) return []
  return t.split(/\n{2,}/).map(s => s.trim()).filter(Boolean)
})
</script>
