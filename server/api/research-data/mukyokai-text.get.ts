import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

// 「無教會主義研究資料」的全文（逐件一個 .txt，key 由 index.json 提供）。
const PREFIX = 'mukyokai-fulltext/'

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
    return { available: true, text: (await r.Body?.transformToString('utf-8')) ?? '' }
  } catch {
    return { available: false }
  }
})
