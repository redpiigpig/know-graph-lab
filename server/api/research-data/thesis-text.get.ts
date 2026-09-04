import { requireAdmin } from '~/server/utils/auth-helper'

// 各校機構典藏下載的學位論文全文，逐頁一列。
//
// 🚨 全文不進 repo：repo 是公開的，把他人的學位論文全文放 public/content/
//    等於公開重製，而且 git 歷史刪不掉。全文放 R2 private，這支端點驗證後供應。
// 🚨 一定要 requireAdmin——「網站有密碼」在 API 這一層不會自動成立。
const PREFIX = 'research-private/theses'

interface Page {
  page: number
  text: string
}

const cache = new Map<string, Page[]>()

export default defineEventHandler(async (event) => {
  await requireAdmin(event)

  const id = String(getQuery(event).id ?? '')
  // 這個 id 是 sha1 前 16 碼，正常只會是十六進位；擋掉別的形狀免得被拿去拼路徑
  if (!/^[0-9a-f]{16}$/.test(id)) {
    throw createError({ statusCode: 400, message: 'bad id' })
  }

  if (!cache.has(id)) {
    const body = await r2Text(`${PREFIX}/${id}.jsonl.gz`)
    if (body === null) return { available: false, pages: [] }
    cache.set(id, parseJsonl<Page>(body))
  }
  return { available: true, pages: cache.get(id) }
})
