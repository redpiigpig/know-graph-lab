export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const body = await readBody(event)

  const payload = {
    name_zh:           body.name_zh           || null,
    name_en:           body.name_en           || null,
    see:               body.see               || null,
    church:            body.church            || null,
    succession_number: body.succession_number != null ? Number(body.succession_number) : null,
    start_year:        body.start_year        != null ? Number(body.start_year)        : null,
    end_year:          body.end_year          != null ? Number(body.end_year)          : null,
    end_reason:        body.end_reason        || null,
    appointed_by:      body.appointed_by      || null,
    status:            body.status            || '正統',
    sources:           body.sources           || null,
    notes:             body.notes             || null,
  }

  if (!payload.name_zh) throw createError({ statusCode: 400, message: '中文名為必填' })
  if (!payload.see)     throw createError({ statusCode: 400, message: '主教座為必填' })

  const { data, error } = await supabase
    .from('episcopal_succession')
    .insert(payload)
    .select()
    .single()

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data
})
