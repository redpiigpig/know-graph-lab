import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

// 回傳「台灣基督長老教會研究資料」collection 裡某一篇的全文。
// 逐篇一個 .txt（pct-fulltext/<刊>/<檔>.txt），與教會公報那支按年打包的不同，
// 所以另開一支：這裡直接取單一 key，不必整批解析。
const PREFIX = 'pct-fulltext/'

export default defineEventHandler(async (event) => {
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
    const text = (await r.Body?.transformToString('utf-8')) ?? ''
    return { available: true, text }
  } catch {
    return { available: false }
  }
})
