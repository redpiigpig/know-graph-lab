export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { data, error } = await supabase
    .from('biblical_people')
    .select('*')
    .order('sort_order', { ascending: true, nullsFirst: false })

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data ?? []
})
