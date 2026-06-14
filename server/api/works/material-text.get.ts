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

export default defineEventHandler(async (event) => {
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
