/**
 * 教官登入（Email OTP）— 前端已用 Supabase Email 驗證碼登入，帶 Supabase access token 過來；
 * 後端驗證該使用者 email 是否為教官信箱，是則換發長效教官 token。
 */
import { createClient } from '@supabase/supabase-js'
import { sdSignToken, SD_CHIEF_CALLSIGN } from '~/server/utils/soldierDiary'

export default defineEventHandler(async (event) => {
  const token = getHeader(event, 'authorization')?.replace('Bearer ', '')
  if (!token) throw createError({ statusCode: 401, message: '缺少登入憑證' })

  const config = useRuntimeConfig()
  const userClient = createClient(config.public.supabaseUrl, config.public.supabaseKey, {
    global: { headers: { Authorization: `Bearer ${token}` } },
    auth: { persistSession: false },
  })

  const { data: { user }, error } = await userClient.auth.getUser()
  if (error || !user) throw createError({ statusCode: 401, message: '登入憑證無效或已過期' })

  const chiefEmail = (process.env.SOLDIER_CHIEF_EMAIL || 'redpiigpig@gmail.com').toLowerCase()
  if ((user.email || '').toLowerCase() !== chiefEmail)
    throw createError({ statusCode: 403, message: '此 Email 非教官帳號' })

  const callsign = process.env.SOLDIER_CHIEF_CALLSIGN || SD_CHIEF_CALLSIGN
  const auth = { id: 0, role: 'chief' as const, callsign, name: '教官' }
  return { token: sdSignToken(auth), ...auth }
})
