// GET /api/gnostic/versions — all gnostic_versions + per-version section count.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { data: versions, error } = await supabase
    .from('gnostic_versions')
    .select('*')
    .order('display_order', { ascending: true })
  if (error) throw createError({ statusCode: 500, message: error.message })

  const { data: counts, error: cErr } = await supabase
    .from('gnostic_sections')
    .select('version_code')
  if (cErr) throw createError({ statusCode: 500, message: cErr.message })

  const tally: Record<string, number> = {}
  for (const r of (counts ?? []) as { version_code: string }[]) {
    tally[r.version_code] = (tally[r.version_code] ?? 0) + 1
  }

  return (versions ?? []).map((v: any) => ({ ...v, section_count: tally[v.code] ?? 0 }))
})
