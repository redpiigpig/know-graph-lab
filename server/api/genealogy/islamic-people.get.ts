export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { data, error } = await supabase
    .from('islamic_people')
    .select('*')
    .order('generation', { ascending: true, nullsFirst: false })
    .order('sort_order', { ascending: true, nullsFirst: false })

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data ?? []
})
