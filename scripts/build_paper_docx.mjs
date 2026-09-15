/**
 * /works 論文計畫的改寫草稿 markdown → 交付用 Word（歷史論文格式）
 *
 * 與 server/api/works/draft-docx.get.ts 同版式，但多支援這三種草稿裡真的會出現、
 * 而端點會原樣印成亂碼的語法：
 *   - markdown 表格 → 真 Word 表格（附錄年表）
 *   - [文字](網址) → 真超連結（書目的典藏／全文連結）
 *   - 1. 數字清單 → 保留編號的懸掛縮排
 *
 * 跑法：node scripts/build_paper_docx.mjs <ref> "<輸出路徑.docx>"
 *   ref 指 public/content/works/<ref>-revision-draft.md
 */
import { readFileSync, writeFileSync } from 'node:fs'
import {
  AlignmentType, BorderStyle, Document, ExternalHyperlink, FootnoteReferenceRun,
  Packer, Paragraph, Table, TableCell, TableRow, TextRun, WidthType,
  convertMillimetersToTwip,
} from 'docx'

const BODY_CJK = '新細明體'
const QUOTE_CJK = '標楷體'
const EN = 'Times New Roman'
const L = { line: 360, lineRule: 'auto' }

const mkRun = (text, o = {}) => new TextRun({
  text,
  bold: o.bold,
  italics: o.italics,
  size: o.size ?? 24,
  color: o.color ?? '000000',
  underline: o.underline,
  font: { ascii: EN, hAnsi: EN, cs: EN, eastAsia: o.cjk ?? BODY_CJK },
})

/** 行內：**粗體** / *斜體* / [文字](網址) / 〔註N〕 */
function inlineRuns(text, notes, o = {}) {
  const out = []
  const re = /\*\*(.+?)\*\*|\*([^*]+?)\*|\[([^\]]+)\]\(([^)\s]+)\)|〔註(\d+)〕/g
  let cursor = 0
  for (const m of text.matchAll(re)) {
    if (m.index > cursor) out.push(mkRun(text.slice(cursor, m.index), o))
    if (m[1] !== undefined) out.push(mkRun(m[1], { ...o, bold: true }))
    else if (m[2] !== undefined) out.push(mkRun(m[2], { ...o, italics: true }))
    else if (m[3] !== undefined) {
      out.push(new ExternalHyperlink({
        link: m[4],
        children: [mkRun(m[3], { ...o, color: '0563C1', underline: {} })],
      }))
    } else {
      const n = Number(m[5])
      if (notes[n]) out.push(new FootnoteReferenceRun(n))
      else out.push(mkRun(m[0], o))
    }
    cursor = m.index + m[0].length
  }
  if (cursor < text.length) out.push(mkRun(text.slice(cursor), o))
  return out.length ? out : [mkRun('', o)]
}

/** 文末「## 註釋」段 → {N: 註文}，正文去掉該段 */
function extractNotes(lines) {
  const idx = lines.findIndex(l => /^##\s+註釋\s*$/.test(l.trim()))
  if (idx < 0) return { notes: {}, body: lines }
  const notes = {}
  for (const l of lines.slice(idx + 1)) {
    const m = l.trim().match(/^〔註(\d+)〕(.+)$/)
    if (m) notes[Number(m[1])] = m[2].trim()
  }
  return { notes, body: lines.slice(0, idx) }
}

const splitRow = t => t.replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim())
const isSep = t => /^\|[\s:|-]+\|$/.test(t)

function buildTable(rows, notes) {
  const cols = Math.max(...rows.map(r => r.length))
  const thin = { style: BorderStyle.SINGLE, size: 4, color: '999999' }
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: thin, bottom: thin, left: thin, right: thin, insideHorizontal: thin, insideVertical: thin },
    rows: rows.map((cells, r) => new TableRow({
      tableHeader: r === 0,
      children: Array.from({ length: cols }, (_, c) => new TableCell({
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({
          spacing: { after: 0, line: 280, lineRule: 'auto' },
          children: inlineRuns(cells[c] ?? '', notes, { size: 22, bold: r === 0 }),
        })],
      })),
    })),
  })
}

function buildBody(md) {
  const { notes, body } = extractNotes(md.split(/\r?\n/))
  const out = []
  let seenAbstract = false
  for (let i = 0; i < body.length; i++) {
    const t = body[i].trim()

    // 表格：連續的 | 行吃成一塊
    if (t.startsWith('|')) {
      const rows = []
      while (i < body.length && body[i].trim().startsWith('|')) {
        const line = body[i].trim()
        if (!isSep(line)) rows.push(splitRow(line))
        i++
      }
      i--
      if (rows.length) out.push(buildTable(rows, notes))
      out.push(new Paragraph({ spacing: { after: 120 }, children: [] }))
      continue
    }

    if (!t || t === '---') {
      out.push(new Paragraph({ spacing: { after: 0, line: 240, lineRule: 'auto' }, children: [] }))
      continue
    }
    if (t.startsWith('# ')) {
      out.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 120, after: 120, ...L },
        children: inlineRuns(t.slice(2), notes, { size: 36, bold: true }),
      }))
      continue
    }
    if (t.startsWith('### ')) {
      const inner = t.slice(4)
      if (/^摘要/.test(inner)) seenAbstract = true
      const isSubsection = /^（[一二三四五六七八九十]+）/.test(inner)
      out.push(new Paragraph({
        alignment: isSubsection ? undefined : AlignmentType.CENTER,
        spacing: { before: isSubsection ? 200 : 60, after: isSubsection ? 100 : 60, ...L },
        children: inlineRuns(inner, notes, { size: isSubsection ? 24 : 22, bold: true }),
      }))
      continue
    }
    if (t.startsWith('## ')) {
      out.push(new Paragraph({
        spacing: { before: 280, after: 140, ...L },
        children: inlineRuns(t.slice(3), notes, { size: 28, bold: true }),
      }))
      continue
    }
    if (t.startsWith('>')) {
      out.push(new Paragraph({
        indent: { left: 720, right: 480 },
        spacing: { before: 120, after: 120, ...L },
        children: inlineRuns(t.replace(/^>\s?/, ''), notes, { cjk: QUOTE_CJK }),
      }))
      continue
    }
    const num = t.match(/^(\d+)\.\s+(.*)$/)
    if (num) {
      out.push(new Paragraph({
        indent: { left: 600, hanging: 600 },
        spacing: { after: 60, ...L },
        children: inlineRuns(`${num[1]}. ${num[2]}`, notes),
      }))
      continue
    }
    if (/^[-*]\s+/.test(t)) {
      out.push(new Paragraph({
        indent: { left: 480, hanging: 480 },
        spacing: { after: 60, ...L },
        children: inlineRuns(t.replace(/^[-*]\s+/, ''), notes),
      }))
      continue
    }
    // 摘要前的短行（英文題名／作者）置中；書目段不縮排
    if (!seenAbstract && t.length <= 30 && !/[。，、；：？！]/.test(t)) {
      out.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 60, ...L },
        children: inlineRuns(t, notes),
      }))
      continue
    }
    out.push(new Paragraph({
      indent: { firstLine: 480 },
      spacing: { after: 0, ...L },
      children: inlineRuns(t, notes),
    }))
  }
  return { children: out, notes }
}

const [ref, outPath] = process.argv.slice(2)
if (!ref || !outPath) {
  console.error('usage: node scripts/build_paper_docx.mjs <ref> <out.docx>')
  process.exit(1)
}
const md = readFileSync(`public/content/works/${ref}-revision-draft.md`, 'utf-8')
const title = md.match(/^#\s+(.+)$/m)?.[1]?.trim() || ref
const { children, notes } = buildBody(md)
const footnotes = Object.fromEntries(Object.entries(notes).map(([n, text]) => [Number(n), {
  children: [new Paragraph({
    spacing: { after: 0, line: 240, lineRule: 'auto' },
    children: [mkRun(' ' + text, { size: 20 })],
  })],
}]))

const doc = new Document({
  creator: '論文寫作計畫',
  title,
  styles: { default: { document: { run: { font: { name: EN, eastAsia: BODY_CJK }, size: 24 } } } },
  footnotes: Object.keys(footnotes).length ? footnotes : undefined,
  sections: [{
    properties: {
      page: {
        size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297) },
        margin: {
          top: convertMillimetersToTwip(25), bottom: convertMillimetersToTwip(25),
          left: convertMillimetersToTwip(25), right: convertMillimetersToTwip(25),
        },
      },
    },
    children,
  }],
})

const buf = await Packer.toBuffer(doc)
writeFileSync(outPath, buf)
console.log('written:', outPath, buf.length, 'bytes')
