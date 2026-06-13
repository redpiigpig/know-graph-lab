import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'

// 簽名下載《當代的大愛道革命》研究資料（R2 dadaodao-materials/ 前綴）。
// key 由 manifest 提供；嚴格限定前綴，避免任意取用 bucket 其它物件。
const ALLOWED_PREFIX = 'dadaodao-materials/'

export default defineEventHandler(async (event) => {
  const key = String(getQuery(event).key ?? '')
  if (!key.startsWith(ALLOWED_PREFIX) || key.includes('..')) {
    throw createError({ statusCode: 400, message: 'invalid key' })
  }
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
      ResponseContentDisposition: `attachment; filename*=UTF-8''${encodeURIComponent(filename)}`,
    }),
    { expiresIn: 3600 }
  )
  return sendRedirect(event, signedUrl, 302)
})
