// POST /api/speech/edit/[id]
// 編輯演講（逐字稿 .txt + metadata .meta.json）— 登入才能用
import { writeFile, mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'

const ALLOWED_IDS = new Set([
  '2026-05-19-hsuanchuang',
])

const ALLOWED_META_FIELDS = [
  'title', 'subtitle', 'date', 'duration',
  'venue', 'organizer', 'course', 'category', 'description',
] as const

export default defineEventHandler(async (event) => {
  await requireAuth(event)

  const id = getRouterParam(event, 'id') || ''
  if (!ALLOWED_IDS.has(id)) {
    throw createError({ statusCode: 404, message: 'Speech not registered' })
  }

  const body = await readBody(event) as {
    content?: string
    meta?: Record<string, string>
  }

  const dir = resolve(process.cwd(), 'public', 'content', 'speech')
  await mkdir(dir, { recursive: true })

  // 寫逐字稿
  if (typeof body.content === 'string') {
    if (body.content.length > 500_000) {
      throw createError({ statusCode: 413, message: 'content too large (>500KB)' })
    }
    await writeFile(resolve(dir, `${id}.txt`), body.content, 'utf-8')
  }

  // 寫 metadata
  if (body.meta && typeof body.meta === 'object') {
    const cleanMeta: Record<string, string> = {}
    for (const k of ALLOWED_META_FIELDS) {
      const v = body.meta[k]
      if (typeof v === 'string') cleanMeta[k] = v
    }
    await writeFile(
      resolve(dir, `${id}.meta.json`),
      JSON.stringify(cleanMeta, null, 2) + '\n',
      'utf-8'
    )
  }

  return { ok: true }
})
