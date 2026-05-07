export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const config = useRuntimeConfig()
  const url = config.public.supabaseUrl
  const key = config.supabaseServiceRoleKey

  const rows = await $fetch<{ content: string; title: string; episode: number; video_date: string | null; youtube_id: string | null; ppt_r2_key: string | null }[]>(
    `${url}/rest/v1/video_transcripts?id=eq.${id}&select=content,title,episode,video_date,youtube_id,ppt_r2_key&limit=1`,
    { headers: { apikey: key, Authorization: `Bearer ${key}` } }
  ).catch(() => [])

  if (!(rows as any[]).length) {
    throw createError({ statusCode: 404, message: 'Transcript not found' })
  }
  return (rows as any[])[0]
})
