import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const config = useRuntimeConfig()
  const supabase = createClient(
    config.public.supabaseUrl,
    config.supabaseServiceRoleKey
  )
  const { data, error } = await supabase
    .from('pong_remembrance')
    .select('*')
    .eq('id', id)
    .eq('is_published', true)
    .single()
  if (error) throw createError({ statusCode: 404, message: '找不到此文章' })
  return data
})
