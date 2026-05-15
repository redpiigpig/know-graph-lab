export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const id = getRouterParam(event, 'id')
  const body = await readBody(event)

  const allowed = [
    'name_zh', 'name_ar', 'name_en', 'kunya',
    'gender', 'nationality',
    'generation', 'sort_order',
    'birth_year', 'death_year', 'child_year', 'age',
    'spouse', 'children', 'sources', 'notes',
    'tradition',
    'tradition_children', 'tradition_spouse', 'tradition_hide_children',
  ]
  const ALLOWED_TRADITIONS = new Set([
    'quranic', 'sunni', 'shia_twelver', 'shia_ismaili', 'shia_zaidi', 'sufi', 'historical',
  ])

  const patch: Record<string, any> = {}
  for (const key of allowed) {
    if (key in body) {
      const val = body[key]
      patch[key] = (val === '' || val === undefined) ? null : val
    }
  }

  if ('tradition' in patch && patch.tradition && !ALLOWED_TRADITIONS.has(patch.tradition)) {
    throw createError({ statusCode: 400, message: `tradition 必為以下之一：${[...ALLOWED_TRADITIONS].join(', ')}` })
  }

  const { data, error } = await supabase
    .from('islamic_people')
    .update(patch)
    .eq('id', id)
    .select()
    .single()

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data
})
