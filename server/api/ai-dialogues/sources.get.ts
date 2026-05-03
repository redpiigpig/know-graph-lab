export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const [{ count: gCount }, { count: cCount }] = await Promise.all([
    supabase.from('ai_dialogues_gemini').select('id', { count: 'exact', head: true }),
    supabase.from('ai_dialogues_chatgpt').select('id', { count: 'exact', head: true }),
  ])

  return {
    gemini: gCount ?? 0,
    chatgpt: cCount ?? 0,
    all: (gCount ?? 0) + (cCount ?? 0),
  }
})
