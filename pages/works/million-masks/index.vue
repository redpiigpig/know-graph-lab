<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/works" class="text-gray-400 hover:text-gray-700 transition text-sm">← 寫作計畫</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">{{ project?.title ?? '千面上帝' }}</span>
        <span v-if="user" class="ml-auto text-xs text-gray-400">{{ user.email }}</span>
        <NuxtLink v-else to="/login" class="ml-auto text-xs text-blue-600 hover:underline">登入</NuxtLink>
      </div>
    </nav>

    <!-- 封面 -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-5xl mx-auto px-6 py-10">
        <div v-if="!project" class="text-gray-400 text-sm">載入中⋯</div>

        <template v-else>
          <div class="flex items-center gap-2 mb-3">
            <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-100 text-amber-700">寫作計畫</span>
            <WorksInlineEdit
              tag="span"
              :model-value="project.status"
              :editable="!!user"
              placeholder-hint="（點擊設定狀態）"
              display-class="text-xs text-gray-400"
              @save="patch({ status: $event })"
            />
          </div>

          <WorksInlineEdit
            tag="h1"
            :model-value="project.title"
            :editable="!!user"
            placeholder="標題"
            display-class="text-xl font-bold text-gray-900 leading-snug mb-1 block"
            @save="patch({ title: $event })"
          />

          <WorksInlineEdit
            tag="p"
            :model-value="project.subtitle"
            :editable="!!user"
            placeholder="英文書名 / 副標"
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

    <!-- 分頁 -->
    <div class="bg-white border-b border-gray-100 sticky top-14 z-30">
      <div class="max-w-5xl mx-auto px-6">
        <div class="flex">
          <button v-for="tab in visibleTabs" :key="tab.id" @click="activeTab = tab.id"
            :class="['px-5 py-3.5 text-sm font-medium border-b-2 transition-colors', activeTab === tab.id ? 'border-amber-600 text-amber-700' : 'border-transparent text-gray-500 hover:text-gray-800']">
            {{ tab.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- 內容 -->
    <div class="max-w-5xl mx-auto px-6 py-8">

      <!-- 宗教史讀書會 -->
      <div v-show="activeTab === 'reading-club'">
        <div class="mb-6">
          <h2 class="text-base font-semibold text-gray-900">宗教史讀書會</h2>
          <p class="text-xs text-gray-500 mt-0.5">YouTube 讀書會影片逐字稿，共 {{ sessions.length }} 集</p>
        </div>

        <div v-if="sessionsLoading" class="flex items-center justify-center h-32 text-gray-400 text-sm">載入中⋯</div>

        <div v-else-if="sessions.length === 0" class="flex flex-col items-center justify-center h-40 text-gray-400 text-sm gap-2">
          <span class="text-3xl">🎬</span>
          <span>逐字稿轉錄中，請稍後再來</span>
        </div>

        <div v-else class="grid gap-3 sm:grid-cols-2">
          <NuxtLink v-for="s in sessions" :key="s.id"
            :to="`/works/million-masks/reading-club/${s.id}`"
            class="bg-white rounded-xl border border-gray-100 p-4 hover:border-amber-200 hover:shadow-sm transition-all no-underline">
            <div class="flex items-start gap-3">
              <div class="w-9 h-9 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center text-sm flex-shrink-0 font-bold">
                {{ s.episode }}
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-sm font-semibold text-gray-900 leading-snug mb-0.5">{{ s.title }}</h3>
                <p v-if="s.date" class="text-xs text-gray-400">{{ s.date }}</p>
                <p class="text-xs text-amber-500 mt-1.5">閱讀逐字稿 →</p>
              </div>
            </div>
          </NuxtLink>
        </div>
      </div>

      <!-- 書摘與構思（登入者限定） -->
      <div v-if="user" v-show="activeTab === 'notes'">
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

    </div>
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'

useHead({ title: '千面上帝 — 寫作計畫 — Know Graph Lab' })
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
const activeTab = ref<'reading-club' | 'notes'>('reading-club')

const tabs = [
  { id: 'reading-club' as const, label: '宗教史讀書會' },
  { id: 'notes' as const, label: '書摘與構思' },
]

const visibleTabs = computed(() => user.value ? tabs : tabs.filter(t => t.id !== 'notes'))

// 讀書會 sessions（公開）
const sessionsLoading = ref(true)
const sessions = ref<{ id: string; episode: number; title: string; date: string | null }[]>([])

async function loadSessions() {
  sessionsLoading.value = true
  try {
    const data = await $fetch<{ sessions: typeof sessions.value }>('/api/works/million-masks-readings')
    sessions.value = data.sessions ?? []
  } catch {
    sessions.value = []
  }
  sessionsLoading.value = false
}

// 專案資料（封面 + content_json）
async function loadProject() {
  let token = ''
  if (user.value) {
    const { data: { session } } = await supabase.auth.getSession()
    token = session?.access_token ?? ''
  }
  const data = await $fetch<{ project: Project }>('/api/works/projects/million-masks', {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  project.value = data.project
  notesHtml.value = (typeof data.project.content_json === 'string' ? data.project.content_json : '') || ''
  editorKey.value++ // force editor remount with new content
}

onMounted(() => {
  loadSessions()
  loadProject()
})

// 封面 inline-edit save
async function patch(updates: Record<string, unknown>) {
  if (!project.value) return
  try {
    const res = await authedFetch<{ project: Project }>(`/api/works/projects/${project.value.slug}`, {
      method: 'PATCH',
      body: updates,
    })
    project.value = { ...project.value, ...res.project }
  } catch (err: any) {
    alert(`儲存失敗：${err?.data?.message ?? err?.message ?? err}`)
  }
}

// Tiptap notes（HTML 字串存進 content_json JSONB 欄位）
const notesHtml = ref('')
const editorKey = ref(0)
const notesStatus = ref('')
const lastSavedHtml = ref('')

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

watch(notesHtml, () => { lastSavedHtml.value = lastSavedHtml.value || notesHtml.value }, { once: true })
</script>
