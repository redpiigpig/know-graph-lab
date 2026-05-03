import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async (event) => {
  const { email, password } = await readBody(event)

  if (!email || !password)
    throw createError({ statusCode: 400, message: '請輸入帳號密碼' })

  const normalizedEmail = email.trim().toLowerCase()

  // Chief editor check
  const chiefEmail = (process.env.PONG_CHIEF_EMAIL || '').toLowerCase()
  const chiefPassword = process.env.PONG_CHIEF_PASSWORD || ''

  if (normalizedEmail === chiefEmail && password === chiefPassword) {
    return { id: 0, name: '總編輯', email: chiefEmail, role: 'chief' }
  }

  // Editor check — fixed code
  const editorCode = process.env.PONG_EDITOR_CODE || ''
  if (password !== editorCode)
    throw createError({ statusCode: 401, message: '帳號或密碼錯誤' })

  const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
  )

  const { data, error } = await supabase
    .from('pong_editors')
    .select('id, name, email, status, role')
    .eq('email', normalizedEmail)
    .single()

  if (error || !data)
    throw createError({ statusCode: 401, message: '帳號或密碼錯誤' })

  if (data.status === 'pending')
    throw createError({ statusCode: 403, message: '帳號尚待審核，請等候總編輯核准後再登入' })

  if (data.status === 'rejected')
    throw createError({ statusCode: 403, message: '申請未獲批准，如有疑問請聯絡主辦單位' })

  await supabase
    .from('pong_editors')
    .update({ last_login: new Date().toISOString() })
    .eq('id', data.id)

  return { id: data.id, name: data.name, email: data.email, role: data.role || 'editor' }
})
