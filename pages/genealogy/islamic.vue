<template>
  <div class="flex flex-col bg-slate-50" style="height: 100dvh;">
    <nav class="flex items-center gap-2 px-4 h-12 bg-white border-b border-gray-100 flex-shrink-0 z-30">
      <NuxtLink to="/genealogy" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">伊斯蘭族譜</span>
      <span class="text-xs text-gray-400 ml-1">{{ people.length > 0 ? `${people.length} 人` : '' }}</span>
      <div class="flex-1" />
      <div class="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5">
        <span class="text-xs px-2.5 py-1 rounded-md font-medium bg-white shadow-sm text-gray-900">表格</span>
        <NuxtLink
          to="/genealogy/islamic-tree"
          class="text-xs px-2.5 py-1 rounded-md font-medium transition text-gray-500 hover:text-gray-700"
        >族譜圖</NuxtLink>
      </div>
      <button
        class="text-xs px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-medium transition shadow-sm ml-1"
        @click="openAdd"
      >+ 新增人物</button>
    </nav>

    <!-- Filter bar -->
    <div class="flex flex-wrap items-center gap-2 px-4 py-2 bg-white border-b border-gray-100 flex-shrink-0">
      <div class="relative">
        <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-300 text-[11px] pointer-events-none select-none">🔍</span>
        <input
          v-model="search"
          class="pl-7 pr-3 py-1 text-xs border border-gray-200 rounded-lg outline-none focus:border-emerald-400 transition bg-white w-56"
          placeholder="搜尋姓名（中文／阿拉伯／英文）…"
        />
      </div>
      <div class="flex flex-wrap gap-1">
        <button
          v-for="t in traditionOptions"
          :key="t.value"
          class="text-xs px-2.5 py-1 rounded-lg border transition"
          :class="traditionFilter === t.value
            ? `${t.bg} ${t.border} ${t.text} font-medium`
            : 'border-gray-200 text-gray-500 hover:bg-gray-50'"
          @click="traditionFilter = traditionFilter === t.value ? '' : t.value"
        >
          <span class="inline-block w-2 h-2 rounded-full mr-1 align-middle" :class="t.dot" />
          {{ t.label }}
        </button>
      </div>
      <span v-if="search || traditionFilter" class="text-xs text-gray-400">{{ filtered.length }} / {{ people.length }} 筆</span>
    </div>

    <!-- Table -->
    <div class="flex-1 min-h-0 overflow-auto p-4">
      <div v-if="loading" class="flex items-center justify-center h-32 text-gray-400 text-sm">載入中…</div>
      <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200">
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap w-14">代</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">中文姓名</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap" dir="rtl">الاسم</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">英文</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">傳統</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600 whitespace-nowrap">性別</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600">配偶</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600">兒女</th>
              <th class="px-3 py-2.5 text-left font-medium text-gray-600">出處</th>
              <th class="px-3 py-2.5 w-16"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filtered.length === 0">
              <td colspan="10" class="px-4 py-10 text-center text-gray-400">
                {{ people.length === 0 ? '尚無資料' : '沒有符合的搜尋結果' }}
              </td>
            </tr>
            <tr
              v-for="p in filtered"
              :key="p.id"
              class="border-b border-gray-100 hover:bg-gray-50 transition group"
              :class="rowBg(p.tradition)"
            >
              <td class="px-3 py-2 text-gray-400 text-xs">{{ p.generation ?? '—' }}</td>
              <td class="px-3 py-2 font-medium text-gray-900 whitespace-nowrap">{{ p.name_zh }}<span v-if="p.kunya" class="ml-1 text-xs text-gray-400">·{{ p.kunya }}</span></td>
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap" dir="rtl">{{ p.name_ar }}</td>
              <td class="px-3 py-2 text-gray-500 text-xs whitespace-nowrap">{{ p.name_en }}</td>
              <td class="px-3 py-2 whitespace-nowrap">
                <span class="text-[10px] px-1.5 py-0.5 rounded font-medium" :class="traditionBadge(p.tradition)">{{ traditionLabel(p.tradition) }}</span>
              </td>
              <td class="px-3 py-2 text-gray-500 text-xs">{{ p.gender }}</td>
              <td class="px-3 py-2 text-gray-700 text-xs max-w-[200px] truncate" :title="p.spouse">{{ p.spouse || '—' }}</td>
              <td class="px-3 py-2 text-gray-700 text-xs max-w-[260px] truncate" :title="p.children">{{ p.children || '—' }}</td>
              <td class="px-3 py-2 text-gray-500 text-xs max-w-[320px] truncate" :title="p.sources">{{ p.sources || '—' }}</td>
              <td class="px-3 py-2">
                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                  <button class="p-1 rounded hover:bg-emerald-100 text-emerald-600 text-xs" @click="openEdit(p)">編輯</button>
                  <button class="p-1 rounded hover:bg-red-50 text-red-400 text-xs" @click="deletePerson(p.id)">刪除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add / Edit modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 px-4" @click.self="showModal = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-900">{{ editingId ? '編輯人物' : '新增人物' }}</h2>
          <button class="text-gray-400 hover:text-gray-600 text-lg leading-none" @click="showModal = false">×</button>
        </div>
        <div class="p-5 grid grid-cols-2 gap-3">
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">中文姓名 *</label>
            <input v-model="form.name_zh" class="field" placeholder="例：阿里（艾比·塔利卜之子）" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">阿拉伯文姓名</label>
            <input v-model="form.name_ar" class="field" placeholder="علي بن أبي طالب" dir="rtl" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">英文姓名</label>
            <input v-model="form.name_en" class="field" placeholder="Ali ibn Abi Talib" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Kunya（父子稱呼）</label>
            <input v-model="form.kunya" class="field" placeholder="Abu al-Hasan" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">性別</label>
            <select v-model="form.gender" class="field">
              <option value="">—</option>
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">傳統 *</label>
            <select v-model="form.tradition" class="field">
              <option v-for="t in traditionOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">國別／族別</label>
            <input v-model="form.nationality" class="field" placeholder="例：阿拉伯人、古先民、科普特人" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">第幾代（阿丹 = 1）</label>
            <input v-model.number="form.generation" type="number" class="field" placeholder="44" min="1" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">同代排序</label>
            <input v-model.number="form.sort_order" type="number" class="field" placeholder="0" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">出生年（公元前負數）</label>
            <input v-model.number="form.birth_year" type="number" class="field" placeholder="570" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">死亡年</label>
            <input v-model.number="form.death_year" type="number" class="field" placeholder="632" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">生子年</label>
            <input v-model.number="form.child_year" type="number" class="field" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">歲數</label>
            <input v-model.number="form.age" type="number" class="field" placeholder="63" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">配偶（、或逗號分隔）</label>
            <input v-model="form.spouse" class="field" placeholder="例：赫蒂徹、阿伊莎" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">兒女（、或逗號分隔）</label>
            <input v-model="form.children" class="field" placeholder="例：法蒂瑪（穆聖之女）、嘎西姆" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">出處（古蘭章節 ／ 聖訓 ／ 史料）</label>
            <input v-model="form.sources" class="field" placeholder="例：古蘭 33:37-38" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">備注</label>
            <textarea v-model="form.notes" class="field resize-none h-20" />
          </div>
        </div>
        <div class="flex justify-end gap-2 px-5 py-4 border-t border-gray-100">
          <button class="px-4 py-2 text-sm rounded-lg text-gray-600 hover:bg-gray-100 transition" @click="showModal = false">取消</button>
          <button
            class="px-4 py-2 text-sm rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-medium transition disabled:opacity-50"
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
useHead({ title: '伊斯蘭族譜 — Know Graph Lab' })

type Person = {
  id: string
  name_zh: string
  name_ar?: string | null
  name_en?: string | null
  kunya?: string | null
  gender?: string | null
  nationality?: string | null
  generation?: number | null
  sort_order?: number | null
  birth_year?: number | null
  death_year?: number | null
  child_year?: number | null
  age?: number | null
  tradition: string
  spouse?: string | null
  children?: string | null
  sources?: string | null
  notes?: string | null
}

// ── Auth ───────────────────────────────────────────────────
const supabase = useSupabaseClient()
const router   = useRouter()

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) { router.push('/login'); return null }
  return session.access_token
}

const people = ref<Person[]>([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const editingId = ref<string | null>(null)
const search = ref('')
const traditionFilter = ref('')

const traditionOptions = [
  { value: 'quranic',      label: '古蘭明文',   bg: 'bg-white',        border: 'border-gray-400',  text: 'text-gray-900',  dot: 'bg-gray-400' },
  { value: 'sunni',        label: '順尼派',     bg: 'bg-emerald-50',   border: 'border-emerald-400', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  { value: 'shia_twelver', label: '十二伊瑪目', bg: 'bg-rose-50',      border: 'border-rose-400',  text: 'text-rose-700',  dot: 'bg-rose-500' },
  { value: 'shia_ismaili', label: '伊斯瑪儀',   bg: 'bg-purple-50',    border: 'border-purple-400',text: 'text-purple-700',dot: 'bg-purple-500' },
  { value: 'shia_zaidi',   label: '栽德派',     bg: 'bg-orange-50',    border: 'border-orange-400',text: 'text-orange-700',dot: 'bg-orange-500' },
  { value: 'sufi',         label: '蘇菲',       bg: 'bg-teal-50',      border: 'border-teal-400',  text: 'text-teal-700',  dot: 'bg-teal-500' },
  { value: 'historical',   label: '史傳',       bg: 'bg-gray-100',     border: 'border-gray-400',  text: 'text-gray-700',  dot: 'bg-gray-400' },
]

function rowBg(t: string) {
  const m: Record<string, string> = {
    quranic: '',
    sunni: 'bg-emerald-50/40',
    shia_twelver: 'bg-rose-50/40',
    shia_ismaili: 'bg-purple-50/40',
    shia_zaidi: 'bg-orange-50/40',
    sufi: 'bg-teal-50/40',
    historical: 'bg-gray-50/60',
  }
  return m[t] ?? ''
}

function traditionBadge(t: string) {
  const m: Record<string, string> = {
    quranic: 'bg-gray-100 text-gray-700',
    sunni: 'bg-emerald-100 text-emerald-700',
    shia_twelver: 'bg-rose-100 text-rose-700',
    shia_ismaili: 'bg-purple-100 text-purple-700',
    shia_zaidi: 'bg-orange-100 text-orange-700',
    sufi: 'bg-teal-100 text-teal-700',
    historical: 'bg-gray-100 text-gray-500',
  }
  return m[t] ?? 'bg-gray-100 text-gray-500'
}

function traditionLabel(t: string) {
  return traditionOptions.find(o => o.value === t)?.label ?? t
}

const filtered = computed(() => {
  let list = people.value
  if (traditionFilter.value) list = list.filter(p => p.tradition === traditionFilter.value)
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    list = list.filter(p =>
      (p.name_zh || '').toLowerCase().includes(q) ||
      (p.name_ar || '').toLowerCase().includes(q) ||
      (p.name_en || '').toLowerCase().includes(q)
    )
  }
  return list
})

// ── CRUD ───────────────────────────────────────────────────
function emptyForm() {
  return {
    name_zh: '', name_ar: '', name_en: '', kunya: '',
    gender: '', nationality: '',
    generation: null as number | null,
    sort_order: null as number | null,
    birth_year: null as number | null,
    death_year: null as number | null,
    child_year: null as number | null,
    age: null as number | null,
    spouse: '', children: '', sources: '', notes: '',
    tradition: 'sunni',
  }
}

const form = ref(emptyForm())

async function load() {
  loading.value = true
  try {
    const token = await getToken()
    if (!token) { loading.value = false; return }
    people.value = await $fetch<Person[]>('/api/genealogy/islamic-people', {
      headers: { Authorization: `Bearer ${token}` },
    })
  } finally {
    loading.value = false
  }
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
    name_ar:     p.name_ar     || '',
    name_en:     p.name_en     || '',
    kunya:       p.kunya       || '',
    gender:      p.gender      || '',
    nationality: p.nationality || '',
    generation:  p.generation  ?? null,
    sort_order:  p.sort_order  ?? null,
    birth_year:  p.birth_year  ?? null,
    death_year:  p.death_year  ?? null,
    child_year:  p.child_year  ?? null,
    age:         p.age         ?? null,
    spouse:      p.spouse      || '',
    children:    p.children    || '',
    sources:     p.sources     || '',
    notes:       p.notes       || '',
    tradition:   p.tradition   || 'sunni',
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
      const updated = await $fetch<Person>(`/api/genealogy/islamic-people/${editingId.value}`, {
        method: 'PATCH', body: form.value,
        headers: { Authorization: `Bearer ${token}` },
      })
      const idx = people.value.findIndex(p => p.id === editingId.value)
      if (idx >= 0) people.value[idx] = updated
    } else {
      const created = await $fetch<Person>('/api/genealogy/islamic-people', {
        method: 'POST', body: form.value,
        headers: { Authorization: `Bearer ${token}` },
      })
      people.value.push(created)
    }
    showModal.value = false
  } finally {
    saving.value = false
  }
}

async function deletePerson(id: string) {
  if (!confirm('確定刪除此人物？')) return
  const token = await getToken()
  if (!token) return
  await $fetch(`/api/genealogy/islamic-people/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  people.value = people.value.filter(p => p.id !== id)
}

onMounted(load)
</script>

<style scoped>
.field {
  @apply w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-200 transition bg-white;
}
</style>
