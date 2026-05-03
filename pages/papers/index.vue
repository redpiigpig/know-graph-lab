<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/writing" class="text-gray-400 hover:text-gray-700 transition text-sm">← 論文寫作系統</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">學術著作目錄</span>
      </div>
    </nav>

    <!-- 頁眉 -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-5xl mx-auto px-6 py-10">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-teal-100 text-teal-700">學術著作目錄</span>
          <span class="text-xs text-gray-400">張辰瑋</span>
        </div>
        <h1 class="text-xl font-bold text-gray-900 mb-4">期刊論文 · 會議論文 · 報紙社論</h1>
        <div class="flex flex-wrap gap-x-6 gap-y-1.5 text-sm text-gray-500">
          <span><span class="font-semibold text-gray-800">{{ journals.length }}</span> 篇期刊論文</span>
          <span><span class="font-semibold text-gray-800">{{ conferences.length }}</span> 篇會議論文</span>
          <span><span class="font-semibold text-gray-800">{{ editorials.length }}</span> 篇報紙社論</span>
        </div>
      </div>
    </div>

    <!-- 篩選 -->
    <div class="bg-white border-b border-gray-100 sticky top-14 z-30">
      <div class="max-w-5xl mx-auto px-6">
        <div class="flex">
          <button v-for="f in filters" :key="f.id" @click="active = f.id"
            :class="['px-5 py-3.5 text-sm font-medium border-b-2 transition-colors', active === f.id ? 'border-teal-600 text-teal-700' : 'border-transparent text-gray-500 hover:text-gray-800']">
            {{ f.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- 內容 -->
    <div class="max-w-5xl mx-auto px-6 py-8 space-y-8">

      <!-- 期刊論文 -->
      <section v-if="active === 'all' || active === 'journal'">
        <h2 v-if="active === 'all'" class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">期刊論文</h2>
        <div class="space-y-3">
          <div
            v-for="p in journals" :key="p.id"
            @click="() => p.hasText && navigateTo(`/papers/${p.id}`)"
            :class="['bg-white rounded-2xl border border-gray-100 p-5 transition-all',
              p.hasText ? 'cursor-pointer hover:border-teal-200 hover:shadow-sm' : 'hover:border-gray-200']"
          >
            <div class="flex items-start gap-3">
              <div class="flex-1 min-w-0">
                <div class="flex flex-wrap gap-1.5 mb-2">
                  <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-purple-50 text-purple-700">期刊論文</span>
                  <span :class="statusStyle(p.status)" class="text-xs font-medium px-2 py-0.5 rounded-full">{{ statusLabel(p.status) }}</span>
                  <span v-if="p.hasText" class="text-xs font-medium px-2 py-0.5 rounded-full bg-teal-50 text-teal-700">全文</span>
                </div>
                <h3 class="text-sm font-semibold text-gray-900 leading-snug mb-2">{{ p.title }}</h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-0.5 text-xs text-gray-500">
                  <span><span class="text-gray-400">期刊　</span>《{{ p.venue }}》</span>
                  <span><span class="text-gray-400">ISSN　</span>{{ p.issn }}</span>
                  <span><span class="text-gray-400">卷期　</span>{{ p.issue }}</span>
                  <span><span class="text-gray-400">出版　</span>{{ p.publisher }}</span>
                  <span><span class="text-gray-400">日期　</span>{{ p.date }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 會議論文 -->
      <section v-if="active === 'all' || active === 'conference'">
        <h2 v-if="active === 'all'" class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">會議論文</h2>
        <div class="space-y-3">
          <div
            v-for="p in conferences" :key="p.id"
            @click="() => p.hasText && navigateTo(`/papers/${p.id}`)"
            :class="['bg-white rounded-2xl border border-gray-100 p-5 transition-all',
              p.hasText ? 'cursor-pointer hover:border-teal-200 hover:shadow-sm' : 'hover:border-gray-200']"
          >
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap gap-1.5 mb-2">
                <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-teal-50 text-teal-700">會議論文</span>
                <span :class="statusStyle(p.status)" class="text-xs font-medium px-2 py-0.5 rounded-full">{{ statusLabel(p.status) }}</span>
                <span v-if="p.hasText" class="text-xs font-medium px-2 py-0.5 rounded-full bg-teal-50 text-teal-700">全文</span>
                <span v-if="p.bilingual" class="text-xs font-medium px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600">中英雙語</span>
              </div>
              <h3 class="text-sm font-semibold text-gray-900 leading-snug mb-2">{{ p.title }}</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-0.5 text-xs text-gray-500">
                <span class="sm:col-span-2"><span class="text-gray-400">研討會　</span>{{ p.venue }}</span>
                <span><span class="text-gray-400">主辦　</span>{{ p.organizer }}</span>
                <span><span class="text-gray-400">日期　</span>{{ p.date }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 報紙社論 -->
      <section v-if="active === 'all' || active === 'editorial'">
        <h2 v-if="active === 'all'" class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">報紙社論</h2>
        <div class="space-y-3">
          <div
            v-for="p in editorials" :key="p.id"
            @click="() => p.hasText && navigateTo(`/papers/${p.id}`)"
            :class="['bg-white rounded-2xl border border-gray-100 p-5 transition-all',
              p.hasText ? 'cursor-pointer hover:border-teal-200 hover:shadow-sm' : 'hover:border-gray-200']"
          >
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap gap-1.5 mb-2">
                <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-orange-50 text-orange-700">報紙社論</span>
                <span v-if="p.hasText" class="text-xs font-medium px-2 py-0.5 rounded-full bg-teal-50 text-teal-700">全文</span>
              </div>
              <h3 class="text-sm font-semibold text-gray-900 leading-snug mb-2">{{ p.title }}</h3>
              <div class="flex flex-wrap gap-x-6 gap-y-0.5 text-xs text-gray-500">
                <span><span class="text-gray-400">報紙　</span>{{ p.venue }}</span>
                <span><span class="text-gray-400">期次　</span>第 {{ p.issue }} 期</span>
                <span><span class="text-gray-400">日期　</span>{{ p.date }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup lang="ts">
useHead({ title: '學術著作目錄 — 張辰瑋' })

const active = ref('all')
const filters = [
  { id: 'all', label: '全部' },
  { id: 'journal', label: '期刊論文' },
  { id: 'conference', label: '會議論文' },
  { id: 'editorial', label: '報紙社論' },
]

type Status = 'published' | 'review' | 'upcoming'

interface JournalPaper {
  id: string; title: string; venue: string; issn: string; issue: string
  publisher: string; date: string; status: Status; hasText?: boolean
}
interface ConferencePaper {
  id: string; title: string; venue: string; organizer: string
  date: string; status: Status; hasText?: boolean; bilingual?: boolean
}
interface EditorialPaper {
  id: string; title: string; venue: string; issue: string; date: string; hasText?: boolean
}

const journals: JournalPaper[] = [
  {
    id: 'j1',
    title: '信仰與學術的交互作用：近半世紀印順學與印順學派歷史發展回顧（1973–2023）',
    venue: '玄奘佛學研究',
    issn: '1813-3649',
    issue: '待定',
    publisher: '玄奘大學',
    date: '已通過審查，刊登中',
    status: 'review',
    hasText: true,
  },
  {
    id: 'j2',
    title: '從「青年佛教」之精神看印順學派的歷史發展',
    venue: '法印學報',
    issn: '2224-1299',
    issue: '第 15 期',
    publisher: '財團法人弘誓文教基金會',
    date: '2024 年 12 月',
    status: 'published',
    hasText: true,
  },
  {
    id: 'j3',
    title: '昭慧法師與性廣法師對印順學的傳承與實踐──以經營佛教弘誓學院、參與社運、闡揚人間佛教禪法為例',
    venue: '法印學報',
    issn: '2224-1299',
    issue: '第 14 期',
    publisher: '財團法人弘誓文教基金會',
    date: '2023 年 12 月',
    status: 'published',
    hasText: true,
  },
]

const conferences: ConferencePaper[] = [
  {
    id: 'c1',
    title: '昭慧法師的戒律學思想與實踐：以性別議題為核心',
    venue: '第六屆中華國際佛學會議',
    organizer: '法鼓山中華佛學研究所',
    date: '2025 年 10 月 30 日–11 月 1 日',
    status: 'published',
    hasText: true,
  },
  {
    id: 'c2',
    title: '從同理心到倫理秩序：主體性動物倫理的建構與社會實踐',
    venue: '第二十三屆印順導師思想之理論與實踐學術研討會',
    organizer: '玄奘大學台灣佛教研究中心',
    date: '2025 年 9 月 28 日',
    status: 'published',
    hasText: true,
    bilingual: true,
  },
  {
    id: 'c3',
    title: '傳道法師與台南妙心寺對印順學派成立之貢獻',
    venue: '臺南府城佛影：人間菩薩傳道法師圓寂十週年學術研討會',
    organizer: '國立台南大學人文學院',
    date: '2024 年 12 月 28 日',
    status: 'published',
    hasText: true,
  },
  {
    id: 'c4',
    title: '信仰與學術的交互作用：近半世紀印順學與印順學派歷史發展回顧（1973–2023）',
    venue: '第三屆「臺灣佛教論壇」暨「臺灣佛教之傳承與展望」國際學術會議',
    organizer: '玄奘大學台灣佛教研究中心',
    date: '2024 年 11 月 16–17 日',
    status: 'published',
    hasText: true,
  },
  {
    id: 'c5',
    title: '耶佛之間的跨宗教友誼與跨宗教合作：以釋昭慧法師、盧俊義牧師、洪山川主教為例',
    venue: '台灣宗教學會 2024 年會「跨域與研修」',
    organizer: '台灣宗教學會',
    date: '2024 年 10 月 25–26 日',
    status: 'published',
    hasText: true,
  },
  {
    id: 'c6',
    title: '台灣佛教的宗教反抗傳統：以林秋梧、釋迦宗聖、釋傳道、釋昭慧為例',
    venue: '第三十五屆全國佛學論文聯合發表會',
    organizer: '台灣大學佛學研究中心',
    date: '2024 年 9 月 27–29 日',
    status: 'published',
  },
  {
    id: 'c7',
    title: '從「青年佛教」之精神看印順學派的歷史發展',
    venue: '第二十二屆印順導師思想之理論與實踐學術研討會',
    organizer: '佛教慈濟慈善基金會',
    date: '2024 年 8 月 24–25 日',
    status: 'published',
  },
  {
    id: 'c8',
    title: '台灣漢傳佛教的未來藍圖：以白聖、印順、星雲等長老的芻議為例',
    venue: '2023 年慧炬大學院校佛學論文及佛教文學創作獎學金',
    organizer: '慧炬雜誌社',
    date: '2023 年 12 月',
    status: 'published',
  },
  {
    id: 'c9',
    title: '臺灣師資培育制度的體質檢視：以校內師資培育制度多軌並行的某國立教育大學為例',
    venue: '「教育體質的檢視與再造：教改 30 面向未來」國際學術研討會',
    organizer: '國立台灣師範大學教育學系',
    date: '2023 年 11 月 17–18 日',
    status: 'published',
  },
  {
    id: 'c10',
    title: '昭慧法師與性廣法師對印順學的傳承與實踐：以經營佛教弘誓學院、參與社運、闡揚人間佛教禪法為例',
    venue: '第二十一屆印順導師思想之理論與實踐學術研討會',
    organizer: '玄奘大學台灣佛教研究中心',
    date: '2023 年 8 月 12–13 日',
    status: 'published',
    hasText: true,
  },
  {
    id: 'c11',
    title: '1960–70 年代福音派運動在台灣華語教會中的崛起',
    venue: '2023 第 16 屆「全國研究生歷史學論文研討會」',
    organizer: '台灣歷史學會',
    date: '2023 年 6 月 10 日',
    status: 'published',
  },
]

const editorials: EditorialPaper[] = [
  { id: 'e1', title: '自由派究竟是什麼？', venue: '台灣教會公報', issue: '3473', date: '2018 年 9 月 21 日', hasText: true },
  { id: 'e2', title: '中產階級的講台', venue: '台灣教會公報', issue: '3471', date: '2018 年 9 月 7 日', hasText: true },
  { id: 'e3', title: '盡智', venue: '台灣教會公報', issue: '3435', date: '2017 年 12 月 26 日', hasText: true },
]

function statusStyle(status: Status) {
  const m: Record<Status, string> = {
    published: 'bg-green-50 text-green-700',
    review: 'bg-amber-50 text-amber-700',
    upcoming: 'bg-gray-100 text-gray-500',
  }
  return m[status]
}
function statusLabel(status: Status) {
  const m: Record<Status, string> = {
    published: '已發表',
    review: '刊登中',
    upcoming: '籌備中',
  }
  return m[status]
}
</script>
