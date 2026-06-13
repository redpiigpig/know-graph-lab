// 把碩士論文「論文資料」archive（C:\tmp\dadaodao_files.json）轉成《當代的大愛道革命》
// 研究資料 manifest，依 7 大「主題軸」重分類（每檔依關鍵字路由），保留出處為子群組。
// 原檔上傳 R2（scripts/upload_dadaodao_r2.py），網站經 /api/works/material 簽名下載。
//   重跑：PowerShell 重列檔 → C:\tmp\dadaodao_files.json，再 `node scripts/build_dadaodao_materials.mjs`
import { readFileSync, writeFileSync } from 'node:fs'

const SLUG = 'mahaprajapati-revolution'
const R2_PREFIX = 'dadaodao-materials'
const SRC = 'C:/tmp/dadaodao_files.json'
const OUT = `public/content/works/${SLUG}-materials.json`

const { root, files } = JSON.parse(readFileSync(SRC, 'utf8').replace(/^﻿/, ''))
const base = (rel) => rel.split('/').pop()
const fileEntry = (f) => ({ name: base(f.rel), key: `${R2_PREFIX}/${f.rel}`, size: f.size })

// ── 出處（provenance）子群組：作者名／議題／資料夾 ──
function source(rel) {
  const p = rel.split('/')
  switch (p[0]) {
    case '作者': return p[1]
    case '議題': return p.length > 2 ? p[1] : '議題雜項'
    case '弘誓': return p[1] === '學位論文' ? '弘誓僧團學位論文' : '《弘誓》雙月刊'
    case '印順學研討會': return '印順學研討會'
    case '人間佛教研究期刊': return '人間佛教研究期刊'
    case '福嚴會訊': return '福嚴會訊'
    case '檔案': return p.length >= 3 ? (p[2] ?? '國家檔案局') : '檔案綜覽'
    case '表格': return '彙整表格與圖'
    default: return p[0] || '其他'
  }
}

// ── 7 主題軸：依檔名／資料夾關鍵字路由 ──
const KW = {
  gender: /八敬法|性別|女性|比丘尼|兩性|同志|同性|婚姻平權|二部受戒|大愛道|尼僧|女眾|出櫃|平權|壹同寺|女佛|Women|Nuns?|Gender|Ordination|Bhikkhuni|female/i,
  meditation: /禪觀|禪修|禪七|四念處|帕奧|養生|四界|四大|定慧|止觀|健身|禪法|禪堂|燃燈|共修|乾淨飲食|食安/i,
  dialogue: /天主教|主教|神父|修女|基督|長老教會|牧師|宗教對話|宗教交談|宗教對談|交談|古倫|盧俊義|洪山川|公署|跨宗教/i,
  activism: /社運|社會運動|入世|參與佛教|engaged|動保|動物|護生|護生|生態|環保|反賭|博弈|博奕|政治|公民社會|左翼|林義雄|烈火|安樂死|安貝卡|復興運動|TBMSG|入世佛教/i,
  historiography: /白色恐怖|查禁|善導寺|戰後|史料|口述歷史|口述訪問|年鑑|教育年鑑|遷讓|叛亂|周聯華|戴華光|高俊明|檔案|沿革/i,
}
// 出處 → 預設主題（無關鍵字命中時）
const SRC_DEFAULT = {
  '佛教性別議題': 'gender', '昭慧法師': 'thought', '性廣法師': 'meditation',
  '入世佛教': 'activism', '游祥洲': 'activism',
  '法鼓山': 'historiography', '佛光山': 'historiography', '慈濟': 'historiography', '趙樸初': 'historiography', '現代禪': 'historiography', '太虛大師': 'thought',
  '印順學': 'thought', '人間佛教研究': 'thought', '議題雜項': 'thought',
  '印順學研討會': 'thought', '人間佛教研究期刊': 'thought',
  '福嚴會訊': 'historiography', '檔案綜覽': 'historiography', '國家檔案局': 'historiography', '彙整表格與圖': 'historiography',
  '《弘誓》雙月刊': 'sangha', '弘誓僧團學位論文': 'sangha',
  '釋昭慧': 'sangha', '釋性廣': 'meditation', '釋傳法': 'sangha', '釋見岸': 'sangha',
  '侯坤宏': 'thought', '邱敏捷': 'thought', '林建德': 'thought', '楊惠南': 'thought',
  '江燦騰': 'thought', '藍吉富': 'thought', '闞正宗': 'thought', '李志夫': 'thought',
  '釋悟殷': 'thought', '釋傳道': 'thought', '黃運喜': 'historiography', '釋印順': 'thought',
  '洪山川': 'dialogue', '盧俊義': 'dialogue',
}
function theme(rel, src) {
  const hay = rel // 用整段相對路徑（含資料夾＋檔名）比對
  for (const t of ['gender', 'meditation', 'dialogue', 'activism', 'historiography']) {
    if (KW[t].test(hay)) return t
  }
  // 國家檔案局案件夾（無檔名語意）一律史料
  if (rel.startsWith('檔案/')) return 'historiography'
  return SRC_DEFAULT[src] ?? 'thought'
}

const THEME_META = {
  thought: { label: '人間佛教思想與印順學脈絡', icon: '🌱', desc: '印順導師人間佛教的體系、印順學派的成立與分流，及太虛以降的思想傳承' },
  gender: { label: '性別平權與大愛道革命', icon: '⚖️', desc: '八敬法廢除、女性出家與二部受戒、佛教女性研究、同志婚姻平權的佛學反思', core: true },
  activism: { label: '社會運動與入世佛教', icon: '✊', desc: '動物保護、反賭博、生態環保、國際入世佛教與當代台灣佛教社會運動' },
  meditation: { label: '禪觀修持與佛教養生', icon: '🧘', desc: '性廣法師的禪觀思想、帕奧禪法、四念處與「四界調和」佛教養生學' },
  dialogue: { label: '宗教對話', icon: '🕊️', desc: '與天主教（洪山川總主教）、基督長老教會（盧俊義牧師）的跨宗教交談與合作' },
  sangha: { label: '弘誓教團與人物', icon: '🪷', desc: '佛教弘誓學院／僧團的建置與人物、《弘誓》雙月刊、訪談錄與相關學位論文' },
  historiography: { label: '史料與當代台灣佛教脈絡', icon: '🗄️', desc: '國家檔案局白色恐怖檔案、福嚴會訊、彙整表格，及法鼓山／佛光山／慈濟等對比山頭' },
}
const THEME_ORDER = ['thought', 'gender', 'activism', 'meditation', 'dialogue', 'sangha', 'historiography']

// 出處子群組在各主題內的排序：兩位法師與其教團優先
const SRC_PRIORITY = ['釋昭慧', '釋性廣', '佛教性別議題', '昭慧法師', '性廣法師', '釋傳法', '釋見岸', '《弘誓》雙月刊', '弘誓僧團學位論文', '釋悟殷']

// 聚合：theme → source → files
const tmap = new Map(THEME_ORDER.map((t) => [t, new Map()]))
for (const f of files) {
  const src = source(f.rel)
  const t = theme(f.rel, src)
  const g = tmap.get(t)
  if (!g.has(src)) g.set(src, [])
  g.get(src).push(fileEntry(f))
}

function sortSources(names) {
  const head = SRC_PRIORITY.filter((n) => names.includes(n))
  const tail = names.filter((n) => !SRC_PRIORITY.includes(n)).sort((a, b) => a.localeCompare(b, 'zh-Hant'))
  return [...head, ...tail]
}

const categories = THEME_ORDER.filter((t) => tmap.get(t).size).map((t) => {
  const meta = THEME_META[t]
  const gmap = tmap.get(t)
  const groups = sortSources([...gmap.keys()]).map((src) => {
    const fs = gmap.get(src).sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant'))
    const g = { label: src, count: fs.length, size: fs.reduce((s, f) => s + f.size, 0), files: fs }
    if (['釋昭慧', '釋性廣', '佛教性別議題', '《弘誓》雙月刊'].includes(src)) g.tag = '核心'
    return g
  })
  const count = groups.reduce((s, g) => s + g.count, 0)
  return { key: t, label: meta.label, icon: meta.icon, desc: meta.desc, count, groups }
})

const manifest = {
  book: '當代的大愛道革命',
  subtitle: '昭慧法師與性廣法師的人間佛教思想與實踐',
  source: root,
  note: '原碩士論文研究資料全數移入並上傳雲端，依 7 大主題軸重新分類（出處保留為子群組），每件可線上下載。',
  interviews: true,
  thesis: {
    title: '印順導師人間佛教思想的傳承與實踐：以昭慧法師、性廣法師為核心',
    note: '碩士論文全文（本專書改寫底稿）。國立臺北教育大學台灣文化研究所，2025。',
    pdfKey: 'dadaodao-materials/碩士文稿/張辰瑋碩士論文.pdf',
    contentBase: '/content/thesis',
    chapters: [
      { id: 'abstract', title: '摘要 / Abstract' },
      { id: 'ch1', title: '第一章　緒論' },
      { id: 'ch2', title: '第二章　印順導師人間佛教的體系演變與思想傳承' },
      { id: 'ch3', title: '第三章　昭慧法師與性廣法師的人間佛教事業' },
      { id: 'ch4', title: '第四章　社運界、教育界的行動' },
      { id: 'ch5', title: '第五章　昭慧法師與性廣法師的思想特徵' },
      { id: 'ch6', title: '第六章　結論' },
      { id: 'app2', title: '附錄一、二　組織圖・年表' },
      { id: 'app3', title: '附錄三　著作目錄' },
      { id: 'app4', title: '附錄四　訪談人物分類表' },
    ],
  },
  totalFiles: files.length,
  totalBytes: files.reduce((s, f) => s + f.size, 0),
  categories,
}

writeFileSync(OUT, JSON.stringify(manifest, null, 2), 'utf8')
console.log(`Wrote ${OUT}: ${categories.length} themes, ${manifest.totalFiles} files, ${(manifest.totalBytes / 1024 / 1024).toFixed(0)} MB`)
for (const c of categories) console.log(`  ${c.icon} ${c.label}: ${c.count} 件 / ${c.groups.length} 出處`)
