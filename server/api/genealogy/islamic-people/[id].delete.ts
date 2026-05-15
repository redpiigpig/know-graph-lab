export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const id = getRouterParam(event, 'id')

  const { error } = await supabase
    .from('islamic_people')
    .delete()
    .eq('id', id)

  if (error) throw createError({ statusCode: 500, message: error.message })
  return { ok: true }
})
