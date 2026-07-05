/** 長官後台 — 待批閱日記佇列（跨全體兵員，含兵員姓名與代號）。 */
import { sdSupabase, sdRequireChief } from '~/server/utils/soldierDiary'

export default defineEventHandler(async (event) => {
  sdRequireChief(event)
  const q = getQuery(event)
  const supabase = sdSupabase()

  let query = supabase
    .from('sd_logs')
    .select('id, member_id, log_date, type, payload, self_score, xp_awarded, status, officer_note, officer_score, created_at, sd_members(name, callsign)')
    .order('log_date', { ascending: false })
    .order('id', { ascending: false })
    .limit(200)

  if (q.status === 'submitted') query = query.eq('status', 'submitted')

  const { data, error } = await query
  if (error) throw createError({ statusCode: 500, message: error.message })

  const logs = (data || []).map((l: any) => ({
    id: l.id, memberId: l.member_id,
    memberName: l.sd_members?.name || '', memberCallsign: l.sd_members?.callsign || '',
    logDate: l.log_date, type: l.type, payload: l.payload,
    selfScore: l.self_score, xpAwarded: l.xp_awarded, status: l.status,
    officerNote: l.officer_note, officerScore: l.officer_score, createdAt: l.created_at,
  }))
  return { logs }
})
