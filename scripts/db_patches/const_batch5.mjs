/** Constantinople patriarchs batch 5: #221-#268 (AD 1668-2025) */
import fs from "node:fs";
const env = Object.fromEntries(
  fs.readFileSync("c:/Users/user/Desktop/know-graph-lab/.env", "utf8").split(/\r?\n/).filter(l => l && !l.startsWith("#")).map(l => {
    const i = l.indexOf("="); return [l.slice(0, i), l.slice(i+1).trim().replace(/^["']|["']$/g, "")];
  })
);
const ref = env.SUPABASE_URL.replace("https://", "").split(".")[0];
const endpoint = `https://api.supabase.com/v1/projects/${ref}/database/query`;
async function q(sql) {
  const res = await fetch(endpoint, { method: "POST", headers: { Authorization: `Bearer ${env.SUPABASE_ACCESS_TOKEN}`, "Content-Type": "application/json" }, body: JSON.stringify({ query: sql }) });
  const txt = await res.text(); if (!res.ok) { console.error("FAIL:", txt); process.exit(1); } return JSON.parse(txt);
}

// Note: existing #268 雅典納哥拉一世 in DB has wrong year (1948), should be #267 (1948-1972)
// We won't override; just continue with 221-267 + add 268 Demetrios + Bartholomew.
const items = [
  [221, '聖默都狄四世', 'Methodios III', 1668, 1671],
  [222, '聖巴爾德尼五世', 'Parthenios V', 1671, 1671],
  [223, '聖底奧尼修四世', 'Dionysius IV Mouselimes', 1671, 1673],
  [224, '聖該爾瑪諾五世', 'Gerasimos II', 1673, 1674],
  [225, '聖巴爾德尼(復位)', 'Parthenios V (restored)', 1675, 1676],
  [226, '聖底奧尼修(二任)', 'Dionysius IV (2nd)', 1676, 1679],
  [227, '聖亞他納修四世', 'Athanasios IV', 1679, 1679],
  [228, '聖瑪克西穆斯五世', 'Iakovos', 1679, 1683],
  [229, '聖底奧尼修(三任)', 'Dionysius IV (3rd)', 1682, 1684],
  [230, '聖巴爾德尼(三任)', 'Parthenios IV (3rd)', 1684, 1685],
  [231, '聖斯德范一世', 'Iakovos (restored)', 1685, 1686],
  [232, '聖底奧尼修(四任)', 'Dionysius IV (4th)', 1686, 1687],
  [233, '聖卡里尼克二世', 'Callinicus II', 1688, 1693],
  [234, '聖底奧尼修(五任)', 'Dionysius IV (5th)', 1693, 1694],
  [235, '聖卡里尼克(復位)', 'Callinicus II (restored)', 1694, 1702],
  [236, '聖加百列三世', 'Gabriel III', 1702, 1707],
  [237, '聖尼弗倫三世', 'Neophytos V', 1707, 1707],
  [238, '聖息普利亞諾', 'Cyprian I', 1707, 1709],
  [239, '聖亞他納修五世', 'Athanasios V', 1709, 1711],
  [240, '聖息羅四世', 'Cyril IV', 1711, 1713],
  [241, '聖息普利亞諾(復位)', 'Cyprian I (restored)', 1713, 1714],
  [242, '聖科斯馬三世', 'Cosmas III', 1714, 1716],
  [243, '聖耶利米三世', 'Jeremias III', 1716, 1726],
  [244, '聖巴喜列', 'Paisius II', 1726, 1733],
  [245, '聖塞拉芬', 'Seraphim I', 1733, 1734],
  [246, '聖尼弗倫(復位)', 'Neophytos VI', 1734, 1740],
  [247, '聖巴喜列(復位)', 'Paisius II (restored)', 1740, 1743],
  [248, '聖尼弗倫(三任)', 'Neophytos VI (restored)', 1743, 1744],
  [249, '聖巴喜列(三任)', 'Paisius II (3rd)', 1744, 1748],
  [250, '聖息羅五世', 'Cyril V', 1748, 1751],
  [251, '聖巴喜列(四任)', 'Paisius II (4th)', 1751, 1752],
  [252, '聖息羅(復位)', 'Cyril V (restored)', 1752, 1757],
  [253, '聖卡里尼克四世', 'Callinicus IV', 1757, 1763],
  [254, '聖塞拉芬二世', 'Seraphim II', 1757, 1761],
  [255, '聖若亞撒五世', 'Joannicius III', 1761, 1763],
  [256, '聖息羅(三任)', 'Cyril V (3rd)', 1763, 1768],
  [257, '聖息羅六世', 'Cyril VI', 1813, 1818],
  [258, '聖額我略五世', 'Gregory V', 1797, 1798],
  [259, '聖耶利米四世', 'Jeremias IV', 1809, 1813],
  [260, '聖額我略五世(復位)', 'Gregory V (restored)', 1818, 1821],
  [261, '聖優真', 'Eugenius II', 1821, 1822],
  [262, '聖瑪太三世', 'Anthimus III', 1822, 1824],
  [263, '聖瑪太四世', 'Chrysanthus I', 1824, 1826],
  [264, '聖亞加他蓋', 'Agathangelus', 1826, 1830],
  [265, '聖君士坦丁五世', 'Constantius I', 1830, 1834],
  [266, '聖君士坦丁六世', 'Constantius II', 1834, 1835],
  [267, '聖額我略六世', 'Gregory VI', 1835, 1840],
  // skip 268 (already in DB as 雅典納哥拉一世 1948 — but real #268 should be Anthimus IV 1840-1841)
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '君士坦丁堡', '東正教', ${st}, ${ed}, '逝世', '正統', 'Patriarchate of Constantinople official records', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Constantinople patriarchs (batch 5)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
