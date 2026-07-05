/**
 * 提交／更新當日日記 — 兵員（chief 可代填，帶 memberId）。
 * 只能操練「當前軍種」的項目（一一突破）；計算 XP 與品質成長套到兵員身上。
 * 每日一篇；重送當日則以差額回滾更新。
 */
import { sdSupabase, sdRequireAuth } from '~/server/utils/soldierDiary'
import {
  computeLogRewards, applyQualityDelta, activeBranch, trainingItemMap,
  type DiaryPayload, type QualityKey,
} from '~/data/soldierDiaryConfig'
import { tzToday } from '~/server/utils/today'

export default defineEventHandler(async (event) => {
  const auth = sdRequireAuth(event)
  const body = await readBody(event)

  const memberId = auth.role === 'chief' && body?.memberId ? Number(body.memberId) : auth.id
  if (!memberId) throw createError({ statusCode: 400, message: '缺少兵員 id' })

  const supabase = sdSupabase()
  const { data: m, error: e0 } = await supabase
    .from('sd_members')
    .select('id, xp, q_obedience, q_strength, q_endurance, q_composure, q_challenge, status')
    .eq('id', memberId).maybeSingle()
  if (e0) throw createError({ statusCode: 500, message: e0.message })
  if (!m) throw createError({ statusCode: 404, message: '查無此兵員' })
  if (m.status === 'discharged')
    throw createError({ statusCode: 403, message: '此帳號已退伍停用' })

  let curQ: Record<QualityKey, number> = {
    obedience: m.q_obedience, strength: m.q_strength, endurance: m.q_endurance,
    composure: m.q_composure, challenge: m.q_challenge,
  }

  // 一一突破：操練項目必須屬於當前軍種（全破後才自由操練）
  const active = activeBranch(curQ)
  const rawItems = Array.isArray(body?.trainingItems) ? body.trainingItems.map(String) : []
  const items = active
    ? rawItems.filter((k) => trainingItemMap[k]?.branchKey === active.key)
    : rawItems.filter((k) => !!trainingItemMap[k])

  const payload: DiaryPayload = {
    trainingItems: items,
    durationMin: Math.max(0, Math.min(600, Number(body?.durationMin) || 0)),
    missions: Array.isArray(body?.missions) ? body.missions.map(String) : [],
    note: String(body?.note || '').slice(0, 500),
  }
  const selfScore = Math.max(0, Math.min(5, Math.floor(Number(body?.selfScore) || 0)))

  if (payload.trainingItems.length === 0 && payload.missions.length === 0)
    throw createError({ statusCode: 400, message: '至少要記錄一項當前軍種的操練或一項任務' })

  const logDate = /^\d{4}-\d{2}-\d{2}$/.test(body?.logDate) ? body.logDate : tzToday()
  const type = active ? active.key : 'graduate'
  const reward = computeLogRewards(payload, selfScore)

  const { data: existing } = await supabase
    .from('sd_logs')
    .select('id, xp_awarded, attr_delta')
    .eq('member_id', memberId).eq('log_date', logDate)
    .maybeSingle()

  let curXp = m.xp
  if (existing) {
    const oldDelta = (existing.attr_delta || {}) as Record<string, number>
    const negated: Record<string, number> = {}
    for (const k of Object.keys(oldDelta)) negated[k] = -(oldDelta[k] || 0)
    curQ = applyQualityDelta(curQ, negated as any)
    curXp = Math.max(0, curXp - (existing.xp_awarded || 0))
  }

  const newQ = applyQualityDelta(curQ, reward.qualityDelta)
  const newXp = curXp + reward.xp

  const logRow = {
    member_id: memberId, log_date: logDate, type,
    payload, self_score: selfScore,
    xp_awarded: reward.xp, attr_delta: reward.qualityDelta, status: 'submitted',
  }
  if (existing) {
    const { error } = await supabase.from('sd_logs').update(logRow).eq('id', existing.id)
    if (error) throw createError({ statusCode: 500, message: error.message })
  } else {
    const { error } = await supabase.from('sd_logs').insert(logRow)
    if (error) throw createError({ statusCode: 500, message: error.message })
  }

  const { error: e2 } = await supabase.from('sd_members').update({
    xp: newXp,
    q_obedience: newQ.obedience, q_strength: newQ.strength, q_endurance: newQ.endurance,
    q_composure: newQ.composure, q_challenge: newQ.challenge,
  }).eq('id', memberId)
  if (e2) throw createError({ statusCode: 500, message: e2.message })

  const nowActive = activeBranch(newQ)
  const conquered = active && (!nowActive || nowActive.key !== active.key) ? active.name : null

  return {
    ok: true, updated: !!existing,
    xpAwarded: reward.xp, qualityDelta: reward.qualityDelta,
    xp: newXp, qualities: newQ,
    conqueredBranch: conquered, // 本次是否突破了軍種
    graduated: !nowActive,
  }
})
