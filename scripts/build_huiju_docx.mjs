/**
 * 慧炬大學院校佛學論文獎學金「學術論文組」書寫格式 → Word
 * （依 2026 年【附件一】文稿書寫格式說明、【附件二】學術論文格式範例）
 *
 *   邊界上下 2.5cm、左右 3cm；題目標楷體 18 級置中；摘要新細明體 12 級；
 *   關鍵字新細明體 10 級加粗；正文標題新細明體 14 級；正文新細明體 12 級；
 *   獨立引文標楷體 12 級、左縮 3 字元、上下空一行；隨頁注腳新細明體 10 級；
 *   英數 Times New Roman；頁碼頁尾置中、距底 1cm；題目與摘要頁不加注。
 *
 * 跑法：node scripts/build_huiju_docx.mjs <稿.md> <輸出.docx> [--named="學校系級　姓名"]
 *   不給 --named ＝匿名稿（第一份）；給了＝具名稿（題目下方標楷體 12 級、上下空一行）。
 *
 * 稿件 md 慣例（與 build_paper_docx.mjs 相同）：`# 題目`、`### 摘要`、`關鍵字：…`、
 * `## 一、前言`、`（一）小節` 獨立成行、`> 引文`、行內〔註N〕、文末 `## 註釋` 以「N. 註文」列出。
 * 註號依正文出現順序重新編號（草稿中途插註不必手動改號）。
 */
import { readFileSync, writeFileSync } from 'node:fs'
import {
  AlignmentType, Document, Footer, FootnoteReferenceRun, Packer, PageBreak, PageNumber,
  Paragraph, TextRun, convertMillimetersToTwip,
} from 'docx'

const MING = '新細明體'
const KAI = '標楷體'
const EN = 'Times New Roman'
const LINE = { line: 360, lineRule: 'auto' }   // 1.5 倍行高

const run = (text, o = {}) => new TextRun({
  text, bold: o.bold, italics: o.italics, size: o.size ?? 24,
  font: { ascii: EN, hAnsi: EN, cs: EN, eastAsia: o.cjk ?? MING },
})

function inline(text, noteMap, o = {}) {
  const out = []
  const re = /\*\*(.+?)\*\*|\*([^*]+?)\*|〔註(\d+)〕/g
  let c = 0
  for (const m of text.matchAll(re)) {
    if (m.index > c) out.push(run(text.slice(c, m.index), o))
    if (m[1] !== undefined) out.push(run(m[1], { ...o, bold: true }))
    else if (m[2] !== undefined) out.push(run(m[2], { ...o, italics: true }))
    else {
      const n = noteMap.get(Number(m[3]))
      if (n) { out.push(new FootnoteReferenceRun(n)); out.push(run(' ', o)) }  // 注號後空一半形
      else out.push(run(m[0], o))
    }
    c = m.index + m[0].length
  }
  if (c < text.length) out.push(run(text.slice(c), o))
  return out.length ? out : [run('', o)]
}

const blank = () => new Paragraph({ spacing: { after: 0, ...LINE }, children: [] })

const argv = process.argv.slice(2)
const named = argv.find(a => a.startsWith('--named='))?.slice(8)
const [src, outPath] = argv.filter(a => !a.startsWith('--'))
if (!src || !outPath) {
  console.error('usage: node scripts/build_huiju_docx.mjs <稿.md> <out.docx> [--named="學校系級　姓名"]')
  process.exit(1)
}

const lines = readFileSync(src, 'utf-8').split(/\r?\n/)
const ni = lines.findIndex(l => /^##\s+註釋\s*$/.test(l.trim()))
const body = ni >= 0 ? lines.slice(0, ni) : lines
const rawNotes = {}
if (ni >= 0) {
  for (const l of lines.slice(ni + 1)) {
    const m = l.trim().match(/^(\d+)\.\s+(.*)$/)
    if (m) rawNotes[Number(m[1])] = m[2]
  }
}
// 依正文出現順序重新編號
const noteMap = new Map()
for (const m of body.join('\n').matchAll(/〔註(\d+)〕/g)) {
  const k = Number(m[1])
  if (rawNotes[k] && !noteMap.has(k)) noteMap.set(k, noteMap.size + 1)
}
const missing = [...body.join('\n').matchAll(/〔註(\d+)〕/g)].map(m => Number(m[1])).filter(k => !rawNotes[k])
if (missing.length) console.warn('⚠ 正文有註號但註釋缺：', [...new Set(missing)].join(', '))
const unused = Object.keys(rawNotes).map(Number).filter(k => !noteMap.has(k))
if (unused.length) console.warn('⚠ 註釋未被引用：', unused.join(', '))

const children = []
let stage = 'title'          // title → abstract → body
let inBib = false
let prevQuote = false
for (const raw of body) {
  const t = raw.trim()
  if (!t || t === '---') { continue }
  const isQuote = t.startsWith('>')
  if (prevQuote && !isQuote) children.push(blank())
  prevQuote = isQuote

  if (t.startsWith('# ')) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 0, ...LINE },
      children: [run(t.slice(2), { size: 36, cjk: KAI })],
    }))
    children.push(blank())
    if (named) {
      children.push(new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { after: 0, ...LINE },
        children: [run(named, { size: 24, cjk: KAI })],
      }))
      children.push(blank())
    }
    continue
  }
  if (t.startsWith('### ') && /摘要/.test(t)) {
    stage = 'abstract'
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 120, ...LINE },
      children: [run('摘　要', { size: 24, bold: true })],
    }))
    continue
  }
  if (/^關鍵字/.test(t)) {
    children.push(blank())
    children.push(new Paragraph({ spacing: { after: 0, ...LINE }, children: [run(t, { size: 20, bold: true })] }))
    continue
  }
  if (t.startsWith('## ')) {
    if (stage === 'abstract') { children.push(new Paragraph({ children: [new PageBreak()] })); stage = 'body' }
    inBib = /參考文獻/.test(t)
    if (inBib) children.push(new Paragraph({ children: [new PageBreak()] }))
    children.push(new Paragraph({
      spacing: { before: 240, after: 120, ...LINE },
      alignment: inBib ? AlignmentType.CENTER : undefined,
      children: [run(t.slice(3), { size: 28, bold: true })],
    }))
    continue
  }
  if (inBib && /^（?[一二三四五六七八九十]+[、）]/.test(t) && t.length <= 30) {
    children.push(new Paragraph({ spacing: { before: 120, after: 60, ...LINE }, children: [run(t, { bold: true })] }))
    continue
  }
  if (/^（[一二三四五六七八九十]+）/.test(t) && t.length <= 40 && !/[。；]$/.test(t)) {
    children.push(new Paragraph({ spacing: { before: 180, after: 60, ...LINE }, children: inline(t, noteMap, { bold: true }) }))
    continue
  }
  if (isQuote) {
    // 獨立引文：左縮 3 字元（12 級字一字 240 twip），上下間隔一行，不另加引號
    const last = children[children.length - 1]
    if (!last || !(last.__quote)) children.push(blank())
    const p = new Paragraph({
      indent: { left: 720 }, spacing: { after: 0, ...LINE },
      children: inline(t.replace(/^>\s?/, ''), noteMap, { cjk: KAI }),
    })
    p.__quote = true
    children.push(p)
    continue
  }
  if (inBib) {
    children.push(new Paragraph({ indent: { left: 480, hanging: 480 }, spacing: { after: 60, ...LINE }, children: inline(t, noteMap) }))
    continue
  }
  const noNotes = stage !== 'body'   // 題目、摘要頁不加注
  children.push(new Paragraph({
    indent: { firstLine: 480 }, alignment: AlignmentType.JUSTIFIED, spacing: { after: 0, ...LINE },
    children: noNotes ? [run(t.replace(/〔註\d+〕/g, ''))] : inline(t, noteMap),
  }))
}

const footnotes = {}
for (const [k, n] of noteMap) {
  footnotes[n] = {
    children: [new Paragraph({
      alignment: AlignmentType.JUSTIFIED,
      spacing: { after: 0, line: 240, lineRule: 'auto' },
      children: inline(' ' + rawNotes[k], new Map(), { size: 20 }),
    })],
  }
}

const doc = new Document({
  styles: { default: { document: { run: { font: { name: EN, eastAsia: MING }, size: 24 } } } },
  footnotes,
  sections: [{
    properties: {
      page: {
        size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297) },
        margin: {
          top: convertMillimetersToTwip(25), bottom: convertMillimetersToTwip(25),
          left: convertMillimetersToTwip(30), right: convertMillimetersToTwip(30),
          footer: convertMillimetersToTwip(10), gutter: 0,
        },
      },
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], size: 20, font: EN })],
        })],
      }),
    },
    children,
  }],
})

writeFileSync(outPath, await Packer.toBuffer(doc))
console.log(`written: ${outPath}（${named ? '具名' : '匿名'}稿，注腳 ${noteMap.size} 條）`)
