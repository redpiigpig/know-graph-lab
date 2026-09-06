import { requireAdmin } from '~/server/utils/auth-helper'

// 一貫道研究資料（書目、清單、年表、研究報告、每月進度）。
//
// 🚨 **這批不進 git**。repo 是公開的（github.com/redpiigpig/know-graph-lab，
//    visibility=public），而這些檔案帶著檔案局目錄裡的人名，還加上「此人被列管
//    21 年」這類分析。書目在檔案局網站上本來就查得到，但把分析放進公開 repo
//    是另一回事——2026-09-06 使用者定調搬 R2、加這支需登入的端點。
//    本機那份留著（.gitignore 擋住），上傳走 scripts/yiguandao_r2_sync.py。
//
// 🚨 端點一定要 requireAdmin。2026-09-02 之前 research-data 的九支 API 全都沒有
//    驗證，未登入直接打就回 200 連同全文——「網站有密碼」在 API 這一層是假的。
const PREFIX = 'research-private/yiguandao/'

// 白名單，與 yiguandao_r2_sync.py 的 FILES 必須一致。不接受任意 key：
// 這支端點通往 research-private/，一個沒擋住的 `..` 就等於整個私有區外洩。
const ALLOWED = new Set([
  'archives-index.json',
  'biblio-zhong.json',
  'guoshiguan.json',
  'inventory.json',
  'timeline.json',
  'report.md',
  'progress/2026-09.md',
])

export default defineEventHandler(async (event) => {
  await requireAdmin(event)

  const name = String(getQuery(event).name ?? '')
  if (!ALLOWED.has(name)) {
    throw createError({ statusCode: 400, message: 'invalid name' })
  }

  const body = await r2Text(`${PREFIX}${name}`)
  if (body === null) return { available: false }

  // .json 直接回物件、.md 回字串，呼叫端不必再判型別。
  // 🚨 壞掉的 JSON 要回 available:false，不要讓例外變成 500——頁面拿到 500 會
  //    整批 catch 掉，六個分頁一起變空白，看不出是哪一份出問題。
  if (name.endsWith('.json')) {
    try {
      return { available: true, name, data: JSON.parse(body) as unknown }
    } catch {
      return { available: false, name, error: 'malformed json' }
    }
  }
  return { available: true, name, data: body }
})
