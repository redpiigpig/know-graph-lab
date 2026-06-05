<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="翻譯定名" :back="{ to: '/', label: '返回主頁' }">
      <template #actions>
        <span v-if="activeTab !== 'principles'" class="text-xs text-gray-400">{{ activeTabCount }} 項</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">翻譯定名</h1>
        <p class="text-sm text-gray-500">各領域名物的中譯定名與翻譯原則，每筆主譯標示為 <span class="text-amber-700 font-medium">★ 建議中譯</span>。</p>
      </div>

      <!-- Tabs -->
      <div class="flex flex-wrap items-center gap-1 mb-5 border-b border-gray-200">
        <button
          v-for="t in tabs" :key="t.key"
          @click="activeTab = t.key"
          class="px-3.5 py-2 text-sm border-b-2 -mb-px transition"
          :class="activeTab === t.key ? 'border-stone-700 text-stone-900 font-semibold' : 'border-transparent text-gray-500 hover:text-gray-800'"
        >{{ t.label }}<span v-if="t.key !== 'principles'" class="text-xs text-gray-400 ml-0.5">({{ tabCount(t.key) }})</span></button>
      </div>

      <!-- ───────── 翻譯原則頁 ───────── -->
      <div v-if="activeTab === 'principles'" class="max-w-3xl space-y-5 text-sm text-gray-800 leading-relaxed">
        <p class="text-gray-600">本工具的譯名定名鐵則。新增／校對任何條目、或翻譯任何書時都依此判準。</p>
        <ol class="space-y-4 list-none pl-0">
          <li v-for="(p, i) in principles" :key="i" class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="flex items-baseline gap-2 mb-1">
              <span class="text-amber-700 font-bold">{{ i + 1 }}.</span>
              <span class="font-semibold text-gray-900">{{ p.title }}</span>
            </div>
            <p class="text-gray-700">{{ p.body }}</p>
            <div v-if="p.examples" class="mt-2 flex flex-wrap gap-2">
              <span v-for="(ex, j) in p.examples" :key="j" class="text-xs px-2 py-1 rounded bg-emerald-50 text-emerald-800 border border-emerald-100">{{ ex }}</span>
            </div>
          </li>
        </ol>
        <div class="bg-stone-50 border border-stone-200 rounded-lg p-4">
          <div class="font-semibold text-stone-800 mb-1">名根一致性檢查</div>
          <p class="text-gray-700 text-xs mb-2">同一來源根（name_root）的譯名要一致；以下是目前掛了 root 卻沒含 root 字串的條目（請修正）。</p>
          <div v-if="rootIssues.length === 0" class="text-xs text-emerald-700">✓ 目前無不一致</div>
          <ul v-else class="text-xs space-y-1">
            <li v-for="b in rootIssues" :key="b.id" class="text-red-600">
              「{{ b.name_recommended }}」 掛 root <b>{{ b.name_root }}</b> 卻未含此字串（{{ b._tableLabel }}）
            </li>
          </ul>
        </div>
      </div>

      <template v-else>
        <!-- Sub-tabs (人名 only) — era buckets -->
        <div v-if="activeTab === 'people'" class="flex flex-wrap items-center gap-1 mb-4">
          <button v-for="e in personEras" :key="e.key" @click="activePersonEra = e.key"
            class="text-xs px-2.5 py-1 rounded-full border transition"
            :class="activePersonEra === e.key ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-gray-600 border-gray-200 hover:border-stone-300'"
          >{{ e.label }} <span class="ml-0.5 text-[10px] opacity-70">{{ personEraCount(e.key) }}</span></button>
        </div>

        <!-- Search -->
        <div class="flex flex-wrap items-center gap-2 mb-4">
          <input v-model="q" type="search" placeholder="搜尋（原文／英文／中譯／名根任一）"
            class="text-sm px-3 py-1.5 border border-gray-300 rounded-md w-72 focus:outline-none focus:border-stone-500" />
          <button v-if="editMode" @click="addNew" class="text-xs px-3 py-1 rounded-md bg-stone-900 text-white hover:bg-stone-800">+ 新增</button>
        </div>

        <div v-if="loading" class="text-sm text-gray-500 py-12 text-center">載入中…</div>

        <!-- People table (人名 — theologians, era buckets) -->
        <div v-else-if="activeTab === 'people'" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-stone-50 border-b border-gray-200 text-xs text-gray-600">
              <tr>
                <th class="px-3 py-2 text-left font-medium" style="width:18%">英文</th>
                <th class="px-3 py-2 text-left font-medium" style="width:16%">原文</th>
                <th class="px-3 py-2 text-left font-medium" style="width:20%">★ 中文翻譯</th>
                <th v-if="showBiblicalCols" class="px-3 py-2 text-left font-medium" style="width:16%">新教變體</th>
                <th v-if="showBiblicalCols" class="px-3 py-2 text-left font-medium" style="width:16%">天主教變體</th>
                <th class="px-3 py-2 text-left font-medium" style="width:22%">首次出現出處</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="row in filteredPeople" :key="row.id">
                <tr class="border-b border-gray-100 hover:bg-stone-50/60 cursor-pointer" @click="toggleExpand(row.id)">
                  <td class="px-3 py-2 font-medium text-gray-900">{{ row.name_english }}</td>
                  <td class="px-3 py-2 text-gray-700 font-serif">{{ row.name_original || '—' }}</td>
                  <td class="px-3 py-2 font-semibold text-amber-700">{{ row.name_recommended || '—' }}</td>
                  <td v-if="showBiblicalCols" class="px-3 py-2 text-gray-700">{{ row.name_protestant || '—' }}</td>
                  <td v-if="showBiblicalCols" class="px-3 py-2 text-gray-700">{{ row.name_catholic_sgs || '—' }}</td>
                  <td class="px-3 py-2 text-gray-600 text-xs">{{ row.first_source || '—' }}</td>
                </tr>
                <tr v-if="expanded === row.id" class="border-b border-gray-200 bg-stone-50/40">
                  <td :colspan="showBiblicalCols ? 6 : 4" class="px-5 py-4">
                    <div v-if="!editMode" class="text-xs text-gray-700 grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div><div class="text-gray-500 mb-1">★ 中文翻譯</div><div class="text-amber-700 font-medium">{{ row.name_recommended || '—' }}</div></div>
                      <div><div class="text-gray-500 mb-1">新教變體</div><div>{{ row.name_protestant || '—' }}</div></div>
                      <div><div class="text-gray-500 mb-1">天主教變體</div><div>{{ row.name_catholic_sgs || '—' }}</div></div>
                      <div v-if="row.name_root"><div class="text-gray-500 mb-1">名根</div><div>{{ row.name_root }}</div></div>
                      <div class="md:col-span-3"><div class="text-gray-500 mb-1">首次出現出處</div><div>{{ row.first_source || '—' }}</div></div>
                      <div v-if="row.recommendation_reason" class="md:col-span-3"><div class="text-gray-500 mb-1">備註</div><div class="whitespace-pre-wrap">{{ row.recommendation_reason }}</div></div>
                    </div>
                    <div v-else class="flex flex-col gap-2 text-xs">
                      <label class="text-gray-500">★ 中文翻譯</label>
                      <input v-model="editPerson.name_recommended" class="px-2 py-1 border border-gray-300 rounded w-full" />
                      <div class="grid grid-cols-3 gap-2 mt-1">
                        <div><label class="text-gray-500">新教變體</label><input v-model="editPerson.name_protestant" class="px-2 py-1 border border-gray-300 rounded w-full" /></div>
                        <div><label class="text-gray-500">天主教變體</label><input v-model="editPerson.name_catholic_sgs" class="px-2 py-1 border border-gray-300 rounded w-full" /></div>
                        <div><label class="text-gray-500">名根</label><input v-model="editPerson.name_root" class="px-2 py-1 border border-gray-300 rounded w-full" placeholder="如 亞歷山" /></div>
                      </div>
                      <label class="text-gray-500 mt-1">分類</label>
                      <select v-model="editPerson.person_era" class="px-2 py-1 border border-gray-300 rounded w-full">
                        <option value="biblical">聖經人物</option><option value="early">初代教會（-638）</option>
                        <option value="medieval">中世紀教會（-1517）</option><option value="modern">近代教會（-1910）</option><option value="contemporary">現代教會</option>
                      </select>
                      <label class="text-gray-500 mt-1">首次出現出處</label>
                      <input v-model="editPerson.first_source" class="px-2 py-1 border border-gray-300 rounded w-full" />
                      <label class="text-gray-500 mt-1">備註</label>
                      <textarea v-model="editPerson.recommendation_reason" rows="2" class="px-2 py-1 border border-gray-300 rounded w-full" />
                      <div class="flex gap-2 mt-1">
                        <button @click.stop="savePerson(row.id)" class="px-3 py-1 bg-stone-900 text-white rounded hover:bg-stone-800">儲存</button>
                        <button @click.stop="expanded = null" class="px-3 py-1 bg-gray-100 text-gray-700 rounded">取消</button>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
              <tr v-if="filteredPeople.length === 0"><td :colspan="showBiblicalCols ? 6 : 4" class="px-3 py-12 text-center text-sm text-gray-400">{{ theologians.length === 0 ? '尚無資料' : '無符合搜尋條件' }}</td></tr>
            </tbody>
          </table>
        </div>

        <!-- Theology terms table (神學名詞/地名/作品名/教派名 — theological_terms by entity_type) -->
        <div v-else-if="isTermTab" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-stone-50 border-b border-gray-200 text-xs text-gray-600">
              <tr>
                <th class="px-3 py-2 text-left font-medium" style="width:18%">英文</th>
                <th class="px-3 py-2 text-left font-medium" style="width:16%">原文</th>
                <th class="px-3 py-2 text-left font-medium" style="width:20%">★ 中文翻譯</th>
                <th v-if="activeTab === 'term'" class="px-3 py-2 text-left font-medium" style="width:16%">新教變體</th>
                <th v-if="activeTab === 'term'" class="px-3 py-2 text-left font-medium" style="width:16%">天主教變體</th>
                <th class="px-3 py-2 text-left font-medium" style="width:22%">首次出現出處</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="row in filteredTerms" :key="row.id">
                <tr class="border-b border-gray-100 hover:bg-stone-50/60 cursor-pointer" @click="toggleExpand(row.id)">
                  <td class="px-3 py-2 font-medium text-gray-900">{{ row.term_english }}</td>
                  <td class="px-3 py-2 text-gray-700 font-serif">{{ row.term_original || '—' }}</td>
                  <td class="px-3 py-2 font-semibold text-amber-700">{{ row.zh_recommended || '—' }}</td>
                  <td v-if="activeTab === 'term'" class="px-3 py-2 text-gray-700">{{ row.zh_protestant || '—' }}</td>
                  <td v-if="activeTab === 'term'" class="px-3 py-2 text-gray-700">{{ row.zh_catholic_sgs || '—' }}</td>
                  <td class="px-3 py-2 text-gray-600 text-xs">{{ row.first_source || '—' }}</td>
                </tr>
                <tr v-if="expanded === row.id" class="border-b border-gray-200 bg-stone-50/40">
                  <td :colspan="activeTab === 'term' ? 6 : 4" class="px-5 py-4">
                    <div v-if="!editMode" class="text-xs text-gray-700 grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div><div class="text-gray-500 mb-1">★ 中文翻譯</div><div class="text-amber-700 font-medium">{{ row.zh_recommended || '—' }}</div></div>
                      <div><div class="text-gray-500 mb-1">新教變體</div><div>{{ row.zh_protestant || '—' }}</div></div>
                      <div><div class="text-gray-500 mb-1">天主教變體</div><div>{{ row.zh_catholic_sgs || '—' }}</div></div>
                      <div v-if="row.definition_zh" class="md:col-span-3"><div class="text-gray-500 mb-1">中文釋義</div><div class="whitespace-pre-wrap">{{ row.definition_zh }}</div></div>
                    </div>
                    <div v-else class="flex flex-col gap-2 text-xs">
                      <label class="text-gray-500">★ 中文翻譯</label>
                      <input v-model="editTerm.zh_recommended" class="px-2 py-1 border border-gray-300 rounded w-full" />
                      <div class="grid grid-cols-2 gap-2 mt-1">
                        <div><label class="text-gray-500">新教變體</label><input v-model="editTerm.zh_protestant" class="px-2 py-1 border border-gray-300 rounded w-full" /></div>
                        <div><label class="text-gray-500">天主教變體</label><input v-model="editTerm.zh_catholic_sgs" class="px-2 py-1 border border-gray-300 rounded w-full" /></div>
                      </div>
                      <label class="text-gray-500 mt-1">中文釋義</label>
                      <textarea v-model="editTerm.definition_zh" rows="2" class="px-2 py-1 border border-gray-300 rounded w-full" />
                      <div class="flex gap-2 mt-1">
                        <button @click.stop="saveTerm(row.id)" class="px-3 py-1 bg-stone-900 text-white rounded hover:bg-stone-800">儲存</button>
                        <button @click.stop="expanded = null" class="px-3 py-1 bg-gray-100 text-gray-700 rounded">取消</button>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
              <tr v-if="filteredTerms.length === 0"><td :colspan="activeTab === 'term' ? 6 : 4" class="px-3 py-12 text-center text-sm text-gray-400">此類別尚無資料，編輯模式 → + 新增</td></tr>
            </tbody>
          </table>
        </div>

        <!-- Generic domains (philosophers/scientists/rulers/places/deities — shared shape) -->
        <div v-else class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-stone-50 border-b border-gray-200 text-xs text-gray-600">
              <tr>
                <th class="px-3 py-2 text-left font-medium" style="width:20%">英文</th>
                <th class="px-3 py-2 text-left font-medium" style="width:16%">原文</th>
                <th class="px-3 py-2 text-left font-medium" style="width:20%">★ 中文翻譯</th>
                <th v-for="ex in genericExtras" :key="ex[0]" class="px-3 py-2 text-left font-medium">{{ ex[1] }}</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="row in filteredGeneric" :key="row.id">
                <tr class="border-b border-gray-100 hover:bg-stone-50/60 cursor-pointer" @click="toggleExpand(row.id)">
                  <td class="px-3 py-2 font-medium text-gray-900">{{ row.name_english }}</td>
                  <td class="px-3 py-2 text-gray-700 font-serif">{{ row.name_original || row.name_romanized || '—' }}</td>
                  <td class="px-3 py-2 font-semibold text-amber-700">{{ row.name_recommended || '—' }}</td>
                  <td v-for="ex in genericExtras" :key="ex[0]" class="px-3 py-2 text-gray-600 text-xs">{{ row[ex[0]] || '—' }}</td>
                </tr>
                <tr v-if="expanded === row.id" class="border-b border-gray-200 bg-stone-50/40">
                  <td :colspan="3 + genericExtras.length" class="px-5 py-4">
                    <div v-if="!editMode" class="text-xs text-gray-700 grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div><div class="text-gray-500 mb-1">★ 中文翻譯</div><div class="text-amber-700 font-medium">{{ row.name_recommended || '—' }}</div></div>
                      <div v-if="row.name_variants"><div class="text-gray-500 mb-1">其他譯名</div><div>{{ row.name_variants }}</div></div>
                      <div v-if="row.name_root"><div class="text-gray-500 mb-1">名根</div><div>{{ row.name_root }}</div></div>
                      <div v-if="row.name_romanized"><div class="text-gray-500 mb-1">羅馬化</div><div class="font-serif">{{ row.name_romanized }}</div></div>
                      <div v-for="ex in genericExtras" :key="ex[0]" v-show="row[ex[0]]"><div class="text-gray-500 mb-1">{{ ex[1] }}</div><div>{{ row[ex[0]] }}</div></div>
                      <div v-if="row.recommendation_reason" class="md:col-span-3"><div class="text-gray-500 mb-1">理由 / 備註</div><div class="whitespace-pre-wrap">{{ row.recommendation_reason }}</div></div>
                    </div>
                    <div v-else class="flex flex-col gap-2 text-xs">
                      <div class="grid grid-cols-3 gap-2">
                        <div><label class="text-gray-500">★ 中文翻譯</label><input v-model="editGeneric.name_recommended" class="px-2 py-1 border border-gray-300 rounded w-full" /></div>
                        <div><label class="text-gray-500">其他譯名（；分隔）</label><input v-model="editGeneric.name_variants" class="px-2 py-1 border border-gray-300 rounded w-full" /></div>
                        <div><label class="text-gray-500">名根</label><input v-model="editGeneric.name_root" class="px-2 py-1 border border-gray-300 rounded w-full" placeholder="如 塞琉 / 密特" /></div>
                      </div>
                      <div class="grid gap-2 mt-1" :style="{ gridTemplateColumns: `repeat(${Math.max(1, genericExtras.length)}, minmax(0,1fr))` }">
                        <div v-for="ex in genericExtras" :key="ex[0]"><label class="text-gray-500">{{ ex[1] }}</label><input v-model="editGeneric[ex[0]]" class="px-2 py-1 border border-gray-300 rounded w-full" /></div>
                      </div>
                      <label class="text-gray-500 mt-1">理由 / 備註</label>
                      <textarea v-model="editGeneric.recommendation_reason" rows="2" class="px-2 py-1 border border-gray-300 rounded w-full" />
                      <div class="flex gap-2 mt-1">
                        <button @click.stop="saveGeneric(row.id)" class="px-3 py-1 bg-stone-900 text-white rounded hover:bg-stone-800">儲存</button>
                        <button @click.stop="expanded = null" class="px-3 py-1 bg-gray-100 text-gray-700 rounded">取消</button>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
              <tr v-if="filteredGeneric.length === 0"><td :colspan="3 + genericExtras.length" class="px-3 py-12 text-center text-sm text-gray-400">此類別尚無資料，編輯模式 → + 新增</td></tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '翻譯定名 — Know Graph Lab' })

const supabase = useSupabaseClient<any>()

// Tabs: principles page + theology (people/term buckets) + 5 generic new-domain tables.
const tabs = [
  { key: 'principles',   label: '翻譯原則' },
  { key: 'people',       label: '人名' },
  { key: 'term',         label: '神學名詞' },
  { key: 'place',        label: '聖經地名' },
  { key: 'work',         label: '作品名' },
  { key: 'sect',         label: '教派名' },
  { key: 'philosophers', label: '哲學家' },
  { key: 'scientists',   label: '科學家' },
  { key: 'rulers',       label: '歷代帝王' },
  { key: 'places',       label: '國名與城市' },
  { key: 'deities',      label: '神祇與宗教名詞' },
] as const
type TabKey = typeof tabs[number]['key']
const activeTab = ref<TabKey>('principles')

// Generic new-domain config (all share one table shape).
const GENERIC: Record<string, { table: string; extras: [string, string][] }> = {
  philosophers: { table: 'philosophers',      extras: [['school', '學派'], ['era', '時期'], ['nationality', '國籍']] },
  scientists:   { table: 'scientists',        extras: [['field', '領域'], ['era', '時期'], ['nationality', '國籍']] },
  rulers:       { table: 'historical_rulers', extras: [['polity', '朝代/帝國'], ['title', '稱號'], ['region', '地區']] },
  places:       { table: 'place_names',       extras: [['place_type', '類型'], ['modern_name', '今名'], ['region', '地區']] },
  deities:      { table: 'deities',           extras: [['religion', '宗教'], ['entity_type', '類型'], ['domain_of', '掌管']] },
}
const TERM_TABS = ['term', 'place', 'work', 'sect']
const isTermTab = computed(() => TERM_TABS.includes(activeTab.value))
const isGenericTab = computed(() => activeTab.value in GENERIC)
const genericExtras = computed(() => GENERIC[activeTab.value]?.extras ?? [])

const principles = [
  { title: '按原文，不按英文', body: '以希臘／拉丁／希伯來／原民族語的拼寫與發音為準，而非英文形式。' },
  { title: '沿用良好古譯／既有意譯', body: '若已有通行良好的古譯或意譯就沿用，不強制全部重新音譯。' },
  { title: '音意結合', body: '有良好音譯能配合意涵時優先採用；不為純音譯而捨棄更達意的形式。', examples: ['亞歷山卓 ＞ 亞歷山大城', '馬爾堡 ＞ 馬布爾'] },
  { title: '名根一致（name_root）', body: '同一來源根的所有名字，其根的中譯要一致。掛上 name_root 後系統會自動檢查每筆建議譯名是否含該根字串。', examples: ['密特 → 密特拉／密特里達迪', '塞琉 → 塞琉古／塞琉西亞／塞琉西亞-泰西封'] },
  { title: '王朝命名（帝國／國名）', body: '以王朝命名的帝國／國名採「王朝名-民族（或國名）帝國」格式，點出統治王朝與民族雙重身分；但若該政權只跟單一人物相關（建立者一人、逝後即分裂或更名），則直接用人名，不加王朝-民族。', examples: ['鄂圖曼-土耳其帝國／阿契美尼德-波斯帝國／阿拔斯-阿拉伯帝國／卡洛林-法蘭克帝國', '例外（單一人物）：亞歷山大帝國／帖木兒帝國／拿破崙帝國'] },
]

const personEras = [
  { key: 'all', label: '全部' }, { key: 'biblical', label: '聖經人物' }, { key: 'early', label: '初代教會' },
  { key: 'medieval', label: '中世紀教會' }, { key: 'modern', label: '近代教會' }, { key: 'contemporary', label: '現代教會' },
] as const
type PersonEra = typeof personEras[number]['key']
const activePersonEra = ref<PersonEra>('all')
const showBiblicalCols = computed(() => activeTab.value === 'people' && activePersonEra.value === 'biblical')

const loading = ref(true)
const theologians = ref<any[]>([])
const terms = ref<any[]>([])
const genericData = reactive<Record<string, any[]>>({ philosophers: [], scientists: [], historical_rulers: [], place_names: [], deities: [] })

const q = ref('')
const expanded = ref<string | null>(null)
const editMode = useEditMode()
const editPerson = ref<any>({})
const editTerm = ref<any>({})
const editGeneric = ref<any>({})

function tabCount(key: TabKey): number {
  if (key === 'people') return theologians.value.length
  if (TERM_TABS.includes(key)) return terms.value.filter(t => (t.entity_type || 'term') === key).length
  if (key in GENERIC) return genericData[GENERIC[key].table].length
  return 0
}
const activeTabCount = computed(() => tabCount(activeTab.value))
function personEraCount(era: PersonEra): number {
  if (era === 'all') return theologians.value.length
  return theologians.value.filter(p => (p.person_era || 'early') === era).length
}

const filteredPeople = computed(() => {
  const query = q.value.trim().toLowerCase(); const era = activePersonEra.value
  const rows = theologians.value.filter(r => {
    if (era !== 'all' && (r.person_era || 'early') !== era) return false
    if (!query) return true
    return [r.name_english, r.name_original, r.name_latin_std, r.name_recommended, r.name_root, r.role, r.first_source]
      .filter(Boolean).some((v: string) => v.toLowerCase().includes(query))
  })
  return [...rows].sort((a, b) => effectiveYear(a) - effectiveYear(b))
})
const filteredTerms = computed(() => {
  const query = q.value.trim().toLowerCase()
  return terms.value.filter(r => {
    if ((r.entity_type || 'term') !== activeTab.value) return false
    if (!query) return true
    return [r.term_english, r.term_original, r.term_latin_translit, r.zh_recommended, r.first_source, r.definition_zh]
      .filter(Boolean).some((v: string) => v.toLowerCase().includes(query))
  })
})
const filteredGeneric = computed(() => {
  if (!(activeTab.value in GENERIC)) return []
  const rows = genericData[GENERIC[activeTab.value].table] || []
  const query = q.value.trim().toLowerCase()
  const out = rows.filter(r => {
    if (!query) return true
    return [r.name_english, r.name_original, r.name_romanized, r.name_recommended, r.name_variants, r.name_root]
      .filter(Boolean).some((v: string) => v.toLowerCase().includes(query))
  })
  return [...out].sort((a, b) => (a.sort_order ?? 9999) - (b.sort_order ?? 9999) || String(a.name_english).localeCompare(String(b.name_english)))
})

// Name-root consistency across every loaded table (powers the principles-page check).
const rootIssues = computed(() => {
  const out: any[] = []
  const check = (rows: any[], recField: string, label: string) => {
    for (const r of rows) {
      const root = (r.name_root || '').trim()
      if (root && !(r[recField] || '').includes(root)) out.push({ ...r, name_recommended: r[recField], name_root: root, _tableLabel: label })
    }
  }
  check(theologians.value, 'name_recommended', '人名')
  check(terms.value, 'zh_recommended', '神學名詞')
  for (const [key, cfg] of Object.entries(GENERIC)) check(genericData[cfg.table], 'name_recommended', tabs.find(t => t.key === key)?.label || key)
  return out
})

async function addNew() {
  const english = prompt('英文／拉丁名（必填）')?.trim(); if (!english) return
  const original = prompt('原文（可空）')?.trim() || null
  const chinese = prompt('★ 中文翻譯（必填）')?.trim(); if (!chinese) return
  const root = prompt('名根（可空，如 塞琉／密特）')?.trim() || null
  if (activeTab.value === 'people') {
    const era = activePersonEra.value === 'all' ? 'early' : activePersonEra.value
    const { data, error } = await supabase.from('theologians').insert({ name_english: english, name_original: original, name_latin_std: english, name_recommended: chinese, name_protestant: chinese, name_root: root, person_era: era }).select().single()
    if (error) return alert('新增失敗：' + error.message); theologians.value.push(data)
  } else if (isTermTab.value) {
    const { data, error } = await supabase.from('theological_terms').insert({ term_english: english, term_original: original, zh_recommended: chinese, zh_protestant: chinese, name_root: root, entity_type: activeTab.value }).select().single()
    if (error) return alert('新增失敗：' + error.message); terms.value.push(data)
  } else if (isGenericTab.value) {
    const table = GENERIC[activeTab.value].table
    const { data, error } = await supabase.from(table).insert({ name_english: english, name_original: original, name_recommended: chinese, name_root: root }).select().single()
    if (error) return alert('新增失敗：' + error.message); genericData[table].push(data)
  }
}

function effectiveYear(r: any): number {
  if (r.died_year != null) return r.died_year
  if (r.born_year != null) return r.born_year + 40
  const m = r.century?.match(/^(\d+)(?:-(\d+))?c/i)
  if (m) { const a = parseInt(m[1]); const b = m[2] ? parseInt(m[2]) : a; return (a + b - 1) * 50 }
  return 9999
}

function toggleExpand(id: string) {
  if (expanded.value === id) { expanded.value = null; return }
  expanded.value = id
  if (activeTab.value === 'people') {
    const row = theologians.value.find(r => r.id === id)
    editPerson.value = { name_recommended: row?.name_recommended || '', name_protestant: row?.name_protestant || '', name_catholic_sgs: row?.name_catholic_sgs || '', name_root: row?.name_root || '', first_source: row?.first_source || '', person_era: row?.person_era || 'early', recommendation_reason: row?.recommendation_reason || '' }
  } else if (isTermTab.value) {
    const row = terms.value.find(r => r.id === id)
    editTerm.value = { zh_recommended: row?.zh_recommended || '', zh_protestant: row?.zh_protestant || '', zh_catholic_sgs: row?.zh_catholic_sgs || '', definition_zh: row?.definition_zh || '' }
  } else if (isGenericTab.value) {
    const row = (genericData[GENERIC[activeTab.value].table] || []).find(r => r.id === id) || {}
    const e: any = { name_recommended: row.name_recommended || '', name_variants: row.name_variants || '', name_root: row.name_root || '', recommendation_reason: row.recommendation_reason || '' }
    for (const [k] of genericExtras.value) e[k] = row[k] || ''
    editGeneric.value = e
  }
}

async function savePerson(id: string) {
  const patch = { ...editPerson.value, updated_at: new Date().toISOString() }
  const { error } = await supabase.from('theologians').update(patch).eq('id', id)
  if (error) return alert('儲存失敗：' + error.message); Object.assign(theologians.value.find(r => r.id === id), patch); expanded.value = null
}
async function saveTerm(id: string) {
  const patch = { ...editTerm.value, updated_at: new Date().toISOString() }
  const { error } = await supabase.from('theological_terms').update(patch).eq('id', id)
  if (error) return alert('儲存失敗：' + error.message); Object.assign(terms.value.find(r => r.id === id), patch); expanded.value = null
}
async function saveGeneric(id: string) {
  const table = GENERIC[activeTab.value].table
  const patch = { ...editGeneric.value, updated_at: new Date().toISOString() }
  const { error } = await supabase.from(table).update(patch).eq('id', id)
  if (error) return alert('儲存失敗：' + error.message); Object.assign(genericData[table].find(r => r.id === id), patch); expanded.value = null
}

onMounted(async () => {
  const [p, t, ph, sc, ru, pl, de] = await Promise.all([
    supabase.from('theologians').select('*'),
    supabase.from('theological_terms').select('*').order('sort_order', { ascending: true, nullsFirst: false }),
    supabase.from('philosophers').select('*'),
    supabase.from('scientists').select('*'),
    supabase.from('historical_rulers').select('*'),
    supabase.from('place_names').select('*'),
    supabase.from('deities').select('*'),
  ])
  theologians.value = p.data || []
  terms.value = t.data || []
  genericData.philosophers = ph.data || []
  genericData.scientists = sc.data || []
  genericData.historical_rulers = ru.data || []
  genericData.place_names = pl.data || []
  genericData.deities = de.data || []
  loading.value = false
})
</script>
