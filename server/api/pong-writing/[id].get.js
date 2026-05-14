import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const config = useRuntimeConfig()
  const supabase = createClient(config.public.supabaseUrl, config.supabaseServiceRoleKey)

  const { data, error } = await supabase
    .from('pong_writings')
    .select('id, title, title_en, category, publication, published_date, date_approximate, source_url, cloudinary_urls, tags, content, editor, colophon, page_range, author')
    .eq('id', id)
    .eq('is_published', true)
    .single()

  if (error || !data) throw createError({ statusCode: 404, message: '找不到此篇文章' })
  return data
})
