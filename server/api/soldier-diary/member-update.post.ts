/**
 * 長官後台 — 更新兵員：改小隊/備註/狀態、重設通行碼、手動微調五品質或 XP（獎懲）。
 */
import { sdSupabase, sdRequireChief } from '~/server/utils/soldierDiary'
import { QUALITY_MIN, QUALITY_MAX, QUALITIES } from '~/data/soldierDiaryConfig'

const clampQ = (n: number) => Math.max(QUALITY_MIN, Math.min(QUALITY_MAX, Math.round(n)))
const COL: Record<string, string> = {
  obedience: 'q_obedience', strength: 'q_strength', endurance: 'q_endurance',
  composure: 'q_composure', challenge: 'q_challenge',
}

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

  // 五品質覆寫（絕對值）
  const q = body.qualities || {}
  for (const def of QUALITIES) {
    if (typeof q[def.key] === 'number') patch[COL[def.key]] = clampQ(q[def.key])
  }

  // XP 增減 / 覆寫（獎懲）
  if (typeof body.xpDelta === 'number' && body.xpDelta !== 0)
    patch.xp = Math.max(0, cur.xp + Math.round(body.xpDelta))
  if (typeof body.xp === 'number') patch.xp = Math.max(0, Math.round(body.xp))

  if (Object.keys(patch).length === 0) return { ok: true, unchanged: true }

  const { error } = await supabase.from('sd_members').update(patch).eq('id', id)
  if (error) throw createError({ statusCode: 500, message: error.message })
  return { ok: true }
})
