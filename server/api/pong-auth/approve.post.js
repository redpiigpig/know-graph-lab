import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async (event) => {
  const { id, action, approver } = await readBody(event)

  if (!id || !['approve', 'reject'].includes(action))
    throw createError({ statusCode: 400, message: 'Invalid params' })

  const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
  )

  const { error } = await supabase
    .from('pong_editors')
    .update({
      status: action === 'approve' ? 'approved' : 'rejected',
      approved_at: new Date().toISOString(),
      approved_by: approver || '總編輯',
    })
    .eq('id', id)

  if (error) throw createError({ statusCode: 500, message: error.message })

  return { ok: true }
})
