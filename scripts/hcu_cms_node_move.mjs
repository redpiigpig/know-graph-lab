// 調整節點在樹裡的順序（後台 UI 的拖拉功能被關掉了，但 api/move-node.ashx 還在）。
//
// 參數就是 jstree 傳給那支 API 的三個：id=要搬的節點、rid=參考節點、p=位置
// （'first'／'last'／'before'／'after'）。從後台頁面裡 fetch，才帶得到 cookie 與 referer。
//
// 用法：
//   node scripts/hcu_cms_node_move.mjs --list <父節點rid>              # 列子節點與順序
//   node scripts/hcu_cms_node_move.mjs --id <節點> --rid <參考> --p first
import { existsSync } from 'fs'
import { chromium } from 'playwright'

const OUT = 'c:/tmp/hcu-cms'
if (!existsSync(`${OUT}/state.json`)) { console.error('先跑 hcu_cms_login.mjs'); process.exit(2) }
function arg(n, d = null) { const i = process.argv.indexOf(`--${n}`); return i > 0 ? process.argv[i + 1] : d }
const LIST = arg('list'), ID = arg('id'), RID = arg('rid'), P = arg('p', 'first')

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: `${OUT}/state.json` })
const page = await ctx.newPage()
await page.goto('https://www.hcu.edu.tw/backend/MngCms/NodeList.aspx', { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(3000)
if (/login\.aspx/i.test(page.url())) { console.log('❌ session 過期'); await browser.close(); process.exit(1) }

async function children(parent) {
  return await page.evaluate(async id => {
    const r = await fetch('api/get-nodes.ashx', {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ id }).toString(),
    })
    return JSON.parse(await r.text()).map(n => ({ id: n.metadata.id, title: n.data.title }))
  }, parent)
}

if (LIST) {
  const kids = await children(LIST)
  kids.forEach((k, i) => console.log(`${i + 1}. ${k.title}  ${k.id}`))
  await browser.close(); process.exit(0)
}
if (!ID || !RID) { console.error('要 --id 與 --rid（或用 --list）'); await browser.close(); process.exit(2) }

const res = await page.evaluate(async ({ id, rid, p }) => {
  const r = await fetch('api/move-node.ashx', {
    method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ id, rid, p }).toString(),
  })
  return { status: r.status, text: (await r.text()).slice(0, 200) }
}, { id: ID, rid: RID, p: P })
console.log('[move-node]', JSON.stringify(res))
const kids = await children(RID)
console.log('[搬完順序]')
kids.forEach((k, i) => console.log(`  ${i + 1}. ${k.title}`))
await browser.close()
