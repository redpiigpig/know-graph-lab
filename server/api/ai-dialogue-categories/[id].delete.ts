export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const id = getRouterParam(event, 'id')

  const { error } = await supabase.from('ai_dialogue_categories').delete().eq('id', id)
  if (error) throw createError({ statusCode: 500, message: error.message })
  return { ok: true }
})
