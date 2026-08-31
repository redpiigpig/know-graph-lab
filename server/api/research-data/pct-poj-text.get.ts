import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

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

  const config = useRuntimeConfig()
  const s3 = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: { accessKeyId: config.r2AccessKey, secretAccessKey: config.r2SecretKey },
  })
  let body: string
  try {
    const r = await s3.send(new GetObjectCommand({ Bucket: config.r2Bucket, Key: `${PREFIX}${decade}.jsonl` }))
    body = (await r.Body?.transformToString('utf-8')) ?? ''
  } catch {
    return null
  }

  const rows = new Map<string, PojRow>()
  for (const line of body.split('\n')) {
    if (!line.trim()) continue
    try {
      const row = JSON.parse(line) as PojRow
      rows.set(row.id, row)
    } catch { /* 單行壞掉不該讓整個年代讀不出來 */ }
  }
  if (cache.size >= MAX_DECADES_CACHED) cache.delete(cache.keys().next().value as string)
  cache.set(decade, rows)
  return rows
}

export default defineEventHandler(async (event) => {
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
