export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { data, error } = await supabase
    .from('ai_dialogue_categories')
    .select('*')
    .order('created_at')

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data ?? []
})
