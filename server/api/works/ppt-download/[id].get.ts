import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const config = useRuntimeConfig()
  const url = config.public.supabaseUrl
  const key = config.supabaseServiceRoleKey

  const rows = await $fetch<{ ppt_r2_key: string | null; title: string }[]>(
    `${url}/rest/v1/video_transcripts?id=eq.${id}&select=ppt_r2_key,title&limit=1`,
    { headers: { apikey: key, Authorization: `Bearer ${key}` } }
  ).catch(() => [])

  const row = (rows as any[])[0]
  if (!row?.ppt_r2_key) {
    throw createError({ statusCode: 404, message: 'PPT not available' })
  }

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
      Key: row.ppt_r2_key,
      ResponseContentDisposition: `attachment; filename="${encodeURIComponent(row.title)}.pptx"`,
    }),
    { expiresIn: 3600 }
  )

  return sendRedirect(event, signedUrl, 302)
})
