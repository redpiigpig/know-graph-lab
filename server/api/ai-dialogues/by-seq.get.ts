// Look up a single dialogue by its citation number (seq_label), e.g. C-01234 / G-00789.
// Lets readers trace a citation in the 創生哲學 books back to the original dialogue.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const { seq } = getQuery(event) as { seq?: string }
  const label = (seq ?? '').trim().toUpperCase()
  if (!/^[CG]-\d{1,6}$/.test(label)) {
    throw createError({ statusCode: 400, message: '編號格式須為 C-12345 或 G-00789' })
  }
  const table = label.startsWith('C') ? 'ai_dialogues_chatgpt' : 'ai_dialogues_gemini'
  const source = label.startsWith('C') ? 'chatgpt' : 'gemini'
  const { data, error } = await supabase
    .from(table)
    .select('id, seq_label, dialogue_date, dialogue_time, title, prompt, response')
    .eq('seq_label', label)
    .maybeSingle()
  if (error) throw createError({ statusCode: 500, message: error.message })
  if (!data) throw createError({ statusCode: 404, message: `找不到對話 ${label}` })
  return { ...data, source }
})
