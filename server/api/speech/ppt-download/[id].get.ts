import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'

// 演講 PPT 與 R2 key 的對照（與 stores/speech.ts 保持同步）
const SPEECH_PPT_KEYS: Record<string, { key: string; filename: string }> = {
  '2026-05-19-hsuanchuang': {
    key: 'talks-ppt/2026-05-19-hsuanchuang.pptx',
    filename: '2026.05.19 玄奘宗教系講座 — 台灣佛教具有民主基因嗎.pptx',
  },
}

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id') || ''
  const meta = SPEECH_PPT_KEYS[id]
  if (!meta) {
    throw createError({ statusCode: 404, message: 'Speech PPT not registered' })
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
      Key: meta.key,
      ResponseContentDisposition: `attachment; filename="${encodeURIComponent(meta.filename)}"`,
    }),
    { expiresIn: 3600 }
  )

  return sendRedirect(event, signedUrl, 302)
})
