export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const id = getRouterParam(event, 'id')
  const body = await readBody(event)

  const allowed = ['name_zh','name_en','gender','nationality','generation','birth_year','death_year','child_year','age','spouse','children','sources','notes']
  const patch: Record<string, any> = {}
  for (const key of allowed) {
    if (key in body) {
      const val = body[key]
      patch[key] = (val === '' || val === undefined) ? null : val
    }
  }

  const { data, error } = await supabase
    .from('biblical_people')
    .update(patch)
    .eq('id', id)
    .select()
    .single()

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data
})
