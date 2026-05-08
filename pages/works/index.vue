<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/" class="text-gray-400 hover:text-gray-700 transition text-sm">← 返回主頁</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">寫作計畫</span>
        <span v-if="user" class="ml-auto text-xs text-gray-400">{{ user.email }}</span>
        <NuxtLink v-else to="/login" class="ml-auto text-xs text-blue-600 hover:underline">登入</NuxtLink>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-6 py-12">
      <div class="mb-10 flex items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 mb-1">寫作計畫</h1>
          <p class="text-sm text-gray-500">書寫計畫管理：構思中的書籍、讀書會影音逐字稿、章節草稿</p>
        </div>
        <button v-if="user" @click="startCreate" class="px-3 py-1.5 text-sm rounded-lg bg-amber-600 text-white hover:bg-amber-700 transition flex-shrink-0">
          + 新增計畫
        </button>
      </div>

      <div v-if="loading" class="flex items-center justify-center h-32 text-gray-400 text-sm">載入中⋯</div>

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

        <!-- existing project cards -->
        <div v-for="(p, idx) in projects" :key="p.id" class="relative group">

          <!-- view mode -->
          <NuxtLink v-if="editingSlug !== p.slug" :to="`/works/${p.slug}`"
            class="project-card no-underline block"
            :class="`border-${p.color}-100 hover:border-${p.color}-300 hover:shadow-${p.color}-100`">
            <div class="flex items-start gap-4">
              <div class="project-icon flex-shrink-0" :class="`bg-${p.color}-50 text-${p.color}-600`">{{ p.emoji }}</div>
              <div class="flex-1 min-w-0">
                <h2 class="project-title">{{ p.title }}</h2>
                <p class="project-desc">{{ p.description }}</p>
                <div class="mt-2 flex items-center gap-2 text-xs">
                  <span v-if="p.status" class="px-2 py-0.5 rounded-full" :class="`bg-${p.color}-50 text-${p.color}-700`">{{ p.status }}</span>
                  <span v-if="p.subtitle" class="text-gray-400 italic truncate">{{ p.subtitle }}</span>
                </div>
              </div>
            </div>
          </NuxtLink>

          <!-- edit mode -->
          <div v-else class="project-card border-amber-300 bg-amber-50/30">
            <div class="space-y-2">
              <div class="flex items-center gap-2">
                <input v-model="editForm.emoji" maxlength="2" class="w-12 px-2 py-1 text-center text-xl rounded border border-gray-200 bg-white" />
                <input v-model="editForm.title" placeholder="標題" class="flex-1 px-2 py-1 text-sm font-semibold rounded border border-gray-200 bg-white" />
              </div>
              <input v-model="editForm.subtitle" placeholder="副標（如英文書名）" class="w-full px-2 py-1 text-xs italic text-gray-500 rounded border border-gray-200 bg-white" />
              <textarea v-model="editForm.description" placeholder="描述" rows="2" class="w-full px-2 py-1 text-xs rounded border border-gray-200 bg-white resize-none"></textarea>
              <div class="flex items-center gap-2">
                <select v-model="editForm.color" class="px-2 py-1 text-xs rounded border border-gray-200 bg-white">
                  <option v-for="c in COLORS" :key="c" :value="c">{{ c }}</option>
                </select>
                <input v-model="editForm.status" placeholder="狀態（如：構思中）" class="flex-1 px-2 py-1 text-xs rounded border border-gray-200 bg-white" />
              </div>
              <input v-if="editingSlug === '__new__'" v-model="editForm.slug" placeholder="URL slug（留空自動產生）" class="w-full px-2 py-1 text-xs font-mono rounded border border-gray-200 bg-white" />
              <div class="flex items-center justify-end gap-2 pt-1">
                <button @click="cancelEdit" class="px-3 py-1 text-xs text-gray-500 hover:text-gray-700">取消</button>
                <button @click="saveEdit" :disabled="saving" class="px-3 py-1 text-xs rounded bg-amber-600 text-white hover:bg-amber-700 disabled:opacity-50">
                  {{ saving ? '儲存中⋯' : '儲存' }}
                </button>
              </div>
            </div>
          </div>

          <!-- hover toolbar (only when logged in & not editing) -->
          <div v-if="user && editingSlug !== p.slug" class="absolute top-2 right-2 hidden group-hover:flex items-center gap-1 bg-white/95 backdrop-blur rounded-lg shadow-sm border border-gray-200 px-1 py-1 z-10">
            <button v-if="idx > 0" @click.stop.prevent="move(idx, -1)" title="上移" class="card-tool">↑</button>
            <button v-if="idx < projects.length - 1" @click.stop.prevent="move(idx, 1)" title="下移" class="card-tool">↓</button>
            <button @click.stop.prevent="startEdit(p)" title="編輯" class="card-tool">✏️</button>
            <button @click.stop.prevent="deleteProject(p)" title="刪除" class="card-tool text-red-600">🗑️</button>
          </div>
        </div>

        <!-- new project edit card -->
        <div v-if="editingSlug === '__new__'" class="project-card border-amber-300 bg-amber-50/30">
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <input v-model="editForm.emoji" maxlength="2" class="w-12 px-2 py-1 text-center text-xl rounded border border-gray-200 bg-white" />
              <input v-model="editForm.title" placeholder="標題（必填）" class="flex-1 px-2 py-1 text-sm font-semibold rounded border border-gray-200 bg-white" />
            </div>
            <input v-model="editForm.subtitle" placeholder="副標（如英文書名）" class="w-full px-2 py-1 text-xs italic text-gray-500 rounded border border-gray-200 bg-white" />
            <textarea v-model="editForm.description" placeholder="描述" rows="2" class="w-full px-2 py-1 text-xs rounded border border-gray-200 bg-white resize-none"></textarea>
            <div class="flex items-center gap-2">
              <select v-model="editForm.color" class="px-2 py-1 text-xs rounded border border-gray-200 bg-white">
                <option v-for="c in COLORS" :key="c" :value="c">{{ c }}</option>
              </select>
              <input v-model="editForm.status" placeholder="狀態（如：構思中）" class="flex-1 px-2 py-1 text-xs rounded border border-gray-200 bg-white" />
            </div>
            <input v-model="editForm.slug" placeholder="URL slug（留空自動產生）" class="w-full px-2 py-1 text-xs font-mono rounded border border-gray-200 bg-white" />
            <div class="flex items-center justify-end gap-2 pt-1">
              <button @click="cancelEdit" class="px-3 py-1 text-xs text-gray-500 hover:text-gray-700">取消</button>
              <button @click="saveEdit" :disabled="saving" class="px-3 py-1 text-xs rounded bg-amber-600 text-white hover:bg-amber-700 disabled:opacity-50">
                {{ saving ? '建立中⋯' : '建立' }}
              </button>
            </div>
          </div>
        </div>

      </div>

      <div v-if="!loading && projects.length === 0 && !user" class="mt-12 text-center text-gray-400 text-sm">
        尚無寫作計畫。
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useHead({ title: '寫作計畫 — Know Graph Lab' })
const user = useSupabaseUser()

const COLORS = ['amber','blue','rose','emerald','violet','sky','indigo','cyan','orange','stone','purple']

interface Project {
  id: string
  slug: string
  title: string
  subtitle: string | null
  description: string | null
  emoji: string
  color: string
  status: string | null
  sort_order: number
}

const projects = ref<Project[]>([])
const loading = ref(true)
const saving = ref(false)
const editingSlug = ref<string | null>(null)
const editForm = reactive({ slug: '', title: '', subtitle: '', description: '', emoji: '📝', color: 'amber', status: '' })

async function load() {
  loading.value = true
  try {
    const data = await $fetch<{ projects: Project[] }>('/api/works/projects')
    projects.value = data.projects ?? []
  } finally {
    loading.value = false
  }
}
onMounted(load)

function startCreate() {
  editingSlug.value = '__new__'
  Object.assign(editForm, { slug: '', title: '', subtitle: '', description: '', emoji: '📝', color: 'amber', status: '構思中' })
}

function startEdit(p: Project) {
  editingSlug.value = p.slug
  Object.assign(editForm, {
    slug: p.slug,
    title: p.title,
    subtitle: p.subtitle ?? '',
    description: p.description ?? '',
    emoji: p.emoji,
    color: p.color,
    status: p.status ?? '',
  })
}

function cancelEdit() {
  editingSlug.value = null
}

async function saveEdit() {
  if (!editForm.title.trim()) return
  saving.value = true
  try {
    if (editingSlug.value === '__new__') {
      const res = await authedFetch<{ project: Project }>('/api/works/projects', {
        method: 'POST',
        body: { ...editForm, slug: editForm.slug || undefined },
      })
      projects.value.push(res.project)
    } else if (editingSlug.value) {
      const res = await authedFetch<{ project: Project }>(`/api/works/projects/${editingSlug.value}`, {
        method: 'PATCH',
        body: editForm,
      })
      const idx = projects.value.findIndex(p => p.slug === editingSlug.value)
      if (idx >= 0) projects.value[idx] = res.project
    }
    editingSlug.value = null
  } catch (err: any) {
    alert(`儲存失敗：${err?.data?.message ?? err?.message ?? err}`)
  } finally {
    saving.value = false
  }
}

async function deleteProject(p: Project) {
  if (!confirm(`確定刪除「${p.title}」？此操作會連動刪除所有逐字稿，無法復原。`)) return
  try {
    await authedFetch(`/api/works/projects/${p.slug}`, { method: 'DELETE' })
    projects.value = projects.value.filter(x => x.id !== p.id)
  } catch (err: any) {
    alert(`刪除失敗：${err?.data?.message ?? err?.message ?? err}`)
  }
}

async function move(idx: number, delta: number) {
  const newIdx = idx + delta
  if (newIdx < 0 || newIdx >= projects.value.length) return
  const arr = [...projects.value]
  const [it] = arr.splice(idx, 1)
  arr.splice(newIdx, 0, it)
  projects.value = arr
  try {
    await authedFetch('/api/works/projects/reorder', {
      method: 'PATCH',
      body: { order: arr.map((p, i) => ({ slug: p.slug, sort_order: i })) },
    })
    arr.forEach((p, i) => { p.sort_order = i })
  } catch (err: any) {
    alert(`排序失敗：${err?.data?.message ?? err?.message ?? err}`)
    await load()
  }
}
</script>

<style scoped>
.project-card {
  @apply flex items-start gap-4 p-6 rounded-2xl bg-white border-2 transition-all duration-200 hover:shadow-lg cursor-pointer;
}
.project-icon {
  @apply w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0;
}
.project-title {
  @apply text-sm font-semibold text-gray-900 mb-1;
}
.project-desc {
  @apply text-xs text-gray-500 leading-relaxed line-clamp-3;
}
.card-tool {
  @apply w-7 h-7 rounded-md hover:bg-gray-100 flex items-center justify-center text-sm transition;
}
</style>

<!-- Dynamic Tailwind colors (bg-${color}-*, text-${color}-*, border-${color}-*) are safelisted in tailwind.config.ts -->
