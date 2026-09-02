import { requireAdmin } from '~/server/utils/auth-helper'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

// 《基督教論壇報》逐篇全文（evangelical-fulltext/ct/<ID>.txt）。
// 與教會公報那支按年打包不同，論壇報是逐篇一個 .txt，直接取單一 key。
const PREFIX = 'evangelical-fulltext/'

// 🚨 頁面的 `middleware: 'auth'` 只擋頁面，**不擋這個資料端點**。
//    2026-09-02 實測：未登入直接打這支 API 會回 HTTP 200 連同全文。
//    所有 research-data 的端點都要自己驗，否則「網站有密碼」是假的。
export default defineEventHandler(async (event) => {
  await requireAdmin(event)

  const key = String(getQuery(event).key ?? '')
  if (!key.startsWith(PREFIX) || key.includes('..')) {
    throw createError({ statusCode: 400, message: 'invalid key' })
  }
  const config = useRuntimeConfig()
  const s3 = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: { accessKeyId: config.r2AccessKey, secretAccessKey: config.r2SecretKey },
  })
  try {
    const r = await s3.send(new GetObjectCommand({ Bucket: config.r2Bucket, Key: key }))
    return { available: true, text: (await r.Body?.transformToString('utf-8')) ?? '' }
  } catch {
    return { available: false }
  }
})
