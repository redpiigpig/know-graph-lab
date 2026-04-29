// Update birth_year (Anno Mundi 創世紀元) for biblical people
// Source: Genesis 5, 11, 21:5, 25:26 (Masoretic text)
// AM 1 = year of creation; positive integer stored as-is in birth_year column
const TOKEN = '>[REDACTED_PAT_1]'
const REF   = 'vloqgautkahgmqcwgfuo'
const URL   = `https://api.supabase.com/v1/projects/${REF}/database/query`

async function sql(query) {
  const r = await fetch(URL, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!r.ok) console.error('HTTP', r.status, await r.text())
  return r
}

// Each entry: [name_zh, birth_year_AM]
// Genesis 5 lineage (Adam → Noah)
// Genesis 11 lineage (Shem → Abraham)
// Then Isaac, Jacob
const DATA = [
  // ── 創世記 5 章 ──────────────────────────────────────
  ['亞當',            1],     // 始祖
  ['夏娃',            1],     // 始祖
  // 該隱、亞伯：創世記未記出生年，略過
  ['塞特',          130],     // 亞當 130 歲生塞特（創5:3）
  ['以挪士',        235],     // 塞特 105 歲（創5:6）
  ['該南',          325],     // 以挪士 90 歲（創5:9）
  ['瑪哈拉利',      395],     // 該南 70 歲（創5:12）
  ['雅列',          460],     // 瑪哈拉利 65 歲（創5:15）
  ['以諾（雅列之子）', 622],  // 雅列 162 歲（創5:18）
  ['瑪土撒拉',      687],     // 以諾 65 歲（創5:21）
  ['拉麥（挪亞之父）', 874],  // 瑪土撒拉 187 歲（創5:25）
  ['挪亞',         1056],     // 拉麥 182 歲（創5:28）

  // 挪亞三子：創5:32「挪亞五百歲生了閃、含、雅弗」
  // 創10:21 雅弗為長；閃約洪水前98年生（創11:10推算）
  ['雅弗',         1556],     // 挪亞 500 歲生，最長（AM 1556）
  ['閃',           1558],     // 洪水後2年（AM 1658）閃100歲 → 生於 AM 1558
  ['含',           1557],     // 介於閃雅弗之間（估）

  // ── 創世記 11 章 ─────────────────────────────────────
  ['亞法撒',       1658],     // 閃 100 歲，洪水後2年（創11:10）
  ['沙拉',         1693],     // 亞法撒 35 歲（創11:12）
  ['希伯',         1723],     // 沙拉 30 歲（創11:14）
  ['法勒',         1757],     // 希伯 34 歲（創11:16）
  ['約坍',         1757],     // 法勒孿生兄弟（同年估）
  ['拉吳',         1787],     // 法勒 30 歲（創11:18）
  ['西鹿',         1819],     // 拉吳 32 歲（創11:20）
  ['拿鶴（西鹿之子）', 1849], // 西鹿 30 歲（創11:22）
  ['他拉',         1878],     // 拿鶴 29 歲（創11:24）

  // 他拉生亞伯拉罕：創11:26「他拉七十歲生了亞伯蘭、拿鶴、哈蘭」
  // 但亞伯拉罕實際在他拉 130 歲時生（徒7:4，他拉205歲卒，亞伯拉罕離哈蘭時75歲）
  ['哈蘭',         1948],     // 他拉 70 歲生（長子，創11:26）
  ['拿鶴（他拉之子）', 1958], // 估（介於哈蘭與亞伯拉罕之間）
  ['亞伯拉罕',     2008],     // 他拉 130 歲生（徒7:4 + 創12:4 推算）
  ['撒拉',         2018],     // 亞伯拉罕小10歲（創17:17）

  // 亞伯拉罕→以撒→雅各
  ['以實瑪利',     2094],     // 亞伯拉罕 86 歲（創16:16）
  ['以撒',         2108],     // 亞伯拉罕 100 歲（創21:5）
  ['利百加',       2108],     // 與以撒同代（估）
  ['以掃',         2168],     // 以撒 60 歲（創25:26）
  ['雅各',         2168],     // 孿生，同年
]

const rows = DATA

const BATCH = 50
for (let i = 0; i < rows.length; i += BATCH) {
  const slice = rows.slice(i, i + BATCH)
  const cases = slice.map(([name, yr]) => `WHEN '${name.replace(/'/g, "''")}' THEN ${yr}`).join('\n    ')
  const names = slice.map(([name]) => `'${name.replace(/'/g, "''")}'`).join(',')
  const query = `
    UPDATE biblical_people
    SET birth_year = CASE name_zh
      ${cases}
    END
    WHERE name_zh IN (${names})
  `
  const r = await sql(query)
  console.log(`Batch ${i}–${i + slice.length}: status ${r.status}`)
}

console.log('Done — 創世紀元出生年已更新。')
