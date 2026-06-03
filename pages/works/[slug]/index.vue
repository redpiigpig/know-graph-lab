<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader :title="project?.title ?? '載入中…'" :back="{ to: '/works', label: '寫作計畫' }" container-class="max-w-5xl" />

    <div v-if="notFound" class="max-w-5xl mx-auto px-6 py-24 text-center">
      <div class="text-4xl mb-4">📭</div>
      <h1 class="text-lg font-semibold text-gray-700 mb-1">找不到此寫作計畫</h1>
      <p class="text-sm text-gray-400 mb-6">slug：{{ slug }}</p>
      <NuxtLink to="/works" class="text-sm text-amber-600 hover:underline">← 回寫作計畫列表</NuxtLink>
    </div>

    <template v-else>
      <!-- 封面 -->
      <div class="bg-white border-b border-gray-100">
        <div class="max-w-5xl mx-auto px-6 py-10">
          <div v-if="!project" class="text-gray-400 text-sm">載入中⋯</div>
          <template v-else>
            <div class="flex items-center gap-2 mb-3">
              <span class="text-xs font-medium px-2.5 py-1 rounded-full" :class="`bg-${project.color}-100 text-${project.color}-700`">寫作計畫</span>
              <WorksInlineEdit
                tag="span"
                :model-value="project.status"
                :editable="editMode && !!user"
                placeholder-hint="（點擊設定狀態）"
                display-class="text-xs text-gray-400"
                @save="patch({ status: $event })"
              />
            </div>

            <div class="flex items-center gap-3 mb-1">
              <WorksInlineEdit
                tag="span"
                :model-value="project.emoji"
                :editable="editMode && !!user"
                placeholder="📝"
                display-class="text-2xl"
                @save="patch({ emoji: $event })"
              />
              <WorksInlineEdit
                tag="h1"
                :model-value="project.title"
                :editable="editMode && !!user"
                placeholder="標題"
                display-class="text-xl font-bold text-gray-900 leading-snug flex-1"
                @save="patch({ title: $event })"
              />
            </div>

            <WorksInlineEdit
              tag="p"
              :model-value="project.subtitle"
              :editable="editMode && !!user"
              placeholder="副標 / 英文書名"
              display-class="text-sm text-gray-400 italic mb-4 block"
              @save="patch({ subtitle: $event })"
            />

            <WorksInlineEdit
              tag="p"
              :model-value="project.description"
              :editable="editMode && !!user"
              multiline
              :rows="3"
              placeholder="描述"
              display-class="text-sm text-gray-600 leading-relaxed max-w-2xl block"
              @save="patch({ description: $event })"
            />
          </template>
        </div>
      </div>

      <!-- 書摘與構思 — 登入者限定 -->
      <div v-if="user" class="max-w-5xl mx-auto px-6 py-8">
        <div class="mb-3 flex items-center justify-between">
          <div>
            <h2 class="text-base font-semibold text-gray-900">書摘與構思</h2>
            <p class="text-xs text-gray-500 mt-0.5">章節草稿 · 引用筆記 · 此分頁僅登入者可見</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="editMode"
              class="px-3 py-1.5 text-xs rounded-lg border border-blue-300 text-blue-700 hover:bg-blue-50"
              @click="showPicker = true"
            >📎 插入引用</button>
            <button
              class="px-3 py-1.5 text-xs rounded-lg border border-purple-300 text-purple-700 hover:bg-purple-50"
              @click="showExport = true"
            >📄 預覽 + 書目</button>
            <span class="text-xs text-gray-400 ml-2">{{ editMode ? notesStatus : '檢視中（按右上「編輯」可修改）' }}</span>
          </div>
        </div>

        <p v-if="pickerToast" class="text-xs text-emerald-600 mb-2">{{ pickerToast }}</p>
        <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden" style="min-height: 400px;">
          <ClientOnly>
            <GenealogyRichTextEditor
              v-if="editMode"
              :key="editorKey"
              v-model="notesHtml"
              @update:model-value="onNotesUpdate"
            />
            <div v-else-if="notesHtml" class="prose-notes px-6 py-5" v-html="notesHtml"></div>
            <div v-else class="px-6 py-12 text-center text-gray-400 text-sm">
              <div class="text-3xl mb-2">📝</div>
              <p>尚無筆記。按右上「編輯」開始撰寫。</p>
            </div>
          </ClientOnly>
        </div>
      </div>

      <div v-else-if="project?.kind !== 'paper'" class="max-w-5xl mx-auto px-6 py-24 text-center text-gray-400 text-sm">
        登入後可看到「書摘與構思」筆記分頁
      </div>

      <!-- 研究回顧（文獻綜述） — 論文計畫頁底，公開可見 -->
      <div v-if="project?.kind === 'paper'" class="max-w-5xl mx-auto px-6 py-8 border-t border-gray-100">
        <div class="mb-4">
          <h2 class="text-base font-semibold text-gray-900">研究回顧</h2>
          <p class="text-xs text-gray-500 mt-0.5">
            文獻綜述 · 共 {{ litEntries.length }} 筆
            <span v-if="litEntries.length"> · 開放取用外文文獻提供 <span class="text-teal-600">原文／逐段中譯</span> 兩欄對照</span>
          </p>
        </div>

        <div v-if="litLoading" class="text-gray-400 text-sm py-8 text-center">載入中⋯</div>
        <div v-else-if="litEntries.length === 0" class="text-gray-400 text-sm py-8 text-center">
          尚無文獻綜述。
        </div>

        <div v-else class="space-y-8">
          <section v-for="grp in litGroups" :key="grp.theme">
            <h3 v-if="grp.theme" class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">{{ grp.theme }}</h3>
            <div class="space-y-3">
              <div v-for="e in grp.items" :key="e.id"
                class="bg-white rounded-2xl border border-gray-100 p-5 transition-all"
                :class="e.has_fulltext ? 'cursor-pointer hover:border-teal-200 hover:shadow-sm' : ''"
                @click="() => e.has_fulltext && navigateTo(`/works/${slug}/review/${e.ref_key}`)">
                <div class="flex flex-wrap items-center gap-1.5 mb-2">
                  <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{{ langLabel(e.language) }}</span>
                  <span v-if="e.dimension" class="text-xs font-medium px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600">{{ e.dimension }}</span>
                  <span v-if="e.stance" class="text-xs font-medium px-2 py-0.5 rounded-full bg-rose-50 text-rose-600">立場：{{ e.stance }}</span>
                  <span v-if="e.has_fulltext" class="text-xs font-medium px-2 py-0.5 rounded-full bg-teal-50 text-teal-700">原文／中譯對照</span>
                </div>
                <h4 class="text-sm font-semibold text-gray-900 leading-snug mb-1">
                  {{ e.authors }}<span v-if="e.year"> （{{ e.year }}）</span>　{{ e.title }}
                </h4>
                <p v-if="e.venue" class="text-xs text-gray-500 mb-2">{{ e.venue }}</p>
                <p v-if="e.abstract_zh" class="text-sm text-gray-700 leading-relaxed">{{ e.abstract_zh }}</p>
                <div class="mt-2 flex items-center gap-3 text-xs">
                  <NuxtLink v-if="e.has_fulltext" :to="`/works/${slug}/review/${e.ref_key}`" @click.stop
                    class="text-teal-700 hover:underline font-medium">閱讀全文（原文／中譯）→</NuxtLink>
                  <a v-if="e.fulltext_url" :href="e.fulltext_url" target="_blank" rel="noopener" @click.stop
                    class="text-blue-600 hover:underline">原始連結 ↗</a>
                  <span v-if="!e.has_fulltext && !e.fulltext_url" class="text-gray-300 italic">無線上全文</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </template>

    <ExcerptPicker
      :open="showPicker"
      @close="showPicker = false"
      @picked="onPicked"
    />
    <DocumentExportModal
      :open="showExport"
      :source-html="notesHtml"
      @close="showExport = false"
    />
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'

const route = useRoute()
const slug = computed(() => String(route.params.slug ?? ''))
const user = useSupabaseUser()
const supabase = useSupabaseClient()
const editMode = useEditMode()

interface Project {
  id: string
  slug: string
  title: string
  subtitle: string | null
  description: string | null
  emoji: string
  color: string
  status: string | null
  content_json: string | null
  kind: 'book' | 'paper'
  paper_ref: string | null
}

interface LitEntry {
  id: number
  ref_key: string
  authors: string
  year: number | null
  title: string
  venue: string | null
  language: string | null
  theme: string | null
  dimension: string | null
  stance: string | null
  abstract_zh: string | null
  fulltext_url: string | null
  fulltext_status: string
  has_fulltext: boolean
}

const LANG_LABELS: Record<string, string> = {
  en: '英文', zh: '中文', de: '德文', fr: '法文', ja: '日文',
  la: '拉丁文', grc: '希臘文', es: '西班牙文', it: '義大利文', other: '其他',
}
function langLabel(code: string | null) {
  return LANG_LABELS[code ?? ''] ?? (code || '—')
}

const project = ref<Project | null>(null)
const notFound = ref(false)
const notesHtml = ref('')
const editorKey = ref(0)
const notesStatus = ref('')
const lastSavedHtml = ref('')
const showPicker = ref(false)
const showExport = ref(false)
const pickerToast = ref('')

function onPicked(payload: { id: string; marker: string; toastMsg: string }) {
  pickerToast.value = payload.toastMsg
  setTimeout(() => { pickerToast.value = '' }, 3500)
}

useHead(() => ({ title: project.value ? `${project.value.title} — 寫作計畫` : '寫作計畫' }))

async function loadProject() {
  let token = ''
  if (user.value) {
    const { data: { session } } = await supabase.auth.getSession()
    token = session?.access_token ?? ''
  }
  try {
    const data = await $fetch<{ project: Project }>(`/api/works/projects/${slug.value}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    project.value = data.project
    notesHtml.value = (typeof data.project.content_json === 'string' ? data.project.content_json : '') || ''
    editorKey.value++
  } catch (err: any) {
    if (err?.statusCode === 404) notFound.value = true
    else console.error(err)
  }
}

onMounted(loadProject)
watch(() => user.value, loadProject)

// ── 研究回顧（文獻綜述）─────────────────────────────────────────────
const litEntries = ref<LitEntry[]>([])
const litLoading = ref(false)

async function loadLitReview() {
  if (project.value?.kind !== 'paper') { litEntries.value = []; return }
  litLoading.value = true
  try {
    const res = await $fetch<{ entries: LitEntry[] }>('/api/lit-review/entries', { query: { slug: slug.value } })
    litEntries.value = res.entries ?? []
  } catch { litEntries.value = [] } finally { litLoading.value = false }
}
watch(() => project.value?.kind, loadLitReview)

// Group entries by theme, preserving server order (display_order encodes theme grouping)
const litGroups = computed(() => {
  const groups: { theme: string; items: LitEntry[] }[] = []
  for (const e of litEntries.value) {
    const theme = e.theme ?? ''
    let g = groups.find(x => x.theme === theme)
    if (!g) { g = { theme, items: [] }; groups.push(g) }
    g.items.push(e)
  }
  return groups
})

async function patch(updates: Record<string, unknown>) {
  if (!project.value) return
  try {
    const res = await authedFetch<{ project: Project }>(`/api/works/projects/${project.value.slug}`, {
      method: 'PATCH',
      body: updates,
    })
    const slugChanged = res.project.slug !== project.value.slug
    project.value = { ...project.value, ...res.project }
    if (slugChanged) navigateTo(`/works/${res.project.slug}`)
  } catch (err: any) {
    alert(`儲存失敗：${err?.data?.message ?? err?.message ?? err}`)
  }
}

const saveNotes = useDebounceFn(async (html: string) => {
  if (!project.value || !user.value) return
  if (html === lastSavedHtml.value) return
  notesStatus.value = '儲存中⋯'
  try {
    await authedFetch(`/api/works/projects/${project.value.slug}`, {
      method: 'PATCH',
      body: { content_json: html },
    })
    lastSavedHtml.value = html
    notesStatus.value = '已儲存'
    setTimeout(() => { if (notesStatus.value === '已儲存') notesStatus.value = '' }, 1500)
  } catch (err: any) {
    notesStatus.value = `儲存失敗：${err?.data?.message ?? err?.message ?? err}`
  }
}, 800)

function onNotesUpdate(html: string) {
  notesHtml.value = html
  saveNotes(html)
}
</script>

<style scoped>
.prose-notes :deep(p)   { margin: 0 0 0.4em; line-height: 1.75; color: #374151; font-size: 14px; }
.prose-notes :deep(h1)  { font-size: 1.5rem; font-weight: 700; margin: 0.6em 0 0.3em; color: #111827; }
.prose-notes :deep(h2)  { font-size: 1.2rem; font-weight: 600; margin: 0.5em 0 0.25em; color: #1f2937; }
.prose-notes :deep(h3)  { font-size: 1.05rem; font-weight: 600; margin: 0.4em 0 0.2em; color: #374151; }
.prose-notes :deep(ul)  { list-style: disc; padding-left: 1.4em; margin: 0.3em 0; }
.prose-notes :deep(ol)  { list-style: decimal; padding-left: 1.4em; margin: 0.3em 0; }
.prose-notes :deep(blockquote) { border-left: 3px solid #f59e0b; padding-left: 0.8em; color: #6b7280; margin: 0.4em 0; }
</style>
