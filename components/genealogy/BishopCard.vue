<template>
  <Teleport to="body">
    <div
      v-if="bishopId"
      class="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 backdrop-blur-sm px-4 py-6"
      @click.self="$emit('close')"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[92vh] overflow-hidden flex flex-col">

        <!-- ── Header ──────────────────────────────────── -->
        <div
          class="flex items-center justify-between px-5 py-3 border-b border-gray-100 flex-shrink-0"
          :style="{ background: tradColor.bg }"
        >
          <div class="flex items-baseline gap-2 min-w-0">
            <span class="text-xs font-medium text-white/80 truncate">{{ detail?.see?.name_zh ?? bishop?.see ?? '' }}</span>
            <span class="text-xs text-white/50">·</span>
            <span class="text-xs font-medium text-white truncate">{{ detail?.see?.tradition ?? '—' }}</span>
          </div>
          <button class="text-white/80 hover:text-white text-xl leading-none px-1" @click="$emit('close')">×</button>
        </div>

        <!-- ── Body ──────────────────────────────────── -->
        <div v-if="loading" class="flex items-center justify-center py-16 text-gray-400 text-sm">載入中…</div>
        <div v-else-if="err" class="flex items-center justify-center py-16 text-red-500 text-sm">{{ err }}</div>
        <div v-else-if="bishop" class="flex-1 overflow-y-auto">

          <!-- Top: portrait + identity ─────────────────── -->
          <div class="flex gap-4 px-5 py-5 border-b border-gray-100">
            <!-- Portrait -->
            <div class="flex-shrink-0">
              <div
                class="w-32 h-40 rounded-lg overflow-hidden shadow-md border border-gray-200 bg-gray-50"
              >
                <img
                  :src="portraitSrc"
                  :alt="bishop.name_zh"
                  class="w-full h-full object-cover"
                  @error="handlePortraitError"
                />
              </div>
              <div v-if="!bishop.portrait_url" class="mt-1 text-[10px] text-gray-400 text-center">通用肖像</div>
            </div>

            <!-- Identity -->
            <div class="flex-1 min-w-0">
              <div class="flex items-baseline gap-2 flex-wrap">
                <h2 class="text-xl font-bold text-gray-900 leading-tight">{{ bishop.name_zh }}</h2>
                <span v-if="bishop.succession_number != null && bishop.succession_number > 0" class="text-sm text-gray-400 font-mono">#{{ bishop.succession_number }}</span>
              </div>
              <p v-if="bishop.name_en" class="text-sm text-gray-500 mt-0.5">{{ bishop.name_en }}</p>

              <div class="flex flex-wrap gap-1.5 mt-2.5">
                <span
                  class="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                  :style="{ background: tradColor.bg, color: '#fff' }"
                >{{ detail?.see?.tradition ?? '' }}</span>
                <span class="text-[10px] font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-700">{{ bishop.church }}</span>
                <span
                  class="text-[10px] font-medium px-2 py-0.5 rounded-full"
                  :class="statusClass(bishop.status)"
                >{{ bishop.status }}</span>
              </div>

              <div class="mt-3 space-y-1 text-xs">
                <div class="flex gap-2">
                  <span class="text-gray-400 w-12 flex-shrink-0">任期</span>
                  <span class="font-mono text-gray-700">{{ formatYear(bishop.start_year) }}{{ bishop.end_year != null ? ` – ${formatYear(bishop.end_year)}` : ' – 至今' }}</span>
                  <span v-if="tenureYears" class="text-gray-400">({{ tenureYears }})</span>
                </div>
                <div v-if="bishop.end_reason" class="flex gap-2">
                  <span class="text-gray-400 w-12 flex-shrink-0">卸任</span>
                  <span class="text-gray-700">{{ bishop.end_reason }}</span>
                </div>
                <div v-if="bishop.appointed_by" class="flex gap-2">
                  <span class="text-gray-400 w-12 flex-shrink-0">任命</span>
                  <span class="text-gray-700">{{ bishop.appointed_by }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Consecrator / consecrated ─────────────── -->
          <div v-if="detail?.consecrator || (detail?.consecrated?.length ?? 0) > 0" class="px-5 py-4 border-b border-gray-100">
            <h3 class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">使徒按立鏈</h3>
            <div v-if="detail?.consecrator" class="mb-2 text-xs">
              <span class="text-gray-400">由</span>
              <button class="ml-1 text-violet-600 hover:underline font-medium" @click="$emit('open', detail.consecrator.id)">
                {{ detail.consecrator.name_zh }}
              </button>
              <span class="text-gray-400 ml-1">（{{ detail.consecrator.see }} #{{ detail.consecrator.succession_number ?? '—' }}）按立</span>
            </div>
            <div v-if="(detail?.consecrated?.length ?? 0) > 0" class="text-xs">
              <span class="text-gray-400">按立過：</span>
              <span v-for="(c, idx) in detail.consecrated" :key="c.id" class="inline-block">
                <button class="text-violet-600 hover:underline" @click="$emit('open', c.id)">{{ c.name_zh }}</button><span class="text-gray-300 mx-1" v-if="idx < detail.consecrated.length - 1">·</span>
              </span>
            </div>
          </div>

          <!-- Teachers / students (church_teachings) ─── -->
          <div v-if="(detail?.teachers?.length ?? 0) > 0 || (detail?.students?.length ?? 0) > 0" class="px-5 py-4 border-b border-gray-100">
            <h3 class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">師徒／教導關係</h3>
            <div v-if="(detail?.teachers?.length ?? 0) > 0" class="mb-2 text-xs">
              <span class="text-gray-400">受教於：</span>
              <span v-for="t in detail.teachers" :key="t.id" class="inline-block mr-2">
                <button v-if="t.teacher_bishop_id" class="text-orange-600 hover:underline" @click="$emit('open', t.teacher_bishop_id)">
                  {{ t.teacher_name_zh }}
                </button>
                <span v-else class="text-orange-700">{{ t.teacher_name_zh }}</span>
                <span v-if="t.period_year" class="text-gray-400 ml-1">({{ formatYear(t.period_year) }})</span>
              </span>
            </div>
            <div v-if="(detail?.students?.length ?? 0) > 0" class="text-xs">
              <span class="text-gray-400">教導過：</span>
              <span v-for="s in detail.students" :key="s.id" class="inline-block mr-2">
                <button v-if="s.student_bishop_id" class="text-orange-600 hover:underline" @click="$emit('open', s.student_bishop_id)">
                  {{ s.student_name_zh }}
                </button>
                <span v-else class="text-orange-700">{{ s.student_name_zh }}</span>
                <span v-if="s.period_year" class="text-gray-400 ml-1">({{ formatYear(s.period_year) }})</span>
              </span>
            </div>
          </div>

          <!-- Notes ─────────────────────────────────── -->
          <div v-if="bishop.notes" class="px-5 py-4 border-b border-gray-100">
            <h3 class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">事蹟／神學立場</h3>
            <p class="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">{{ bishop.notes }}</p>
          </div>

          <!-- Sources ───────────────────────────────── -->
          <div v-if="bishop.sources" class="px-5 py-4 border-b border-gray-100">
            <h3 class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">史料來源</h3>
            <p class="text-xs text-gray-600 font-mono leading-relaxed">{{ bishop.sources }}</p>
          </div>

          <!-- Portrait edit (admin) ─────────────────── -->
          <div class="px-5 py-4 bg-gray-50">
            <details>
              <summary class="text-[11px] font-semibold text-gray-400 uppercase tracking-wider cursor-pointer hover:text-gray-600">編輯肖像連結</summary>
              <div class="mt-2 flex gap-2">
                <input
                  v-model="portraitInput"
                  type="url"
                  placeholder="https://upload.wikimedia.org/..."
                  class="flex-1 text-xs border border-gray-200 rounded px-2 py-1.5 outline-none focus:border-violet-400"
                />
                <button
                  class="text-xs px-3 py-1.5 rounded bg-violet-500 hover:bg-violet-600 text-white font-medium disabled:opacity-50"
                  :disabled="savingPortrait || portraitInput === (bishop.portrait_url ?? '')"
                  @click="savePortrait"
                >{{ savingPortrait ? '...' : '存' }}</button>
              </div>
            </details>
          </div>
        </div>

        <!-- ── Footer nav: prev/next ─────────────────── -->
        <div v-if="bishop" class="flex items-center justify-between px-4 py-2.5 border-t border-gray-100 bg-gray-50 flex-shrink-0">
          <button
            class="text-xs px-3 py-1.5 rounded text-gray-600 hover:bg-gray-200 transition disabled:opacity-30 disabled:cursor-not-allowed"
            :disabled="!prevId"
            @click="prevId && $emit('open', prevId)"
          >← 前一任</button>
          <span class="text-[10px] text-gray-400">{{ siblingPosition }}</span>
          <button
            class="text-xs px-3 py-1.5 rounded text-gray-600 hover:bg-gray-200 transition disabled:opacity-30 disabled:cursor-not-allowed"
            :disabled="!nextId"
            @click="nextId && $emit('open', nextId)"
          >下一任 →</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
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
  consecrator_bishop_id: string | null
  status: string
  sources: string | null
  notes: string | null
  portrait_url: string | null
}

interface BishopDetail {
  bishop: Bishop
  see: {
    id: string
    see_zh: string
    name_zh: string
    name_en: string | null
    church: string
    tradition: string
    rite: string | null
    founded_year: number | null
    location: string | null
    current_patriarch_zh: string | null
    notes: string | null
  } | null
  consecrator: { id: string; name_zh: string; see: string; succession_number: number | null } | null
  consecrated: Array<{ id: string; name_zh: string; see: string; succession_number: number | null }>
  teachers: Array<{ id: string; teacher_name_zh: string; teacher_bishop_id: string | null; period_year: number | null }>
  students: Array<{ id: string; student_name_zh: string; student_bishop_id: string | null; period_year: number | null }>
}

const props = defineProps<{
  bishopId: string | null
  siblings?: Bishop[]   // current see's bishop list for prev/next nav
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'open', id: string): void
  (e: 'updated', bishop: Bishop): void
}>()

const supabase = useSupabaseClient()
const router   = useRouter()

const detail = ref<BishopDetail | null>(null)
const loading = ref(false)
const err = ref<string | null>(null)
const portraitInput = ref('')
const savingPortrait = ref(false)
const imageBroken = ref(false)

const bishop = computed(() => detail.value?.bishop ?? null)

const TRAD_COLORS: Record<string, { bg: string; key: string }> = {
  '羅馬公教':       { bg: '#dc2626', key: 'rome' },
  '希臘正教':       { bg: '#2563eb', key: 'constantinople' },
  '科普特正教':     { bg: '#d97706', key: 'alexandria' },
  '敘利亞正教':     { bg: '#0891b2', key: 'antioch' },
  '亞美尼亞使徒教會': { bg: '#9333ea', key: 'armenia' },
  '亞述景教':       { bg: '#475569', key: 'assyria' },
  '基督新教':       { bg: '#16a34a', key: 'protestant' },
}

const tradColor = computed(() => {
  const t = detail.value?.see?.tradition
  return TRAD_COLORS[t ?? ''] ?? { bg: '#64748b', key: 'protestant' }
})

const portraitSrc = computed(() => {
  if (bishop.value?.portrait_url && !imageBroken.value) return bishop.value.portrait_url
  return `/episcopal-portraits/${tradColor.value.key}.svg`
})

function handlePortraitError() {
  imageBroken.value = true
}

const tenureYears = computed(() => {
  const b = bishop.value
  if (!b?.start_year) return null
  const end = b.end_year ?? new Date().getFullYear()
  const n = end - b.start_year
  if (n < 0) return null
  return `${n} 年`
})

const siblingIdx = computed(() => {
  if (!props.siblings || !bishop.value) return -1
  return props.siblings.findIndex(s => s.id === bishop.value!.id)
})
const prevId = computed(() => {
  if (siblingIdx.value <= 0) return null
  return props.siblings?.[siblingIdx.value - 1]?.id ?? null
})
const nextId = computed(() => {
  if (siblingIdx.value < 0 || !props.siblings) return null
  return props.siblings[siblingIdx.value + 1]?.id ?? null
})
const siblingPosition = computed(() => {
  if (siblingIdx.value < 0 || !props.siblings) return ''
  return `${siblingIdx.value + 1} / ${props.siblings.length}`
})

function statusClass(s: string) {
  if (s === '正統')       return 'bg-emerald-50 text-emerald-700'
  if (s === '對立')       return 'bg-red-50 text-red-600'
  if (s === '廢黜後復位') return 'bg-amber-50 text-amber-700'
  return 'bg-gray-100 text-gray-500'
}

function formatYear(y: number | null | undefined) {
  if (y == null) return '—'
  return y < 0 ? `主前 ${Math.abs(y)}` : `${y}`
}

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) { router.push('/login'); return null }
  return session.access_token
}

async function load(id: string) {
  loading.value = true
  err.value = null
  imageBroken.value = false
  try {
    const token = await getToken()
    if (!token) return
    detail.value = await $fetch<BishopDetail>(`/api/genealogy/episcopal-bishop/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    portraitInput.value = detail.value.bishop.portrait_url ?? ''
  } catch (e: unknown) {
    err.value = e instanceof Error ? e.message : '載入失敗'
  } finally {
    loading.value = false
  }
}

async function savePortrait() {
  if (!bishop.value) return
  savingPortrait.value = true
  try {
    const token = await getToken()
    if (!token) return
    const updated = await $fetch<Bishop>(`/api/genealogy/episcopal-succession/${bishop.value.id}`, {
      method: 'PATCH',
      body: { portrait_url: portraitInput.value.trim() || null },
      headers: { Authorization: `Bearer ${token}` },
    })
    if (detail.value) detail.value.bishop = { ...detail.value.bishop, portrait_url: updated.portrait_url }
    imageBroken.value = false
    emit('updated', updated)
  } finally {
    savingPortrait.value = false
  }
}

watch(() => props.bishopId, (id) => {
  if (id) load(id)
  else { detail.value = null; portraitInput.value = '' }
}, { immediate: true })

// Esc to close
function onKey(e: KeyboardEvent) {
  if (!props.bishopId) return
  if (e.key === 'Escape') emit('close')
  if (e.key === 'ArrowLeft' && prevId.value) emit('open', prevId.value)
  if (e.key === 'ArrowRight' && nextId.value) emit('open', nextId.value)
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>
