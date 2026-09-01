import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import { buildParallelColumns } from '../lib/ebook-render'

// 🚨 三欄的資料在 JSONL 裡對齊，不代表讀者頁排得出來——欄與欄是「按索引」拉鍊
//    起來的，少一列就整欄錯位。這幾筆走的是真正的 render 路徑。
const DIR = 'G:/我的雲端硬碟/資料/知識圖工作室/_chunks'
const CASES: [string, string, string][] = [
  ['dffaae40-e088-41c1-ab7f-9b96f9249661', '阿諾比烏《駁異教徒》 第61-70章', 'la'],
  ['dffaae40-e088-41c1-ab7f-9b96f9249661', '美多德《十處女宴飲集／論童貞》 第51-60章', 'grc'],
  ['3c48472c-fbca-48fb-9db1-ca5a08827ef3', '書信 第3封', 'grc'],
  ['e01917ab-7429-41a0-9859-eddad413ef60', '駁亞流派講辭 第18章', 'grc'],
  ['24c53ede-8787-442e-a3ba-0cd55d0effac', '勒蘭的文生《勸誡錄》 第1-10章', 'la'],
  ['0e08c662-540b-4186-b250-9bca0cfe1002', '諾瓦提安《論三位一體》 第1章', 'la'],
  ['d7f66759-3fa9-4633-abde-87003cdbcc06', '奧古斯丁教義論集 卷一 第121-130章', 'la'],
  ['29782dd6-ece9-446a-83ed-9cc0892d7cc7', '蘇格拉底教會史 卷八 第41-48章', 'grc'],
  ['29782dd6-ece9-446a-83ed-9cc0892d7cc7', '索佐門教會史 卷十 第11-17章', 'grc'],
  ['24c53ede-8787-442e-a3ba-0cd55d0effac', '蘇皮修《神聖歷史》 第101-106章', 'la'],
  ['75d8aae0-7431-4be9-baee-c57d26599653', '拉克坦提烏《論逼迫者之死》 第51-54章', 'la'],
  ['c98d358d-7066-4691-a896-b7232707b0db', '坡旅甲殉道記 第1-10章', 'grc'],
]

const hasDrive = fs.existsSync(DIR)

describe.skipIf(!hasDrive)('教父卷第三欄真的排得出來', () => {
  for (const [id, chapterPath, lang] of CASES) {
    it(chapterPath, () => {
      const lines = fs.readFileSync(`${DIR}/${id}.jsonl`, 'utf8').split('\n').filter(Boolean)
      const chunk = lines.map((l) => JSON.parse(l)).find((c) => c.chapter_path === chapterPath)
      expect(chunk, '找不到那一段').toBeTruthy()
      expect(chunk.sources?.[lang], '沒有原文欄').toBeTruthy()

      const order: string[] = chunk.source_order ?? Object.keys(chunk.sources)
      const out = buildParallelColumns(chunk.content, chunk.sources, order, 0)
      expect(out.langs).toContain(lang)
      for (const row of out.rows) expect(Object.keys(row.cols)).toEqual(order)

      const strip = (s: string) => s.replace(/\u200b/g, '').replace(/<[^>]*>/g, '').trim()
      const filled = out.rows.filter((r) => strip(r.cols[lang])).length
      expect(filled, '原文欄整欄是空的').toBeGreaterThan(0)
      expect(filled).toBeLessThanOrEqual(out.rows.length)
    })
  }
})

// 目錄頁的「附原典」標籤是硬寫的一份 id 清單。清單與實際資料一旦脫節，頁面就會
// 宣稱某一卷有第三欄而點進去沒有——金口若望那一卷就差點這樣（OCR 還沒跑完就先
// 列進去了）。這支逐個回頭查 JSONL。
describe.skipIf(!hasDrive)('目錄頁的「附原典」清單與實際資料一致', () => {
  const page = fs.readFileSync('pages/fathers/index.vue', 'utf8')
  const block = page.slice(page.indexOf('const ORIGINAL_IDS'))
  const listed = (block.slice(0, block.indexOf('])')).match(/'([0-9a-f-]{36})'/g) || [])
    .map((s) => s.replace(/'/g, ''))

  it('清單不是空的', () => expect(listed.length).toBeGreaterThan(5))

  for (const id of listed) {
    it(id.slice(0, 8), () => {
      const lines = fs.readFileSync(`${DIR}/${id}.jsonl`, 'utf8').split(String.fromCharCode(10))
      const has = lines.some((l) => {
        if (!l.trim()) return false
        const src = JSON.parse(l).sources || {}
        return Object.keys(src).some((k) => k !== 'en')
      })
      expect(has, '標了附原典，實際卻沒有原文欄').toBe(true)
    })
  }
})
