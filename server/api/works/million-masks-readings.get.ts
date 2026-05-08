export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const url = config.public.supabaseUrl
  const key = config.supabaseServiceRoleKey

  const resp = await $fetch<{ id: string; episode: number; title: string; video_date: string | null }[]>(
    `${url}/rest/v1/video_transcripts?project_slug=eq.million-masks&select=id,episode,title,video_date&order=episode.asc`,
    { headers: { apikey: key, Authorization: `Bearer ${key}` } }
  ).catch(() => [])

  const sessions = (resp as any[]).map((r) => ({
    id: r.id,
    episode: r.episode,
    title: r.title,
    date: r.video_date ?? null,
  }))

  return { sessions }
})
