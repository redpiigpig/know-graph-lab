export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const dialogue_id = getRouterParam(event, 'id')
  const { category_id, source } = await readBody(event) as { category_id: string, source?: string }

  // Store source info if provided, otherwise use composite key
  const entry: any = { dialogue_id, category_id }
  if (source) {
    entry.source = source
  }

  const { error } = await supabase
    .from('ai_dialogue_entry_categories')
    .upsert(entry, source ? { onConflict: 'dialogue_id,source,category_id' } : { onConflict: 'dialogue_id,category_id' })

  if (error) throw createError({ statusCode: 500, message: error.message })
  return { ok: true }
})
