// Compute death_year = birth_year + lifespan - 1 for biblical patriarchs
// Sources: Gen 5, 9:29, 11, 23:1, 25:7,17, 35:28, 47:28
const TOKEN = '>[REDACTED_PAT_2]'
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

// [name_zh, birth_year_AM, lifespan]  → death_year = birth + lifespan - 1
const DATA = [
  // ── 創世記 5 章 ────────────────────────────────
  ['亞當',               1,  930],  // 創5:5
  ['塞特',             130,  912],  // 創5:8
  ['以挪士',           235,  905],  // 創5:11
  ['該南',             325,  910],  // 創5:14
  ['瑪哈拉利',         395,  895],  // 創5:17
  ['雅列',             460,  962],  // 創5:20
  ['以諾（雅列之子）', 622,  365],  // 創5:23（被神取去）
  ['瑪土撒拉',         687,  969],  // 創5:27（聖經最長壽）
  ['拉麥（挪亞之父）', 874,  777],  // 創5:31
  ['挪亞',            1056,  950],  // 創9:29

  // ── 挪亞三子（壽命未記，略）────────────────────
  ['閃',              1558,  600],  // 創11:11

  // ── 創世記 11 章 ───────────────────────────────
  ['亞法撒',          1658,  438],  // 創11:13
  ['沙拉',            1693,  433],  // 創11:15
  ['希伯',            1723,  464],  // 創11:17
  ['法勒',            1757,  239],  // 創11:19
  ['拉吳',            1787,  239],  // 創11:21
  ['西鹿',            1819,  230],  // 創11:23
  ['拿鶴（西鹿之子）',1849,  148],  // 創11:25
  ['他拉',            1878,  205],  // 創11:32

  // ── 亞伯拉罕家族 ──────────────────────────────
  ['亞伯拉罕',        2008,  175],  // 創25:7
  ['撒拉',            2018,  127],  // 創23:1
  ['以實瑪利',        2094,  137],  // 創25:17
  ['以撒',            2108,  180],  // 創35:28
  ['雅各',            2168,  147],  // 創47:28
]

const BATCH = 50
for (let i = 0; i < DATA.length; i += BATCH) {
  const slice = DATA.slice(i, i + BATCH)
  const cases = slice
    .map(([name, birth, life]) =>
      `WHEN '${name.replace(/'/g, "''")}' THEN ${birth + life - 1}`)
    .join('\n    ')
  const names = slice.map(([name]) => `'${name.replace(/'/g, "''")}'`).join(',')
  const query = `
    UPDATE biblical_people
    SET death_year = CASE name_zh
      ${cases}
    END
    WHERE name_zh IN (${names})
  `
  const r = await sql(query)
  console.log(`Batch ${i}–${i + slice.length}: status ${r.status}`)
}

console.log('Done — 死亡年已更新。')
console.log('')
console.log('參考數據：')
for (const [name, birth, life] of DATA) {
  console.log(`  ${name.padEnd(12)} 生 AM ${birth}  壽 ${life}  卒 AM ${birth + life - 1}`)
}
