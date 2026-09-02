import { requireAdmin } from '~/server/utils/auth-helper'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

// 回傳弘誓刊物某原檔的全文轉錄。傳入原檔 key（yinshun-hongshi/<刊>/X.pdf），
// 映射到全文前綴 yinshun-hongshi-fulltext/<刊>/X.txt。
const SRC_PREFIX = 'yinshun-hongshi/'
const TXT_PREFIX = 'yinshun-hongshi-fulltext/'

async function readKey(s3: S3Client, bucket: string, key: string): Promise<string | null> {
  try {
    const r = await s3.send(new GetObjectCommand({ Bucket: bucket, Key: key }))
    return (await r.Body?.transformToString('utf-8')) ?? null
  } catch {
    return null
  }
}

// 🚨 頁面的 `middleware: 'auth'` 只擋頁面，**不擋這個資料端點**。
//    2026-09-02 實測：未登入直接打這支 API 會回 HTTP 200 連同全文。
//    所有 research-data 的端點都要自己驗，否則「網站有密碼」是假的。
export default defineEventHandler(async (event) => {
  await requireAdmin(event)

  const srcKey = String(getQuery(event).key ?? '')
  if (!srcKey.startsWith(SRC_PREFIX) || srcKey.includes('..')) {
    throw createError({ statusCode: 400, message: 'invalid key' })
  }
  const rel = srcKey.slice(SRC_PREFIX.length).replace(/\.pdf$/i, '')
  const config = useRuntimeConfig()
  const s3 = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: { accessKeyId: config.r2AccessKey, secretAccessKey: config.r2SecretKey },
  })

  const text = await readKey(s3, config.r2Bucket, `${TXT_PREFIX}${rel}.txt`)
  if (text === null) return { available: false }
  return { available: true, text }
})
