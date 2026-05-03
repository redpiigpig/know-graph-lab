import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const supabase = createClient(
    config.public.supabaseUrl,
    config.supabaseServiceRoleKey
  )
  const { data, error } = await supabase
    .from('pong_writings')
    .select('id, title, title_en, category, publication, published_date, date_approximate, source_url, cloudinary_urls, tags')
    .eq('is_published', true)
    .order('sort_order', { ascending: true })
  if (error) throw createError({ statusCode: 500, message: error.message })
  return data || []
})
