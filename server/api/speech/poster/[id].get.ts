import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'

// 演講海報的 R2 key（與 stores/speech.ts 的 posterPath 對應）
const SPEECH_POSTER_KEYS: Record<string, string> = {
  '2026-05-19-hsuanchuang': 'speech-posters/2026-05-19-hsuanchuang.jpg',
}

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id') || ''
  const key = SPEECH_POSTER_KEYS[id]
  if (!key) {
    throw createError({ statusCode: 404, message: 'Speech poster not registered' })
  }

  const config = useRuntimeConfig()
  const s3 = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: {
      accessKeyId: config.r2AccessKey,
      secretAccessKey: config.r2SecretKey,
    },
  })

  const signedUrl = await getSignedUrl(
    s3,
    new GetObjectCommand({
      Bucket: config.r2Bucket,
      Key: key,
    }),
    { expiresIn: 3600 }
  )

  return sendRedirect(event, signedUrl, 302)
})
