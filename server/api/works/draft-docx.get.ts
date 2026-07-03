/**
 * 把 /works 論文計畫「修改草稿」（public/content/works/<ref>-revision-draft.md）
 * 即時轉成 .docx 下載。md 改了，下載出來的 Word 就跟著變。
 *
 * 樣式：A4、頁邊 25mm、內文 12pt Times New Roman + NSimSun、首行縮排兩全形空白；
 * # 主標 20pt／## 節標 16pt／### 子標 14pt 加粗；> 引文灰色縮排；- 條列前置「‧」；
 * 行內 **粗體** 轉 bold run；--- 與 markdown 語法符號不輸出。
 */
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import {
  AlignmentType,
  Document,
  Packer,
  Paragraph,
  TextRun,
  convertMillimetersToTwip,
} from 'docx'

const FONT_BODY_CJK = 'NSimSun'
const FONT_EN = 'Times New Roman'
const INDENT = '　　'

interface RunOpts { size?: number; bold?: boolean; color?: string }

function runsWithBold(text: string, opts: RunOpts = {}): TextRun[] {
  // 行內 **bold** → bold run；其餘平樸
  const runs: TextRun[] = []
  const re = /\*\*(.+?)\*\*/g
  let cursor = 0
  const mk = (t: string, bold?: boolean) => new TextRun({
    text: t,
    bold: bold ?? opts.bold,
    size: opts.size,
    color: opts.color ?? '000000',
    font: { ascii: FONT_EN, hAnsi: FONT_EN, cs: FONT_EN, eastAsia: FONT_BODY_CJK },
  })
  for (const m of text.matchAll(re)) {
    if (m.index! > cursor) runs.push(mk(text.slice(cursor, m.index!)))
    runs.push(mk(m[1], true))
    cursor = m.index! + m[0].length
  }
  if (cursor < text.length) runs.push(mk(text.slice(cursor)))
  return runs.length ? runs : [mk('')]
}

function para(children: TextRun[]): Paragraph {
  return new Paragraph({
    spacing: { after: 0, line: 300, lineRule: 'auto' as any },
    children,
  })
}

function buildParagraphs(md: string): Paragraph[] {
  const out: Paragraph[] = []
  for (const line of md.split(/\r?\n/)) {
    const t = line.trim()
    if (!t || t === '---') { out.push(new Paragraph({ spacing: { after: 0, line: 240, lineRule: 'auto' as any }, children: [] })); continue }
    if (t.startsWith('### ')) { out.push(para(runsWithBold(t.slice(4), { size: 28, bold: true }))); continue }
    if (t.startsWith('## ')) { out.push(para(runsWithBold(t.slice(3), { size: 32, bold: true }))); continue }
    if (t.startsWith('# ')) {
      out.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200, line: 300, lineRule: 'auto' as any },
        children: runsWithBold(t.slice(2), { size: 40, bold: true }),
      }))
      continue
    }
    if (t.startsWith('> ')) {
      out.push(new Paragraph({
        indent: { left: convertMillimetersToTwip(10) },
        spacing: { after: 0, line: 300, lineRule: 'auto' as any },
        children: runsWithBold(t.slice(2), { size: 22, color: '595959' }),
      }))
      continue
    }
    if (/^[-*]\s+/.test(t)) {
      out.push(new Paragraph({
        indent: { left: convertMillimetersToTwip(6) },
        spacing: { after: 0, line: 300, lineRule: 'auto' as any },
        children: runsWithBold('‧ ' + t.replace(/^[-*]\s+/, '')),
      }))
      continue
    }
    if (/^〔註\d+〕/.test(t)) { out.push(para(runsWithBold(t, { size: 20 }))); continue }
    out.push(para(runsWithBold(INDENT + t)))
  }
  return out
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

  // 檔名用草稿第一個 # 標題，抓不到就用 ref
  const title = md.match(/^#\s+(.+)$/m)?.[1]?.trim() || `${safe}-draft`

  const doc = new Document({
    creator: '論文寫作計畫',
    title,
    styles: {
      default: {
        document: { run: { font: { name: FONT_EN, eastAsia: FONT_BODY_CJK }, size: 24 } },
      },
    },
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
      children: buildParagraphs(md),
    }],
  })

  const buffer = await Packer.toBuffer(doc)
  setHeader(event, 'Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
  setHeader(event, 'Content-Disposition', `attachment; filename*=UTF-8''${encodeURIComponent(`${title}.docx`)}`)
  setHeader(event, 'Cache-Control', 'no-store')
  return buffer
})
