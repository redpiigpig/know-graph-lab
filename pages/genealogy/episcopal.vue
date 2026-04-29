<template>
  <div class="flex flex-col bg-slate-50" style="height: 100dvh;">
    <!-- Nav -->
    <nav class="flex items-center gap-2 px-4 h-12 bg-white border-b border-gray-100 flex-shrink-0 z-30">
      <NuxtLink to="/genealogy" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">使徒統緒</span>
      <span class="text-xs text-gray-400 ml-1">{{ bishops.length > 0 ? `${bishops.length} 位` : '' }}</span>
      <div class="flex-1" />
      <button
        class="text-xs px-3 py-1.5 rounded-lg bg-violet-500 hover:bg-violet-600 text-white font-medium transition shadow-sm"
        @click="openAdd"
      >+ 新增主教</button>
    </nav>

    <!-- Filter bar -->
    <div class="flex items-center gap-2 px-4 h-10 bg-white border-b border-gray-100 flex-shrink-0 flex-wrap">
      <div class="relative">
        <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-300 text-[11px] pointer-events-none select-none">🔍</span>
        <input
          v-model="search"
          class="pl-7 pr-3 py-1 text-xs border border-gray-200 rounded-lg outline-none focus:border-violet-400 transition bg-white w-44"
          placeholder="搜尋姓名…"
        />
      </div>
      <!-- See filter -->
      <div class="flex gap-1">
        <button
          v-for="s in seeOptions"
          :key="s"
          class="text-xs px-2.5 py-1 rounded-lg border transition"
          :class="seeFilter === s
            ? 'bg-violet-50 border-violet-300 text-violet-700 font-medium'
            : 'border-gray-200 text-gray-500 hover:bg-gray-50'"
          @click="seeFilter = s"
        >{{ s === '' ? '全部' : s }}</button>
      </div>
      <div class="w-px h-5 bg-gray-200" />
      <!-- Status filter -->
      <div class="flex gap-1">
        <button
          v-for="st in statusOptions"
          :key="st.value"
          class="text-xs px-2.5 py-1 rounded-lg border transition"
          :class="statusFilter === st.value
            ? 'bg-gray-800 border-gray-800 text-white font-medium'
            : 'border-gray-200 text-gray-500 hover:bg-gray-50'"
          @click="statusFilter = st.value"
        >{{ st.label }}</button>
      </div>
      <span v-if="search || seeFilter || statusFilter" class="text-xs text-gray-400">{{ filtered.length }} / {{ bishops.length }} 筆</span>
    </div>

    <!-- Table -->
    <div class="flex-1 min-h-0 overflow-auto p-4">
      <div v-if="loading" class="flex items-center justify-center h-32 text-gray-400 text-sm">載入中…</div>

      <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200">
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">主教座</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">教會傳統</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">任次</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">中文名</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">英文名</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">身份</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">就任年</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">卸任年</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">卸任原因</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">任命者</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">出處</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">備注</th>
              <th class="px-3 py-2.5 w-16"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filtered.length === 0">
              <td colspan="13" class="px-4 py-10 text-center text-gray-400">
                {{ bishops.length === 0 ? '尚無資料，點擊「新增主教」開始建立' : '沒有符合的搜尋結果' }}
              </td>
            </tr>
            <template v-for="(group, see) in groupedFiltered" :key="see">
              <!-- See header row -->
              <tr class="bg-violet-50/60 border-b border-violet-100">
                <td colspan="13" class="px-3 py-1.5">
                  <span class="text-xs font-semibold text-violet-700">{{ see }}</span>
                </td>
              </tr>
              <tr
                v-for="bishop in group"
                :key="bishop.id"
                class="border-b border-gray-100 hover:bg-violet-50/20 transition group"
              >
                <td class="px-3 py-2 text-gray-500 whitespace-nowrap text-xs">{{ bishop.see }}</td>
                <td class="px-3 py-2 text-gray-600 whitespace-nowrap text-xs max-w-[120px] truncate" :title="bishop.church || ''">{{ bishop.church || '—' }}</td>
                <td class="px-3 py-2 text-gray-500 whitespace-nowrap text-xs">{{ bishop.succession_number != null ? `第 ${bishop.succession_number} 任` : '—' }}</td>
                <td class="px-3 py-2 font-medium text-gray-900 whitespace-nowrap">{{ bishop.name_zh }}</td>
                <td class="px-3 py-2 text-gray-600 whitespace-nowrap text-xs">{{ bishop.name_en || '—' }}</td>
                <td class="px-3 py-2 whitespace-nowrap">
                  <span :class="statusClass(bishop.status)" class="px-1.5 py-0.5 rounded text-xs font-medium">
                    {{ bishop.status }}
                  </span>
                </td>
                <td class="px-3 py-2 text-gray-600 whitespace-nowrap text-xs">{{ formatYear(bishop.start_year) }}</td>
                <td class="px-3 py-2 text-gray-600 whitespace-nowrap text-xs">{{ formatYear(bishop.end_year) }}</td>
                <td class="px-3 py-2 text-gray-500 whitespace-nowrap text-xs">{{ bishop.end_reason || '—' }}</td>
                <td class="px-3 py-2 text-gray-600 whitespace-nowrap text-xs max-w-[120px] truncate" :title="bishop.appointed_by || ''">{{ bishop.appointed_by || '—' }}</td>
                <td
                  class="px-3 py-2 max-w-[180px] truncate text-xs"
                  :class="bishop.sources ? 'text-indigo-600 cursor-pointer hover:text-indigo-800 hover:underline' : 'text-gray-300'"
                  @click="bishop.sources && openDetail('出處', bishop.sources, bishop.name_zh)"
                >{{ bishop.sources || '—' }}</td>
                <td
                  class="px-3 py-2 max-w-[160px] truncate text-xs"
                  :class="bishop.notes ? 'text-gray-500 cursor-pointer hover:text-gray-800 hover:underline' : 'text-gray-300'"
                  @click="bishop.notes && openDetail('備注', bishop.notes, bishop.name_zh)"
                >{{ bishop.notes || '—' }}</td>
                <td class="px-3 py-2">
                  <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                    <button class="p-1 rounded hover:bg-violet-100 text-violet-600 text-xs" @click="openEdit(bishop)">編輯</button>
                    <button class="p-1 rounded hover:bg-red-50 text-red-400 text-xs" @click="deleteBishop(bishop.id)">刪除</button>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Detail modal -->
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
          <p v-else class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ detail.body }}</p>
        </div>
      </div>
    </div>

    <!-- Add / Edit modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 px-4" @click.self="showModal = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-900">{{ editingId ? '編輯主教' : '新增主教' }}</h2>
          <button class="text-gray-400 hover:text-gray-600 text-lg leading-none" @click="showModal = false">×</button>
        </div>
        <div class="p-5 grid grid-cols-2 gap-3">
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">中文名 *</label>
            <input v-model="form.name_zh" class="field" placeholder="例：聖伯多祿" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">英文名</label>
            <input v-model="form.name_en" class="field" placeholder="Saint Peter" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">主教座 *</label>
            <input v-model="form.see" class="field" placeholder="例：羅馬、安提阿" list="see-list" />
            <datalist id="see-list">
              <option v-for="s in knownSees" :key="s" :value="s" />
            </datalist>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">教會傳統</label>
            <input v-model="form.church" class="field" placeholder="例：未分裂教會、東正教" list="church-list" />
            <datalist id="church-list">
              <option v-for="c in knownChurches" :key="c" :value="c" />
            </datalist>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">任次</label>
            <input v-model.number="form.succession_number" type="number" class="field" placeholder="1" min="1" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">身份</label>
            <select v-model="form.status" class="field">
              <option value="正統">正統</option>
              <option value="對立">對立</option>
              <option value="廢黜後復位">廢黜後復位</option>
              <option value="爭議">爭議</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">就任年（主前負數）</label>
            <input v-model.number="form.start_year" type="number" class="field" placeholder="30" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">卸任年</label>
            <input v-model.number="form.end_year" type="number" class="field" placeholder="64" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">卸任原因</label>
            <select v-model="form.end_reason" class="field">
              <option value="">—</option>
              <option value="殉道">殉道</option>
              <option value="自然死亡">自然死亡</option>
              <option value="辭職">辭職</option>
              <option value="廢黜">廢黜</option>
              <option value="不明">不明</option>
            </select>
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">任命者（第一任適用）</label>
            <input v-model="form.appointed_by" class="field" placeholder="例：耶穌基督、使徒彼得" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">出處（分號分隔多處）</label>
            <input v-model="form.sources" class="field" placeholder="例：Eusebius, HE III.3; Irenaeus, AH III.3" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">備注</label>
            <textarea v-model="form.notes" class="field resize-none h-20" placeholder="補充說明…" />
          </div>
        </div>
        <div class="flex justify-end gap-2 px-5 py-4 border-t border-gray-100">
          <button class="px-4 py-2 text-sm rounded-lg text-gray-600 hover:bg-gray-100 transition" @click="showModal = false">取消</button>
          <button
            class="px-4 py-2 text-sm rounded-lg bg-violet-500 hover:bg-violet-600 text-white font-medium transition disabled:opacity-50"
            :disabled="saving || !form.name_zh.trim() || !form.see.trim()"
            @click="save"
          >{{ saving ? '儲存中…' : '儲存' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '使徒統緒 — Know Graph Lab' })

interface Bishop {
  id: string
  name_zh: string
  name_en: string | null
  see: string
  church: string | null
  succession_number: number | null
  start_year: number | null
  end_year: number | null
  end_reason: string | null
  appointed_by: string | null
  status: string
  sources: string | null
  notes: string | null
}

const supabase = useSupabaseClient()
const router   = useRouter()

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) { router.push('/login'); return null }
  return session.access_token
}

// ── State ──────────────────────────────────────────────────
const loading   = ref(true)
const saving    = ref(false)
const showModal = ref(false)
const editingId = ref<string | null>(null)
const bishops   = ref<Bishop[]>([])
const form      = ref(emptyForm())

// ── Filters ────────────────────────────────────────────────
const search       = ref('')
const seeFilter    = ref('')
const statusFilter = ref('')

const knownSees     = ['羅馬', '君士坦丁堡', '亞歷山大', '安提阿', '耶路撒冷']
const knownChurches = ['未分裂教會', '東正教', '天主教', '科普特正教', '科普特天主教', '敘利亞正教', '敘利亞天主教', '馬龍尼特禮天主教', '希臘天主教麥勒基特禮', '亞美尼亞正教', '天主教（拉丁禮）', '天主教（亞維農系）', '天主教（比薩系）']

const seeOptions    = computed(() => ['', ...Array.from(new Set(bishops.value.map(b => b.see))).sort()])
const statusOptions = [
  { value: '', label: '全部' },
  { value: '正統', label: '正統' },
  { value: '對立', label: '對立' },
]

const filtered = computed(() => {
  let list = bishops.value
  if (seeFilter.value)    list = list.filter(b => b.see === seeFilter.value)
  if (statusFilter.value) list = list.filter(b => b.status === statusFilter.value)
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    list = list.filter(b =>
      b.name_zh.toLowerCase().includes(q) ||
      (b.name_en || '').toLowerCase().includes(q)
    )
  }
  return list
})

const groupedFiltered = computed(() => {
  const groups: Record<string, Bishop[]> = {}
  for (const b of filtered.value) {
    if (!groups[b.see]) groups[b.see] = []
    groups[b.see].push(b)
  }
  return groups
})

// ── Detail popup ───────────────────────────────────────────
const detail = ref({ show: false, title: '', body: '', personName: '' })
function openDetail(title: string, body: string, personName: string) {
  detail.value = { show: true, title, body, personName }
}

// ── CRUD ───────────────────────────────────────────────────
function emptyForm() {
  return {
    name_zh: '', name_en: '', see: '', church: '',
    succession_number: null as number | null,
    start_year: null as number | null,
    end_year: null as number | null,
    end_reason: '',
    appointed_by: '',
    status: '正統',
    sources: '', notes: '',
  }
}

async function load() {
  loading.value = true
  const token = await getToken()
  if (!token) { loading.value = false; return }
  bishops.value = await $fetch<Bishop[]>('/api/genealogy/episcopal-succession', {
    headers: { Authorization: `Bearer ${token}` },
  })
  loading.value = false
}

function openAdd() {
  editingId.value = null
  form.value = emptyForm()
  showModal.value = true
}

function openEdit(b: Bishop) {
  editingId.value = b.id
  form.value = {
    name_zh:           b.name_zh           || '',
    name_en:           b.name_en           || '',
    see:               b.see               || '',
    church:            b.church            || '',
    succession_number: b.succession_number ?? null,
    start_year:        b.start_year        ?? null,
    end_year:          b.end_year          ?? null,
    end_reason:        b.end_reason        || '',
    appointed_by:      b.appointed_by      || '',
    status:            b.status            || '正統',
    sources:           b.sources           || '',
    notes:             b.notes             || '',
  }
  showModal.value = true
}

async function save() {
  if (!form.value.name_zh.trim() || !form.value.see.trim()) return
  saving.value = true
  try {
    const token = await getToken()
    if (!token) return
    if (editingId.value) {
      const updated = await $fetch<Bishop>(`/api/genealogy/episcopal-succession/${editingId.value}`, {
        method: 'PATCH', body: form.value,
        headers: { Authorization: `Bearer ${token}` },
      })
      const idx = bishops.value.findIndex(b => b.id === editingId.value)
      if (idx >= 0) bishops.value[idx] = updated
    } else {
      const created = await $fetch<Bishop>('/api/genealogy/episcopal-succession', {
        method: 'POST', body: form.value,
        headers: { Authorization: `Bearer ${token}` },
      })
      bishops.value.push(created)
      bishops.value.sort((a, b) =>
        a.see.localeCompare(b.see) ||
        (a.church || '').localeCompare(b.church || '') ||
        ((a.succession_number ?? 9999) - (b.succession_number ?? 9999))
      )
    }
    showModal.value = false
  } finally {
    saving.value = false
  }
}

async function deleteBishop(id: string) {
  if (!confirm('確定刪除此筆資料？')) return
  const token = await getToken()
  if (!token) return
  await $fetch(`/api/genealogy/episcopal-succession/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  bishops.value = bishops.value.filter(b => b.id !== id)
}

function formatYear(y: number | null) {
  if (y == null) return '—'
  return y < 0 ? `主前 ${Math.abs(y)}` : `${y}`
}

function statusClass(s: string) {
  if (s === '正統')    return 'bg-emerald-50 text-emerald-700'
  if (s === '對立')    return 'bg-red-50 text-red-600'
  if (s === '廢黜後復位') return 'bg-amber-50 text-amber-700'
  return 'bg-gray-100 text-gray-500'
}

onMounted(load)
</script>

<style scoped>
.field {
  @apply w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-violet-400 focus:ring-1 focus:ring-violet-200 transition bg-white;
}
</style>
