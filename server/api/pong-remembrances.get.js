import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const supabase = createClient(
    config.public.supabaseUrl,
    config.supabaseServiceRoleKey
  )
  const { data, error } = await supabase
    .from('pong_remembrance')
    .select('id, title, author, source, source_url, published_at, category, summary, content')
    .eq('is_published', true)
    .order('sort_order', { ascending: true })
  if (error) throw createError({ statusCode: 500, message: error.message })
  return data || []
})
