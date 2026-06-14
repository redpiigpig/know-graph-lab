import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'

// 簽名下載「印順學派與弘誓研究資料」collection 的原檔（R2 yinshun-hongshi/ 前綴）。
// key 由各 index.json 提供；嚴格限定前綴，避免任意取用 bucket 其它物件。
const ALLOWED_PREFIX = 'yinshun-hongshi/'

export default defineEventHandler(async (event) => {
  const key = String(getQuery(event).key ?? '')
  if (!key.startsWith(ALLOWED_PREFIX) || key.includes('..')) {
    throw createError({ statusCode: 400, message: 'invalid key' })
  }
  const download = String(getQuery(event).download ?? '') === '1'
  const config = useRuntimeConfig()
  const s3 = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: { accessKeyId: config.r2AccessKey, secretAccessKey: config.r2SecretKey },
  })

  const filename = key.split('/').pop() || 'download'
  const signedUrl = await getSignedUrl(
    s3,
    new GetObjectCommand({
      Bucket: config.r2Bucket,
      Key: key,
      ...(download
        ? { ResponseContentDisposition: `attachment; filename*=UTF-8''${encodeURIComponent(filename)}` }
        : {}),
    }),
    { expiresIn: 3600 }
  )
  return sendRedirect(event, signedUrl, 302)
})
