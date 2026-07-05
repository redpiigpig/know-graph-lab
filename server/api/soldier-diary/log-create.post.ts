/**
 * 提交／更新當日日記 — 兵員（chief 可代填，帶 memberId）。
 * 計算 XP 與屬性成長套到兵員身上。每日每型別一篇；重送當日則以差額更新。
 */
import { sdSupabase, sdRequireAuth } from '~/server/utils/soldierDiary'
import {
  computeLogRewards, applyAttrDelta, type DiaryPayload, type AttrKey,
} from '~/data/soldierDiaryConfig'
import { tzToday } from '~/server/utils/today'

export default defineEventHandler(async (event) => {
  const auth = sdRequireAuth(event)
  const body = await readBody(event)

  const memberId = auth.role === 'chief' && body?.memberId ? Number(body.memberId) : auth.id
  if (!memberId) throw createError({ statusCode: 400, message: '缺少兵員 id' })

  const payload: DiaryPayload = {
    drillItems: Array.isArray(body?.drillItems) ? body.drillItems.map(String) : [],
    durationMin: Math.max(0, Math.min(600, Number(body?.durationMin) || 0)),
    missions: Array.isArray(body?.missions) ? body.missions.map(String) : [],
    note: String(body?.note || '').slice(0, 500),
  }
  const selfScore = Math.max(0, Math.min(5, Math.floor(Number(body?.selfScore) || 0)))

  if (payload.drillItems.length === 0 && payload.missions.length === 0)
    throw createError({ statusCode: 400, message: '至少要記錄一項操課或一項任務' })

  const logDate = /^\d{4}-\d{2}-\d{2}$/.test(body?.logDate) ? body.logDate : tzToday()
  const type = 'drill'

  const supabase = sdSupabase()
  const { data: m, error: e0 } = await supabase
    .from('sd_members')
    .select('id, xp, attr_strength, attr_endurance, attr_discipline, attr_bearing, status')
    .eq('id', memberId).maybeSingle()
  if (e0) throw createError({ statusCode: 500, message: e0.message })
  if (!m) throw createError({ statusCode: 404, message: '查無此兵員' })
  if (m.status === 'discharged')
    throw createError({ statusCode: 403, message: '此帳號已退伍停用' })

  const reward = computeLogRewards(payload, selfScore)

  // 當日是否已有同型別日記 → 先回滾舊獎勵再套新獎勵
  const { data: existing } = await supabase
    .from('sd_logs')
    .select('id, xp_awarded, attr_delta')
    .eq('member_id', memberId).eq('log_date', logDate).eq('type', type)
    .maybeSingle()

  let curAttrs: Record<AttrKey, number> = {
    strength: m.attr_strength, endurance: m.attr_endurance,
    discipline: m.attr_discipline, bearing: m.attr_bearing,
  }
  let curXp = m.xp

  if (existing) {
    // 回滾舊獎勵
    const oldDelta = existing.attr_delta || {}
    const negated: Record<string, number> = {}
    for (const k of Object.keys(oldDelta)) negated[k] = -(oldDelta[k] || 0)
    curAttrs = applyAttrDelta(curAttrs, negated as any)
    curXp = Math.max(0, curXp - (existing.xp_awarded || 0))
  }

  // 套新獎勵
  const newAttrs = applyAttrDelta(curAttrs, reward.attrDelta)
  const newXp = curXp + reward.xp

  // 寫入／更新日記
  const logRow = {
    member_id: memberId, log_date: logDate, type,
    payload, self_score: selfScore,
    xp_awarded: reward.xp, attr_delta: reward.attrDelta, status: 'submitted',
  }
  if (existing) {
    const { error } = await supabase.from('sd_logs').update(logRow).eq('id', existing.id)
    if (error) throw createError({ statusCode: 500, message: error.message })
  } else {
    const { error } = await supabase.from('sd_logs').insert(logRow)
    if (error) throw createError({ statusCode: 500, message: error.message })
  }

  // 更新兵員屬性與 XP
  const { error: e2 } = await supabase.from('sd_members').update({
    xp: newXp,
    attr_strength: newAttrs.strength, attr_endurance: newAttrs.endurance,
    attr_discipline: newAttrs.discipline, attr_bearing: newAttrs.bearing,
  }).eq('id', memberId)
  if (e2) throw createError({ statusCode: 500, message: e2.message })

  return {
    ok: true, updated: !!existing,
    xpAwarded: reward.xp, attrDelta: reward.attrDelta,
    xp: newXp, attrs: newAttrs,
  }
})
