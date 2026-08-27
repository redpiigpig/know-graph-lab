import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

// 跨語料關鍵詞年表的計數表。scripts/corpus_terms.py --build 產出後放 R2；
// 整份只有數百 KB（策展詞表，不是全文索引），所以一次回傳、行程內快取即可。
const KEY = 'corpus-index/term-counts.json'
let cached: unknown = null

export default defineEventHandler(async () => {
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
