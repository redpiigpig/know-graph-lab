import { requireAdmin } from '~/server/utils/auth-helper'

// 回傳白話字《台灣教會公報》某一篇的全文（漢羅＋台羅兩種寫法）。
// 全文按十年打包成 JSONL 放 R2（pct-fulltext/poj/<年代>.jsonl），一包最大約 1 MB，
// 所以整包解析一次就留在行程記憶體——讀者通常會在同一個年代裡連看好幾篇。
const PREFIX = 'pct-fulltext/poj/'
const cache = new Map<string, Map<string, PojRow>>()
const MAX_DECADES_CACHED = 3

interface PojRow {
  id: string
  mag: string
  date: string
  issue: string
  page: string
  author: string
  title: string
  titlePoj: string
  hanlo: string
  tailo: string
}

async function loadDecade(decade: string): Promise<Map<string, PojRow> | null> {
  const hit = cache.get(decade)
  if (hit) return hit

  const body = await r2Text(`${PREFIX}${decade}.jsonl`)
  if (body === null) return null

  const rows = new Map<string, PojRow>()
  for (const row of parseJsonl<PojRow>(body)) rows.set(row.id, row)
  if (cache.size >= MAX_DECADES_CACHED) cache.delete(cache.keys().next().value as string)
  cache.set(decade, rows)
  return rows
}

// 🚨 頁面的 `middleware: 'auth'` 只擋頁面，**不擋這個資料端點**。
//    2026-09-02 實測：未登入直接打這支 API 會回 HTTP 200 連同全文。
//    所有 research-data 的端點都要自己驗，否則「網站有密碼」是假的。
export default defineEventHandler(async (event) => {
  await requireAdmin(event)

  const q = getQuery(event)
  const decade = String(q.decade ?? '')
  // 年代是 1880…1960，另有一桶「未詳」給日期寫「不詳」的那幾筆
  if (!/^(\d{4}|未詳)$/.test(decade)) {
    throw createError({ statusCode: 400, message: 'decade (YYYY or 未詳) required' })
  }
  const id = String(q.id ?? '')
  if (!id) throw createError({ statusCode: 400, message: 'id required' })

  const row = (await loadDecade(decade))?.get(id)
  if (!row) return { available: false }
  return { available: true, hanlo: row.hanlo, tailo: row.tailo, title: row.title, titlePoj: row.titlePoj }
})
