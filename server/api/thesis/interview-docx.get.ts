/**
 * 即時把 /thesis?tab=interviews 的訪談紀錄打包成 .docx
 *
 * 來源：public/content/interviews/{name}.txt
 * 樣式對齊 pages/thesis/interview/[name].vue formatInterview() 與 :deep(.i-*) CSS
 * 每次請求現場生成 → .txt 改了就直接反映在下載出來的 Word。
 */
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import {
  AlignmentType,
  BorderStyle,
  Document,
  HeightRule,
  Packer,
  Paragraph,
  ShadingType,
  TextRun,
  convertInchesToTwip,
} from 'docx'

const CN_FONT = 'Noto Serif TC'
const EN_FONT = 'Georgia'

const FOOTNOTE_RE = /\[(\d+)\]\(#footnote\d+\)/g
const ANSWER_RE = /^([一-鿿]{1,5}(?:法師|教授|主教|和尚|居士|博士|老師|牧師|女士|先生|主任|院長|住持))：(.+)$/
const META_RE = /^(受訪者|訪問者|訪問時間|訪問地點|訪談時間|訪談地點|採訪者|採訪時間|採訪地點)：/
const SECTION_RE = /^[一二三四五六七八九十]+、/
const SUB_RE = /^（[一二三四五六七八九十]+）/
const NUM_SUB_RE = /^\d+\.\s+\S/

const COLOR = {
  title: '111827',
  meta: '6B7280',
  section: '374151',
  subsection: '4B5563',
  para: '1F2937',
  qLabel: '6B7280',
  qBody: '374151',
  aLabel: '7C3AED',
  aBody: '111827',
  qShade: 'F9FAFB',
  qBorder: 'D1D5DB',
  sectionRule: 'E5E7EB',
}

interface RunOpts {
  size?: number  // half-points
  color?: string
  bold?: boolean
  italics?: boolean
  superScript?: boolean
}

function mkRun(text: string, opts: RunOpts = {}): TextRun {
  return new TextRun({
    text,
    bold: opts.bold,
    italics: opts.italics,
    superScript: opts.superScript,
    size: opts.size ?? 24,
    color: opts.color ?? COLOR.para,
    font: { name: EN_FONT, eastAsia: CN_FONT },
  })
}

/** 把 body 文字裡的 [N](#footnoteN) 轉成上標 run。 */
function bodyRuns(text: string, opts: RunOpts = {}): TextRun[] {
  const runs: TextRun[] = []
  let cursor = 0
  FOOTNOTE_RE.lastIndex = 0
  for (const m of text.matchAll(FOOTNOTE_RE)) {
    if (m.index! > cursor) {
      runs.push(mkRun(text.slice(cursor, m.index!), opts))
    }
    runs.push(mkRun(`[${m[1]}]`, { ...opts, superScript: true, size: Math.max((opts.size ?? 24) - 4, 16) }))
    cursor = m.index! + m[0].length
  }
  if (cursor < text.length) runs.push(mkRun(text.slice(cursor), opts))
  return runs
}

function title(text: string): Paragraph {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 360 },
    children: [mkRun(text, { size: 44, color: COLOR.title, bold: true })],
  })
}

function meta(text: string): Paragraph {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 40 },
    children: [mkRun(text, { size: 22, color: COLOR.meta })],
  })
}

function section(text: string): Paragraph {
  return new Paragraph({
    spacing: { before: 440, after: 200 },
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 12, color: COLOR.sectionRule, space: 4 },
    },
    children: [mkRun(text, { size: 34, color: COLOR.section, bold: true })],
  })
}

function subsection(text: string): Paragraph {
  return new Paragraph({
    spacing: { before: 280, after: 120 },
    children: [mkRun(text, { size: 28, color: COLOR.subsection, bold: true })],
  })
}

function para(text: string): Paragraph {
  return new Paragraph({
    spacing: { after: 80, line: 460, lineRule: 'auto' as any },
    indent: { firstLine: 480 },
    children: bodyRuns(text, { size: 24, color: COLOR.para }),
  })
}

function question(body: string): Paragraph {
  return new Paragraph({
    spacing: { before: 200, after: 80, line: 400, lineRule: 'auto' as any },
    indent: { left: 200 },
    shading: { type: ShadingType.CLEAR, fill: COLOR.qShade, color: 'auto' },
    border: {
      left: { style: BorderStyle.SINGLE, size: 24, color: COLOR.qBorder, space: 8 },
    },
    children: [
      mkRun('問　', { size: 20, color: COLOR.qLabel, bold: true }),
      ...bodyRuns(body, { size: 24, color: COLOR.qBody, italics: true }),
    ],
  })
}

function answer(label: string, body: string): Paragraph {
  return new Paragraph({
    spacing: { before: 80, after: 200, line: 460, lineRule: 'auto' as any },
    children: [
      mkRun(`${label}　`, { size: 20, color: COLOR.aLabel, bold: true }),
      ...bodyRuns(body, { size: 24, color: COLOR.aBody }),
    ],
  })
}

function blank(): Paragraph {
  return new Paragraph({ spacing: { after: 40 }, children: [] })
}

function buildParagraphs(raw: string): Paragraph[] {
  const out: Paragraph[] = []
  let isFirst = true
  for (const line of raw.split(/\r?\n/)) {
    const t = line.trim()
    if (!t) { out.push(blank()); continue }
    if (isFirst) { isFirst = false; out.push(title(t)); continue }
    if (META_RE.test(t)) { out.push(meta(t)); continue }
    if (SECTION_RE.test(t)) { out.push(section(t)); continue }
    if (SUB_RE.test(t) || NUM_SUB_RE.test(t)) { out.push(subsection(t)); continue }
    if (t.startsWith('筆者：')) { out.push(question(t.slice(3))); continue }
    const ans = t.match(ANSWER_RE)
    if (ans) { out.push(answer(ans[1], ans[2])); continue }
    if (t.length <= 25 && !/[。，、；：？！…]$/.test(t) && !/^[\[【（〔]/.test(t)) {
      out.push(section(t)); continue
    }
    out.push(para(t))
  }
  return out
}

export default defineEventHandler(async (event) => {
  const { name } = getQuery(event) as { name?: string }
  if (!name) throw createError({ statusCode: 400, message: 'Missing name' })

  // 防 path traversal
  const safe = name.replace(/[\\/]/g, '').replace(/\.\./g, '')
  if (safe !== name) throw createError({ statusCode: 400, message: 'Invalid name' })

  const txtPath = join(process.cwd(), 'public', 'content', 'interviews', `${safe}.txt`)
  let raw: string
  try {
    raw = await readFile(txtPath, 'utf-8')
  } catch {
    throw createError({ statusCode: 404, message: `Interview not found: ${safe}` })
  }

  const doc = new Document({
    creator: '碩士論文口述訪談',
    title: safe,
    styles: {
      default: {
        document: {
          run: { font: { name: EN_FONT, eastAsia: CN_FONT }, size: 24 },
        },
      },
    },
    sections: [{
      properties: {
        page: {
          margin: { top: 1247, bottom: 1247, left: 1418, right: 1418 },
        },
      },
      children: buildParagraphs(raw),
    }],
  })

  const buffer = await Packer.toBuffer(doc)

  setHeader(event, 'Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
  setHeader(event, 'Content-Disposition', `attachment; filename*=UTF-8''${encodeURIComponent(`${safe}.docx`)}`)
  setHeader(event, 'Cache-Control', 'no-store')

  return buffer
})
