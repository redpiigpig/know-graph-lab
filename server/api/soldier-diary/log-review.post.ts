/** 長官批閱日記 — 寫評語、評分（1..5），可加減 XP 獎懲，標記已閱。 */
import { sdSupabase, sdRequireChief } from '~/server/utils/soldierDiary'

export default defineEventHandler(async (event) => {
  sdRequireChief(event)
  const body = await readBody(event)
  const id = Number(body?.id)
  if (!id) throw createError({ statusCode: 400, message: '缺少日記 id' })

  const supabase = sdSupabase()
  const { data: log, error: e0 } = await supabase
    .from('sd_logs').select('id, member_id').eq('id', id).maybeSingle()
  if (e0) throw createError({ statusCode: 500, message: e0.message })
  if (!log) throw createError({ statusCode: 404, message: '查無此日記' })

  const patch: Record<string, unknown> = { status: 'reviewed' }
  if (typeof body.note === 'string') patch.officer_note = body.note.slice(0, 500)
  if (typeof body.score === 'number') patch.officer_score = Math.max(1, Math.min(5, Math.round(body.score)))

  const { error } = await supabase.from('sd_logs').update(patch).eq('id', id)
  if (error) throw createError({ statusCode: 500, message: error.message })

  // 額外 XP 獎懲
  if (typeof body.xpDelta === 'number' && body.xpDelta !== 0) {
    const { data: m } = await supabase
      .from('sd_members').select('xp').eq('id', log.member_id).maybeSingle()
    if (m) {
      await supabase.from('sd_members')
        .update({ xp: Math.max(0, m.xp + Math.round(body.xpDelta)) })
        .eq('id', log.member_id)
    }
  }

  return { ok: true }
})
