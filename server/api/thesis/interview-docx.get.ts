/**
 * 即時把 /thesis?tab=interviews 的訪談紀錄打包成 .docx
 *
 * 來源：public/content/interviews/{name}.txt
 * 樣式參考：~/Desktop/nonchurch-nuxt/stores/無境界者雜誌/ 的編輯排版
 *   - B5 版型、頁邊 2cm
 *   - 主標 24pt 華康中黑體 bold 置中
 *   - 棕色 【口述訪談】 tag (文鼎中行書 14pt 靠右)
 *   - 受訪者／時間／地點 文鼎中行書 11pt 靠右
 *   - 章節 14pt NSimSun bold；子章節 12pt bold
 *   - 內文 12pt Times New Roman + NSimSun eastAsia，行距 1.25，無首行縮排
 *   - 筆者／受訪者 用棕色 label，無底色塊
 *   - footnote [N] 上標
 * 每次請求現場生成 → .txt 改了就直接反映在下載出來的 Word。
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

const FONT_TITLE = '華康中黑體'
const FONT_DECO = '文鼎中行書'
const FONT_CN = 'NSimSun'
const FONT_EN = 'Times New Roman'

const COLOR_ACCENT = '833C0B'  // 棕色，編輯室裝飾用
const COLOR_LABEL = '595959'    // 深灰，標籤用
const COLOR_BODY = '111111'
const COLOR_MUTED = '595959'

const FOOTNOTE_RE = /\[(\d+)\]\(#footnote\d+\)/g
const ANSWER_RE = /^([一-鿿]{1,5}(?:法師|教授|主教|和尚|居士|博士|老師|牧師|女士|先生|主任|院長|住持))：(.+)$/
const META_RE = /^(受訪者|訪問者|訪問時間|訪問地點|訪談時間|訪談地點|採訪者|採訪時間|採訪地點)：/
const SECTION_RE = /^[一二三四五六七八九十]+、/
const SUB_RE = /^（[一二三四五六七八九十]+）/
const NUM_SUB_RE = /^\d+\.\s+\S/

interface RunOpts {
  size?: number  // half-points
  color?: string
  bold?: boolean
  italics?: boolean
  superScript?: boolean
  font?: string
}

function mkRun(text: string, opts: RunOpts = {}): TextRun {
  return new TextRun({
    text,
    bold: opts.bold,
    italics: opts.italics,
    superScript: opts.superScript,
    size: opts.size ?? 24,
    color: opts.color ?? COLOR_BODY,
    font: { name: opts.font ?? FONT_EN, eastAsia: opts.font && !/[A-Za-z]/.test(opts.font) ? opts.font : FONT_CN },
  })
}

/** [39](#footnote39) → 上標 [39] */
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
    spacing: { after: 80 },
    children: [mkRun(text, { font: FONT_DECO, size: 28, color: COLOR_ACCENT })],
  })
}

function title(text: string): Paragraph {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 80, after: 240 },
    children: [mkRun(text, { font: FONT_TITLE, size: 48, bold: true })],
  })
}

function meta(text: string): Paragraph {
  return new Paragraph({
    alignment: AlignmentType.RIGHT,
    spacing: { after: 40, line: 320, lineRule: 'auto' as any },
    children: [mkRun(text, { font: FONT_DECO, size: 22, color: COLOR_MUTED })],
  })
}

function section(text: string): Paragraph {
  return new Paragraph({
    spacing: { before: 360, after: 160, line: 320, lineRule: 'auto' as any },
    children: [mkRun(text, { font: FONT_CN, size: 28, bold: true })],
  })
}

function subsection(text: string): Paragraph {
  return new Paragraph({
    spacing: { before: 200, after: 80, line: 300, lineRule: 'auto' as any },
    children: [mkRun(text, { font: FONT_CN, size: 24, bold: true })],
  })
}

function para(text: string): Paragraph {
  return new Paragraph({
    spacing: { after: 60, line: 360, lineRule: 'auto' as any },
    children: bodyRuns(text, { size: 24, color: COLOR_BODY }),
  })
}

function question(body: string): Paragraph {
  return new Paragraph({
    spacing: { before: 160, after: 60, line: 360, lineRule: 'auto' as any },
    children: [
      mkRun('筆者　', { size: 24, color: COLOR_ACCENT, bold: true }),
      ...bodyRuns(body, { size: 24, color: COLOR_BODY }),
    ],
  })
}

function answer(label: string, body: string): Paragraph {
  return new Paragraph({
    spacing: { before: 60, after: 160, line: 360, lineRule: 'auto' as any },
    children: [
      mkRun(`${label}　`, { size: 24, color: COLOR_LABEL, bold: true }),
      ...bodyRuns(body, { size: 24, color: COLOR_BODY }),
    ],
  })
}

function blank(): Paragraph {
  return new Paragraph({ spacing: { after: 0, line: 240, lineRule: 'auto' as any }, children: [] })
}

function buildParagraphs(raw: string): Paragraph[] {
  const out: Paragraph[] = []
  const lines = raw.split(/\r?\n/)
  let titleDone = false
  out.push(tagLine('【口述訪談】'))
  for (const line of lines) {
    const t = line.trim()
    if (!t) {
      if (titleDone) out.push(blank())
      continue
    }
    if (!titleDone) { titleDone = true; out.push(title(t)); continue }
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
          run: { font: { name: FONT_EN, eastAsia: FONT_CN }, size: 24 },
        },
      },
    },
    sections: [{
      properties: {
        page: {
          size: {
            width: convertMillimetersToTwip(182),   // B5
            height: convertMillimetersToTwip(257),
          },
          margin: {
            top: convertMillimetersToTwip(20),
            bottom: convertMillimetersToTwip(20),
            left: convertMillimetersToTwip(20),
            right: convertMillimetersToTwip(20),
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
