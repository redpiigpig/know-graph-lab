import { requireAdmin } from '~/server/utils/auth-helper'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

// 回傳某研究資料的全文轉錄（dadaodao-fulltext/<rel>.txt）＋（若有）繁中翻譯（.zh.txt）。
// 傳入的是 manifest 裡的 material key（dadaodao-materials/...），這裡映射到全文前綴。
const MAT_PREFIX = 'dadaodao-materials/'
const TXT_PREFIX = 'dadaodao-fulltext/'

async function readKey(s3: S3Client, bucket: string, key: string): Promise<string | null> {
  try {
    const r = await s3.send(new GetObjectCommand({ Bucket: bucket, Key: key }))
    return (await r.Body?.transformToString('utf-8')) ?? null
  } catch {
    return null
  }
}

// 🚨 頁面的 `middleware: 'auth'` 只擋頁面，**不擋這個資料端點**。
//    姊妹檔 yinshun-hongshi-text.get.ts 在 2026-09-02 就記過這件事並補了驗證，
//    但這一支漏掉了——未登入直接打 `/api/works/material-text?key=…`
//    會回 HTTP 200 連同《大愛道革命》研究資料的全文（含福嚴會訊 71 期）。
//    2026-09-16 補上。加 requireAdmin 時**呼叫端要一起改**：$fetch 預設不帶
//    Authorization，不補 header 的話 401 會讓「全文」鈕靜默變成沒有內容。
//
//    ⚠️ 同一夾的 material.get.ts（PDF 下載）還沒補，因為它是 `<a href>` 直連，
//    帶不了 Bearer header。要修得另外走簽章網址或 cookie，不能照抄這裡。
export default defineEventHandler(async (event) => {
  await requireAdmin(event)

  const matKey = String(getQuery(event).key ?? '')
  if (!matKey.startsWith(MAT_PREFIX) || matKey.includes('..')) {
    throw createError({ statusCode: 400, message: 'invalid key' })
  }
  const rel = matKey.slice(MAT_PREFIX.length)
  const config = useRuntimeConfig()
  const s3 = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: { accessKeyId: config.r2AccessKey, secretAccessKey: config.r2SecretKey },
  })

  const text = await readKey(s3, config.r2Bucket, `${TXT_PREFIX}${rel}.txt`)
  if (text === null) return { available: false }
  const zh = await readKey(s3, config.r2Bucket, `${TXT_PREFIX}${rel}.zh.txt`)
  return { available: true, text, zh: zh ?? null }
})
