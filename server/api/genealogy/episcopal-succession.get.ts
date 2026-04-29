export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { data, error } = await supabase
    .from('episcopal_succession')
    .select('*')
    .order('see',               { ascending: true })
    .order('church',            { ascending: true })
    .order('succession_number', { ascending: true, nullsFirst: false })
    .order('start_year',        { ascending: true, nullsFirst: false })

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data ?? []
})
