import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async () => {
  const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
  )

  const { data, error } = await supabase
    .from('pong_editors')
    .select('id, name, gender, age_group, email, church, how_knew, how_to_help, role, status, applied_at, approved_at, approved_by, last_login')
    .order('applied_at', { ascending: false })

  if (error) throw createError({ statusCode: 500, message: error.message })

  return data
})
