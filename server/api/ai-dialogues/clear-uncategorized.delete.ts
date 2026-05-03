export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const { source = 'gemini' } = getQuery(event) as { source?: string }

  // Get IDs that have at least one category
  const { data: catIds } = await supabase
    .from('ai_dialogue_entry_categories')
    .select('dialogue_id')

  const assigned = [...new Set((catIds ?? []).map((r: any) => r.dialogue_id))]

  // Determine which tables to clear from
  const tables = source === 'all' ? ['ai_dialogues_gemini', 'ai_dialogues_chatgpt'] : [`ai_dialogues_${source}`]

  let totalDeleted = 0
  for (const tableName of tables) {
    let query = supabase.from(tableName).delete()
    if (assigned.length > 0) {
      query = query.not('id', 'in', `(${assigned.join(',')})`)
    }

    const { error, count } = await query.select('id', { count: 'exact', head: true })
    if (error) throw createError({ statusCode: 500, message: error.message })

    totalDeleted += (count ?? 0)
  }

  return { ok: true, deleted: totalDeleted }
})
