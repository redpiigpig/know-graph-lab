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
