/** 長官後台 — 新增兵員（手動建帳號，無開放註冊）。 */
import { sdSupabase, sdRequireChief } from '~/server/utils/soldierDiary'
import { ATTR_START } from '~/data/soldierDiaryConfig'

export default defineEventHandler(async (event) => {
  sdRequireChief(event)
  const { name, callsign, code, squad, note } = await readBody(event)

  const nm = String(name || '').trim()
  const cs = String(callsign || '').trim()
  const pw = String(code || '').trim()
  if (!nm || !cs || !pw)
    throw createError({ statusCode: 400, message: '姓名、代號、通行碼皆為必填' })
  if (cs === (process.env.SOLDIER_CHIEF_CALLSIGN || '教官'))
    throw createError({ statusCode: 400, message: '此代號保留給長官，請換一個' })

  const supabase = sdSupabase()
  const { data: existing } = await supabase
    .from('sd_members').select('id').eq('callsign', cs).maybeSingle()
  if (existing) throw createError({ statusCode: 409, message: '此代號已被使用' })

  const { data, error } = await supabase
    .from('sd_members')
    .insert({
      name: nm, callsign: cs, access_code: pw,
      squad: String(squad || '').trim(), note: String(note || '').trim(),
      attr_strength: ATTR_START, attr_endurance: ATTR_START,
      attr_discipline: ATTR_START, attr_bearing: ATTR_START,
    })
    .select('id')
    .single()

  if (error) throw createError({ statusCode: 500, message: error.message })
  return { ok: true, id: data.id }
})
