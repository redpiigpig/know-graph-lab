export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const { name, color = 'slate', parent_id = null } = await readBody(event)

  if (!name?.trim()) throw createError({ statusCode: 400, message: 'name required' })

  const { data, error } = await supabase
    .from('ai_dialogue_categories')
    .insert({ name: name.trim(), color, parent_id: parent_id || null })
    .select()
    .single()

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data
})
