<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/works" class="text-gray-400 hover:text-gray-700 transition text-sm">← 寫作計畫</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700 truncate">{{ project?.title ?? '載入中…' }}</span>
        <span v-if="user" class="ml-auto text-xs text-gray-400">{{ user.email }}</span>
        <NuxtLink v-else to="/login" class="ml-auto text-xs text-blue-600 hover:underline">登入</NuxtLink>
      </div>
    </nav>

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
                :editable="!!user"
                placeholder-hint="（點擊設定狀態）"
                display-class="text-xs text-gray-400"
                @save="patch({ status: $event })"
              />
            </div>

            <div class="flex items-center gap-3 mb-1">
              <WorksInlineEdit
                tag="span"
                :model-value="project.emoji"
                :editable="!!user"
                placeholder="📝"
                display-class="text-2xl"
                @save="patch({ emoji: $event })"
              />
              <WorksInlineEdit
                tag="h1"
                :model-value="project.title"
                :editable="!!user"
                placeholder="標題"
                display-class="text-xl font-bold text-gray-900 leading-snug flex-1"
                @save="patch({ title: $event })"
              />
            </div>

            <WorksInlineEdit
              tag="p"
              :model-value="project.subtitle"
              :editable="!!user"
              placeholder="副標 / 英文書名"
              display-class="text-sm text-gray-400 italic mb-4 block"
              @save="patch({ subtitle: $event })"
            />

            <WorksInlineEdit
              tag="p"
              :model-value="project.description"
              :editable="!!user"
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
          <span class="text-xs text-gray-400">{{ notesStatus }}</span>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden" style="min-height: 400px;">
          <ClientOnly>
            <GenealogyRichTextEditor
              :key="editorKey"
              v-model="notesHtml"
              @update:model-value="onNotesUpdate"
            />
          </ClientOnly>
        </div>
      </div>

      <div v-else class="max-w-5xl mx-auto px-6 py-24 text-center text-gray-400 text-sm">
        登入後可看到「書摘與構思」筆記分頁
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'

const route = useRoute()
const slug = computed(() => String(route.params.slug ?? ''))
const user = useSupabaseUser()
const supabase = useSupabaseClient()

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
}

const project = ref<Project | null>(null)
const notFound = ref(false)
const notesHtml = ref('')
const editorKey = ref(0)
const notesStatus = ref('')
const lastSavedHtml = ref('')

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
