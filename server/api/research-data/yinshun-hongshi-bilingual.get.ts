import { requireAdmin } from '~/server/utils/auth-helper'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

// 外文論文的「原文／中譯」逐段對照。傳入條目 id（如 japan/1976-makita-xxx），
// 讀 R2 的 yinshun-hongshi-fulltext/<id>.json：{ paras: [{ page, orig, zh }] }。
// 產檔器：scripts/yinshun_japan_bilingual.py。
const PREFIX = 'yinshun-hongshi-fulltext/'

// 🚨 頁面的 middleware 不擋資料端點，這支一樣要自己驗（見 yinshun-hongshi-text.get.ts）。
export default defineEventHandler(async (event) => {
  await requireAdmin(event)

  const id = String(getQuery(event).id ?? '')
  if (!/^[a-z]+\/[\w.-]+$/.test(id)) {
    throw createError({ statusCode: 400, message: 'invalid id' })
  }
  const config = useRuntimeConfig()
  const s3 = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: { accessKeyId: config.r2AccessKey, secretAccessKey: config.r2SecretKey },
  })
  try {
    const r = await s3.send(new GetObjectCommand({ Bucket: config.r2Bucket, Key: `${PREFIX}${id}.json` }))
    const body = await r.Body?.transformToString('utf-8')
    if (!body) return { available: false }
    return { available: true, ...JSON.parse(body) }
  } catch {
    return { available: false }
  }
})
