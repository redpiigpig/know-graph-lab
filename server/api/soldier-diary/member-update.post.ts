/**
 * 長官後台 — 更新兵員：可改小隊/備註/狀態、重設通行碼、手動微調屬性或 XP（獎懲）。
 */
import { sdSupabase, sdRequireChief } from '~/server/utils/soldierDiary'
import { ATTR_MIN, ATTR_MAX } from '~/data/soldierDiaryConfig'

const clampAttr = (n: number) => Math.max(ATTR_MIN, Math.min(ATTR_MAX, Math.round(n)))

export default defineEventHandler(async (event) => {
  sdRequireChief(event)
  const body = await readBody(event)
  const id = Number(body?.id)
  if (!id) throw createError({ statusCode: 400, message: '缺少兵員 id' })

  const supabase = sdSupabase()
  const { data: cur, error: e0 } = await supabase
    .from('sd_members').select('*').eq('id', id).maybeSingle()
  if (e0) throw createError({ statusCode: 500, message: e0.message })
  if (!cur) throw createError({ statusCode: 404, message: '查無此兵員' })

  const patch: Record<string, unknown> = {}
  if (typeof body.squad === 'string') patch.squad = body.squad.trim()
  if (typeof body.note === 'string') patch.note = body.note.trim()
  if (body.status === 'active' || body.status === 'discharged') patch.status = body.status
  if (typeof body.code === 'string' && body.code.trim()) patch.access_code = body.code.trim()

  // 屬性覆寫（絕對值）
  const a = body.attrs || {}
  if (typeof a.strength === 'number') patch.attr_strength = clampAttr(a.strength)
  if (typeof a.endurance === 'number') patch.attr_endurance = clampAttr(a.endurance)
  if (typeof a.discipline === 'number') patch.attr_discipline = clampAttr(a.discipline)
  if (typeof a.bearing === 'number') patch.attr_bearing = clampAttr(a.bearing)

  // XP 增減（獎懲）
  if (typeof body.xpDelta === 'number' && body.xpDelta !== 0)
    patch.xp = Math.max(0, cur.xp + Math.round(body.xpDelta))
  if (typeof body.xp === 'number') patch.xp = Math.max(0, Math.round(body.xp))

  if (Object.keys(patch).length === 0) return { ok: true, unchanged: true }

  const { error } = await supabase.from('sd_members').update(patch).eq('id', id)
  if (error) throw createError({ statusCode: 500, message: error.message })
  return { ok: true }
})
