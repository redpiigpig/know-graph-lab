<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Nav header — 左：回上一頁、右：編輯按鈕；container 跟內文同寬 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between gap-4">
        <NuxtLink to="/speech" class="text-gray-400 hover:text-gray-700 transition text-sm">← 演講活動</NuxtLink>
        <div v-if="canEdit" class="flex gap-2">
          <template v-if="!editMode">
            <button @click="startEdit" class="px-3 py-1.5 rounded bg-rose-600 hover:bg-rose-700 text-white text-xs font-medium transition">編輯</button>
          </template>
          <template v-else>
            <button @click="cancelEdit" :disabled="saving" class="px-3 py-1.5 rounded bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium transition">取消</button>
            <button @click="saveEdit" :disabled="saving" class="px-3 py-1.5 rounded bg-rose-600 hover:bg-rose-700 disabled:opacity-50 text-white text-xs font-medium transition">{{ saving ? '儲存中…' : '儲存' }}</button>
          </template>
        </div>
      </div>
    </nav>

    <div v-if="!talk" class="text-center text-gray-400 py-20 text-sm">找不到這場演講</div>

    <template v-else>
      <!-- 標題區 -->
      <div class="bg-white border-b border-gray-100">
        <div class="max-w-6xl mx-auto px-6 py-10 flex flex-col md:flex-row gap-8">
          <!-- 左：海報 -->
          <a v-if="merged.posterPath" :href="merged.posterPath" target="_blank" rel="noopener" class="flex-shrink-0 md:w-48 group">
            <img :src="merged.posterPath" :alt="merged.title" class="w-full rounded-lg shadow-md border border-gray-100 group-hover:shadow-lg group-hover:opacity-90 transition cursor-zoom-in" />
          </a>

          <!-- 右：資訊 -->
          <div class="flex-1 min-w-0">
            <!-- 閱讀模式 -->
            <template v-if="!editMode">
              <div class="flex flex-wrap gap-1.5 mb-3">
                <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-rose-50 text-rose-700">演講活動</span>
                <span class="text-xs text-gray-500">{{ formatDate(merged.date) }}<span v-if="merged.duration"> ‧ {{ merged.duration }}</span></span>
              </div>
              <h1 class="text-2xl font-bold text-gray-900 leading-snug mb-2">{{ merged.title }}</h1>
              <p v-if="merged.subtitle" class="text-base text-gray-600 mb-5">── {{ merged.subtitle }}</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-xs text-gray-500 mb-4">
                <span class="sm:col-span-2"><span class="text-gray-400">場地　</span>{{ merged.venue }}</span>
                <span><span class="text-gray-400">主辦　</span>{{ merged.organizer }}</span>
                <span v-if="merged.course"><span class="text-gray-400">課程　</span>{{ merged.course }}</span>
              </div>
              <p v-if="merged.description" class="text-xs text-gray-500 leading-relaxed mt-3 mb-4">{{ merged.description }}</p>
              <div class="flex flex-wrap gap-2 mt-5">
                <a v-if="talk.pptR2Key"
                  :href="`/api/speech/ppt-download/${talk.id}`"
                  class="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-700 text-xs font-medium transition"
                >📑 下載投影片 (PPTX)</a>
              </div>
            </template>

            <!-- 編輯模式 -->
            <template v-else>
              <div class="space-y-3">
                <label class="block">
                  <span class="text-xs text-gray-500">講題</span>
                  <input v-model="draftMeta.title" class="mt-0.5 w-full text-2xl font-bold text-gray-900 border border-gray-200 rounded px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-rose-300" />
                </label>
                <label class="block">
                  <span class="text-xs text-gray-500">副標</span>
                  <input v-model="draftMeta.subtitle" class="mt-0.5 w-full text-base text-gray-600 border border-gray-200 rounded px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-rose-300" />
                </label>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <label class="block">
                    <span class="text-xs text-gray-500">日期 (YYYY-MM-DD)</span>
                    <input v-model="draftMeta.date" class="mt-0.5 w-full text-sm border border-gray-200 rounded px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-rose-300" />
                  </label>
                  <label class="block">
                    <span class="text-xs text-gray-500">時段</span>
                    <input v-model="draftMeta.duration" placeholder="08:30–10:15" class="mt-0.5 w-full text-sm border border-gray-200 rounded px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-rose-300" />
                  </label>
                  <label class="block sm:col-span-2">
                    <span class="text-xs text-gray-500">場地</span>
                    <input v-model="draftMeta.venue" class="mt-0.5 w-full text-sm border border-gray-200 rounded px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-rose-300" />
                  </label>
                  <label class="block">
                    <span class="text-xs text-gray-500">主辦單位</span>
                    <input v-model="draftMeta.organizer" class="mt-0.5 w-full text-sm border border-gray-200 rounded px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-rose-300" />
                  </label>
                  <label class="block">
                    <span class="text-xs text-gray-500">課程</span>
                    <input v-model="draftMeta.course" class="mt-0.5 w-full text-sm border border-gray-200 rounded px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-rose-300" />
                  </label>
                  <label class="block sm:col-span-2">
                    <span class="text-xs text-gray-500">分類</span>
                    <select v-model="draftMeta.category" class="mt-0.5 w-full text-sm border border-gray-200 rounded px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-rose-300">
                      <option value="lecture">學系專題講座</option>
                      <option value="seminar">研討會專題</option>
                      <option value="public">公開講座</option>
                      <option value="invited">受邀演講</option>
                      <option value="panel">論壇與談</option>
                    </select>
                  </label>
                </div>
                <label class="block">
                  <span class="text-xs text-gray-500">摘要</span>
                  <textarea v-model="draftMeta.description" rows="3" class="mt-0.5 w-full text-sm border border-gray-200 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-rose-300 resize-y"></textarea>
                </label>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- 逐字稿 -->
      <div class="max-w-6xl mx-auto px-6 py-10">
        <div v-if="pending" class="text-center text-gray-400 py-20 text-sm">載入逐字稿…</div>
        <div v-else-if="error" class="text-center text-red-400 py-20 text-sm">無法載入逐字稿</div>
        <article v-else class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          <!-- 編輯模式：整篇 textarea -->
          <div v-if="editMode" class="px-8 py-6 md:px-14">
            <p class="text-xs text-gray-500 mb-2">支援 Markdown：## 主標、### 小標、*斜體*、**粗體**、講者：／提問A：</p>
            <textarea
              v-model="draftContent"
              class="w-full min-h-[70vh] text-base leading-8 text-gray-800 font-mono resize-y border border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-rose-300"
              spellcheck="false"
            ></textarea>
            <p v-if="saveErr" class="mt-2 text-xs text-red-500">儲存失敗：{{ saveErr }}</p>
          </div>

          <!-- 閱讀模式 -->
          <div v-else class="px-8 py-10 md:px-14">
            <template v-for="(b, i) in blocks" :key="i">
              <h2 v-if="b.type === 'h2'" class="text-lg font-bold text-gray-900 mt-10 mb-3 pl-3 border-l-4 border-rose-300">{{ b.text }}</h2>
              <h3 v-else-if="b.type === 'h3'" class="text-base font-semibold text-rose-700 mt-6 mb-2">{{ b.text }}</h3>
              <div v-else-if="b.type === 'speaker'" class="mt-4 mb-1 text-sm font-semibold text-rose-600">{{ b.text }}</div>
              <p v-else-if="b.type === 'note'" class="text-sm text-gray-400 italic my-2 text-center">{{ b.text }}</p>
              <p v-else class="text-base leading-8 text-gray-800 mb-4 indent-[2em]" v-html="inline(b.text)"></p>
            </template>
          </div>
        </article>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useSpeechStore } from '~/stores/speech'

const route = useRoute()
const store = useSpeechStore()
const talk = computed(() => store.talks.find(t => t.id === route.params.id))
const user = useSupabaseUser()
const canEdit = computed(() => !!user.value)

// 載入逐字稿
const { data: txtData, pending, error, refresh: refreshTxt } = useAsyncData(
  () => `speech-txt-${route.params.id}`,
  () => $fetch<string>(`/content/speech/${route.params.id}.txt`, {
    parseResponse: (t) => t,
  }),
  { watch: [() => route.params.id] }
)

// 載入 metadata 旁存檔（若不存在，fallback 為 store 內 entry）
const { data: metaData, refresh: refreshMeta } = useAsyncData(
  () => `speech-meta-${route.params.id}`,
  async () => {
    try {
      return await $fetch<any>(`/content/speech/${route.params.id}.meta.json`)
    } catch { return null }
  },
  { watch: [() => route.params.id] }
)

// 合併 store entry + meta.json（meta.json 優先）
const merged = computed(() => {
  const base = talk.value || ({} as any)
  return { ...base, ...(metaData.value || {}) }
})

useHead({ title: () => (merged.value?.title ? `${merged.value.title} — 演講活動` : '演講活動') })

// 編輯狀態
const editMode = ref(false)
const draftContent = ref('')
const draftMeta = reactive<Record<string, string>>({
  title: '', subtitle: '', date: '', duration: '',
  venue: '', organizer: '', course: '', category: 'lecture', description: '',
})
const saving = ref(false)
const saveErr = ref('')

function startEdit() {
  draftContent.value = (txtData.value as string) || ''
  for (const k of Object.keys(draftMeta)) {
    draftMeta[k] = String((merged.value as any)[k] ?? '')
  }
  saveErr.value = ''
  editMode.value = true
}
function cancelEdit() {
  const dirty =
    draftContent.value !== ((txtData.value as string) || '') ||
    Object.keys(draftMeta).some(k => draftMeta[k] !== String((merged.value as any)[k] ?? ''))
  if (dirty && !confirm('放棄未儲存的修改？')) return
  editMode.value = false
  saveErr.value = ''
}
async function saveEdit() {
  saving.value = true
  saveErr.value = ''
  try {
    await authedFetch(`/api/speech/edit/${route.params.id}`, {
      method: 'POST',
      body: { content: draftContent.value, meta: { ...draftMeta } },
    })
    await Promise.all([refreshTxt(), refreshMeta()])
    editMode.value = false
  } catch (e: any) {
    saveErr.value = e?.statusMessage || e?.message || String(e)
  } finally {
    saving.value = false
  }
}

function formatDate(d: string) {
  if (!d) return ''
  const [y, m, day] = d.split('-')
  return `${y} 年 ${parseInt(m)} 月 ${parseInt(day)} 日`
}

function inline(text: string): string {
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  return escaped
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
}

type Block = { type: 'h2' | 'h3' | 'speaker' | 'note' | 'para'; text: string }

const blocks = computed((): Block[] => {
  if (!txtData.value) return []
  const result: Block[] = []
  for (const raw of (txtData.value as string).split('\n')) {
    const t = raw.trim()
    if (!t) continue
    if (t.startsWith('## ')) { result.push({ type: 'h2', text: t.slice(3).trim() }); continue }
    if (t.startsWith('### ')) { result.push({ type: 'h3', text: t.slice(4).trim() }); continue }
    if (/^（(休息|中斷|備註)/.test(t) || /^\(/.test(t)) { result.push({ type: 'note', text: t }); continue }
    const sp = t.match(/^(講者|主持人|提問[A-Z]?)：(.*)$/)
    if (sp) {
      result.push({ type: 'speaker', text: sp[1] })
      if (sp[2].trim()) result.push({ type: 'para', text: sp[2].trim() })
      continue
    }
    result.push({ type: 'para', text: t })
  }
  return result
})
</script>
