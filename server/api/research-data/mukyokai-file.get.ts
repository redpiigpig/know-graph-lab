import fs from 'node:fs'
import { stat } from 'node:fs/promises'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'
import { resolveResearchFile } from '~/server/utils/research-files'

// 「日本無教會主義研究資料」的原檔（學位論文、專書掃描，皆為 PDF）。
//
// 取檔順序：**Drive 正本 → R2 後備**。本機跑站時 G: 槽掛著 Drive，直接串流檔案；
// 雲端部署沒有 Drive，才退回 R2 簽名網址。這批是零星取得的論文 PDF、單件多在
// 數 MB，符合 docs/r2-policy.md 的小體積衍生物，故兩邊都放。
const ALLOWED_PREFIX = 'mukyokai/'

export default defineEventHandler(async (event) => {
  const key = String(getQuery(event).key ?? '')
  if (!key.startsWith(ALLOWED_PREFIX) || key.includes('..')) {
    throw createError({ statusCode: 400, message: 'invalid key' })
  }
  const download = String(getQuery(event).download ?? '') === '1'
  const filename = key.split('/').pop() || 'download'

  const local = resolveResearchFile(key)
  if (local) {
    const st = await stat(local).catch(() => null)
    if (st?.isFile()) {
      setResponseHeaders(event, {
        'Content-Type': 'application/pdf',
        'Content-Length': String(st.size),
        'Cache-Control': 'private, max-age=3600',
        ...(download
          ? { 'Content-Disposition': `attachment; filename*=UTF-8''${encodeURIComponent(filename)}` }
          : {}),
      })
      return sendStream(event, fs.createReadStream(local))
    }
  }

  const config = useRuntimeConfig()
  const s3 = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: { accessKeyId: config.r2AccessKey, secretAccessKey: config.r2SecretKey },
  })
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
