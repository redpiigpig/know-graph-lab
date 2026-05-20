// POST /api/speech/edit/[id]
// 編輯演講逐字稿（登入才能用）
import { writeFile, mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'

const ALLOWED_IDS = new Set([
  '2026-05-19-hsuanchuang',
])

export default defineEventHandler(async (event) => {
  await requireAuth(event)

  const id = getRouterParam(event, 'id') || ''
  if (!ALLOWED_IDS.has(id)) {
    throw createError({ statusCode: 404, message: 'Speech not registered' })
  }

  const body = await readBody(event) as { content?: string }
  const content = body.content ?? ''
  if (typeof content !== 'string') {
    throw createError({ statusCode: 400, message: 'content must be a string' })
  }
  if (content.length > 500_000) {
    throw createError({ statusCode: 413, message: 'content too large (>500KB)' })
  }

  const target = resolve(process.cwd(), 'public', 'content', 'speech', `${id}.txt`)
  await mkdir(resolve(process.cwd(), 'public', 'content', 'speech'), { recursive: true })
  await writeFile(target, content, 'utf-8')

  return { ok: true, bytes: Buffer.byteLength(content, 'utf-8') }
})
