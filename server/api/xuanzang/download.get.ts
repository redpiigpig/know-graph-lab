import { readFileSync } from 'fs'
import { join } from 'path'

const FILES: Record<string, string> = {
  submission: '英網-1 投稿指引(徵稿函).docx',
  editorial: '英網-2 編輯團隊資訊.docx',
  ethics: '英網-3 草擬學術倫理聲明260213.docx',
  review: '英網-4 期刊審查流程260213.docx',
}

export default defineEventHandler((event) => {
  const { file } = getQuery(event) as { file: string }
  const filename = FILES[file]
  if (!filename) throw createError({ statusCode: 404, message: 'File not found' })

  const filePath = join(process.cwd(), 'stores', '玄奘佛學研究', filename)
  const content = readFileSync(filePath)

  setHeader(event, 'Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
  setHeader(event, 'Content-Disposition', `attachment; filename*=UTF-8''${encodeURIComponent(filename)}`)

  return content
})
