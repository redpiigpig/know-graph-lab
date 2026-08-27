import { GetObjectCommand } from '@aws-sdk/client-s3'
import * as mammoth from 'mammoth'
import { getR2Client } from '~/server/utils/r2'
import { sdRequireAuth } from '~/server/utils/soldierDiary'

const RULES_KEY = 'soldier-diary/basic-rules/禮兵調教守則(2024.12.30).docx'
let cached: { html: string; messages: string[] } | null = null

export default defineEventHandler(async (event) => {
  sdRequireAuth(event)
  if (cached) return cached

  const config = useRuntimeConfig()
  try {
    const object = await getR2Client().send(new GetObjectCommand({
      Bucket: config.r2Bucket as string,
      Key: RULES_KEY,
    }))
    if (!object.Body) throw new Error('文件內容為空')

    const bytes = await object.Body.transformToByteArray()
    const converted = await mammoth.convertToHtml({ buffer: Buffer.from(bytes) })
    cached = {
      html: converted.value,
      messages: converted.messages.map((message) => message.message),
    }
    return cached
  } catch (error: any) {
    throw createError({
      statusCode: error?.$metadata?.httpStatusCode === 404 ? 404 : 500,
      message: error?.$metadata?.httpStatusCode === 404 ? '基本守則文件尚未上傳' : '基本守則載入失敗',
    })
  }
})
