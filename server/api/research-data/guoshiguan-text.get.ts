import { requireAdmin } from '~/server/utils/auth-helper'

// 國史館兩份「勿外傳」檔案的全文。
//
// 🚨 **這批全文絕不可進 git**。repo 是公開的（github.com/redpiigpig/know-graph-lab，
//    visibility=public），把 12 萬字放進 public/content/ 就等於公開流傳——正是
//    取得者要求避免的事，而且 git 歷史留著、事後刪不掉。
//    所以全文放 R2（research-private/），repo 只留書目層，由這支端點供應。
//
// 🚨 端點一定要 requireAdmin。2026-09-02 之前 research-data 的九支 API 全都沒有
//    驗證，未登入直接打就回 200 連同全文——「網站有密碼」在 API 這一層是假的。
const KEY = 'research-private/guoshiguan/docs.jsonl.gz'

interface GsgDoc {
  title: string
  fonds: string
  archiveNo: string
  dateRange: string
  declassified: string
  note: string
  lines: number
  chars: number
  text: string
}

let cache: GsgDoc[] | null = null

export default defineEventHandler(async (event) => {
  await requireAdmin(event)

  if (!cache) {
    const body = await r2Text(KEY)
    if (body === null) return { available: false, docs: [] }
    cache = parseJsonl<GsgDoc>(body)
  }

  const q = getQuery(event)
  const no = String(q.archiveNo ?? '')
  if (!no) {
    // 不帶檔號就只回書目，不吐全文
    return {
      available: true,
      docs: cache.map(({ text, ...meta }) => meta),
    }
  }
  const doc = cache.find((d) => d.archiveNo === no)
  return doc ? { available: true, doc } : { available: false }
})
