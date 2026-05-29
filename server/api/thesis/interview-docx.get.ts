/**
 * 即時把 /thesis?tab=interviews 的訪談紀錄打包成 .docx
 *
 * 樣式對齊 ~/Desktop/nonchurch-nuxt/stores/無境界者雜誌/04-第四期/4-4 與 4-5（人物專訪）
 *   - B5 (182×257mm)、頁邊 20mm
 *   - 【口述訪談】 tag 14pt 金 #FFC000，文鼎中行書，靠右
 *   - 主標 24pt 華康中黑體 bold 左對齊
 *   - 受訪者／時間／地點 文鼎中行書 預設大小靠右
 *   - 章節 14pt NSimSun bold；子章節 12pt bold
 *   - 內文 12pt Times New Roman + NSimSun，line-spacing 1.25，首行縮排以「　　」實作
 *   - 筆者／受訪者 label 完全平樸，不加粗不上色（編輯排版風格）
 *   - footnote [N] 9pt 上標
 * 每次請求現場生成 → .txt 改了就反映在下載出來的 Word。
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

const FONT_TITLE_CJK = '華康中黑體'
const FONT_DECO_CJK = '文鼎中行書'
const FONT_BODY_CJK = 'NSimSun'
const FONT_EN = 'Times New Roman'

const COLOR_TAG = 'FFC000'
const COLOR_BODY = '000000'

const FOOTNOTE_RE = /\[(\d+)\]\(#footnote\d+\)/g
const ANSWER_RE = /^([一-鿿]{1,5}(?:法師|教授|主教|和尚|居士|博士|老師|牧師|女士|先生|主任|院長|住持))：(.+)$/
const META_RE = /^(受訪者|訪問者|訪問時間|訪問地點|訪談時間|訪談地點|採訪者|採訪時間|採訪地點)：/
const SECTION_RE = /^[一二三四五六七八九十]+、/
const SUB_RE = /^（[一二三四五六七八九十]+）/
const NUM_SUB_RE = /^\d+\.\s+\S/

const INDENT = '　　'  // 兩個全形空白 = 首行縮排 2 字

interface RunOpts {
  size?: number
  color?: string
  bold?: boolean
  italics?: boolean
  superScript?: boolean
  fontEn?: string
  fontCjk?: string
}

function mkRun(text: string, opts: RunOpts = {}): TextRun {
  const ascii = opts.fontEn ?? FONT_EN
  const cjk = opts.fontCjk ?? FONT_BODY_CJK
  return new TextRun({
    text,
    bold: opts.bold,
    italics: opts.italics,
    superScript: opts.superScript,
    size: opts.size,
    color: opts.color ?? COLOR_BODY,
    font: { ascii, hAnsi: ascii, cs: ascii, eastAsia: cjk },
  })
}

/** body 文字裡 [N](#footnoteN) → 9pt 上標 [N] */
function bodyRuns(text: string, opts: RunOpts = {}): TextRun[] {
  const runs: TextRun[] = []
  let cursor = 0
  FOOTNOTE_RE.lastIndex = 0
  for (const m of text.matchAll(FOOTNOTE_RE)) {
    if (m.index! > cursor) runs.push(mkRun(text.slice(cursor, m.index!), opts))
    runs.push(mkRun(`[${m[1]}]`, { ...opts, superScript: true, size: 18 }))
    cursor = m.index! + m[0].length
  }
  if (cursor < text.length) runs.push(mkRun(text.slice(cursor), opts))
  return runs
}

function tagLine(text: string): Paragraph {
  return new Paragraph({
    alignment: AlignmentType.RIGHT,
    spacing: { after: 60, line: 300, lineRule: 'auto' as any },
    children: [mkRun(text, {
      size: 28, color: COLOR_TAG,
      fontEn: FONT_DECO_CJK, fontCjk: FONT_DECO_CJK,
    })],
  })
}

function title(text: string): Paragraph {
  return new Paragraph({
    spacing: { before: 60, after: 200, line: 300, lineRule: 'auto' as any },
    children: [mkRun(text, {
      size: 48, bold: true,
      fontCjk: FONT_TITLE_CJK,
    })],
  })
}

function meta(text: string): Paragraph {
  return new Paragraph({
    alignment: AlignmentType.RIGHT,
    spacing: { after: 0, line: 300, lineRule: 'auto' as any },
    children: [mkRun(text, {
      fontEn: FONT_DECO_CJK, fontCjk: FONT_DECO_CJK,
    })],
  })
}

function section(text: string): Paragraph {
  return new Paragraph({
    spacing: { before: 180, after: 180, line: 300, lineRule: 'auto' as any },
    children: [mkRun(text, { size: 28, bold: true })],
  })
}

function subsection(text: string): Paragraph {
  return new Paragraph({
    spacing: { before: 120, after: 60, line: 300, lineRule: 'auto' as any },
    children: [mkRun(text, { size: 24, bold: true })],
  })
}

function bodyPara(text: string): Paragraph {
  return new Paragraph({
    spacing: { after: 0, line: 300, lineRule: 'auto' as any },
    children: bodyRuns(INDENT + text),
  })
}

function dialogue(label: string, body: string): Paragraph {
  // Q/A：label 加粗（筆者：／釋昭慧法師：），body 平樸
  return new Paragraph({
    spacing: { after: 0, line: 300, lineRule: 'auto' as any },
    children: [
      mkRun(label, { bold: true }),
      ...bodyRuns(body),
    ],
  })
}

function blank(): Paragraph {
  return new Paragraph({ spacing: { after: 0, line: 240, lineRule: 'auto' as any }, children: [] })
}

function buildParagraphs(raw: string): Paragraph[] {
  const out: Paragraph[] = []
  let titleDone = false
  out.push(tagLine('【口述訪談】'))
  for (const line of raw.split(/\r?\n/)) {
    const t = line.trim()
    if (!t) { if (titleDone) out.push(blank()); continue }
    if (!titleDone) { titleDone = true; out.push(title(t)); continue }
    if (META_RE.test(t)) { out.push(meta(t)); continue }
    if (SECTION_RE.test(t)) { out.push(section(t)); continue }
    if (SUB_RE.test(t) || NUM_SUB_RE.test(t)) { out.push(subsection(t)); continue }
    if (t.startsWith('筆者：')) { out.push(dialogue('筆者：', t.slice(3))); continue }
    const ans = t.match(ANSWER_RE)
    if (ans) { out.push(dialogue(`${ans[1]}：`, ans[2])); continue }
    if (t.length <= 25 && !/[。，、；：？！…]$/.test(t) && !/^[\[【（〔]/.test(t)) {
      out.push(section(t)); continue
    }
    out.push(bodyPara(t))
  }
  return out
}

export default defineEventHandler(async (event) => {
  const { name } = getQuery(event) as { name?: string }
  if (!name) throw createError({ statusCode: 400, message: 'Missing name' })
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
          run: { font: { name: FONT_EN, eastAsia: FONT_BODY_CJK }, size: 24 },
        },
      },
    },
    sections: [{
      properties: {
        page: {
          size: {
            width: convertMillimetersToTwip(210),   // A4
            height: convertMillimetersToTwip(297),
          },
          margin: {
            top: convertMillimetersToTwip(25),
            bottom: convertMillimetersToTwip(25),
            left: convertMillimetersToTwip(25),
            right: convertMillimetersToTwip(25),
          },
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
