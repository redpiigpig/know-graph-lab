export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { title, source = 'all' } = getQuery(event) as {
    title?: string
    source?: string
  }

  if (!title) {
    throw createError({ statusCode: 400, message: 'title query param required' })
  }

  const tables = source === 'all'
    ? ['ai_dialogues_gemini', 'ai_dialogues_chatgpt']
    : [`ai_dialogues_${source}`]

  let totalDeleted = 0
  for (const tableName of tables) {
    const { error, count } = await supabase
      .from(tableName)
      .delete({ count: 'exact' })
      .eq('title', title)

    if (error) {
      // some tables may not have the title column yet (gemini before migration); skip cleanly
      if (/title.*does not exist/i.test(error.message)) continue
      throw createError({ statusCode: 500, message: error.message })
    }
    totalDeleted += (count ?? 0)
  }

  return { ok: true, deleted: totalDeleted }
})
