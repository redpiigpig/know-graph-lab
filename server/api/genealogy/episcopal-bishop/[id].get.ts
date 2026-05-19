/**
 * GET /api/genealogy/episcopal-bishop/[id]
 *
 * Detail payload for one bishop (BishopCard modal on /genealogy/episcopal).
 * Returns the bishop row + see info + relationship data:
 *   - consecrator:    the bishop who consecrated this one (via consecrator_bishop_id)
 *   - consecrated:    bishops this one consecrated (reverse lookup)
 *   - teachers:       church_teachings rows where this bishop is the student
 *   - students:       church_teachings rows where this bishop is the teacher
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const id = getRouterParam(event, 'id')

  if (!id) throw createError({ statusCode: 400, message: 'id required' })

  const { data: bishop, error: bErr } = await supabase
    .from('episcopal_succession')
    .select('*')
    .eq('id', id)
    .single()
  if (bErr || !bishop) throw createError({ statusCode: 404, message: 'bishop not found' })

  // see info (tradition / church / spine color)
  const { data: see } = await supabase
    .from('episcopal_sees')
    .select('id, see_zh, name_zh, name_en, church, tradition, rite, founded_year, location, current_patriarch_zh, notes')
    .eq('see_zh', bishop.see)
    .in('church', [bishop.church, '未分裂教會'])
    .limit(1)
    .maybeSingle()

  // consecrator (跨教座按立鏈)
  let consecrator: any = null
  if (bishop.consecrator_bishop_id) {
    const { data } = await supabase
      .from('episcopal_succession')
      .select('id, name_zh, name_en, see, church, succession_number, start_year, end_year')
      .eq('id', bishop.consecrator_bishop_id)
      .maybeSingle()
    consecrator = data ?? null
  }

  // bishops this one has consecrated (reverse query)
  const { data: consecrated } = await supabase
    .from('episcopal_succession')
    .select('id, name_zh, name_en, see, church, succession_number, start_year, end_year')
    .eq('consecrator_bishop_id', id)
    .order('start_year', { ascending: true, nullsFirst: false })

  // church_teachings — this bishop as student (有沒有師父)
  const { data: teachers } = await supabase
    .from('church_teachings')
    .select('id, teacher_name_zh, teacher_name_en, period_year, relationship, source, notes, teacher_bishop_id')
    .eq('student_bishop_id', id)
    .order('period_year', { ascending: true, nullsFirst: false })

  // church_teachings — this bishop as teacher (有沒有學生 / 被教導)
  const { data: students } = await supabase
    .from('church_teachings')
    .select('id, student_name_zh, student_name_en, period_year, relationship, source, notes, student_bishop_id')
    .eq('teacher_bishop_id', id)
    .order('period_year', { ascending: true, nullsFirst: false })

  return {
    bishop,
    see,
    consecrator,
    consecrated: consecrated ?? [],
    teachers:    teachers    ?? [],
    students:    students    ?? [],
  }
})
