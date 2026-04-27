import { readFileSync } from 'fs'
import { join } from 'path'

export default defineEventHandler((event) => {
  const filePath = join(process.cwd(), 'stores', '玄奘佛學研究', 'footer_logo.jpg')
  const content = readFileSync(filePath)
  setHeader(event, 'Content-Type', 'image/jpeg')
  setHeader(event, 'Cache-Control', 'public, max-age=86400')
  return content
})
