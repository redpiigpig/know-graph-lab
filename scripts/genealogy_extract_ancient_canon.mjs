// 從《基督教大藏經》古代卷「正藏」切出一二世紀（1–200 CE）的條目，
// 作為〈從使徒到大公〉譜系逐條歸屬表的文獻母體。
//
//   node scripts/genealogy_extract_ancient_canon.mjs [--out <path>]
//
// era 欄是自由文字（正藏 1,093 筆共 503 種寫法），先正規化成 [low, high] 年份區間，
// 再取與 [1, 200] 有交集者。解析不出來的一律列進 unparsed，不靜默丟掉。

import { pathToFileURL } from 'node:url'

import { mkdtempSync, writeFileSync, mkdirSync } from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'

const ROOT = path.resolve(import.meta.dirname, '..')
const SRC = path.join(ROOT, 'data/dazangjing/ancient.ts')
const OUT = process.argv.includes('--out')
  ? process.argv[process.argv.indexOf('--out') + 1]
  : path.join(ROOT, 'data/christian-genealogy/ancient-canon-1-2c.json')

/** era 自由文字 → [low, high] 西元年；前 N 世紀回負數；解析不出回 null */
export function parseEra(raw) {
  if (!raw) return null
  let s = String(raw).replace(/[〜~]/g, '-').replace(/[–—]/g, '-').replace(/\s+/g, '')
  s = s.replace(/^約/, '').replace(/年$/, '')
  const bce = /前/.test(s)
  s = s.replace(/前/g, '')

  // 🚨「3／6 世紀」這種或此或彼的寫法：若含「世紀」，一律走世紀解析，且以最早的世紀為準。
  //    否則 ／ 不被視為分隔符，regex 只吃到開頭的 3，會把三世紀誤讀成「西元 3 年」
  //    （《波菲利引論》曾因此被誤收進一二世紀窗口）。
  if (/世紀/.test(s)) s = s.replace(/[／/、,]/g, '-')

  // N 世紀初/中/末、N-M 世紀
  const cen = s.match(/^(\d+)(?:-(\d+))?世紀(初|中|末|前半|後半)?/)
  if (cen) {
    const a = Number(cen[1])
    const b = cen[2] ? Number(cen[2]) : a
    let low = (a - 1) * 100 + 1
    let high = b * 100
    const q = cen[3]
    if (!cen[2] && q) {
      if (q === '初') high = (a - 1) * 100 + 33
      else if (q === '中') { low = (a - 1) * 100 + 34; high = (a - 1) * 100 + 66 }
      else if (q === '末') low = (a - 1) * 100 + 67
      else if (q === '前半') high = (a - 1) * 100 + 50
      else if (q === '後半') low = (a - 1) * 100 + 51
    }
    return bce ? [-high, -low] : [low, high]
  }

  // 90-100 / 60-62 / 325 / 400
  const span = s.match(/^(\d{1,4})-(\d{1,4})/)
  if (span) {
    const a = Number(span[1]); const b = Number(span[2])
    return bce ? [-b, -a] : [a, b]
  }
  const one = s.match(/^(\d{1,4})/)
  if (one) {
    const a = Number(one[1])
    return bce ? [-a, -a] : [a, a]
  }
  return null
}

const overlaps = (r, low, high) => r && r[1] >= low && r[0] <= high

/** 這一條是不是新約二十七卷本身（那層走逐節，不歸文獻層） */
const NT_DIVISIONS = new Set([
  '福音書部', '行傳部', '第一大公書信部', '保羅書信部', '教牧書信部', '第二大公書信部', '啟示錄部',
])

async function loadEra() {
  const esbuild = await import('esbuild')
  const dir = mkdtempSync(path.join(tmpdir(), 'dzj-'))
  const bundle = path.join(dir, 'ancient.mjs')
  await esbuild.build({
    entryPoints: [SRC], bundle: true, format: 'esm', platform: 'node',
    outfile: bundle, logLevel: 'error',
  })
  const m = await import(pathToFileURL(bundle).href)
  return m.ancient || m.default || Object.values(m).find(v => v && v.collections)
}

const era = await loadEra()
const all = []
for (const c of era.collections) {
  for (const canon of ['zheng', 'wai']) {
    for (const d of c[canon].divisions) {
      for (const w of d.works) {
        all.push({
          canon, collection: c.name, collection_key: c.key, division: d.label,
          title_zh: w.title_zh, title_orig: w.title_orig || null,
          author: w.author || null, era: w.era || null, place: w.place || null,
          language: w.language || null, tier: w.tier || null, source: w.source || null,
          parent: w.parent || null, link: w.link || null,
          range: parseEra(w.era),
        })
      }
    }
  }
}

const unparsed = all.filter(w => !w.range)
const inScope = all.filter(w => overlaps(w.range, 1, 200))
const isNtBook = w => w.canon === 'zheng' && w.collection_key === 'jing' && NT_DIVISIONS.has(w.division)
const ntBooks = inScope.filter(isNtBook)
const literature = inScope.filter(w => !isNtBook(w) && w.canon === 'zheng')
const waiLiterature = inScope.filter(w => w.canon === 'wai')

const byDivision = {}
for (const w of literature) {
  const k = w.collection + '／' + w.division
  byDivision[k] = (byDivision[k] || 0) + 1
}
const waiBySource = {}
for (const w of waiLiterature) {
  const k = w.source || '(未標)'
  waiBySource[k] = (waiBySource[k] || 0) + 1
}

const payload = {
  meta: {
    title: '古代基督教大藏經・正藏・一二世紀（1–200 CE）',
    source: 'data/dazangjing/ancient.ts（正藏 zheng）',
    generated_by: 'scripts/genealogy_extract_ancient_canon.mjs',
    window: [1, 200],
    counts: {
      works_total: all.length,
      era_unparsed: unparsed.length,
      in_window: inScope.length,
      nt_books: ntBooks.length,
      zheng_literature: literature.length,
      wai_literature: waiLiterature.length,
    },
    note: '新約二十七卷本身另走逐節歸屬，不列入 literature',
  },
  by_division: byDivision,
  wai_by_source: waiBySource,
  nt_books: ntBooks,
  literature,
  wai_literature: waiLiterature,
  unparsed: unparsed.map(w => ({ collection: w.collection, division: w.division, title_zh: w.title_zh, era: w.era })),
}

mkdirSync(path.dirname(OUT), { recursive: true })
writeFileSync(OUT, JSON.stringify(payload, null, 2), 'utf8')

console.log('正藏＋外藏總數  ', all.length)
console.log('era 解析失敗    ', unparsed.length)
console.log('落在 1–200 CE  ', inScope.length)
console.log('  新約各卷      ', ntBooks.length, '（走逐節層）')
console.log('  正藏文獻      ', literature.length)
console.log('  外藏文獻      ', waiLiterature.length)
console.log('---- 正藏文獻分佈 ----')
for (const [k, n] of Object.entries(byDivision).sort((a, b) => b[1] - a[1])) {
  console.log(String(n).padStart(4), k)
}
console.log('---- 外藏文獻分佈（依 source）----')
for (const [k, n] of Object.entries(waiBySource).sort((a, b) => b[1] - a[1])) {
  console.log(String(n).padStart(4), k)
}
if (unparsed.length) {
  console.log('---- era 解析失敗（前 20）----')
  for (const w of unparsed.slice(0, 20)) console.log('  ', w.era, '|', w.title_zh)
}
console.log('寫出 →', path.relative(ROOT, OUT))
