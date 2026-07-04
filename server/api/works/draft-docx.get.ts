/**
 * 把 /works 論文計畫「修改草稿」（public/content/works/<ref>-revision-draft.md）
 * 即時轉成「歷史論文格式」的 .docx 下載。md 改了，下載出來的 Word 就跟著變。
 *
 * 版式（對齊根目錄「腳註版」交付檔）：
 *   - A4、頁邊 25mm；內文 12pt Times New Roman + 新細明體，首行縮排兩字，行距 1.5
 *   - # 主標 18pt 置中／## 節標 14pt／### 子標 12pt 加粗
 *   - > 引文 → 標楷體、左右內縮的獨立引文段
 *   - - 條列 → 懸掛縮排書目
 *   - 行內 〔註N〕 → 真‧頁下腳註（w:footnote）；註文取自文末「## 註釋」段的〔註N〕清單
 *   - 「## 註釋」整段本身不再印出（已轉為腳註）；行內 **粗體** 照樣加粗
 */
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import {
  AlignmentType,
  Document,
  FootnoteReferenceRun,
  Packer,
  Paragraph,
  TextRun,
  convertMillimetersToTwip,
} from 'docx'

const BODY_CJK = '新細明體'
const QUOTE_CJK = '標楷體'
const EN = 'Times New Roman'

interface RunOpts { size?: number; bold?: boolean; color?: string; cjk?: string }

const mkRun = (text: string, o: RunOpts = {}) => new TextRun({
  text,
  bold: o.bold,
  size: o.size ?? 24,
  color: o.color ?? '000000',
  font: { ascii: EN, hAnsi: EN, cs: EN, eastAsia: o.cjk ?? BODY_CJK },
})

/** 行內解析：**粗體** + 〔註N〕→ 腳註參照（notes[N] 存在才轉） */
function inlineRuns(text: string, notes: Record<number, string>, o: RunOpts = {}): (TextRun | FootnoteReferenceRun)[] {
  const out: (TextRun | FootnoteReferenceRun)[] = []
  // 先切腳註標記，段內再處理粗體
  const parts = text.split(/(〔註\d+〕)/)
  for (const part of parts) {
    const fn = part.match(/^〔註(\d+)〕$/)
    if (fn) {
      const n = Number(fn[1])
      if (notes[n]) { out.push(new FootnoteReferenceRun(n)); continue }
      out.push(mkRun(part, o)); continue
    }
    let cursor = 0
    for (const m of part.matchAll(/\*\*(.+?)\*\*/g)) {
      if (m.index! > cursor) out.push(mkRun(part.slice(cursor, m.index!), o))
      out.push(mkRun(m[1], { ...o, bold: true }))
      cursor = m.index! + m[0].length
    }
    if (cursor < part.length) out.push(mkRun(part.slice(cursor), o))
  }
  return out.length ? out : [mkRun('', o)]
}

const L = { line: 360, lineRule: 'auto' as any }

/** 抽出文末「## 註釋」段 → {N: 註文}，並回傳去掉該段的正文行 */
function extractNotes(lines: string[]): { notes: Record<number, string>; body: string[] } {
  const idx = lines.findIndex(l => /^##\s+註釋\s*$/.test(l.trim()))
  if (idx < 0) return { notes: {}, body: lines }
  const notes: Record<number, string> = {}
  for (const l of lines.slice(idx + 1)) {
    const m = l.trim().match(/^〔註(\d+)〕(.+)$/)
    if (m) notes[Number(m[1])] = m[2].trim()
  }
  return { notes, body: lines.slice(0, idx) }
}

function buildParagraphs(md: string): { paragraphs: Paragraph[]; notes: Record<number, string> } {
  const rawLines = md.split(/\r?\n/)
  const { notes, body } = extractNotes(rawLines)
  const out: Paragraph[] = []
  let seenAbstract = false
  for (const line of body) {
    const t = line.trim()
    if (!t || t === '---') { out.push(new Paragraph({ spacing: { after: 0, line: 240, lineRule: 'auto' as any }, children: [] })); continue }

    if (t.startsWith('# ')) {
      out.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 120, after: 120, ...L },
        children: [mkRun(t.slice(2), { size: 36, bold: true })],
      }))
      continue
    }
    if (t.startsWith('### ')) {
      const inner = t.slice(4)
      if (/^摘要/.test(inner)) seenAbstract = true
      // 副標／作者資訊型 ### 一律置中；一般子章節（（一）…）靠左加粗
      const isSubsection = /^（[一二三四五六七八九十]+）/.test(inner)
      out.push(new Paragraph({
        alignment: isSubsection ? undefined : AlignmentType.CENTER,
        spacing: { before: isSubsection ? 200 : 60, after: isSubsection ? 100 : 60, ...L },
        children: [mkRun(inner, { size: isSubsection ? 24 : 22, bold: true })],
      }))
      continue
    }
    if (t.startsWith('## ')) {
      out.push(new Paragraph({
        spacing: { before: 280, after: 140, ...L },
        children: [mkRun(t.slice(3), { size: 28, bold: true })],
      }))
      continue
    }
    if (t.startsWith('> ')) {
      out.push(new Paragraph({
        indent: { left: 720, right: 480 },
        spacing: { before: 120, after: 120, ...L },
        children: inlineRuns(t.slice(2), notes, { cjk: QUOTE_CJK }),
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
    // 摘要前的短行（作者／系所）置中；關鍵詞與正文首行縮排
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
  return { paragraphs: out, notes }
}

export default defineEventHandler(async (event) => {
  const { ref } = getQuery(event) as { ref?: string }
  if (!ref) throw createError({ statusCode: 400, message: 'Missing ref' })
  const safe = ref.replace(/[^a-zA-Z0-9_-]/g, '')
  if (safe !== ref) throw createError({ statusCode: 400, message: 'Invalid ref' })

  const mdPath = join(process.cwd(), 'public', 'content', 'works', `${safe}-revision-draft.md`)
  let md: string
  try {
    md = await readFile(mdPath, 'utf-8')
  } catch {
    throw createError({ statusCode: 404, message: `Draft not found: ${safe}` })
  }

  const title = md.match(/^#\s+(.+)$/m)?.[1]?.trim() || `${safe}-draft`

  const { paragraphs, notes } = buildParagraphs(md)
  const footnotes = Object.fromEntries(
    Object.entries(notes as Record<number, string>).map(([n, text]) => [Number(n), {
      children: [new Paragraph({
        spacing: { after: 0, line: 240, lineRule: 'auto' as any },
        children: [mkRun(' ' + text, { size: 20 })],
      })],
    }]),
  )

  const doc = new Document({
    creator: '論文寫作計畫',
    title,
    styles: {
      default: { document: { run: { font: { name: EN, eastAsia: BODY_CJK }, size: 24 } } },
    },
    footnotes: Object.keys(footnotes).length ? footnotes : undefined,
    sections: [{
      properties: {
        page: {
          size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297) },
          margin: {
            top: convertMillimetersToTwip(25),
            bottom: convertMillimetersToTwip(25),
            left: convertMillimetersToTwip(25),
            right: convertMillimetersToTwip(25),
          },
        },
      },
      children: paragraphs,
    }],
  })

  const buffer = await Packer.toBuffer(doc)
  setHeader(event, 'Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
  setHeader(event, 'Content-Disposition', `attachment; filename*=UTF-8''${encodeURIComponent(`${title}.docx`)}`)
  setHeader(event, 'Cache-Control', 'no-store')
  return buffer
})
