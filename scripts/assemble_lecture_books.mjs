/**
 * 講義書組裝：public/content/works/{slug}/chapters/（_head.html + chNN.html 逐章 fragment）
 * → 串成單一書檔（WR1.html / SL1.html）供 /works 章節閱讀器讀取。
 * 世界宗教文化導論 ch06–ch14 於 h2 之後自動插入對應界域地圖 <figure>。
 * 用法：node scripts/assemble_lecture_books.mjs [--split] （--split＝反向：把現有書檔拆成 fragments，僅初始化用）
 */
import fs from 'node:fs'
import path from 'node:path'

const BOOKS = [
  { slug: 'world-religions-intro', out: 'WR1.html', n: 17 },
  { slug: 'sinographic-literature', out: 'SL1.html', n: 16 },
]

// WR 各章地圖（章號 → 圖檔與圖說）
const WR_MAPS = {
  6: ['world-overview', '全球八大人文宗教界域全圖（2026 年現況）'],
  7: ['realm-central', '中央界域及其文化圈（灰階淡色為其他界域；圖例含六個歷史性退場文化圈）'],
  8: ['realm-eastern', '東方界域及其文化圈：印度、漢地、圖博'],
  9: ['realm-western', '西方界域及其文化圈'],
  10: ['realm-northern', '北方界域及其文化圈：圖蘭-突厥、羅斯-韃靼、蒙古-通古斯、西伯利亞'],
  11: ['realm-southern', '南方界域及其文化圈'],
  12: ['realm-asia-pacific', '亞太界域及其文化圈：眉公、黑潮、班努亞、太平洋、紐奧'],
  13: ['realm-north-america', '北美界域及其文化圈：盎格魯美洲、法蘭西美洲、北極'],
  14: ['realm-latin-america', '拉美界域及其文化圈'],
}

const root = path.join(process.cwd(), 'public', 'content', 'works')

function figureHtml(slug, file, caption) {
  return `\n<figure class="chapter-map" style="margin:1.5rem 0">` +
    `<img src="/content/works/${slug}/maps/${file}.png" alt="${caption}" loading="lazy" style="width:100%;border:1px solid #e5e7eb;border-radius:12px" />` +
    `<figcaption style="font-size:12px;color:#6b7280;margin-top:6px">${caption}｜互動地圖見 /maps/world-religions</figcaption></figure>\n`
}

function split() {
  for (const b of BOOKS) {
    const raw = fs.readFileSync(path.join(root, b.slug, b.out), 'utf8')
    const dir = path.join(root, b.slug, 'chapters')
    fs.mkdirSync(dir, { recursive: true })
    const parts = raw.split('<section class="chapter">')
    fs.writeFileSync(path.join(dir, '_head.html'), parts[0].trimEnd() + '\n', 'utf8')
    parts.slice(1).forEach((p, i) => {
      const body = ('<section class="chapter">' + p).trimEnd()
      fs.writeFileSync(path.join(dir, `ch${String(i + 1).padStart(2, '0')}.html`), body + '\n', 'utf8')
    })
    console.log(`${b.slug}: head + ${parts.length - 1} chapters split`)
  }
}

function assemble() {
  for (const b of BOOKS) {
    const dir = path.join(root, b.slug, 'chapters')
    let out = fs.readFileSync(path.join(dir, '_head.html'), 'utf8').trimEnd() + '\n\n'
    for (let i = 1; i <= b.n; i++) {
      const f = path.join(dir, `ch${String(i).padStart(2, '0')}.html`)
      if (!fs.existsSync(f)) { console.warn(`⚠ missing ${f}`); continue }
      let ch = fs.readFileSync(f, 'utf8').trimEnd()
      // 移除 fragment 內既有的 chapter-map（以組裝規則為準，避免重複）
      ch = ch.replace(/\n?<figure class="chapter-map"[\s\S]*?<\/figure>\n?/g, '\n')
      if (b.slug === 'world-religions-intro' && WR_MAPS[i]) {
        const [file, caption] = WR_MAPS[i]
        ch = ch.replace(/(<\/h2>)/, `$1${figureHtml(b.slug, file, caption)}`)
      }
      out += ch + '\n\n'
    }
    fs.writeFileSync(path.join(root, b.slug, b.out), out.trimEnd() + '\n', 'utf8')
    console.log(`${b.slug}/${b.out} assembled (${out.length} chars)`)
  }
}

if (process.argv.includes('--split')) split()
else assemble()
