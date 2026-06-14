// 把碩士論文「論文資料」archive（C:\tmp\dadaodao_files.json）轉成《當代的大愛道革命》
// 研究資料 manifest，**依論文徵引資料的「文獻類別」分類**（仿 ch6.txt 徵引資料）：
//   印順／昭慧／性廣 三師維持「作者」分類；其餘按文獻類別（期刊/研討會/學位論文/雜誌會訊/檔案…）
//   與主題分類。off-topic 且論文未徵引的國家檔案（周聯華/衛理堂/高俊明 等基督教白色恐怖案）剔除。
// 原檔上傳 R2（upload_dadaodao_r2.py），全文 dadaodao-fulltext/，下載走 /api/works/material。
//   重跑：PowerShell 重列檔 → C:\tmp\dadaodao_files.json，再 `node scripts/build_dadaodao_materials.mjs`
import { readFileSync, writeFileSync } from 'node:fs'

const SLUG = 'mahaprajapati-revolution'
const R2_PREFIX = 'dadaodao-materials'
const SRC = 'C:/tmp/dadaodao_files.json'
const OUT = `public/content/works/${SLUG}-materials.json`

const { root, files } = JSON.parse(readFileSync(SRC, 'utf8').replace(/^﻿/, ''))
const base = (rel) => rel.split('/').pop()
const fileEntry = (f) => ({ name: base(f.rel), key: `${R2_PREFIX}/${f.rel}`, size: f.size })

// ── 剔除：論文徵引資料完全未寫到且與主題（印順／昭慧／性廣人間佛教）無關的國家檔案 ──
// 論文只徵引「印順《佛法概論》查禁」一案；以下基督教界白色恐怖案皆未引用且無關。
const OFFTOPIC_ARCHIVE = /周聯華|衛理堂|WCC|高俊明|戴華光|李國民|聖經受政府取締|穆克禮|叛亂犯/
function pruned(rel) {
  return rel.startsWith('檔案/') && OFFTOPIC_ARCHIVE.test(rel)
}

// ── 二手研究專文的主題（依檔名／資料夾關鍵字）──
const KW = {
  '性別平權與大愛道': /八敬法|性別|女性|比丘尼|兩性|同志|同性|婚姻平權|二部受戒|大愛道|尼僧|女眾|出櫃|平權|壹同寺/i,
  '社會運動與入世佛教': /社運|社會運動|入世|參與佛教|動保|動物|護生|生態|環保|反賭|博弈|博奕|政治|左翼|林義雄|烈火|安貝卡|復興運動|TBMSG/i,
  '禪觀修持與佛教養生': /禪觀|禪修|禪七|四念處|帕奧|養生|四界|四大|定慧|止觀|健身|禪法/i,
  '宗教對話': /天主教|主教|神父|修女|基督|長老教會|牧師|宗教對話|宗教交談|交談|古倫/i,
  '當代台灣佛教（對比山頭）': /星雲|佛光山|聖嚴|法鼓|慈濟|證嚴|趙樸初|現代禪|心靈環保/i,
}
function theme(rel) {
  for (const [label, re] of Object.entries(KW)) if (re.test(rel)) return label
  return '印順學與人間佛教思想' // 預設
}

// ── 主分類（文獻類別）；印順／昭慧／性廣 例外用作者分類 ──
function classify(rel) {
  const p = rel.split('/')
  const c = p[0]
  if (c === '作者' && p[1] === '釋印順') return { cat: '印順導師', sub: '釋印順 著作' }
  if ((c === '作者' && p[1] === '釋昭慧') || (c === '議題' && p[1] === '昭慧法師')) return { cat: '昭慧法師', sub: '昭慧法師 著作與相關研究' }
  if ((c === '作者' && p[1] === '釋性廣') || (c === '議題' && p[1] === '性廣法師')) return { cat: '性廣法師', sub: '性廣法師 著作與相關研究' }
  if (c === '人間佛教研究期刊') return { cat: '期刊論文', sub: '《人間佛教研究》' }
  if (c === '印順學研討會') return { cat: '研討會論文', sub: '印順學研討會（印順導師思想之理論與實踐）' }
  if (c === '弘誓' && p[1] === '學位論文') return { cat: '學位論文', sub: '弘誓僧團相關學位論文' }
  if (c === '弘誓') return { cat: '雜誌與會訊', sub: '《弘誓》雙月刊' }
  if (c === '福嚴會訊') return { cat: '雜誌與會訊', sub: '《福嚴會訊》' }
  if (c === '表格') return { cat: '工具書與彙整', sub: '彙整表格與圖' }
  if (c === '檔案') {
    if (/佛法概論/.test(rel)) return { cat: '法規檔案', sub: '印順《佛法概論》查禁案（論文徵引）' }
    if (/善導寺|道安|陳善謙/.test(rel)) return { cat: '法規檔案', sub: '善導寺相關檔案' }
    return { cat: '法規檔案', sub: '國家檔案局其他卷宗（內容待全文轉錄辨識）' }
  }
  // 其餘學者二手研究（作者非三師＋議題其他主題）→ 主題研究專文，依主題分組
  return { cat: '主題研究專文', sub: theme(rel) }
}

const CAT_META = {
  '印順導師': { icon: '📿', desc: '印順導師（釋印順）著作與自述' },
  '昭慧法師': { icon: '🪷', desc: '昭慧法師著作、時論與相關研究（含議題專輯）', core: true },
  '性廣法師': { icon: '🧘', desc: '性廣法師著作、禪觀與相關研究（含議題專輯）', core: true },
  '主題研究專文': { icon: '📚', desc: '其他學者的二手研究專文，依主題分組（非依作者）' },
  '期刊論文': { icon: '📰', desc: '學術期刊刊載之論文' },
  '研討會論文': { icon: '🎓', desc: '研討會發表之論文與側記' },
  '學位論文': { icon: '🎓', desc: '碩博士學位論文' },
  '雜誌與會訊': { icon: '🗞️', desc: '教界雜誌、雙月刊與會訊（《弘誓》雙月刊・《福嚴會訊》）' },
  '法規檔案': { icon: '🗄️', desc: '政府檔案與會議記錄（論文徵引之印順查禁案＋善導寺脈絡；基督教界白色恐怖等無關卷宗已剔除）' },
  '工具書與彙整': { icon: '📊', desc: '彙整表格、分布圖與工具性資料' },
}
const CAT_ORDER = ['印順導師', '昭慧法師', '性廣法師', '主題研究專文', '期刊論文', '研討會論文', '學位論文', '雜誌與會訊', '法規檔案', '工具書與彙整']
const SUB_PRIORITY = ['性別平權與大愛道', '社會運動與入世佛教', '禪觀修持與佛教養生', '宗教對話', '印順學與人間佛教思想', '當代台灣佛教（對比山頭）']

// 聚合：cat → sub → files
const cmap = new Map(CAT_ORDER.map((c) => [c, new Map()]))
let prunedCount = 0
for (const f of files) {
  if (pruned(f.rel)) { prunedCount++; continue }
  const { cat, sub } = classify(f.rel)
  const g = cmap.get(cat)
  if (!g.has(sub)) g.set(sub, [])
  g.get(sub).push(fileEntry(f))
}

function sortSubs(cat, names) {
  if (cat === '主題研究專文') {
    const head = SUB_PRIORITY.filter((n) => names.includes(n))
    return [...head, ...names.filter((n) => !SUB_PRIORITY.includes(n))]
  }
  return names.sort((a, b) => a.localeCompare(b, 'zh-Hant'))
}

const categories = CAT_ORDER.filter((c) => cmap.get(c).size).map((cat) => {
  const meta = CAT_META[cat]
  const gmap = cmap.get(cat)
  const groups = sortSubs(cat, [...gmap.keys()]).map((sub) => {
    const fs = gmap.get(sub).sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant'))
    const g = { label: sub, count: fs.length, size: fs.reduce((s, f) => s + f.size, 0), files: fs }
    if (['性別平權與大愛道'].includes(sub)) g.tag = '核心'
    return g
  })
  const count = groups.reduce((s, g) => s + g.count, 0)
  return { key: cat, label: cat, icon: meta.icon, desc: meta.desc, groups, count }
})

const kept = files.length - prunedCount
const manifest = {
  book: '當代的大愛道革命',
  subtitle: '昭慧法師與性廣法師的人間佛教思想與實踐',
  source: root,
  note: '研究資料依論文徵引資料的文獻類別整理：印順／昭慧／性廣三師維持作者分類，其餘按文獻類別（期刊／研討會／學位論文／雜誌會訊／檔案…）與主題分類。與本書主題無關且論文未徵引的國家檔案（基督教界白色恐怖案）已剔除。原檔可線上下載。',
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
  totalFiles: kept,
  prunedFiles: prunedCount,
  totalBytes: files.filter((f) => !pruned(f.rel)).reduce((s, f) => s + f.size, 0),
  categories,
}

writeFileSync(OUT, JSON.stringify(manifest, null, 2), 'utf8')
console.log(`Wrote ${OUT}: ${categories.length} 類, 保留 ${kept} 件（剔除 ${prunedCount}）`)
for (const c of categories) console.log(`  ${c.icon} ${c.label}: ${c.count} 件 / ${c.groups.length} 組`)
