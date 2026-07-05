/**
 * 登入 — 長官（教官）用固定代號＋密碼；兵員用代號＋通行碼。
 * 回傳無狀態 token（前端存 localStorage，之後帶 Authorization: Bearer）。
 */
import { sdSupabase, sdSignToken, SD_CHIEF_CALLSIGN } from '~/server/utils/soldierDiary'

export default defineEventHandler(async (event) => {
  const { callsign, code } = await readBody(event)
  const cs = String(callsign || '').trim()
  const pw = String(code || '')

  if (!cs || !pw) throw createError({ statusCode: 400, message: '請輸入代號與通行碼' })

  // 長官
  const chiefCallsign = process.env.SOLDIER_CHIEF_CALLSIGN || SD_CHIEF_CALLSIGN
  const chiefCode = process.env.SOLDIER_CHIEF_CODE || ''
  if (cs === chiefCallsign) {
    if (chiefCode && pw === chiefCode) {
      const auth = { id: 0, role: 'chief' as const, callsign: chiefCallsign, name: '教官' }
      return { token: sdSignToken(auth), ...auth }
    }
    throw createError({ statusCode: 401, message: '代號或通行碼錯誤' })
  }

  // 兵員
  const supabase = sdSupabase()
  const { data, error } = await supabase
    .from('sd_members')
    .select('id, name, callsign, access_code, status')
    .eq('callsign', cs)
    .maybeSingle()

  if (error) throw createError({ statusCode: 500, message: error.message })
  if (!data || data.access_code !== pw)
    throw createError({ statusCode: 401, message: '代號或通行碼錯誤' })
  if (data.status === 'discharged')
    throw createError({ statusCode: 403, message: '此帳號已退伍停用' })

  await supabase
    .from('sd_members')
    .update({ last_login: new Date().toISOString() })
    .eq('id', data.id)

  const auth = { id: data.id, role: 'recruit' as const, callsign: data.callsign, name: data.name }
  return { token: sdSignToken(auth), ...auth }
})
