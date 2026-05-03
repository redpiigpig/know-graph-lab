import { createClient } from '@supabase/supabase-js'
import { Resend } from 'resend'

export default defineEventHandler(async (event) => {
  const { name, gender, age_group, email, church, how_knew, how_to_help } = await readBody(event)

  if (!name?.trim() || !email?.trim())
    throw createError({ statusCode: 400, message: '姓名和 Email 為必填' })

  const normalizedEmail = email.trim().toLowerCase()
  const chiefEmail = (process.env.PONG_CHIEF_EMAIL || '').toLowerCase()

  if (normalizedEmail === chiefEmail)
    throw createError({ statusCode: 400, message: '此 Email 無法使用' })

  const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
  )

  const { data: existing } = await supabase
    .from('pong_editors')
    .select('id, status')
    .eq('email', normalizedEmail)
    .single()

  if (existing) {
    if (existing.status === 'pending')
      throw createError({ statusCode: 409, message: '此 Email 已提交申請，請等候審核' })
    if (existing.status === 'approved')
      throw createError({ statusCode: 409, message: '此 Email 已是審核通過的校對者' })
    if (existing.status === 'rejected')
      throw createError({ statusCode: 409, message: '此 Email 的申請未獲批准，如有疑問請聯絡主辦單位' })
  }

  const { data, error } = await supabase
    .from('pong_editors')
    .insert({ name: name.trim(), gender, age_group, email: normalizedEmail, church, how_knew, how_to_help })
    .select('id')
    .single()

  if (error) throw createError({ statusCode: 500, message: error.message })

  // Notify admin via Resend (graceful failure if RESEND_API_KEY / chief email not set)
  if (process.env.RESEND_API_KEY && chiefEmail) {
    try {
      const resend = new Resend(process.env.RESEND_API_KEY)
      await resend.emails.send({
        from: '龐君華會督數位典藏 <onboarding@resend.dev>',
        to: chiefEmail,
        subject: `【新申請】${name.trim()} 申請加入龐君華數位典藏校對團隊`,
        html: `
          <h2 style="font-family:sans-serif;color:#3A3025">新校對者申請通知</h2>
          <table style="border-collapse:collapse;width:100%;max-width:600px;font-family:sans-serif;font-size:14px">
            <tr><td style="padding:8px 12px;background:#f5f0e8;border:1px solid #ddd;width:140px"><b>姓名</b></td><td style="padding:8px 12px;border:1px solid #ddd">${name.trim()}</td></tr>
            <tr><td style="padding:8px 12px;background:#f5f0e8;border:1px solid #ddd"><b>性別</b></td><td style="padding:8px 12px;border:1px solid #ddd">${gender || '—'}</td></tr>
            <tr><td style="padding:8px 12px;background:#f5f0e8;border:1px solid #ddd"><b>年齡層</b></td><td style="padding:8px 12px;border:1px solid #ddd">${age_group || '—'}</td></tr>
            <tr><td style="padding:8px 12px;background:#f5f0e8;border:1px solid #ddd"><b>Email</b></td><td style="padding:8px 12px;border:1px solid #ddd">${normalizedEmail}</td></tr>
            <tr><td style="padding:8px 12px;background:#f5f0e8;border:1px solid #ddd"><b>所屬教會</b></td><td style="padding:8px 12px;border:1px solid #ddd">${church || '—'}</td></tr>
            <tr><td style="padding:8px 12px;background:#f5f0e8;border:1px solid #ddd"><b>認識龐牧師的經過</b></td><td style="padding:8px 12px;border:1px solid #ddd">${how_knew || '—'}</td></tr>
            <tr><td style="padding:8px 12px;background:#f5f0e8;border:1px solid #ddd"><b>希望協助的地方</b></td><td style="padding:8px 12px;border:1px solid #ddd">${how_to_help || '—'}</td></tr>
          </table>
          <p style="font-family:sans-serif;font-size:13px;color:#666;margin-top:20px">請登入龐君華數位典藏，在 header 的「校對者管理」中核准或拒絕此申請。</p>
        `,
      })
    } catch (emailErr) {
      console.error('[pong-register] email error:', emailErr.message)
    }
  }

  return { ok: true, id: data.id }
})
