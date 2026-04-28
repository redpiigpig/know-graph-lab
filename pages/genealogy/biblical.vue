<template>
  <div class="flex flex-col bg-slate-50" style="height: 100dvh;">
    <!-- Nav -->
    <nav class="flex items-center gap-2 px-4 h-12 bg-white border-b border-gray-100 flex-shrink-0 z-30">
      <NuxtLink to="/genealogy" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">聖經人物族譜</span>
      <span class="text-xs text-gray-400 ml-1">{{ people.length > 0 ? `${people.length} 人` : '' }}</span>
      <div class="flex-1" />
      <!-- View toggle -->
      <div class="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5">
        <button
          class="text-xs px-2.5 py-1 rounded-md font-medium transition"
          :class="view === 'table' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700'"
          @click="view = 'table'"
        >表格</button>
        <button
          class="text-xs px-2.5 py-1 rounded-md font-medium transition"
          :class="view === 'tree' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700'"
          @click="view = 'tree'"
        >族譜圖</button>
      </div>
      <button
        v-show="view === 'table'"
        class="text-xs px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white font-medium transition shadow-sm ml-1"
        @click="openAdd"
      >+ 新增人物</button>
    </nav>

    <!-- Filter bar (table view only) -->
    <div
      v-show="view === 'table'"
      class="flex items-center gap-2 px-4 h-10 bg-white border-b border-gray-100 flex-shrink-0"
    >
      <div class="relative">
        <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-300 text-[11px] pointer-events-none select-none">🔍</span>
        <input
          v-model="search"
          class="pl-7 pr-3 py-1 text-xs border border-gray-200 rounded-lg outline-none focus:border-amber-400 transition bg-white w-52"
          placeholder="搜尋姓名（中文或英文）…"
        />
      </div>
      <div class="flex gap-1">
        <button
          v-for="g in genderOptions"
          :key="g.value"
          class="text-xs px-2.5 py-1 rounded-lg border transition"
          :class="genderFilter === g.value
            ? 'bg-amber-50 border-amber-300 text-amber-700 font-medium'
            : 'border-gray-200 text-gray-500 hover:bg-gray-50'"
          @click="genderFilter = g.value"
        >{{ g.label }}</button>
      </div>
      <span v-if="search || genderFilter" class="text-xs text-gray-400">{{ filtered.length }} / {{ people.length }} 筆</span>
    </div>

    <!-- Table view -->
    <div v-show="view === 'table'" class="flex-1 min-h-0 overflow-auto p-4">
      <div v-if="loading" class="flex items-center justify-center h-32 text-gray-400 text-sm">載入中…</div>

      <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200">
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">第幾代</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">中文姓名</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">英文姓名</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">性別</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">國別／族別</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">出生年</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">死亡年</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">生子年</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">歲數</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">配偶</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">兒女</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">出處</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">備注</th>
              <th class="px-3 py-2.5 w-16"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filtered.length === 0">
              <td colspan="14" class="px-4 py-10 text-center text-gray-400">
                {{ people.length === 0 ? '尚無資料，點擊「新增人物」開始建立' : '沒有符合的搜尋結果' }}
              </td>
            </tr>
            <tr
              v-for="person in filtered"
              :key="person.id"
              class="border-b border-gray-100 hover:bg-amber-50/30 transition group"
            >
              <td class="px-3 py-2 text-gray-500 whitespace-nowrap text-xs">{{ person.generation != null ? `第 ${person.generation} 代` : '—' }}</td>
              <td class="px-3 py-2 font-medium text-gray-900 whitespace-nowrap">{{ person.name_zh }}</td>
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap">{{ person.name_en || '—' }}</td>
              <td class="px-3 py-2 whitespace-nowrap">
                <span v-if="person.gender" :class="genderClass(person.gender)" class="px-1.5 py-0.5 rounded text-xs font-medium">
                  {{ person.gender }}
                </span>
                <span v-else class="text-gray-300">—</span>
              </td>
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap">{{ person.nationality || '—' }}</td>
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap">{{ formatYear(person.birth_year) }}</td>
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap">{{ formatYear(person.death_year) }}</td>
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap">{{ formatYear(person.child_year) }}</td>
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap">{{ person.age ?? '—' }}</td>
              <td class="px-3 py-2 text-gray-600 max-w-[140px] truncate" :title="person.spouse || ''">{{ person.spouse || '—' }}</td>
              <td class="px-3 py-2 text-gray-600 max-w-[160px]">
                <span v-if="!person.children">—</span>
                <template v-else-if="person.children.length <= 18">{{ person.children }}</template>
                <template v-else>
                  <span class="truncate block">{{ person.children.slice(0, 18) }}…</span>
                  <button
                    class="text-[10px] text-indigo-500 hover:text-indigo-700 hover:underline leading-none mt-0.5"
                    @click="openDetail('兒女', person.children, person.name_zh)"
                  >展開</button>
                </template>
              </td>
              <td
                class="px-3 py-2 max-w-[200px] truncate text-xs"
                :class="person.sources ? 'text-indigo-600 cursor-pointer hover:text-indigo-800 hover:underline' : 'text-gray-300'"
                @click="person.sources && openDetail('出處', person.sources, person.name_zh)"
              >{{ person.sources || '—' }}</td>
              <td
                class="px-3 py-2 max-w-[180px] truncate text-xs"
                :class="person.notes ? 'text-gray-500 cursor-pointer hover:text-gray-800 hover:underline' : 'text-gray-300'"
                @click="person.notes && openDetail('備注', person.notes, person.name_zh)"
              >{{ person.notes || '—' }}</td>
              <td class="px-3 py-2">
                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                  <button class="p-1 rounded hover:bg-amber-100 text-amber-600 text-xs" @click="openEdit(person)">編輯</button>
                  <button class="p-1 rounded hover:bg-red-50 text-red-400 text-xs" @click="deletePerson(person.id)">刪除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tree view (always mounted so canvas stays alive) -->
    <div v-show="view === 'tree'" class="flex-1 min-h-0 flex flex-col">
      <!-- Tree controls -->
      <div class="flex-shrink-0 flex items-center gap-2 px-4 h-10 bg-white border-b border-gray-100">
        <span class="text-xs text-gray-400">{{ treeStatus }}</span>
        <div class="flex-1" />
        <div class="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5">
          <button
            v-for="d in layoutDirs"
            :key="d.value"
            class="text-xs px-2 py-0.5 rounded-md transition"
            :class="treeDir === d.value ? 'bg-white shadow-sm text-gray-800 font-medium' : 'text-gray-500 hover:text-gray-700'"
            @click="treeDir = d.value; treeCanvasRef?.applyLayout(treeDir)"
          >{{ d.label }}</button>
        </div>
        <button
          class="text-xs px-2.5 py-1 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition"
          @click="treeCanvasRef?.fitAll()"
        >⊡ 適合頁面</button>
      </div>
      <!-- VueFlow canvas -->
      <div class="flex-1 min-h-0">
        <ClientOnly>
          <GenealogyCanvas ref="treeCanvasRef" class="w-full h-full" />
          <template #fallback>
            <div class="w-full h-full flex items-center justify-center text-gray-300 text-sm">載入中…</div>
          </template>
        </ClientOnly>
      </div>
    </div>

    <!-- Detail modal (出處 / 備注) -->
    <div
      v-if="detail.show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 px-4"
      @click.self="detail.show = false"
    >
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div>
            <h2 class="font-semibold text-gray-900">{{ detail.personName }}</h2>
            <p class="text-xs text-gray-400 mt-0.5">{{ detail.title }}</p>
          </div>
          <button class="text-gray-400 hover:text-gray-600 text-lg leading-none" @click="detail.show = false">×</button>
        </div>
        <div class="px-5 py-4 max-h-[60vh] overflow-y-auto">
          <!-- Sources: semicolon-separated list -->
          <template v-if="detail.title === '出處'">
            <ul class="space-y-1.5">
              <li
                v-for="(src, i) in detail.body.split(/[;；]/).map(s => s.trim()).filter(Boolean)"
                :key="i"
                class="flex items-start gap-2 text-sm text-indigo-700"
              >
                <span class="text-indigo-300 mt-0.5 flex-shrink-0">▸</span>
                <span>{{ src }}</span>
              </li>
            </ul>
          </template>
          <!-- Children: comma-separated list -->
          <template v-else-if="detail.title === '兒女'">
            <ul class="space-y-1.5">
              <li
                v-for="(child, i) in detail.body.split(/[,，、]/).map(s => s.trim()).filter(Boolean)"
                :key="i"
                class="flex items-start gap-2 text-sm text-gray-700"
              >
                <span class="text-gray-300 mt-0.5 flex-shrink-0">▸</span>
                <span>{{ child }}</span>
              </li>
            </ul>
          </template>
          <!-- Notes: plain text with line breaks -->
          <p v-else class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ detail.body }}</p>
        </div>
      </div>
    </div>

    <!-- Add / Edit modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 px-4" @click.self="showModal = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-900">{{ editingId ? '編輯人物' : '新增人物' }}</h2>
          <button class="text-gray-400 hover:text-gray-600 text-lg leading-none" @click="showModal = false">×</button>
        </div>
        <div class="p-5 grid grid-cols-2 gap-3">
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">中文姓名 *</label>
            <input v-model="form.name_zh" class="field" placeholder="例：亞伯拉罕" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">英文姓名</label>
            <input v-model="form.name_en" class="field" placeholder="Abraham" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">性別</label>
            <select v-model="form.gender" class="field">
              <option value="">—</option>
              <option value="男">男</option>
              <option value="女">女</option>
              <option value="不明">不明</option>
            </select>
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">國別／族別</label>
            <input v-model="form.nationality" class="field" placeholder="例：希伯來人、猶大支派" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">第幾代（以亞當為第1代）</label>
            <input v-model.number="form.generation" type="number" class="field" placeholder="1" min="1" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">出生年（主前負數）</label>
            <input v-model.number="form.birth_year" type="number" class="field" placeholder="-2000" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">死亡年</label>
            <input v-model.number="form.death_year" type="number" class="field" placeholder="-1825" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">生子年</label>
            <input v-model.number="form.child_year" type="number" class="field" placeholder="-1900" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">歲數</label>
            <input v-model.number="form.age" type="number" class="field" placeholder="175" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">配偶（逗號分隔）</label>
            <input v-model="form.spouse" class="field" placeholder="例：撒拉、夏甲、基土拉" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">兒女（逗號分隔）</label>
            <input v-model="form.children" class="field" placeholder="例：以實瑪利、以撒" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">出處（分號分隔多處）</label>
            <input v-model="form.sources" class="field" placeholder="例：創世記 5:1-5; 歷代志上 1:1" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">備注</label>
            <textarea v-model="form.notes" class="field resize-none h-20" placeholder="聖經記載的額外資訊…" />
          </div>
        </div>
        <div class="flex justify-end gap-2 px-5 py-4 border-t border-gray-100">
          <button class="px-4 py-2 text-sm rounded-lg text-gray-600 hover:bg-gray-100 transition" @click="showModal = false">取消</button>
          <button
            class="px-4 py-2 text-sm rounded-lg bg-amber-500 hover:bg-amber-600 text-white font-medium transition disabled:opacity-50"
            :disabled="saving || !form.name_zh.trim()"
            @click="save"
          >{{ saving ? '儲存中…' : '儲存' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '聖經人物族譜 — Know Graph Lab' })

interface Person {
  id: string
  name_zh: string
  name_en: string | null
  gender: string | null
  nationality: string | null
  generation: number | null
  birth_year: number | null
  death_year: number | null
  child_year: number | null
  age: number | null
  spouse: string | null
  children: string | null
  sources: string | null
  notes: string | null
}

// ── Auth ───────────────────────────────────────────────────
const supabase = useSupabaseClient()
const router   = useRouter()

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) { router.push('/login'); return null }
  return session.access_token
}

// ── Core state ─────────────────────────────────────────────
const loading   = ref(true)
const saving    = ref(false)
const showModal = ref(false)
const editingId = ref<string | null>(null)
const people    = ref<Person[]>([])
const form      = ref(emptyForm())

// ── View / search ──────────────────────────────────────────
const view         = ref<'table' | 'tree'>('table')
const search       = ref('')
const genderFilter = ref('')
const genderOptions = [
  { value: '', label: '全部' },
  { value: '男', label: '男' },
  { value: '女', label: '女' },
]

const filtered = computed(() => {
  let list = people.value
  if (genderFilter.value) list = list.filter(p => p.gender === genderFilter.value)
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    list = list.filter(p =>
      p.name_zh.toLowerCase().includes(q) ||
      (p.name_en || '').toLowerCase().includes(q)
    )
  }
  return list
})

// ── Detail popup (sources / notes) ────────────────────────
const detail = ref({ show: false, title: '', body: '', personName: '' })

function openDetail(title: string, body: string, personName: string) {
  detail.value = { show: true, title, body, personName }
}

// ── Tree view ──────────────────────────────────────────────
const treeCanvasRef = ref()
const treeDir       = ref<'TB' | 'LR'>('TB')
const treeStatus    = ref('點擊「族譜圖」載入')
const treeLoaded    = ref(false)
const layoutDirs    = [
  { value: 'TB', label: '↓ 上下' },
  { value: 'LR', label: '→ 左右' },
]

async function loadTree() {
  if (treeLoaded.value) return
  treeLoaded.value = true
  treeStatus.value = '載入中…'
  try {
    const token = await getToken()
    if (!token) { treeLoaded.value = false; return }
    const { nodes, edges } = await $fetch<{ nodes: any[], edges: any[] }>('/api/genealogy/biblical-graph', {
      headers: { Authorization: `Bearer ${token}` },
    })
    await nextTick()
    treeCanvasRef.value?.importData(nodes, edges)
    const pcCount = edges.filter((e: any) => e.data?.relationshipType === 'parentChild').length
    const spCount = edges.filter((e: any) => e.data?.relationshipType === 'spouse').length
    treeStatus.value = `${nodes.length} 人`
    nextTick(() => {
      treeCanvasRef.value?.applyLayout(treeDir.value)
      treeStatus.value = `${nodes.length} 人 · ${pcCount} 親子 · ${spCount} 配偶`
    })
  } catch {
    treeStatus.value = '載入失敗，請重新整理'
    treeLoaded.value = false
  }
}

watch(view, (val) => {
  if (val === 'tree') loadTree()
})

// ── CRUD ───────────────────────────────────────────────────
function emptyForm() {
  return {
    name_zh: '', name_en: '', gender: '', nationality: '',
    generation: null as number | null,
    birth_year: null as number | null, death_year: null as number | null,
    child_year: null as number | null, age: null as number | null,
    spouse: '', children: '', sources: '', notes: '',
  }
}

async function load() {
  loading.value = true
  const token = await getToken()
  if (!token) { loading.value = false; return }
  const data = await $fetch<Person[]>('/api/genealogy/biblical-people', {
    headers: { Authorization: `Bearer ${token}` },
  })
  people.value = data
  loading.value = false
}

function openAdd() {
  editingId.value = null
  form.value = emptyForm()
  showModal.value = true
}

function openEdit(p: Person) {
  editingId.value = p.id
  form.value = {
    name_zh:     p.name_zh     || '',
    name_en:     p.name_en     || '',
    gender:      p.gender      || '',
    nationality: p.nationality || '',
    generation:  p.generation  ?? null,
    birth_year:  p.birth_year  ?? null,
    death_year:  p.death_year  ?? null,
    child_year:  p.child_year  ?? null,
    age:         p.age         ?? null,
    spouse:      p.spouse      || '',
    children:    p.children    || '',
    sources:     p.sources     || '',
    notes:       p.notes       || '',
  }
  showModal.value = true
}

async function save() {
  if (!form.value.name_zh.trim()) return
  saving.value = true
  try {
    const token = await getToken()
    if (!token) return
    if (editingId.value) {
      const updated = await $fetch<Person>(`/api/genealogy/biblical-people/${editingId.value}`, {
        method: 'PATCH', body: form.value,
        headers: { Authorization: `Bearer ${token}` },
      })
      const idx = people.value.findIndex(p => p.id === editingId.value)
      if (idx >= 0) people.value[idx] = updated
    } else {
      const created = await $fetch<Person>('/api/genealogy/biblical-people', {
        method: 'POST', body: form.value,
        headers: { Authorization: `Bearer ${token}` },
      })
      people.value.push(created)
    }
    showModal.value = false
    // Invalidate tree so it reloads with fresh data
    treeLoaded.value = false
    if (view.value === 'tree') loadTree()
  } finally {
    saving.value = false
  }
}

async function deletePerson(id: string) {
  if (!confirm('確定刪除此人物？')) return
  const token = await getToken()
  if (!token) return
  await $fetch(`/api/genealogy/biblical-people/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  people.value = people.value.filter(p => p.id !== id)
  treeLoaded.value = false
  if (view.value === 'tree') loadTree()
}

function formatYear(y: number | null) {
  if (y == null) return '—'
  return y < 0 ? `主前 ${Math.abs(y)}` : `${y}`
}

function genderClass(g: string) {
  if (g === '男') return 'bg-blue-50 text-blue-700'
  if (g === '女') return 'bg-pink-50 text-pink-700'
  return 'bg-gray-100 text-gray-500'
}

onMounted(load)
</script>

<style scoped>
.field {
  @apply w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-200 transition bg-white;
}
</style>
