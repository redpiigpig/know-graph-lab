// 把本機 PDF 上傳到玄奘校網後台「臺灣佛教研究中心」的檔案庫（檔案庫管理的 Dropzone）。
//
// 上傳後的公開路徑是 /upload/userfiles/<rid>/files/<檔名>，與 43 期既有 PDF 同一個資料夾。
// 🚨 只上傳；不刪除、不覆寫既有檔（同名檔會先點名並跳過，要覆寫請人工確認）。
//
// 用法：node scripts/hcu_cms_upload_files.mjs <資料夾或檔案...> [--list]
//   --list 只列出檔案庫現有檔名，不上傳
import { readdirSync, statSync, existsSync, writeFileSync } from 'fs'
import { join } from 'path'
import { chromium } from 'playwright'

const OUT = 'c:/tmp/hcu-cms'
const STATE = `${OUT}/state.json`
const RID = '436650DB9FC648D783CDF0FEAACE0321'   // 臺灣佛教研究中心
if (!existsSync(STATE)) { console.error('先跑 hcu_cms_login.mjs'); process.exit(2) }

const listOnly = process.argv.includes('--list')
// --images：改用「圖片庫管理」（PictureEditor + api/ajax.ashx，公開路徑 …/Images/），
// 預設是「檔案庫管理」（FileEditor + api/ajax3.ashx，公開路徑 …/files/）
const IMAGES = process.argv.includes('--images')
const delIdx = process.argv.indexOf('--delete')   // --delete "<完整檔名>" …：只刪指定檔名（用於清掉自己傳錯的檔）
const targets = (delIdx > 0 || listOnly) ? [] : process.argv.slice(2).filter(a => !a.startsWith('--'))
const files = []
for (const t of targets) {
  const st = statSync(t)
  const want = IMAGES ? /\.(jpe?g|png|gif|webp)$/i : /\.pdf$/i
  if (st.isDirectory()) for (const f of readdirSync(t)) { if (want.test(f)) files.push(join(t, f)) }
  else files.push(t)
}

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: STATE, viewport: { width: 1440, height: 1000 } })
const page = await ctx.newPage()
const mngUrl = IMAGES
  ? 'https://www.hcu.edu.tw/backend/MngFiles/PictureEditor.aspx'
  : 'https://www.hcu.edu.tw/backend/MngFiles/FileEditor.aspx'
await page.goto(mngUrl, { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(3000)
if (/login\.aspx/i.test(page.url())) { console.log('❌ session 過期'); await browser.close(); process.exit(1) }

// 現有檔名（GetList 會把清單畫在 #content）
// 🚨 清單是 ajax 畫進 #content 的縮圖，檔名在 <p class="caption">，不是 <a href>。
//    用 a[href] 去撈會得到 0 個檔——而「0」看起來很像「檔案庫是空的」。
async function existing() {
  await page.waitForSelector('#content p.caption', { timeout: 20000 }).catch(() => {})
  const names = await page.$$eval('#content p.caption', ps => ps.map(p => p.textContent.trim()).filter(Boolean))
  if (!names.length) throw new Error('檔案庫清單抓到 0 個檔——先確認 #content 有沒有畫出來，別當成空的')
  return new Set(names)
}
let have = await existing()
console.log(`[檔案庫] 現有 ${have.size} 個檔（抓到的連結數）`)
if (listOnly) {
  ;[...have].sort().slice(0, 200).forEach(n => console.log('   ' + n))
  await browser.close(); process.exit(0)
}

// --delete：把指定檔名從檔案庫移除。🚨 只刪參數點名的檔；不做批次、不做模糊比對。
if (delIdx > 0) {
  const victims = process.argv.slice(delIdx + 1).filter(a => !a.startsWith('--'))
  page.on('dialog', d => d.accept())
  for (const name of victims) {
    if (!have.has(name)) { console.log(`  ⏭ 檔案庫沒有這個檔，跳過：${name}`); continue }
    const btn = page.locator('#content .thumbnail', { hasText: name }).locator('button', { hasText: '刪除' }).first()
    if (!(await btn.count())) { console.log(`  ❓ 找不到刪除鈕：${name}`); continue }
    await btn.click()
    await page.waitForTimeout(2500)
    have = await existing()
    console.log(`  ${have.has(name) ? '❌ 仍在' : '🗑 已刪'} ${name}`)
  }
  await browser.close(); process.exit(0)
}

const uploaded = []
for (const f of files) {
  const name = f.split(/[\\/]/).pop()
  if (have.has(name)) { console.log(`  ⏭ 已存在，跳過：${name}`); uploaded.push({ name, skipped: true }); continue }
  const input = page.locator('input.dz-hidden-input').first()
  await input.setInputFiles(f)
  // 等 Dropzone 的 XHR 打完
  await page.waitForTimeout(1200)
  await page.waitForLoadState('networkidle').catch(() => {})
  await page.waitForTimeout(800)
  have = await existing()
  const ok = have.has(name)
  console.log(`  ${ok ? '✔' : '❓'} ${name}  ${(statSync(f).size / 1048576).toFixed(1)} MB`)
  uploaded.push({ name, ok })
}

writeFileSync(`${OUT}/uploaded.json`, JSON.stringify(uploaded, null, 1), 'utf8')
console.log(`\n公開路徑前綴：/upload/userfiles/${RID}/files/`)
await page.screenshot({ path: `${OUT}/filelib-after.png`, fullPage: true })
await browser.close()
