<template>
  <div class="flex flex-col bg-slate-50" style="height: 100dvh;">

    <!-- ── Nav ────────────────────────────────────────────── -->
    <nav class="flex items-center gap-2 px-4 h-12 bg-white border-b border-gray-100 flex-shrink-0 z-30">
      <NuxtLink to="/genealogy" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">使徒統緒</span>
      <template v-if="selectedSee">
        <span class="text-gray-300 text-sm">/</span>
        <span class="text-xs text-gray-500">{{ selectedSee.tradition }}</span>
        <span class="text-gray-300 text-sm">/</span>
        <span class="text-xs font-medium text-gray-700">{{ selectedSee.name_zh }}</span>
      </template>
      <div class="flex-1" />
      <button
        v-if="selectedSee"
        class="text-xs px-3 py-1.5 rounded-lg bg-violet-500 hover:bg-violet-600 text-white font-medium transition shadow-sm"
        @click="openAdd"
      >+ 新增主教</button>
    </nav>

    <!-- ── Two-panel body ─────────────────────────────────── -->
    <div class="flex flex-1 min-h-0">

      <!-- ── Left: tradition tree ──────────────────────────── -->
      <aside class="w-60 flex-shrink-0 border-r border-gray-100 bg-white flex flex-col min-h-0">

        <!-- Sidebar search -->
        <div class="px-3 py-2 border-b border-gray-100 flex-shrink-0">
          <div class="relative">
            <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-300 text-[10px] pointer-events-none">🔍</span>
            <input
              v-model="sidebarSearch"
              class="w-full pl-6 pr-3 py-1.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-violet-400 transition bg-white"
              placeholder="搜尋主教座…"
            />
          </div>
        </div>

        <!-- Tree / search results -->
        <div class="flex-1 overflow-y-auto">

          <!-- Error state -->
          <div v-if="seesError" class="px-4 py-6 text-xs text-red-500 text-center">
            {{ seesError }}
          </div>

          <!-- Search results (flat list) -->
          <template v-else-if="isSearching">
            <div v-if="searchResults.length === 0" class="px-4 py-6 text-xs text-gray-400 text-center">無符合結果</div>
            <button
              v-for="s in searchResults"
              :key="s.see_zh + s.church"
              class="w-full flex flex-col px-4 py-2 text-left hover:bg-violet-50 border-b border-gray-50 transition"
              :class="selectedSee?.see_zh === s.see_zh && selectedSee?.church === s.church ? 'bg-violet-50' : ''"
              @click="selectSee(s)"
            >
              <span class="text-xs font-medium text-gray-800 leading-tight">{{ s.name_zh }}</span>
              <span class="text-[10px] text-gray-400 mt-0.5">{{ s.church }}</span>
            </button>
          </template>

          <!-- Loading state -->
          <div v-else-if="seesLoading" class="px-4 py-6 text-xs text-gray-400 text-center">載入中…</div>

          <!-- Tree view -->
          <template v-else>
            <div v-for="trad in tree" :key="trad.tradition" class="border-b border-gray-50 last:border-0">

              <!-- Tradition header -->
              <button
                class="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-gray-50 transition"
                @click="toggleTradition(trad.tradition)"
              >
                <span class="text-gray-300 text-[10px] w-3 flex-shrink-0 select-none">{{ expandedTraditions.has(trad.tradition) ? '▾' : '▸' }}</span>
                <span
                  class="text-[11px] font-semibold px-1.5 py-0.5 rounded"
                  :class="TRAD_COLOR[trad.tradition] ?? 'bg-gray-100 text-gray-600'"
                >{{ trad.tradition }}</span>
                <span class="ml-auto text-[10px] text-gray-300">{{ trad.seeCount }}</span>
              </button>

              <!-- Sub-groups within tradition -->
              <div v-if="expandedTraditions.has(trad.tradition)">
                <div v-for="sg in trad.subGroups" :key="trad.tradition + '/' + sg.subGroup">

                  <!-- Sub-group header -->
                  <button
                    class="w-full flex items-center gap-2 pl-6 pr-3 py-1.5 text-left hover:bg-gray-50 transition"
                    @click="toggleSubGroup(trad.tradition + '/' + sg.subGroup)"
                  >
                    <span class="text-gray-300 text-[10px] w-3 flex-shrink-0 select-none">{{ expandedSubGroups.has(trad.tradition + '/' + sg.subGroup) ? '▾' : '▸' }}</span>
                    <span class="text-[11px] text-gray-600 truncate">{{ sg.subGroup }}</span>
                    <span class="ml-auto text-[10px] text-gray-300 flex-shrink-0">{{ sg.sees.length }}</span>
                  </button>

                  <!-- Sees list -->
                  <div v-if="expandedSubGroups.has(trad.tradition + '/' + sg.subGroup)">
                    <button
                      v-for="s in sg.sees"
                      :key="s.see_zh + s.church"
                      class="w-full flex items-center gap-2 pl-10 pr-3 py-1.5 text-left transition border-l-2 ml-3"
                      :class="selectedSee?.see_zh === s.see_zh && selectedSee?.church === s.church
                        ? 'border-violet-400 bg-violet-50 text-violet-800'
                        : 'border-transparent hover:bg-gray-50 text-gray-700'"
                      @click="selectSee(s)"
                    >
                      <span class="text-xs truncate leading-tight">{{ s.name_zh }}</span>
                    </button>
                  </div>

                </div>
              </div>

            </div>
          </template>

        </div>
      </aside>

      <!-- ── Right: succession list ─────────────────────────── -->
      <main class="flex-1 min-h-0 overflow-y-auto">

        <!-- Empty state -->
        <div v-if="!selectedSee" class="flex flex-col items-center justify-center h-full gap-3 text-center px-8">
          <div class="text-4xl text-gray-200 select-none">✝</div>
          <p class="text-sm font-medium text-gray-400">選擇左側主教座以查看傳承</p>
          <p v-if="!seesLoading" class="text-xs text-gray-300">共 {{ sees.length }} 個主教座</p>
        </div>

        <!-- See content -->
        <div v-else>

          <!-- See header -->
          <div class="bg-white border-b border-gray-100 px-5 py-4 sticky top-0 z-10 shadow-sm">
            <div class="flex items-start gap-3">
              <div class="flex-1 min-w-0">
                <div class="flex items-baseline gap-2 flex-wrap">
                  <h2 class="text-base font-semibold text-gray-900">{{ selectedSee.name_zh }}</h2>
                  <span v-if="selectedSee.name_en" class="text-xs text-gray-400">{{ selectedSee.name_en }}</span>
                </div>
                <div class="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1.5">
                  <span
                    class="text-[10px] font-semibold px-1.5 py-0.5 rounded"
                    :class="TRAD_COLOR[selectedSee.tradition] ?? 'bg-gray-100 text-gray-600'"
                  >{{ selectedSee.tradition }}</span>
                  <span class="text-xs text-gray-500">{{ selectedSee.church }}</span>
                  <span v-if="selectedSee.rite" class="text-xs text-gray-400">{{ selectedSee.rite }}</span>
                  <span v-if="selectedSee.location" class="text-xs text-gray-400">📍 {{ selectedSee.location }}</span>
                  <span v-if="selectedSee.founded_year" class="text-xs text-gray-400">
                    創立 {{ selectedSee.founded_year < 0 ? `主前 ${Math.abs(selectedSee.founded_year)}` : selectedSee.founded_year }} 年
                  </span>
                </div>
                <div v-if="selectedSee.current_patriarch_zh" class="mt-1 text-xs text-gray-500">
                  <span class="text-gray-400">現任：</span>{{ selectedSee.current_patriarch_zh }}
                  <span v-if="selectedSee.incumbent_since" class="text-gray-400 ml-1">（{{ selectedSee.incumbent_since }}–）</span>
                </div>
              </div>
              <div class="flex-shrink-0 text-right">
                <span v-if="!seqLoading" class="text-xs text-gray-400">{{ seeBishops.length }} 任</span>
              </div>
            </div>
          </div>

          <!-- Loading -->
          <div v-if="seqLoading" class="flex items-center justify-center h-32 text-gray-400 text-sm">載入中…</div>

          <!-- Empty succession -->
          <div v-else-if="seeBishops.length === 0" class="px-5 py-10 text-center text-sm text-gray-400">
            此主教座尚無傳承資料
          </div>

          <!-- Succession table -->
          <div v-else class="p-4">
            <div class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
              <table class="w-full text-sm border-collapse">
                <thead>
                  <tr class="bg-gray-50 border-b border-gray-200">
                    <th class="px-3 py-2 text-left font-medium text-gray-500 text-xs w-10">#</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-500 text-xs">中文名</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-500 text-xs">英文名</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-500 text-xs whitespace-nowrap">任期</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-500 text-xs whitespace-nowrap">卸任原因</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-500 text-xs">任命者</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-500 text-xs w-14">身份</th>
                    <th class="px-3 py-2 w-14"></th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="b in seeBishops" :key="b.id">
                    <!-- Main row -->
                    <tr
                      class="border-b border-gray-100 hover:bg-violet-50/20 transition cursor-pointer group"
                      :class="expandedRows.has(b.id) ? 'bg-amber-50/30' : ''"
                      @click="b.notes ? toggleRow(b.id) : undefined"
                    >
                      <td class="px-3 py-2.5 text-xs text-gray-400 whitespace-nowrap">
                        {{ b.succession_number != null ? b.succession_number : '—' }}
                      </td>
                      <td class="px-3 py-2.5 font-medium text-gray-900 whitespace-nowrap text-sm">
                        <div class="flex items-center gap-1.5">
                          {{ b.name_zh }}
                          <span v-if="b.notes" class="text-[9px] text-amber-400 opacity-60 group-hover:opacity-100">▾</span>
                        </div>
                      </td>
                      <td class="px-3 py-2.5 text-xs text-gray-500 max-w-[160px] truncate" :title="b.name_en || ''">
                        {{ b.name_en || '—' }}
                      </td>
                      <td class="px-3 py-2.5 text-xs text-gray-600 whitespace-nowrap font-mono">
                        {{ formatYear(b.start_year) }}{{ b.end_year != null ? `–${formatYear(b.end_year)}` : b.end_reason ? '' : '–' }}
                      </td>
                      <td class="px-3 py-2.5 text-xs text-gray-500 whitespace-nowrap">
                        {{ b.end_reason || '—' }}
                      </td>
                      <td class="px-3 py-2.5 text-xs text-gray-500 max-w-[140px] truncate" :title="b.appointed_by || ''">
                        {{ b.appointed_by || '—' }}
                      </td>
                      <td class="px-3 py-2.5 whitespace-nowrap">
                        <span :class="statusClass(b.status)" class="px-1.5 py-0.5 rounded text-[10px] font-medium">
                          {{ b.status }}
                        </span>
                      </td>
                      <td class="px-3 py-2.5">
                        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition" @click.stop>
                          <button class="p-1 rounded hover:bg-violet-100 text-violet-600 text-xs" @click="openEdit(b)">編輯</button>
                          <button class="p-1 rounded hover:bg-red-50 text-red-400 text-xs" @click="deleteBishop(b.id)">刪除</button>
                        </div>
                      </td>
                    </tr>
                    <!-- Expanded notes row -->
                    <tr v-if="expandedRows.has(b.id)" class="border-b border-amber-100 bg-amber-50/40">
                      <td colspan="8" class="px-5 py-3">
                        <p class="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">{{ b.notes }}</p>
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </main>
    </div>

    <!-- ── Detail modal (notes/sources popup) ─────────────── -->
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
          <p class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ detail.body }}</p>
        </div>
      </div>
    </div>

    <!-- ── Add / Edit modal ───────────────────────────────── -->
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
              <option v-for="s in sees" :key="s.see_zh" :value="s.see_zh" />
            </datalist>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">教會傳統</label>
            <input v-model="form.church" class="field" placeholder="例：東正教、天主教" list="church-list" />
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
              <option value="逝世">逝世</option>
              <option value="退休">退休</option>
              <option value="辭職">辭職</option>
              <option value="廢黜">廢黜</option>
              <option value="調任">調任</option>
              <option value="流亡">流亡</option>
              <option value="不明">不明</option>
            </select>
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">任命者</label>
            <input v-model="form.appointed_by" class="field" placeholder="例：耶穌基督、普世牧首" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">出處（分號分隔）</label>
            <input v-model="form.sources" class="field" placeholder="例：Eusebius HE III.3; Irenaeus AH III.3" />
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

// ── Types ───────────────────────────────────────────────────
interface See {
  id: string
  see_zh: string
  name_zh: string
  name_en: string | null
  church: string
  tradition: string
  rite: string | null
  founded_year: number | null
  abolished_year: number | null
  status: string | null
  current_patriarch_zh: string | null
  current_patriarch_en: string | null
  incumbent_since: number | null
  location: string | null
  notes: string | null
}

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

interface SubGroupItem { subGroup: string; sees: See[] }
interface TraditionGroup { tradition: string; seeCount: number; subGroups: SubGroupItem[] }

// ── Constants ───────────────────────────────────────────────
const TRADITION_ORDER = ['羅馬公教', '希臘正教', '科普特正教', '敘利亞正教', '亞美尼亞使徒教會', '亞述景教', '基督新教']

const TRAD_COLOR: Record<string, string> = {
  '羅馬公教':       'bg-indigo-100 text-indigo-800',
  '希臘正教':       'bg-blue-100 text-blue-800',
  '科普特正教':     'bg-amber-100 text-amber-800',
  '敘利亞正教':     'bg-teal-100 text-teal-800',
  '亞美尼亞使徒教會': 'bg-red-100 text-red-800',
  '亞述景教':       'bg-cyan-100 text-cyan-800',
  '基督新教':       'bg-green-100 text-green-800',
}

const CATHOLIC_SUBGROUP: Record<string, string> = {
  '天主教':           '拉丁禮教會',
  '天主教（拉丁禮）': '拉丁禮教會',
  '老天主教':         '獨立公教會',
  '德國舊天主教':     '獨立公教會',
  '瑞士基督天主教':   '獨立公教會',
  '奧地利舊天主教':   '獨立公教會',
  '波蘭民族天主教':   '獨立公教會',
}

const PROTESTANT_SUBGROUP: Record<string, string> = {
  '英格蘭教會': '聖公宗', '愛爾蘭教會': '聖公宗', '威爾士教會': '聖公宗', '蘇格蘭聖公會': '聖公宗',
  '美國聖公會': '聖公宗', '澳洲聖公宗': '聖公宗', '加拿大聖公宗': '聖公宗', '紐西蘭聖公宗': '聖公宗',
  '北美聖公宗教會': '聖公宗', '亞歷山卓聖公宗': '聖公宗', '蒲隆地聖公宗': '聖公宗', '南錐聖公宗': '聖公宗',
  '香港聖公宗': '聖公宗', '古巴聖公宗': '聖公宗', '烏干達聖公宗': '聖公宗', '西非聖公宗': '聖公宗',
  '墨西哥聖公宗': '聖公宗', '中非聖公宗': '聖公宗', '西印度群島聖公宗': '聖公宗', '美拉尼西亞聖公宗': '聖公宗',
  '東南亞聖公宗': '聖公宗', '巴紐聖公宗': '聖公宗', '坦尚尼亞聖公宗': '聖公宗', '南非聖公宗': '聖公宗',
  '耶路撒冷及中東聖公宗': '聖公宗', '巴西聖公宗': '聖公宗', '日本聖公宗（日本聖公會）': '聖公宗',
  '印度洋聖公宗': '聖公宗', '盧安達聖公宗': '聖公宗', '菲律賓聖公宗': '聖公宗', '韓國聖公宗': '聖公宗',
  '南蘇丹聖公宗': '聖公宗', '緬甸聖公宗': '聖公宗', '蘇丹聖公宗': '聖公宗', '奈及利亞聖公宗': '聖公宗',
  '肯亞聖公宗': '聖公宗', '耶路撒冷聖公宗': '聖公宗',
  '拉脫維亞信義會': '信義宗', '芬蘭信義會': '信義宗', '瑞典信義會': '信義宗', '愛沙尼亞信義會': '信義宗',
  '挪威信義會': '信義宗', '丹麥信義會': '信義宗', '冰島信義會': '信義宗',
  '德國聯合信義宗': '信義宗', '立陶宛信義會': '信義宗',
  '坦尚尼亞信義宗': '信義宗', '衣索比亞福音教會': '信義宗', '印尼巴塔克基督教': '信義宗',
  '美國福音信義教會': '信義宗', '南非信義宗': '信義宗', '納米比亞信義宗': '信義宗',
  '巴布亞紐幾內亞信義宗': '信義宗', '馬達加斯加信義宗': '信義宗', '喀麥隆福音信義宗': '信義宗',
  '賴比瑞亞信義宗': '信義宗', '安得拉信義宗': '信義宗', '坦米爾信義宗': '信義宗',
  '剛果聖公宗': '聖公宗', '中美洲聖公宗': '聖公宗', '莫三比克聖公宗': '聖公宗',
  '摩拉維亞弟兄會': '弟兄會',
  '美非衛理聖公會': '衛理宗', '美聯合衛理公會': '衛理宗', '非裔衛理錫安聖公宗': '衛理宗',
  '基督衛理聖公宗': '衛理宗', '全球衛理公會': '衛理宗', '南非衛理公會': '衛理宗',
  '印度衛理公會': '衛理宗', '韓國衛理公會': '衛理宗', '自由衛理宗': '衛理宗',
  '北印度教會': '聯合教會', '錫蘭教會': '聯合教會', '巴基斯坦教會': '聯合教會',
  '孟加拉教會': '聯合教會', '南印度教會': '聯合教會',
}

function getSubGroup(church: string, tradition: string): string {
  if (tradition === '羅馬公教') return CATHOLIC_SUBGROUP[church] ?? '東儀天主教'
  if (tradition === '基督新教') return PROTESTANT_SUBGROUP[church] ?? church
  return church
}

const knownChurches = [
  '未分裂教會', '東正教', '俄羅斯正教會', '烏克蘭正教會', '塞爾維亞正教會',
  '羅馬尼亞正教會', '保加利亞正教會', '格魯吉亞正教會',
  '亞美尼亞使徒教會', '亞美尼亞使徒教會（基里基亞）',
  '亞美尼亞使徒教會（君士坦丁堡）', '亞美尼亞使徒教會（耶路撒冷）',
  '敘利亞正統教會', '科普特正統教會', '衣索比亞正統特瓦赫多教會', '馬蘭卡拉正統敘利亞教會',
  '天主教', '烏克蘭希臘禮天主教會', '馬龍尼天主教會', '梅勒基特希臘天主教會',
  '加色丁天主教會', '亞美尼亞天主教會', '敘利亞天主教會', '科普特天主教會',
  '英格蘭教會', '聖公會',
]

// ── Auth helper ─────────────────────────────────────────────
const supabase = useSupabaseClient()
const router   = useRouter()

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) { router.push('/login'); return null }
  return session.access_token
}

// ── Sidebar state ───────────────────────────────────────────
const sees          = ref<See[]>([])
const seesLoading   = ref(true)
const sidebarSearch = ref('')

const expandedTraditions = ref(new Set<string>())
const expandedSubGroups  = ref(new Set<string>())

function toggleTradition(t: string) {
  const s = expandedTraditions.value
  s.has(t) ? s.delete(t) : s.add(t)
  expandedTraditions.value = new Set(s)
}
function toggleSubGroup(key: string) {
  const s = expandedSubGroups.value
  s.has(key) ? s.delete(key) : s.add(key)
  expandedSubGroups.value = new Set(s)
}

// ── Tree computation ────────────────────────────────────────
const tree = computed<TraditionGroup[]>(() => {
  const byTrad = new Map<string, Map<string, See[]>>()
  for (const s of sees.value) {
    const trad = s.tradition || '其他'
    const sg = getSubGroup(s.church, trad)
    if (!byTrad.has(trad)) byTrad.set(trad, new Map())
    const bySG = byTrad.get(trad)!
    if (!bySG.has(sg)) bySG.set(sg, [])
    bySG.get(sg)!.push(s)
  }

  const ordered: TraditionGroup[] = []
  const remaining = new Set(byTrad.keys())

  for (const t of TRADITION_ORDER) {
    if (byTrad.has(t)) {
      const subGroups: SubGroupItem[] = []
      byTrad.get(t)!.forEach((seelist, subGroup) => {
        seelist.sort((a, b) => a.name_zh.localeCompare(b.name_zh, 'zh'))
        subGroups.push({ subGroup, sees: seelist })
      })
      ordered.push({ tradition: t, seeCount: subGroups.reduce((n, sg) => n + sg.sees.length, 0), subGroups })
      remaining.delete(t)
    }
  }
  for (const t of remaining) {
    const subGroups: SubGroupItem[] = []
    byTrad.get(t)!.forEach((seelist, subGroup) => {
      seelist.sort((a, b) => a.name_zh.localeCompare(b.name_zh, 'zh'))
      subGroups.push({ subGroup, sees: seelist })
    })
    ordered.push({ tradition: t, seeCount: subGroups.reduce((n, sg) => n + sg.sees.length, 0), subGroups })
  }
  return ordered
})

const isSearching = computed(() => sidebarSearch.value.trim().length > 0)

const searchResults = computed(() => {
  if (!isSearching.value) return []
  const q = sidebarSearch.value.trim().toLowerCase()
  return sees.value.filter(s =>
    s.name_zh.toLowerCase().includes(q) ||
    (s.name_en || '').toLowerCase().includes(q) ||
    s.see_zh.toLowerCase().includes(q) ||
    s.church.toLowerCase().includes(q)
  )
})

// ── Succession list state ───────────────────────────────────
const selectedSee  = ref<See | null>(null)
const seeBishops   = ref<Bishop[]>([])
const seqLoading   = ref(false)
const expandedRows = ref(new Set<string>())

async function selectSee(s: See) {
  selectedSee.value = s
  expandedRows.value = new Set()
  seqLoading.value = true
  try {
    const token = await getToken()
    if (!token) return
    seeBishops.value = await $fetch<Bishop[]>('/api/genealogy/episcopal-succession', {
      headers: { Authorization: `Bearer ${token}` },
      query: { see: s.see_zh, church: s.church },
    })
  } finally {
    seqLoading.value = false
  }
}

function toggleRow(id: string) {
  const s = expandedRows.value
  s.has(id) ? s.delete(id) : s.add(id)
  expandedRows.value = new Set(s)
}

// ── Add / Edit modal state ──────────────────────────────────
const showModal = ref(false)
const editingId = ref<string | null>(null)
const saving    = ref(false)
const form      = ref(emptyForm())
const detail    = ref({ show: false, title: '', body: '', personName: '' })

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

function openAdd() {
  editingId.value = null
  form.value = emptyForm()
  if (selectedSee.value) {
    form.value.see    = selectedSee.value.see_zh
    form.value.church = selectedSee.value.church
  }
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
      const idx = seeBishops.value.findIndex(b => b.id === editingId.value)
      if (idx >= 0) seeBishops.value[idx] = updated
    } else {
      const created = await $fetch<Bishop>('/api/genealogy/episcopal-succession', {
        method: 'POST', body: form.value,
        headers: { Authorization: `Bearer ${token}` },
      })
      seeBishops.value.push(created)
      seeBishops.value.sort((a, b) =>
        (a.succession_number ?? 9999) - (b.succession_number ?? 9999) ||
        ((a.start_year ?? 9999) - (b.start_year ?? 9999))
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
  seeBishops.value = seeBishops.value.filter(b => b.id !== id)
}

// ── Helpers ─────────────────────────────────────────────────
function formatYear(y: number | null) {
  if (y == null) return '至今'
  return y < 0 ? `主前 ${Math.abs(y)}` : `${y}`
}

function statusClass(s: string) {
  if (s === '正統')       return 'bg-emerald-50 text-emerald-700'
  if (s === '對立')       return 'bg-red-50 text-red-600'
  if (s === '廢黜後復位') return 'bg-amber-50 text-amber-700'
  return 'bg-gray-100 text-gray-500'
}

// ── Load sees on mount ──────────────────────────────────────
const seesError = ref<string | null>(null)

onMounted(async () => {
  const token = await getToken()
  if (!token) return
  seesLoading.value = true
  seesError.value = null
  try {
    sees.value = await $fetch<See[]>('/api/genealogy/episcopal-sees', {
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch (e: unknown) {
    seesError.value = e instanceof Error ? e.message : '載入失敗'
  } finally {
    seesLoading.value = false
  }
})
</script>

<style scoped>
.field {
  @apply w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-violet-400 focus:ring-1 focus:ring-violet-200 transition bg-white;
}
</style>
