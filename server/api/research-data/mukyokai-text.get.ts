import { requireAdmin } from '~/server/utils/auth-helper'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

// 「無教會主義研究資料」的全文（逐件一個 .txt，key 由 index.json 提供）。
const PREFIX = 'mukyokai-fulltext/'

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
