import fs from 'node:fs'
import { stat } from 'node:fs/promises'
import path from 'node:path'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'
import { resolveResearchFile } from '~/server/utils/research-files'

// 下載《當代的大愛道革命》研究資料。
//
// 取檔順序：**Drive 正本 → R2 後備**。本機跑站時 G: 槽掛著 Drive，直接串流檔案；
// 雲端部署沒有 Drive，才退回 R2 簽名網址（R2 只留得下小體積的那幾筆）。
// 大宗掃描原檔不放 R2 —— 見 docs/r2-policy.md。
const ALLOWED_PREFIX = 'dadaodao-materials/'

const CONTENT_TYPES: Record<string, string> = {
  '.pdf': 'application/pdf',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.doc': 'application/msword',
  '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}

export default defineEventHandler(async (event) => {
  const key = String(getQuery(event).key ?? '')
  if (!key.startsWith(ALLOWED_PREFIX) || key.includes('..')) {
    throw createError({ statusCode: 400, message: 'invalid key' })
  }
  const filename = key.split('/').pop() || 'download'

  const local = resolveResearchFile(key)
  if (local) {
    const st = await stat(local).catch(() => null)
    if (st?.isFile()) {
      setResponseHeaders(event, {
        'Content-Type': CONTENT_TYPES[path.extname(local).toLowerCase()] ?? 'application/octet-stream',
        'Content-Length': String(st.size),
        'Content-Disposition': `attachment; filename*=UTF-8''${encodeURIComponent(filename)}`,
        'Cache-Control': 'private, max-age=3600',
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
      ResponseContentDisposition: `attachment; filename*=UTF-8''${encodeURIComponent(filename)}`,
    }),
    { expiresIn: 3600 }
  )
  return sendRedirect(event, signedUrl, 302)
})
