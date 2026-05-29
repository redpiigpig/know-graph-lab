<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/apocrypha" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">{{ docData?.document?.title_zh || '典外文獻' }}</span>
      <span v-if="docData?.document" class="text-xs text-gray-400">{{ docData.document.title_en }}</span>
    </nav>

    <div class="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
      <!-- Loading / error -->
      <div v-if="pending" class="text-center text-gray-400 py-12 text-sm">載入中…</div>
      <div v-else-if="error" class="text-center text-red-500 py-12 text-sm">{{ String(error) }}</div>

      <template v-else-if="docData">
        <!-- Document header -->
        <header class="mb-6">
          <h1 class="text-2xl font-bold text-gray-900">
            {{ docData.document.title_zh }}
          </h1>
          <p class="text-sm text-gray-500 mt-1">
            <span class="font-medium">{{ docData.document.title_en }}</span>
            <span v-if="docData.document.title_orig" class="text-gray-400 ml-2 italic">{{ docData.document.title_orig }}</span>
          </p>
          <div class="flex flex-wrap items-center gap-2 mt-2 text-xs">
            <span class="px-2 py-0.5 rounded bg-stone-100 text-stone-700">{{ categoryLabel(docData.document.category) }}</span>
            <span v-if="docData.document.language_orig" class="px-2 py-0.5 rounded bg-amber-50 text-amber-700">
              原文：{{ languageLabel(docData.document.language_orig) }}
            </span>
            <span v-if="formattedPeriod" class="px-2 py-0.5 rounded bg-gray-50 text-gray-600">
              {{ formattedPeriod }}
            </span>
            <span v-for="(accepted, key) in canonChips" :key="key"
                  v-show="accepted"
                  class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
              {{ canonLabel(key) }}
            </span>
          </div>
          <p v-if="docData.document.summary_zh" class="mt-3 text-sm text-gray-700 leading-relaxed border-l-2 border-stone-200 pl-3">
            {{ docData.document.summary_zh }}
          </p>
        </header>

        <!-- Column controls -->
        <div class="grid gap-3 mb-4" :style="{ gridTemplateColumns: gridCols }">
          <div
            v-for="(col, idx) in columns"
            :key="idx"
            class="bg-white border border-gray-200 rounded-md px-2 py-1.5 flex items-center gap-1"
          >
            <span class="text-[10px] uppercase tracking-wide text-gray-400 mr-1">{{ col.label }}</span>
            <select
              v-model="col.versionCode"
              class="flex-1 text-xs text-gray-800 bg-transparent border-none focus:outline-none cursor-pointer"
            >
              <option
                v-for="v in optionsForCol(col)"
                :key="v.code"
                :value="v.code"
              >{{ v.name_zh.replace(/（[^）]*）/g, '').trim() }}{{ v.public_domain ? '' : ' ©' }}</option>
              <option v-if="optionsForCol(col).length === 0" :value="''" disabled>（暫無資料）</option>
            </select>
            <button
              v-if="columns.length > 1"
              @click="removeColumn(idx)"
              class="text-gray-300 hover:text-red-500 text-xs px-1"
              title="移除此欄"
            >✕</button>
          </div>
          <button
            v-if="columns.length < 4"
            @click="addColumn"
            class="bg-white border border-dashed border-gray-300 rounded-md px-2 py-1.5 text-xs text-gray-500 hover:border-stone-400 hover:text-stone-700"
          >+ 對照欄</button>
        </div>

        <!-- No sections -->
        <div v-if="docData.sections.length === 0" class="text-center text-gray-400 py-16 text-sm">
          此文獻尚無任何已上架版本。<br/>
          <span class="text-xs">中文資料源：基督教典外文獻 (王曉朝主編)；英文／原文版本待補。</span>
        </div>

        <!-- Sections -->
        <div v-else class="space-y-1.5">
          <article
            v-for="s in docData.sections"
            :key="s.order_index"
            :id="`section-${s.order_index}`"
            class="bg-white border border-gray-200 rounded-md overflow-hidden scroll-mt-20"
          >
            <div v-if="s.section_label || s.page_number" class="flex items-baseline gap-2 px-3 py-1 bg-stone-50 border-b border-stone-100 text-[11px]">
              <span v-if="s.section_label" class="font-mono text-stone-600">{{ cleanLabel(s.section_label) }}</span>
              <span v-if="s.page_number" class="text-gray-400 ml-auto">p.{{ s.page_number }}</span>
            </div>
            <div class="grid gap-px bg-gray-100" :style="{ gridTemplateColumns: gridCols }">
              <div
                v-for="(col, idx) in columns"
                :key="idx"
                class="bg-white px-3 py-2.5 text-sm leading-relaxed text-gray-800"
                :class="textClassFor(col.versionCode)"
              >
                <template v-if="col.versionCode && s.byVersion[col.versionCode]">
                  {{ s.byVersion[col.versionCode] }}
                </template>
                <span v-else class="text-gray-300 italic text-xs">—</span>
              </div>
            </div>
          </article>
        </div>

        <!-- Coverage hint -->
        <p class="mt-8 text-[11px] text-gray-400 leading-relaxed">
          已匯入版本：{{ availableVersionsList || '（無）' }}。
          目前中文版本為《基督教典外文獻》OCR 直出，OCR 雜訊與卷次劃分待後續精修。
        </p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const route = useRoute()
const slug = computed(() => String(route.params.slug))

type ApocVersion = {
  code: string
  name_zh: string
  name_en: string
  language: string
  language_zh: string | null
  category: 'chinese' | 'english' | 'source' | 'ancient'
  public_domain: boolean
  display_order: number
  is_default_zh: boolean
  is_default_en: boolean
  is_default_orig: boolean
}
type DocRes = {
  document: {
    slug: string
    title_zh: string
    title_zh_short: string | null
    title_en: string
    title_orig: string | null
    category: string
    testament: string
    language_orig: string | null
    composition_low: number | null
    composition_high: number | null
    canon_status_jsonb: Record<string, boolean> | null
    summary_zh: string | null
  }
  sections: {
    order_index: number
    section_label: string | null
    page_number: number | null
    byVersion: Record<string, string>
  }[]
}

const supabase = useSupabaseClient()
const versions = ref<ApocVersion[]>([])
const docData = ref<DocRes | null>(null)
const pending = ref(true)
const error = ref<string | null>(null)

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}

async function load() {
  pending.value = true
  error.value = null
  try {
    const headers = await authHeaders()
    const [v, d] = await Promise.all([
      $fetch<ApocVersion[]>('/api/apocrypha/versions', { headers }),
      $fetch<DocRes>('/api/apocrypha/document', { headers, query: { slug: slug.value } }),
    ])
    versions.value = v
    docData.value = d
    columns.value = []  // reset; watchEffect picks defaults
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    pending.value = false
  }
}
onMounted(load)
watch(slug, load)

useHead({
  title: () => docData.value ? `${docData.value.document.title_zh} — 典外文獻` : '典外文獻',
})

// ── Columns ─────────────────────────────────────────────────────────────
type ColCategory = 'chinese' | 'english' | 'source'
type Col = { label: string; category: ColCategory; versionCode: string }
const columns = ref<Col[]>([])

const availableVersions = computed(() => {
  if (!docData.value || !versions.value) return [] as ApocVersion[]
  const hasData = new Set<string>()
  for (const s of docData.value.sections) {
    for (const k of Object.keys(s.byVersion)) hasData.add(k)
  }
  return versions.value.filter(v => hasData.has(v.code))
})

const availableVersionsList = computed(() =>
  availableVersions.value.map(v => v.name_zh.replace(/（[^）]*）/g, '').trim()).join(' / ')
)

function pickForCategory(cat: ColCategory): string {
  const avail = availableVersions.value.filter(v => v.category === cat)
  if (avail.length === 0) return ''
  if (cat === 'chinese') {
    const def = avail.find(v => v.is_default_zh)
    if (def) return def.code
  }
  if (cat === 'english') {
    const def = avail.find(v => v.is_default_en)
    if (def) return def.code
  }
  if (cat === 'source') {
    // Prefer one matching document's original language
    const langMap: Record<string, string> = {
      greek: 'greek_orig', hebrew: 'hebrew_orig', aramaic: 'aramaic_orig',
      coptic: 'coptic_orig', syriac: 'syriac_orig', ethiopic: 'ethiopic_orig',
      latin: 'latin_orig',
    }
    const origLang = docData.value?.document.language_orig || ''
    const preferredCode = langMap[origLang]
    if (preferredCode) {
      const v = avail.find(x => x.code === preferredCode)
      if (v) return v.code
    }
    const def = avail.find(v => v.is_default_orig)
    if (def) return def.code
  }
  return avail[0].code
}

watchEffect(() => {
  if (!availableVersions.value.length) {
    // Still render empty columns from full versions list so user sees the picker
    if (columns.value.length > 0 || !versions.value.length) return
    const allChineseEmpty = versions.value.find(v => v.category === 'chinese')
    if (allChineseEmpty) {
      columns.value = [{ label: '中文', category: 'chinese', versionCode: '' }]
    }
    return
  }
  if (columns.value.length > 0) return
  const cols: Col[] = []
  const zh = pickForCategory('chinese')
  cols.push({ label: '中文', category: 'chinese', versionCode: zh })
  const en = pickForCategory('english')
  if (en) cols.push({ label: '英文', category: 'english', versionCode: en })
  const src = pickForCategory('source')
  if (src) cols.push({ label: '原文', category: 'source', versionCode: src })
  // Guarantee 3 columns minimum (empty placeholders for missing)
  if (!en) cols.push({ label: '英文', category: 'english', versionCode: '' })
  if (!src) cols.push({ label: '原文', category: 'source', versionCode: '' })
  columns.value = cols
})

function optionsForCol(col: Col): ApocVersion[] {
  // If no available data, show the full version registry filtered by category
  if (!availableVersions.value.length) {
    return (versions.value ?? []).filter(v => v.category === col.category)
  }
  return availableVersions.value.filter(v => v.category === col.category)
}

function addColumn() {
  const used = new Set(columns.value.map(c => c.versionCode))
  const order: ColCategory[] = ['source', 'english', 'chinese']
  for (const cat of order) {
    const v = availableVersions.value.find(x => x.category === cat && !used.has(x.code))
    if (v) {
      const label = cat === 'source' ? '原文' : cat === 'english' ? '英文' : '中文'
      columns.value.push({ label, category: cat, versionCode: v.code })
      return
    }
  }
}

function removeColumn(idx: number) {
  columns.value.splice(idx, 1)
}

const gridCols = computed(() => `repeat(${columns.value.length}, minmax(0, 1fr))`)

function textClassFor(code: string) {
  const v = versions.value?.find(x => x.code === code)
  if (!v) return ''
  if (v.language === 'hbo') return 'font-serif rtl-text text-right'
  if (v.language === 'grc') return 'font-serif'
  if (v.language === 'lat') return 'font-serif italic'
  if (v.language === 'syr') return 'font-serif rtl-text text-right'
  if (v.language === 'cop') return 'font-serif'
  if (v.language === 'gez') return 'font-serif'
  return ''
}

// ── Labels & helpers ────────────────────────────────────────────────────
const CATEGORY_LABEL: Record<string, string> = {
  ot_apocrypha:      'OT 次經 / 第二正典',
  ot_pseudepigrapha: 'OT 偽典',
  nt_apocrypha:      'NT 偽典',
  nag_hammadi:       'Nag Hammadi 諾斯底',
  qumran:            '昆蘭古卷',
  lost_gospel:       '失傳福音書',
}
function categoryLabel(c: string) { return CATEGORY_LABEL[c] || c }

const LANG_LABEL: Record<string, string> = {
  greek: '希臘文', hebrew: '希伯來文', aramaic: '亞蘭文',
  coptic: '科普特文', syriac: '敘利亞文', ethiopic: 'Ge\'ez 文',
  latin: '拉丁文',
}
function languageLabel(l: string) { return LANG_LABEL[l] || l }

const CANON_LABEL: Record<string, string> = {
  protestant: '新教接受',
  catholic:   '天主教第二正典',
  orthodox:   '東正教接受',
  ethiopian:  '衣索匹亞正典',
  syriac:     '敘利亞接受',
}
function canonLabel(k: string) { return CANON_LABEL[k] || k }

const canonChips = computed(() => {
  const c = docData.value?.document.canon_status_jsonb || {}
  return c
})

const formattedPeriod = computed(() => {
  const d = docData.value?.document
  if (!d) return ''
  const low = d.composition_low
  const high = d.composition_high
  if (low === null && high === null) return ''
  const f = (y: number) => y < 0 ? `${-y} BCE` : `${y} CE`
  if (low === null) return `~${f(high!)}`
  if (high === null) return `${f(low)}~`
  if (low === high) return f(low)
  return `${f(low)} – ${f(high)}`
})

function cleanLabel(label: string) {
  // Strip noise prefixes like "第一部分:" and de-dupe repeated 卷名 noise
  return label
    .replace(/^第[一二三四五六七八九十]+部分:/, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 60)
}
</script>

<style scoped>
.rtl-text {
  direction: rtl;
  unicode-bidi: bidi-override;
}
</style>
