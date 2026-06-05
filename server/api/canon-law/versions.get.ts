// GET /api/canon-law/versions — all canon_law_versions + per-version section count.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { data: versions, error } = await supabase
    .from('canon_law_versions')
    .select('*')
    .order('display_order', { ascending: true })
  if (error) throw createError({ statusCode: 500, message: error.message })

  // Page through sections (PostgREST caps at 1000 rows / db-max-rows) to tally.
  const tally: Record<string, number> = {}
  const PAGE = 1000
  for (let from = 0; ; from += PAGE) {
    const { data, error: cErr } = await supabase
      .from('canon_law_sections')
      .select('version_code')
      .range(from, from + PAGE - 1)
    if (cErr) throw createError({ statusCode: 500, message: cErr.message })
    for (const r of (data ?? []) as { version_code: string }[]) {
      tally[r.version_code] = (tally[r.version_code] ?? 0) + 1
    }
    if (!data || data.length < PAGE) break
  }

  return (versions ?? []).map((v: any) => ({ ...v, section_count: tally[v.code] ?? 0 }))
})
