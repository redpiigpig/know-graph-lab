// 把碩士論文「論文資料」Drive archive 的原始樹（C:\tmp\dadaodao_raw_tree.json）
// 轉成《當代的大愛道革命》研究資料分類索引 manifest。
// 原檔留存 Google Drive（canonical storage）；此 manifest 只是分類索引，不複製檔案。
//   重跑：先用 PowerShell 重新產生 raw tree，再 `node scripts/build_dadaodao_materials.mjs`
import { readFileSync, writeFileSync } from 'node:fs'

const SLUG = 'mahaprajapati-revolution'
const RAW = 'C:/tmp/dadaodao_raw_tree.json'
const OUT = `public/content/works/${SLUG}-materials.json`

const raw = JSON.parse(readFileSync(RAW, 'utf8').replace(/^﻿/, ''))
const top = Object.fromEntries(raw.children.map((c) => [c.name, c]))

// 把一個 Drive 節點轉成 group（label + 檔案清單 + 數量）
function group(node, { label, tag, summary } = {}) {
  const g = { label: label ?? node.name, count: node.recursiveFileCount }
  if (tag) g.tag = tag
  if (summary) { g.summary = summary; return g }
  g.files = node.files ?? []
  if (node.filesTruncated) g.filesTruncated = node.filesTruncated
  if (node.subdirs) g.subdirs = node.subdirs.map((s) => ({ name: s.name, count: s.recursiveFileCount }))
  return g
}

// 依指定順序排 children，未列到的接在後面（保留原序）
function ordered(node, order) {
  const kids = node.children ?? []
  const byName = Object.fromEntries(kids.map((k) => [k.name, k]))
  const head = order.filter((n) => byName[n]).map((n) => byName[n])
  const tail = kids.filter((k) => !order.includes(k.name))
  return [...head, ...tail]
}

const CORE = new Set(['釋昭慧', '釋性廣', '昭慧法師', '性廣法師'])

// ── 作者文獻：兩位宗教師＋弘誓僧團著者優先 ──
const authorOrder = ['釋昭慧', '釋性廣', '釋傳法', '釋見岸', '釋悟殷', '侯坤宏', '邱敏捷', '林建德', '楊惠南', '江燦騰', '藍吉富', '闞正宗', '游祥洲', '李志夫', '釋傳道', '黃運喜', '洪山川', '盧俊義', '釋印順']
const authors = {
  key: 'authors', label: '作者文獻', icon: '🖋️',
  desc: '依作者整理的專文、序跋、訪談錄（19 位）；昭慧、性廣與弘誓僧團著者列於最前',
  groups: ordered(top['作者'], authorOrder).map((n) => group(n, { tag: CORE.has(n.name) ? '核心' : undefined })),
}

// ── 議題：性別／昭慧／性廣／入世佛教優先 ──
const issueOrder = ['佛教性別議題', '昭慧法師', '性廣法師', '入世佛教', '印順學', '人間佛教研究', '太虛大師', '法鼓山', '佛光山', '慈濟', '現代禪', '趙樸初']
const issuesNode = top['議題']
const issues = {
  key: 'issues', label: '議題專輯', icon: '🗂️',
  desc: '依研究議題彙整的二手研究與相關文章',
  groups: [
    ...ordered(issuesNode, issueOrder).map((n) => group(n, { tag: CORE.has(n.name) ? '核心' : undefined })),
    ...(issuesNode.files?.length ? [group({ name: '其他主題文章', files: issuesNode.files, recursiveFileCount: issuesNode.fileCount })] : []),
  ],
}

// ── 弘誓：雙月刊文章 + 學位論文 ──
const hongshiNode = top['弘誓']
const hongshi = {
  key: 'hongshi', label: '弘誓', icon: '📰',
  desc: '《弘誓》雙月刊文章、學院簡介與弘誓僧團相關學位論文',
  groups: [
    group({ name: '《弘誓》雙月刊文章', files: hongshiNode.files, recursiveFileCount: hongshiNode.fileCount }, { tag: '核心' }),
    ...(hongshiNode.children ?? []).map((n) => group(n)),
  ],
}

// ── 研討會 ──
const conf = {
  key: 'conference', label: '印順學研討會', icon: '🎓',
  desc: '歷屆「印順導師思想之理論與實踐」學術會議側記與論文（第 4–20 屆）',
  groups: [group(top['印順學研討會'], { label: '會議側記與論文' })],
}

// ── 期刊 ──
const journal = {
  key: 'journal', label: '人間佛教研究期刊', icon: '📚',
  desc: '《人間佛教研究》刊載之相關論文',
  groups: [group(top['人間佛教研究期刊'], { label: '期刊論文' })],
}

// ── 福嚴會訊（期刊掃描，數量大→摘要）──
const fuyan = {
  key: 'fuyan', label: '福嚴會訊', icon: '🗞️',
  desc: '福嚴佛學院《福嚴會訊》全套會訊掃描',
  groups: [group(top['福嚴會訊'], { label: '會訊全套掃描', summary: '第 1–71 期會訊 PDF（fu001–fu071_eBook.pdf），共 71 期' })],
}

// ── 檔案（國家檔案局白色恐怖檔案，列案件夾不列掃描頁）──
const archiveNode = top['檔案']
const archiveSub = archiveNode.children?.[0] // 國家檔案局檔案(2023.04.15)
const archive = {
  key: 'archive', label: '檔案', icon: '🗄️',
  desc: '國家檔案管理局調閱之白色恐怖時期善導寺／印順《佛法概論》查禁相關政府檔案（2023.04.15 調閱）',
  groups: [
    group({ name: '綜覽文件', files: archiveNode.files, recursiveFileCount: archiveNode.fileCount }),
    {
      label: '國家檔案管理局檔案（依案件）', count: archiveSub.recursiveFileCount,
      subdirs: (archiveSub.subdirs ?? []).map((s) => ({ name: s.name, count: s.count })),
      summary: `共 ${archiveSub.subdirCount} 件案卷、${archiveSub.recursiveFileCount} 個掃描檔；原始掃描存 Drive`,
    },
  ],
}

// ── 表格與圖（整理用）──
const tables = {
  key: 'tables', label: '整理表格與圖', icon: '📊',
  desc: '研究過程自製的彙整表格、分布圖與訪談關係圖',
  groups: [group(top['表格'], { label: '表格與圖檔' })],
}

const manifest = {
  book: '當代的大愛道革命',
  subtitle: '昭慧法師與性廣法師的人間佛教思想與實踐',
  source: 'G:\\我的雲端硬碟\\公事\\國北教\\碩士論文\\論文資料',
  note: '原碩士論文研究資料全數移入，依 Drive 原始分類整理。原檔留存 Google Drive（canonical storage），此處為分類索引。',
  interviews: true, // 書頁顯示「口述訪談」分頁（資料來自 thesisInterviews store）
  totalFiles: raw.recursiveFileCount,
  categories: [authors, issues, hongshi, conf, journal, fuyan, archive, tables],
}

writeFileSync(OUT, JSON.stringify(manifest, null, 2), 'utf8')
const ng = manifest.categories.reduce((s, c) => s + c.groups.length, 0)
console.log(`Wrote ${OUT}: ${manifest.categories.length} categories, ${ng} groups, ${manifest.totalFiles} files total`)
