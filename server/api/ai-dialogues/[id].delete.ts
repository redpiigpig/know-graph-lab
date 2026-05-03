export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const id = getRouterParam(event, 'id')
  const { source = 'gemini' } = getQuery(event) as { source?: string }

  // If source is 'all', try both tables until one succeeds
  const tables = source === 'all' ? ['ai_dialogues_gemini', 'ai_dialogues_chatgpt'] : [`ai_dialogues_${source}`]

  let lastError: any = null
  for (const tableName of tables) {
    const { error } = await supabase.from(tableName).delete().eq('id', id)
    if (!error) return { ok: true }
    lastError = error
  }

  if (lastError) throw createError({ statusCode: 500, message: lastError.message })
  return { ok: true }
})
