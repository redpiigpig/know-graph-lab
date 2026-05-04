export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const body = await readBody<{ from?: string; to?: string; source?: string }>(event)
  const from = body?.from?.trim()
  const to = body?.to?.trim()
  const source = body?.source ?? 'all'

  if (!from) throw createError({ statusCode: 400, message: 'from required' })
  if (!to)   throw createError({ statusCode: 400, message: 'to required' })
  if (from === to) return { ok: true, updated: 0, note: 'identical title, no-op' }

  const tables = source === 'all'
    ? ['ai_dialogues_gemini', 'ai_dialogues_chatgpt']
    : [`ai_dialogues_${source}`]

  let total = 0
  for (const tableName of tables) {
    const { error, count } = await supabase
      .from(tableName)
      .update({ title: to }, { count: 'exact' })
      .eq('title', from)

    if (error) {
      if (/title.*does not exist/i.test(error.message)) continue
      throw createError({ statusCode: 500, message: error.message })
    }
    total += (count ?? 0)
  }

  return { ok: true, updated: total }
})
