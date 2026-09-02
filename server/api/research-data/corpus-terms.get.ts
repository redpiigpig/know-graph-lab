import { requireAdmin } from '~/server/utils/auth-helper'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

// 跨語料關鍵詞年表的計數表。scripts/corpus_terms.py --build 產出後放 R2；
// 整份只有數百 KB（策展詞表，不是全文索引），所以一次回傳、行程內快取即可。
const KEY = 'corpus-index/term-counts.json'
let cached: unknown = null

// 🚨 頁面的 `middleware: 'auth'` 只擋頁面，**不擋這個資料端點**。
//    2026-09-02 實測：未登入直接打這支 API 會回 HTTP 200 連同全文。
//    所有 research-data 的端點都要自己驗，否則「網站有密碼」是假的。
export default defineEventHandler(async (event) => {
  await requireAdmin(event)

  if (cached) return cached
  const config = useRuntimeConfig()
  const s3 = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: { accessKeyId: config.r2AccessKey, secretAccessKey: config.r2SecretKey },
  })
  try {
    const r = await s3.send(new GetObjectCommand({ Bucket: config.r2Bucket, Key: KEY }))
    const body = (await r.Body?.transformToString('utf-8')) ?? '{}'
    cached = { available: true, ...JSON.parse(body) }
    return cached
  } catch {
    return { available: false }
  }
})
