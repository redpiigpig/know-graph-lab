export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const body = await readBody(event)

  const payload = {
    name_zh:     body.name_zh     || null,
    name_en:     body.name_en     || null,
    gender:      body.gender      || null,
    nationality: body.nationality || null,
    generation:  body.generation  != null ? Number(body.generation)  : null,
    birth_year:  body.birth_year  != null ? Number(body.birth_year)  : null,
    death_year:  body.death_year  != null ? Number(body.death_year)  : null,
    child_year:  body.child_year  != null ? Number(body.child_year)  : null,
    age:         body.age         != null ? Number(body.age)         : null,
    spouse:      body.spouse      || null,
    children:    body.children    || null,
    sources:     body.sources     || null,
    notes:       body.notes       || null,
  }

  if (!payload.name_zh) throw createError({ statusCode: 400, message: '中文姓名為必填' })

  const { data, error } = await supabase
    .from('biblical_people')
    .insert(payload)
    .select()
    .single()

  if (error) throw createError({ statusCode: 500, message: error.message })
  return data
})
