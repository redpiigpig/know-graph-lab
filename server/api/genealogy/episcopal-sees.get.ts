export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { data, error } = await supabase
    .from('episcopal_sees')
    .select('id, see_zh, name_zh, name_en, church, tradition, rite, founded_year, abolished_year, status, current_patriarch, location, notes')
    .order('tradition',    { ascending: true, nullsFirst: true })
    .order('church',       { ascending: true })
    .order('founded_year', { ascending: true, nullsFirst: true })
    .order('name_zh',      { ascending: true })

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data ?? []
})
