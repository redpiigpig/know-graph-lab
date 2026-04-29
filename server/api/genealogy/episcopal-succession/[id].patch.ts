export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const id = getRouterParam(event, 'id')
  const body = await readBody(event)

  const allowed = ['name_zh','name_en','see','church','succession_number','start_year','end_year','end_reason','appointed_by','status','sources','notes']
  const patch: Record<string, any> = {}
  for (const key of allowed) {
    if (key in body) {
      const val = body[key]
      patch[key] = (val === '' || val === undefined) ? null : val
    }
  }

  const { data, error } = await supabase
    .from('episcopal_succession')
    .update(patch)
    .eq('id', id)
    .select()
    .single()

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data
})
