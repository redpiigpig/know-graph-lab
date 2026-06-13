// 把碩士論文「論文資料」Drive archive 的檔案清單（C:\tmp\dadaodao_files.json）
// 轉成《當代的大愛道革命》研究資料分類索引 manifest，每個檔案附 R2 下載 key。
// 原檔上傳 R2（scripts/upload_dadaodao_r2.py），網站經 /api/works/material 簽名下載。
//   重跑：先用 PowerShell 重列檔案 → C:\tmp\dadaodao_files.json，再 `node scripts/build_dadaodao_materials.mjs`
import { readFileSync, writeFileSync } from 'node:fs'

const SLUG = 'mahaprajapati-revolution'
const R2_PREFIX = 'dadaodao-materials'
const SRC = 'C:/tmp/dadaodao_files.json'
const OUT = `public/content/works/${SLUG}-materials.json`

const { root, files } = JSON.parse(readFileSync(SRC, 'utf8').replace(/^﻿/, ''))

const base = (rel) => rel.split('/').pop()
const fileEntry = (f) => ({ name: base(f.rel), key: `${R2_PREFIX}/${f.rel}`, size: f.size })

// 把 rel 路徑分派到 (categoryLabel, groupLabel)
function classify(rel) {
  const p = rel.split('/')
  const cat = p[0]
  switch (cat) {
    case '作者':
      return { cat: '作者文獻', group: p[1] }
    case '議題':
      return { cat: '議題專輯', group: p.length > 2 ? p[1] : '其他主題文章' }
    case '弘誓':
      return { cat: '弘誓', group: p[1] === '學位論文' ? '學位論文' : '《弘誓》雙月刊文章' }
    case '印順學研討會':
      return { cat: '印順學研討會', group: '會議側記與論文' }
    case '人間佛教研究期刊':
      return { cat: '人間佛教研究期刊', group: '期刊論文' }
    case '福嚴會訊':
      return { cat: '福嚴會訊', group: '會訊全套掃描' }
    case '檔案':
      if (p.length === 2) return { cat: '檔案', group: '綜覽文件' }
      if (p.length === 3) return { cat: '檔案', group: '國家檔案管理局：總清單' }
      return { cat: '檔案', group: p[2] } // 依案件夾
    case '表格':
      return { cat: '整理表格與圖', group: '表格與圖檔' }
    default:
      return { cat: cat || '其他', group: '檔案' }
  }
}

// 聚合
const cats = new Map()
for (const f of files) {
  const { cat, group } = classify(f.rel)
  if (!cats.has(cat)) cats.set(cat, new Map())
  const g = cats.get(cat)
  if (!g.has(group)) g.set(group, [])
  g.get(group).push(fileEntry(f))
}

// 類別/群組的順序與 metadata
const CAT_META = {
  '作者文獻': { key: 'authors', icon: '🖋️', desc: '依作者整理的專文、序跋、訪談錄（19 位）；昭慧、性廣與弘誓僧團著者列於最前',
    order: ['釋昭慧', '釋性廣', '釋傳法', '釋見岸', '釋悟殷', '侯坤宏', '邱敏捷', '林建德', '楊惠南', '江燦騰', '藍吉富', '闞正宗', '游祥洲', '李志夫', '釋傳道', '黃運喜', '洪山川', '盧俊義', '釋印順'] },
  '議題專輯': { key: 'issues', icon: '🗂️', desc: '依研究議題彙整的二手研究與相關文章',
    order: ['佛教性別議題', '昭慧法師', '性廣法師', '入世佛教', '印順學', '人間佛教研究', '太虛大師', '法鼓山', '佛光山', '慈濟', '現代禪', '趙樸初', '其他主題文章'] },
  '弘誓': { key: 'hongshi', icon: '📰', desc: '《弘誓》雙月刊文章、學院簡介與弘誓僧團相關學位論文', order: ['《弘誓》雙月刊文章', '學位論文'] },
  '印順學研討會': { key: 'conference', icon: '🎓', desc: '歷屆「印順導師思想之理論與實踐」學術會議側記與論文（第 4–20 屆）', order: [] },
  '人間佛教研究期刊': { key: 'journal', icon: '📚', desc: '《人間佛教研究》刊載之相關論文', order: [] },
  '福嚴會訊': { key: 'fuyan', icon: '🗞️', desc: '福嚴佛學院《福嚴會訊》全套會訊掃描（第 1–71 期）', order: [] },
  '檔案': { key: 'archive', icon: '🗄️', desc: '國家檔案管理局調閱之白色恐怖時期善導寺／印順《佛法概論》查禁相關政府檔案（2023.04.15 調閱）', order: ['綜覽文件', '國家檔案管理局：總清單'] },
  '整理表格與圖': { key: 'tables', icon: '📊', desc: '研究過程自製的彙整表格、分布圖與訪談關係圖', order: [] },
}
const CAT_ORDER = ['作者文獻', '議題專輯', '弘誓', '印順學研討會', '人間佛教研究期刊', '福嚴會訊', '檔案', '整理表格與圖']
const CORE_GROUPS = new Set(['釋昭慧', '釋性廣', '昭慧法師', '性廣法師', '《弘誓》雙月刊文章', '佛教性別議題'])

function sortGroups(groupMap, order) {
  const names = [...groupMap.keys()]
  const head = order.filter((n) => groupMap.has(n))
  const tail = names.filter((n) => !order.includes(n)).sort((a, b) => a.localeCompare(b, 'zh-Hant'))
  return [...head, ...tail]
}

const categories = CAT_ORDER.filter((c) => cats.has(c)).map((catLabel) => {
  const meta = CAT_META[catLabel]
  const gmap = cats.get(catLabel)
  const groups = sortGroups(gmap, meta.order).map((gLabel) => {
    const fs = gmap.get(gLabel).sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant'))
    const g = { label: gLabel, count: fs.length, size: fs.reduce((s, f) => s + f.size, 0), files: fs }
    if (CORE_GROUPS.has(gLabel)) g.tag = '核心'
    return g
  })
  return { key: meta.key, label: catLabel, icon: meta.icon, desc: meta.desc, groups }
})

const manifest = {
  book: '當代的大愛道革命',
  subtitle: '昭慧法師與性廣法師的人間佛教思想與實踐',
  source: root,
  note: '原碩士論文研究資料全數移入並上傳雲端，依 Drive 原始分類整理，每件可線上下載。',
  interviews: true,
  // 碩士文稿正文（改寫底稿）：章節文字在 /content/thesis，PDF 原檔上傳 R2
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
const ng = categories.reduce((s, c) => s + c.groups.length, 0)
console.log(`Wrote ${OUT}: ${categories.length} categories, ${ng} groups, ${manifest.totalFiles} files, ${(manifest.totalBytes / 1024 / 1024).toFixed(0)} MB`)
