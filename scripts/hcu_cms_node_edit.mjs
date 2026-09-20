// 讀／改節點設定（右鍵選單的「編輯」＝ NodeEditor.aspx，要從樹上點開才不會被踢回）。
//
// 🚨 預設只讀（--dump）。要改才給 --set 欄位=值，而且一次只動點名的欄位。
//
// 用法：
//   node scripts/hcu_cms_node_edit.mjs --node <節點標題> --dump
//   node scripts/hcu_cms_node_edit.mjs --node <節點標題> --set ListTemplate=
import { existsSync } from 'fs'
import { chromium } from 'playwright'

const OUT = 'c:/tmp/hcu-cms'
if (!existsSync(`${OUT}/state.json`)) { console.error('先跑 hcu_cms_login.mjs'); process.exit(2) }
function arg(n, d = null) { const i = process.argv.indexOf(`--${n}`); return i > 0 ? process.argv[i + 1] : d }
const TITLE = arg('node')
const SETS = process.argv.reduce((acc, a, i, arr) => {
  if (a === '--set') acc.push(arr[i + 1] ?? '')
  return acc
}, []).map(s => { const j = s.indexOf('='); return [s.slice(0, j), s.slice(j + 1)] })
if (!TITLE) { console.error('要 --node <節點標題>'); process.exit(2) }

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: `${OUT}/state.json`, viewport: { width: 1440, height: 1000 } })
const page = await ctx.newPage()
const dialogs = []
page.on('dialog', async d => { dialogs.push(d.message()); await d.accept() })
await page.goto('https://www.hcu.edu.tw/backend/MngCms/NodeList.aspx', { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(4000)

// 展開樹找節點（點 <ins> 展開，不點 <a>——<a> 會導覽走）
let node = null
for (let round = 0; round < 12 && !node; round++) {
  const a = page.locator(`#ctl00_cpContent_tree a:has-text("${TITLE}")`).first()
  if (await a.count()) { node = a; break }
  const closed = page.locator('#ctl00_cpContent_tree li.jstree-closed > ins')
  const n = await closed.count()
  if (!n) break
  for (let i = 0; i < n; i++) { await closed.nth(i).click({ timeout: 5000 }).catch(() => {}); await page.waitForTimeout(700) }
  await page.waitForTimeout(1200)
}
if (!node) { console.log(`❌ 樹上找不到「${TITLE}」`); await browser.close(); process.exit(1) }

await node.click({ button: 'right' })
await page.waitForTimeout(1200)
await page.locator('#vakata-contextmenu a:has-text("編輯")').first().click()
await page.waitForTimeout(4500)
const frame = page.frames().find(f => /NodeEditor\.aspx/.test(f.url()))
if (!frame) { console.log('❌ 沒等到編輯彈窗'); await browser.close(); process.exit(1) }
console.log(`[彈窗] ${frame.url()}`)

const now = await frame.$$eval('input,select', els => els.map(e => ({
  name: e.getAttribute('name'), type: e.getAttribute('type'),
  value: e.tagName === 'SELECT' ? e.value : (e.type === 'radio' ? (e.checked ? e.value : null) : e.value),
})).filter(e => e.name && !/^__/.test(e.name) && e.value !== null))
console.log('[現值]')
for (const f of now) console.log(`  ${f.name} = ${f.value}`)

if (!SETS.length) { console.log('\n[dump] 不修改'); await browser.close(); process.exit(0) }

for (const [k, v] of SETS) {
  const sel = frame.locator(`select[name="${k}"]`)
  const radio = frame.locator(`input[type=radio][name="${k}"][value="${v}"]`)
  if (await sel.count()) { await sel.selectOption(v); console.log(`[改] ${k} → 「${v}」（select）`) }
  else if (await radio.count()) {
    // radio 用 check() 才會帶上 onclick（有些欄位會連動顯示／隱藏其他選項）
    await radio.check({ force: true })
    console.log(`[改] ${k} → 「${v}」（radio）`)
  }
  else { await frame.fill(`input[name="${k}"]`, v); console.log(`[改] ${k} → 「${v}」（input）`) }
}
const btn = frame.locator('#btNew, input[type=submit]').first()
await btn.click()
await page.waitForTimeout(4000)
if (dialogs.length) console.log('[對話框]', dialogs)
await browser.close()
