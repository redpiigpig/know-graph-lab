<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader title="博士論文研究計畫" :back="{ to: '/writing/degrees', label: '學位論文' }" container-class="max-w-6xl" />

    <header class="proposal-cover border-b border-amber-100">
      <div class="max-w-6xl mx-auto px-5 sm:px-6 py-10 sm:py-14">
        <div class="flex flex-wrap items-center gap-2 mb-4">
          <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-amber-100 text-amber-800">博士論文研究計畫</span>
          <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-white/80 text-slate-600 border border-slate-200">第二版草案</span>
          <span class="text-xs text-slate-500">2026 年 7 月 24 日</span>
        </div>

        <p class="text-sm font-medium tracking-wide text-amber-700 mb-3">入世轉向的兩條譜系</p>
        <h1 class="max-w-4xl text-2xl sm:text-3xl font-bold text-slate-900 leading-snug mb-4">
          台灣人間佛教與以長老教會為核心之本土神學的歷史比較及神學比較
        </h1>
        <p class="max-w-4xl text-sm sm:text-base text-slate-600 leading-relaxed mb-2">
          以太虛、印順、傳道、昭慧與黃彰輝、宋泉盛、王憲治、黃伯和為核心
        </p>
        <p class="max-w-4xl text-xs sm:text-sm text-slate-400 italic leading-relaxed">
          Two Genealogies of This-Worldly Engagement: A Historical and Theological Comparison of Humanistic Buddhism and Presbyterian-Centered Taiwanese Contextual Theology
        </p>

        <div class="mt-7 flex flex-wrap gap-3">
          <a :href="secondVersionUrl" target="_blank" rel="noopener noreferrer" class="proposal-action proposal-action-primary">
            下載／開啟第二版 Word
          </a>
          <a :href="firstVersionUrl" target="_blank" rel="noopener noreferrer" class="proposal-action proposal-action-secondary">
            查看第一版 PDF
          </a>
        </div>

        <div class="mt-7 flex flex-wrap gap-x-6 gap-y-2 text-xs sm:text-sm text-slate-600">
          <span><span class="text-slate-400 mr-1.5">研究生</span>張辰瑋</span>
          <span><span class="text-slate-400 mr-1.5">學校</span>玄奘大學宗教與文化學系博士班</span>
          <span><span class="text-slate-400 mr-1.5">狀態</span>未發表草案，供指導與修訂使用</span>
        </div>
      </div>
    </header>

    <div class="max-w-6xl mx-auto px-5 sm:px-6 py-8 sm:py-10 lg:grid lg:grid-cols-[220px_minmax(0,1fr)] lg:gap-8">
      <aside class="hidden lg:block">
        <nav class="sticky top-24 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm" aria-label="研究計畫章節">
          <p class="px-3 pt-2 pb-2 text-xs font-semibold tracking-wider text-slate-400">第二版目錄</p>
          <a v-for="item in sectionNav" :key="item.id" :href="`#${item.id}`" class="block rounded-lg px-3 py-2 text-xs leading-snug text-slate-600 hover:bg-amber-50 hover:text-amber-800">
            {{ item.label }}
          </a>
          <div class="mt-3 border-t border-slate-100 pt-3 px-3 pb-2">
            <p class="text-[11px] leading-relaxed text-slate-400">本版以歷史研究為方法核心；「人間宗教」只在結論階段作為待檢驗命題。</p>
          </div>
        </nav>
      </aside>

      <main class="min-w-0">
        <div class="lg:hidden mb-5">
          <label for="proposal-section" class="sr-only">前往章節</label>
          <select id="proposal-section" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700" @change="jumpToSection">
            <option value="">前往章節</option>
            <option v-for="item in sectionNav" :key="item.id" :value="item.id">{{ item.label }}</option>
          </select>
        </div>

        <div class="mb-5 rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm leading-relaxed text-amber-950">
          <strong class="font-semibold">第二版改寫重點：</strong>
          方法論集中於思想史、概念史、接受史、制度史、口述歷史與比較歷史；神學比較置於歷史重建之後。研究回顧改以人間佛教、本土神學及跨宗教比較研究為主，並以佛教與基督教各四位人物形成兩條可比較、但不強迫對稱的歷史譜系。
        </div>

        <article class="proposal-paper proposal-body" v-html="proposalHtml"></article>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import proposalRaw from '~/data/doctoral_thesis_proposal_v2_draft.md?raw'

useHead({
  title: '博士論文研究計畫第二版 — 入世轉向的兩條譜系',
  meta: [
    { name: 'description', content: '張辰瑋博士論文研究計畫第二版草案：台灣人間佛教與以長老教會為核心之本土神學的歷史比較及神學比較。' },
  ],
})

const firstVersionUrl = 'https://drive.google.com/file/d/1H18e06dkR5RCm-ysdknL-RBPYx1WE2g0/view?usp=drivesdk'
const secondVersionUrl = 'https://docs.google.com/document/d/1kCKEAc8Hye1v5tw722N4UA_4T8qIV8eP/edit?usp=drivesdk&ouid=114506877330190031757&rtpof=true&sd=true'

const sectionNav = [
  { id: 'proposal-摘要', label: '摘要／Abstract' },
  { id: 'proposal-一', label: '一、研究背景與問題意識' },
  { id: 'proposal-二', label: '二、研究回顧' },
  { id: 'proposal-三', label: '三、研究對象、範圍與分期' },
  { id: 'proposal-四', label: '四、研究方法與材料' },
  { id: 'proposal-五', label: '五、主要史料與分析程序' },
  { id: 'proposal-六', label: '六、預期成果與貢獻' },
  { id: 'proposal-七', label: '七、論文章節大綱' },
  { id: 'proposal-八', label: '八、研究進度規劃' },
  { id: 'proposal-九', label: '九、核心參考文獻' },
]

const figuresHeaders = ['傳統', '人物', '歷史位置', '主要場域／媒介', '比較焦點']
const figuresRows = [
  ['人間佛教', '太虛', '近代佛教改革與人生佛教的問題開端', '僧教育、佛教團體、刊物與改革方案', '佛教如何回應現代國家與社會危機'],
  ['人間佛教', '印順', '以佛教史與經典判攝重建人間佛教', '著作、講學、僧團及台灣佛教知識網絡', '歷史敘事如何賦予入世實踐正當性'],
  ['人間佛教', '傳道', '印順思想的制度化、出版化與地方實踐', '妙心寺、中華佛教百科文獻基金會、社會運動', '思想如何透過寺院與組織進入公共領域'],
  ['人間佛教', '昭慧', '人間佛教公共倫理的系統化與行動化', '弘誓學院、戒律詮釋、性別與動物倫理運動', '規範倫理如何連結佛教傳統與社會倡議'],
  ['本土神學', '黃彰輝', '實況化神學與普世神學教育的開創', '神學教育、普世教會網絡、處境化方法', '教會如何在具體歷史處境中重述信仰'],
  ['本土神學', '宋泉盛', '亞洲故事、文化經驗與受苦人民的神學重構', '敘事神學、亞洲神學、普世出版與教學', '人民故事如何成為神學知識與救贖論資源'],
  ['本土神學', '王憲治', '鄉土神學的政治化、制度化與公共實踐', '南神、長老教會神學顧問、鄉土神學研究組織', '人民、土地、權力與上帝如何構成歷史政治論述'],
  ['本土神學', '黃伯和', '出頭天／自決神學與信仰再告白的系統發展', '研究中心、出版、人才培育、跨宗教與國際網絡', '本土神學如何延續、擴張並回應新公共議題'],
]

const scheduleHeaders = ['階段', '主要工作', '材料與方法', '預期成果']
const scheduleRows = [
  ['第一年上', '修訂研究問題、概念界定與史料目錄；完成四位早期人物的初步文獻回顧', '專書、論文、年譜、期刊與檔案盤點；建立人物—概念—機構年表', '緒論、研究回顧與方法章草稿'],
  ['第一年下', '重建兩條譜系的早期歷史處境與思想形成', '思想史、概念史與文本脈絡分析；比對版本與出版時間', '第二、三、五章初稿'],
  ['第二年上', '研究傳道、昭慧、王憲治、黃伯和的制度網絡與公共實踐', '寺院、神學院、教會、基金會、期刊與社運資料；接受史與制度史', '第四、六章初稿；機構與事件資料庫'],
  ['第二年下', '進行訪談並完成跨宗教事件個案的史料校證', '半結構訪談、口述歷史、新聞與組織檔案互證', '訪談逐字稿、事件年表與個案分析'],
  ['第三年上', '展開歷時與共時的比較歷史分析，並進行有限度神學比較', '比較矩陣、概念流變、因果機制與不對稱性分析', '第七章初稿；全論文整合稿'],
  ['第三年下', '撰寫結論並評估「人間宗教」命題的解釋力與界限；全面修訂', '回到史料檢核論證；補訪、格式與引註校訂', '第八章、博士論文完整稿與口試版本'],
]

function escapeHtml(value: string) {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

function formatInline(value: string) {
  const escaped = escapeHtml(value)
  return escaped
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/(https:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')
}

function renderTable(headers: string[], rows: string[][]) {
  return `<div class="proposal-table-wrap"><table><thead><tr>${headers.map(h => `<th>${formatInline(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(cell => `<td>${formatInline(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`
}

function headingId(text: string, level: number) {
  if (text === '摘要') return 'proposal-摘要'
  if (text === 'Abstract') return 'proposal-abstract'
  if (level === 1) {
    const match = text.match(/^([一二三四五六七八九])、/)
    if (match) return `proposal-${match[1]}`
  }
  return `proposal-${text.replace(/[\s、：／/（）()．，。・]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '')}`
}

function renderProposal(markdown: string) {
  const output: string[] = []
  let listType: 'ol' | 'ul' | null = null

  const closeList = () => {
    if (listType) output.push(`</${listType}>`)
    listType = null
  }

  for (const rawLine of markdown.split('\n')) {
    const line = rawLine.trim()
    if (!line) {
      closeList()
      continue
    }
    if (line === '[[TABLE:FIGURES]]') {
      closeList()
      output.push(renderTable(figuresHeaders, figuresRows))
      continue
    }
    if (line === '[[TABLE:SCHEDULE]]') {
      closeList()
      output.push(renderTable(scheduleHeaders, scheduleRows))
      continue
    }
    const heading = line.match(/^(#{1,3})\s+(.+)$/)
    if (heading) {
      closeList()
      const level = heading[1].length
      const text = heading[2]
      const tag = level === 1 ? 'h2' : level === 2 ? 'h3' : 'h4'
      output.push(`<${tag} id="${headingId(text, level)}">${formatInline(text)}</${tag}>`)
      continue
    }
    const ordered = line.match(/^\d+\.\s+(.+)$/)
    if (ordered) {
      if (listType !== 'ol') {
        closeList()
        output.push('<ol>')
        listType = 'ol'
      }
      output.push(`<li>${formatInline(ordered[1])}</li>`)
      continue
    }
    if (line.startsWith('- ')) {
      if (listType !== 'ul') {
        closeList()
        output.push('<ul>')
        listType = 'ul'
      }
      output.push(`<li>${formatInline(line.slice(2))}</li>`)
      continue
    }
    closeList()
    if (line.startsWith('REF: ')) {
      output.push(`<p class="proposal-reference">${formatInline(line.slice(5))}</p>`)
    } else if (line.startsWith('關鍵詞：') || line.startsWith('Keywords:')) {
      output.push(`<p class="proposal-keywords">${formatInline(line)}</p>`)
    } else {
      output.push(`<p>${formatInline(line)}</p>`)
    }
  }
  closeList()
  return output.join('')
}

const proposalHtml = computed(() => renderProposal(proposalRaw))

function jumpToSection(event: Event) {
  const id = (event.target as HTMLSelectElement).value
  if (!id || !import.meta.client) return
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<style scoped>
.proposal-cover {
  background:
    radial-gradient(circle at 85% 15%, rgba(245, 158, 11, 0.13), transparent 32%),
    linear-gradient(135deg, #fffdf7 0%, #ffffff 55%, #f8fafc 100%);
}

.proposal-action {
  @apply inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-sm font-semibold transition-colors no-underline;
}
.proposal-action-primary {
  @apply bg-amber-700 text-white hover:bg-amber-800;
}
.proposal-action-secondary {
  @apply border border-slate-300 bg-white text-slate-700 hover:bg-slate-50;
}

.proposal-paper {
  @apply rounded-2xl border border-slate-200 bg-white px-5 py-7 shadow-sm sm:px-9 sm:py-10;
}

:deep(.proposal-body h2) {
  @apply mt-12 mb-5 scroll-mt-24 border-b border-slate-200 pb-3 text-xl font-bold leading-snug text-slate-900;
}
:deep(.proposal-body h2:first-child) {
  @apply mt-0;
}
:deep(.proposal-body h3) {
  @apply mt-9 mb-3 scroll-mt-24 text-lg font-bold leading-snug text-amber-800;
}
:deep(.proposal-body h4) {
  @apply mt-7 mb-3 scroll-mt-24 text-base font-semibold leading-snug text-slate-800;
}
:deep(.proposal-body p) {
  @apply mb-4 text-[15px] leading-8 text-slate-700;
  text-align: justify;
}
:deep(.proposal-body ol),
:deep(.proposal-body ul) {
  @apply mb-5 ml-6 space-y-2 text-[15px] leading-7 text-slate-700;
}
:deep(.proposal-body ol) {
  @apply list-decimal;
}
:deep(.proposal-body ul) {
  @apply list-disc;
}
:deep(.proposal-body a) {
  @apply break-all text-amber-700 underline decoration-amber-300 underline-offset-2 hover:text-amber-900;
}
:deep(.proposal-body .proposal-keywords) {
  @apply rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600;
  text-align: left;
}
:deep(.proposal-body .proposal-reference) {
  @apply mb-2 pl-6 text-sm leading-6 text-slate-600;
  text-align: left;
  text-indent: -1.5rem;
}
:deep(.proposal-table-wrap) {
  @apply my-6 overflow-x-auto rounded-xl border border-slate-200;
}
:deep(.proposal-table-wrap table) {
  @apply min-w-[760px] w-full border-collapse text-left text-xs leading-5 text-slate-700;
}
:deep(.proposal-table-wrap th) {
  @apply border-b border-r border-slate-200 bg-amber-50 px-3 py-3 font-semibold text-amber-950 last:border-r-0;
}
:deep(.proposal-table-wrap td) {
  @apply border-b border-r border-slate-200 px-3 py-3 align-top last:border-r-0;
}
:deep(.proposal-table-wrap tbody tr:last-child td) {
  @apply border-b-0;
}
:deep(.proposal-table-wrap tbody tr:nth-child(even)) {
  @apply bg-slate-50/70;
}

@media (max-width: 640px) {
  :deep(.proposal-body p) {
    @apply text-sm leading-7;
    text-align: left;
  }
}
</style>
