// Fill missing 雙月刊 issues whose PDF filename didn't match the main regex.
// Broad parse: magazine-?NNN  OR  NNNhongshi . Download the gap issues, append
// to harvest index. Headful CF, paced.
import { chromium } from 'playwright'
import fs from 'fs'
const IDX='C:/tmp/hongshi_magazine_index.json'
const DIR='C:/tmp/hongshi_dl/magazine'
const GAPS=new Set([85,177,178,179,180,188,189,190])
const sleep=ms=>new Promise(r=>setTimeout(r,ms))
const jitter=()=>5000+Math.floor(Math.random()*3000)
const CH=/just a moment|請稍候|稍候|loading|安全驗證|惡意機器人/i
function issueOf(href){ let m=href.match(/magazine-?(\d{2,3})\b/i); if(m)return +m[1]; m=href.match(/\/(\d{2,3})hongshi/i); if(m)return +m[1]; return null }
const b=await chromium.launch({headless:false,channel:'chrome',args:['--disable-blink-features=AutomationControlled']})
const ctx=await b.newContext({locale:'zh-TW'})
await ctx.addInitScript(()=>{Object.defineProperty(navigator,'webdriver',{get:()=>undefined})})
const pg=await ctx.newPage()
async function load(url){await pg.goto(url,{waitUntil:'domcontentloaded',timeout:60000});let t=await pg.title();for(let i=0;i<40&&(CH.test(t)||CH.test((await pg.locator('body').innerText().catch(()=>'')).slice(0,120)));i++){await sleep(1000);t=await pg.title()}await sleep(1200);return t}
const idx=JSON.parse(fs.readFileSync(IDX,'utf-8'))
const have=new Set(idx.map(x=>x.issue))
const found={}
for(const p of [2,3,4,5,22,23,24,25]){
  await load(`https://www.hongshi.org.tw/hongshi-magazine.php?p=${p}`)
  const hrefs=await pg.$$eval('a[href*="admin/upload/file"][href*=".pdf"]',as=>[...new Set(as.map(a=>a.getAttribute('href')))])
  for(const h of hrefs){ const n=issueOf(h); if(n&&GAPS.has(n)&&!found[n]){ found[n]=h.startsWith('http')?h:`https://www.hongshi.org.tw/${h.replace(/^\//,'')}` } }
  console.log(`p=${p}: found gaps so far ${Object.keys(found).join(',')}`)
  await sleep(jitter())
}
console.log('gap URLs:',JSON.stringify(found,null,1))
let ok=0
for(const [n,url] of Object.entries(found)){
  const fn=`${DIR}/弘誓雙月刊-${String(n).padStart(3,'0')}.pdf`
  if(fs.existsSync(fn)&&fs.statSync(fn).size>10000){console.log(`skip ${n}`);continue}
  try{ const r=await ctx.request.get(url,{timeout:60000}); if(!r.ok()){console.log(`✗ ${n} HTTP ${r.status()}`);continue}
    const buf=await r.body(); fs.writeFileSync(fn,buf); ok++
    const m=url.match(/(\d{8})\.pdf/)||url.match(/-(\d{6,7})\.pdf/)
    if(!idx.find(x=>x.issue==n)) idx.push({issue:+n,date:(m?m[1]:''),title:'',pdfs:[url]})
    console.log(`✓ 期${n} ${(buf.length/1024/1024).toFixed(1)}MB`)
  }catch(e){console.log(`✗ ${n} ${e.message.slice(0,50)}`)}
  await sleep(jitter())
}
idx.sort((a,b)=>b.issue-a.issue)
fs.writeFileSync(IDX,JSON.stringify(idx,null,2))
console.log(`\nDONE downloaded ${ok}; index now ${idx.length} issues`)
await b.close()
