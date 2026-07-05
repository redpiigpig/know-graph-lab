/** 長官後台 — 全體兵員名冊（含軍階、屬性、日記數、最近回報日）。 */
import { sdSupabase, sdRequireChief } from '~/server/utils/soldierDiary'
import { rankForXp } from '~/data/soldierDiaryConfig'

export default defineEventHandler(async (event) => {
  sdRequireChief(event)
  const supabase = sdSupabase()

  const { data: members, error } = await supabase
    .from('sd_members')
    .select('id, name, callsign, squad, xp, attr_strength, attr_endurance, attr_discipline, attr_bearing, status, note, created_at, last_login')
    .order('xp', { ascending: false })

  if (error) throw createError({ statusCode: 500, message: error.message })

  // 每人日記數與最近回報日
  const { data: logStats } = await supabase
    .from('sd_logs')
    .select('member_id, log_date, status')

  const byMember: Record<number, { count: number; last: string; pending: number }> = {}
  for (const l of logStats || []) {
    const m = (byMember[l.member_id] ||= { count: 0, last: '', pending: 0 })
    m.count++
    if (l.log_date > m.last) m.last = l.log_date
    if (l.status === 'submitted') m.pending++
  }

  const rows = (members || []).map((m) => ({
    id: m.id,
    name: m.name,
    callsign: m.callsign,
    squad: m.squad,
    status: m.status,
    note: m.note,
    xp: m.xp,
    rank: rankForXp(m.xp).rank,
    attrs: {
      strength: m.attr_strength,
      endurance: m.attr_endurance,
      discipline: m.attr_discipline,
      bearing: m.attr_bearing,
    },
    logCount: byMember[m.id]?.count || 0,
    pendingCount: byMember[m.id]?.pending || 0,
    lastReport: byMember[m.id]?.last || null,
    createdAt: m.created_at,
    lastLogin: m.last_login,
  }))

  return { members: rows }
})
