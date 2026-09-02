import { requireAdmin } from '~/server/utils/auth-helper'

// 回傳《台灣教會公報》新聞網某一篇的全文。全文按年打包成 JSONL 放 R2
// （pct-fulltext/tcnn/<年>.jsonl），一年約 3 MB；讀者通常會在同一年裡連看好幾篇，
// 所以整年解析一次就留在行程記憶體，不必每篇都回 R2 取一次。
const PREFIX = 'pct-fulltext/tcnn/'
const cache = new Map<string, Map<number, TcnnRow>>()
const MAX_YEARS_CACHED = 3

interface TcnnRow {
  id: number
  date: string
  title: string
  link: string
  text: string
}

async function loadYear(year: string): Promise<Map<number, TcnnRow> | null> {
  const hit = cache.get(year)
  if (hit) return hit

  const body = await r2Text(`${PREFIX}${year}.jsonl`)
  if (body === null) return null

  const rows = new Map<number, TcnnRow>()
  for (const row of parseJsonl<TcnnRow>(body)) rows.set(row.id, row)
  if (cache.size >= MAX_YEARS_CACHED) cache.delete(cache.keys().next().value as string)
  cache.set(year, rows)
  return rows
}

// 🚨 頁面的 `middleware: 'auth'` 只擋頁面，**不擋這個資料端點**。
//    2026-09-02 實測：未登入直接打這支 API 會回 HTTP 200 連同全文。
//    所有 research-data 的端點都要自己驗，否則「網站有密碼」是假的。
export default defineEventHandler(async (event) => {
  await requireAdmin(event)

  const q = getQuery(event)
  const year = String(q.year ?? '')
  if (!/^\d{4}$/.test(year)) {
    throw createError({ statusCode: 400, message: 'year (YYYY) required' })
  }
  const rows = await loadYear(year)

  // 沒帶 id 就是要該年篇目清單（題名／日期／連結，不含全文）。逐年清單合計約
  // 6 MB，放 repo 會隨每次重跑整批改寫，所以一律由 R2 供應。
  if (q.id === undefined) {
    if (!rows) return { available: false, articles: [] }
    const articles = [...rows.values()]
      .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0))
      .map(({ id, date, title, link }) => ({ id, date, title, link }))
    return { available: true, articles }
  }

  const id = Number(q.id)
  if (!Number.isInteger(id)) throw createError({ statusCode: 400, message: 'id must be an integer' })
  const row = rows?.get(id)
  if (!row) return { available: false }
  return { available: true, text: row.text, title: row.title, date: row.date, link: row.link }
})
