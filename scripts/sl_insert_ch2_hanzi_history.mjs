/**
 * 宗教系國文講義：在導論(ch1)之後插入新第二章〈漢字的發展〉，
 * 現有 ch2..ch16 順延為 ch3..ch17。確定性腳本，不動 ch1。
 *
 * 步驟：
 *  1. 由高到低把 chNN.html → ch(NN+1).html，並：
 *     - 更新該檔內 fn 命名空間 fn-chNN- / fnref-chNN- → +1
 *  2. 全 SL 片段（含順延後的檔）做「第<中文N>章」→「第<中文N+1>章」的章號位移
 *     （高到低，一次到位，同時修 h2 標題與內文跨章引用；第一章導論不動）
 *  3. 留下 ch2.html 舊內容待覆寫（呼叫方另寫新章）；此處僅搬移與改號。
 *
 * 用法：node scripts/sl_insert_ch2_hanzi_history.mjs        （執行搬移＋改號）
 *       node scripts/sl_insert_ch2_hanzi_history.mjs --dry  （只列印將發生的變更）
 */
import fs from 'node:fs'
import path from 'node:path'

const DRY = process.argv.includes('--dry')
const dir = path.join(process.cwd(), 'public', 'content', 'works', 'sinographic-literature', 'chapters')
const CN = { 1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二',13:'十三',14:'十四',15:'十五',16:'十六',17:'十七' }
const pad = (n) => String(n).padStart(2, '0')

// ── 1. 由高到低搬移檔案並改 fn 命名空間 ──
for (let i = 16; i >= 2; i--) {
  const src = path.join(dir, `ch${pad(i)}.html`)
  const dst = path.join(dir, `ch${pad(i + 1)}.html`)
  let html = fs.readFileSync(src, 'utf8')
  // fn 命名空間 chN → ch(N+1)（該檔只含自身命名空間，安全）
  html = html.replace(new RegExp(`(fn-|fnref-)ch${i}-`, 'g'), `$1ch${i + 1}-`)
             .replace(new RegExp(`#fn-ch${i}-`, 'g'), `#fn-ch${i + 1}-`)
  if (DRY) console.log(`move ch${pad(i)} → ch${pad(i + 1)}  (fn-ch${i}- → fn-ch${i + 1}-)`)
  else { fs.writeFileSync(dst, html, 'utf8') }
}

// ── 2. 章號位移：第<CN[n]>章 → 第<CN[n+1]>章，n 由 16 到 2（含 h2 與跨章引用）──
// 對「順延後」的檔集合（ch3..ch17）以及尚未覆寫的 ch2（舊卜辭，稍後被新章取代，仍先修號一致）套用。
if (!DRY) {
  const files = fs.readdirSync(dir).filter(f => /^ch\d\d\.html$/.test(f))
  for (const f of files) {
    if (f === 'ch01.html' || f === '_head.html') continue
    const p = path.join(dir, f)
    let html = fs.readFileSync(p, 'utf8')
    for (let n = 16; n >= 2; n--) {
      html = html.split(`第${CN[n]}章`).join(`第${CN[n + 1]}章`)
    }
    fs.writeFileSync(p, html, 'utf8')
  }
  console.log('章號位移完成（ch1 導論未動；ch2 為舊卜辭改號後待覆寫成新章）')
} else {
  for (let n = 16; n >= 2; n--) console.log(`renumber 第${CN[n]}章 → 第${CN[n + 1]}章`)
}
