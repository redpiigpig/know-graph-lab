/** 長官後台 — 全體兵員名冊（含軍階、五品質、當前軍種、日記數、最近回報日）。 */
import { sdSupabase, sdRequireChief } from '~/server/utils/soldierDiary'
import { rankForXp, activeBranch, branchStates } from '~/data/soldierDiaryConfig'

export default defineEventHandler(async (event) => {
  sdRequireChief(event)
  const supabase = sdSupabase()

  const { data: members, error } = await supabase
    .from('sd_members')
    .select('id, name, callsign, squad, xp, q_obedience, q_strength, q_endurance, q_composure, q_challenge, status, note, created_at, last_login')
    .order('xp', { ascending: false })
  if (error) throw createError({ statusCode: 500, message: error.message })

  const { data: logStats } = await supabase.from('sd_logs').select('member_id, log_date, status')
  const byMember: Record<number, { count: number; last: string; pending: number }> = {}
  for (const l of logStats || []) {
    const m = (byMember[l.member_id] ||= { count: 0, last: '', pending: 0 })
    m.count++
    if (l.log_date > m.last) m.last = l.log_date
    if (l.status === 'submitted') m.pending++
  }

  const rows = (members || []).map((m) => {
    const qualities = {
      obedience: m.q_obedience, strength: m.q_strength, endurance: m.q_endurance,
      composure: m.q_composure, challenge: m.q_challenge,
    }
    const active = activeBranch(qualities)
    const conqueredCount = branchStates(qualities).filter((s) => s.conquered).length
    return {
      id: m.id, name: m.name, callsign: m.callsign, squad: m.squad,
      status: m.status, note: m.note, xp: m.xp,
      rank: rankForXp(m.xp).rank,
      qualities,
      currentBranch: active ? { key: active.key, name: active.name, quality: active.quality } : null,
      conqueredCount,
      graduated: !active,
      logCount: byMember[m.id]?.count || 0,
      pendingCount: byMember[m.id]?.pending || 0,
      lastReport: byMember[m.id]?.last || null,
      createdAt: m.created_at, lastLogin: m.last_login,
    }
  })
  return { members: rows }
})
