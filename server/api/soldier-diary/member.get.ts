/**
 * 兵員個人檔案 + 日記清單。
 * recruit 只能看自己；chief 可帶 ?id= 看任一人。
 */
import { sdSupabase, sdRequireAuth } from '~/server/utils/soldierDiary'
import { rankForXp, computeBadges, computeStreak } from '~/data/soldierDiaryConfig'
import { tzToday } from '~/server/utils/today'

export default defineEventHandler(async (event) => {
  const auth = sdRequireAuth(event)
  const q = getQuery(event)
  const targetId = auth.role === 'chief' && q.id ? Number(q.id) : auth.id

  if (auth.role === 'recruit' && q.id && Number(q.id) !== auth.id)
    throw createError({ statusCode: 403, message: '只能查看自己的檔案' })
  if (!targetId) throw createError({ statusCode: 400, message: '缺少兵員 id' })

  const supabase = sdSupabase()
  const { data: m, error } = await supabase
    .from('sd_members')
    .select('id, name, callsign, squad, xp, attr_strength, attr_endurance, attr_discipline, attr_bearing, status, note, created_at, last_login')
    .eq('id', targetId)
    .maybeSingle()
  if (error) throw createError({ statusCode: 500, message: error.message })
  if (!m) throw createError({ statusCode: 404, message: '查無此兵員' })

  const { data: logs } = await supabase
    .from('sd_logs')
    .select('id, log_date, type, payload, self_score, xp_awarded, attr_delta, status, officer_note, officer_score, created_at')
    .eq('member_id', targetId)
    .order('log_date', { ascending: false })
    .order('id', { ascending: false })

  const logList = logs || []
  const attrs = {
    strength: m.attr_strength, endurance: m.attr_endurance,
    discipline: m.attr_discipline, bearing: m.attr_bearing,
  }
  const today = tzToday()
  const dates = logList.map((l) => l.log_date)
  const streak = computeStreak(dates, today)
  const totalDrillMin = logList.reduce((s, l) => s + (Number(l.payload?.durationMin) || 0), 0)
  const badges = computeBadges({
    logCount: logList.length,
    streak,
    maxAttr: Math.max(attrs.strength, attrs.endurance, attrs.discipline, attrs.bearing),
    totalDrillMin,
    xp: m.xp,
  })

  return {
    member: {
      id: m.id, name: m.name, callsign: m.callsign, squad: m.squad,
      status: m.status, note: m.note, xp: m.xp, attrs,
      rankInfo: rankForXp(m.xp),
      createdAt: m.created_at, lastLogin: m.last_login,
    },
    logs: logList,
    stats: { streak, totalDrillMin, logCount: logList.length, todayLogged: dates.includes(today) },
    badges,
  }
})
