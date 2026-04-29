export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const { see, church } = getQuery(event) as { see?: string; church?: string }

  let q = supabase.from('episcopal_succession').select('*')
  if (see)    q = q.eq('see', see)
  if (church) q = q.eq('church', church)

  const { data, error } = await q
    .order('see',               { ascending: true })
    .order('church',            { ascending: true })
    .order('succession_number', { ascending: true, nullsFirst: false })
    .order('start_year',        { ascending: true, nullsFirst: false })

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data ?? []
})
