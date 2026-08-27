import { r2SignedUrl } from '~/server/utils/r2'
import { sdRequireAuth } from '~/server/utils/soldierDiary'

const RULES_KEY = 'soldier-diary/basic-rules/禮兵調教守則(2024.12.30).docx'

export default defineEventHandler(async (event) => {
  sdRequireAuth(event)
  const url = await r2SignedUrl(RULES_KEY, 300)
  return { url }
})
