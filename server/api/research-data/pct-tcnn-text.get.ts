import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

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

  const config = useRuntimeConfig()
  const s3 = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: { accessKeyId: config.r2AccessKey, secretAccessKey: config.r2SecretKey },
  })
  let body: string
  try {
    const r = await s3.send(new GetObjectCommand({ Bucket: config.r2Bucket, Key: `${PREFIX}${year}.jsonl` }))
    body = (await r.Body?.transformToString('utf-8')) ?? ''
  } catch {
    return null
  }

  const rows = new Map<number, TcnnRow>()
  for (const line of body.split('\n')) {
    if (!line.trim()) continue
    try {
      const row = JSON.parse(line) as TcnnRow
      rows.set(row.id, row)
    } catch { /* 單行壞掉不該讓整年讀不出來 */ }
  }
  if (cache.size >= MAX_YEARS_CACHED) cache.delete(cache.keys().next().value as string)
  cache.set(year, rows)
  return rows
}

export default defineEventHandler(async (event) => {
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
