export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const dialogue_id = getRouterParam(event, 'id')
  const category_id = getRouterParam(event, 'categoryId')
  const { source } = getQuery(event) as { source?: string }

  let query = supabase
    .from('ai_dialogue_entry_categories')
    .delete()
    .eq('dialogue_id', dialogue_id)
    .eq('category_id', category_id)

  if (source) {
    query = query.eq('source', source)
  }

  const { error } = await query
  if (error) throw createError({ statusCode: 500, message: error.message })
  return { ok: true }
})
