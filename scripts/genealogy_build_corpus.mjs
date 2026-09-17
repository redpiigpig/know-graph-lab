// 由 ancient-canon-1-2c.json 組出〈從使徒到大公〉譜系表的「文獻母體」：
//   正藏 1–2 世紀文獻 ＋ 外藏相關者 ＋ 經藏中非二十七卷的 patristic/eastern tier 五卷
// 使用者裁示（2026-09-17）：母體取 109；馬吉安與孟他努不收（維持「存世自產文獻」標準）。
//
//   node scripts/genealogy_build_corpus.mjs

import { readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(import.meta.dirname, '..')
const IN = path.join(ROOT, 'data/christian-genealogy/ancient-canon-1-2c.json')
const OUT = path.join(ROOT, 'data/christian-genealogy/corpus-1-2c.json')

/** 外藏中與本譜系相關的 source（拉比猶太與希臘羅馬外教不取） */
const WAI_KEEP = new Set(['gnostic', 'manichaean', 'mandaean', 'orthodox-apocrypha', 'jewish-christian', 'heresy'])

/** 使用者裁示不收者（無存世自產文獻，全靠敵證回推） */
const DROP_TITLES = new Set([
  '馬吉安主之福音', '馬吉安使徒書信集', '對觀',
  '孟他努神諭殘篇', '百基拉與馬克西米拉神諭',
])

/** 大藏經自身的同書異名，併到主名 */
const ALIASES = new Map([
  ['猶斯定第一護教詞', '第一護教詞'],
  ['猶斯定第二護教詞', '第二護教詞'],
  ['特土良護教辯', '護教辯'],
  ['波利卡殉道錄', '波利甲殉道錄'],
  ['里昂殉道錄', '里昂與維埃納教會殉道書'],
  ['駁特里風護教詞', '與特里風對話錄'],
  // 以下為音譯不一致造成的同書異名（2026-09-17 逐筆核對時發現）
  ['克勉書', '克勉致哥林多人前書'],
  ['羅馬克勉一書', '克勉致哥林多人前書'],
  ['迦太基的德爾都良致殉道者書', '勸殉道致殉道者書'],
  ['帕皮亞遺篇', '主道論集殘篇'],
  ['〈雷：完美理智辭〉', '雷：完美理智辭'],
  ['波利甲致腓立比人書', '坡旅甲致腓立比人書'],
])

/** 伊格那丟：合集條目與七封單獨條目並存，保留單封、去掉合集 */
const DROP_COLLECTIVE = new Set(['伊格那丟七函'])

const src = JSON.parse(readFileSync(IN, 'utf8'))

const rows = []
const seen = new Map()
const push = (w, bucket) => {
  const title = ALIASES.get(w.title_zh) || w.title_zh
  if (DROP_TITLES.has(title) || DROP_COLLECTIVE.has(title)) return
  const key = title
  if (seen.has(key)) {
    seen.get(key).aka.push(w.title_zh)
    return
  }
  const row = {
    title_zh: title, aka: w.title_zh === title ? [] : [w.title_zh],
    bucket, canon: w.canon, collection: w.collection, division: w.division,
    author: w.author, era: w.era, range: w.range, place: w.place,
    language: w.language, tier: w.tier || null, source: w.source || null,
    title_orig: w.title_orig || null, link: w.link || null,
  }
  seen.set(key, row)
  rows.push(row)
}

// 一、經藏正藏中非二十七卷者（tier 有值＝古抄本／教父推薦或東方次經）
for (const w of src.nt_books) if (w.tier) push(w, 'near-canon')
// 二、正藏 1–2 世紀文獻
for (const w of src.literature) push(w, 'zheng')
// 三、外藏相關者
for (const w of src.wai_literature) if (WAI_KEEP.has(w.source)) push(w, 'wai')

const tally = {}
for (const r of rows) tally[r.bucket] = (tally[r.bucket] || 0) + 1

writeFileSync(OUT, JSON.stringify({
  meta: {
    title: '〈從使徒到大公〉譜系表・文獻母體（1–200 CE）',
    source: 'data/christian-genealogy/ancient-canon-1-2c.json',
    generated_by: 'scripts/genealogy_build_corpus.mjs',
    ruling_2026_09_17: '母體取 109；馬吉安（3 筆）與孟他努神諭（2 筆）不收',
    dropped: [...DROP_TITLES],
    merged_aliases: [...ALIASES.entries()].map(([a, b]) => `${a} → ${b}`),
    counts: { total: rows.length, ...tally },
  },
  works: rows,
}, null, 2), 'utf8')

console.log('文獻母體合計 ', rows.length)
for (const [k, n] of Object.entries(tally)) console.log('  ', k.padEnd(12), n)
const merged = rows.filter(r => r.aka.length)
console.log('併名 ', merged.length, '組：', merged.map(r => r.title_zh + '←' + r.aka.join('/')).join('、'))
console.log('寫出 →', path.relative(ROOT, OUT))
