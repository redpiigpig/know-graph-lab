/** Alexandria Coptic Orthodox patriarchs batch 2: #61-#118 (AD 956-2025) */
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

const items = [
  [61, '聖米迦勒四世', 'Mina I', 956, 974],
  [62, '聖以法蓮', 'Ephraim', 975, 978],
  [63, '聖斐羅德', 'Philotheus', 979, 1003],
  [64, '聖薩查里', 'Zacharias', 1004, 1032],
  [65, '聖薩努達二世', 'Shenouda II', 1032, 1046],
  [66, '聖克利斯多多羅', 'Christodulus', 1047, 1077],
  [67, '聖息羅', 'Cyril II', 1078, 1092],
  [68, '聖米迦勒五世', 'Michael IV', 1092, 1102],
  [69, '聖瑪加略二世', 'Macarius II', 1102, 1128],
  [70, '聖加百利二世', 'Gabriel II', 1131, 1145],
  [71, '聖米迦勒六世', 'Michael V', 1145, 1146],
  [72, '聖約翰五世', 'John V', 1147, 1166],
  [73, '聖瑪可三世', 'Mark III', 1166, 1189],
  [74, '聖約翰六世', 'John VI', 1189, 1216],
  [75, '聖息羅三世', 'Cyril III ibn Laqlaq', 1235, 1243],
  [76, '聖亞他納修三世', 'Athanasius III', 1250, 1261],
  [77, '聖約翰七世', 'John VII', 1262, 1268],
  [78, '聖加百利三世', 'Gabriel III', 1268, 1271],
  [79, '聖約翰八世', 'John VIII', 1300, 1320],
  [80, '聖約翰九世', 'John IX', 1320, 1327],
  [81, '聖班雅明二世', 'Benjamin II', 1327, 1339],
  [82, '聖伯多祿五世', 'Peter V', 1340, 1348],
  [83, '聖瑪可四世', 'Mark IV', 1349, 1363],
  [84, '聖約翰十世', 'John X', 1363, 1369],
  [85, '聖加百利四世', 'Gabriel IV', 1370, 1378],
  [86, '聖瑪太一世', 'Matthew I', 1378, 1408],
  [87, '聖加百利五世', 'Gabriel V', 1409, 1427],
  [88, '聖約翰十一世', 'John XI', 1427, 1452],
  [89, '聖瑪太二世', 'Matthew II', 1452, 1465],
  [90, '聖加百利六世', 'Gabriel VI', 1466, 1474],
  [91, '聖米迦勒七世', 'Michael VI', 1477, 1478],
  [92, '聖約翰十二世', 'John XII', 1480, 1483],
  [93, '聖約翰十三世', 'John XIII', 1483, 1524],
  [94, '聖加百利七世', 'Gabriel VII', 1525, 1568],
  [95, '聖約翰十四世', 'John XIV', 1571, 1585],
  [96, '聖加百利八世', 'Gabriel VIII', 1586, 1601],
  [97, '聖瑪可五世', 'Mark V', 1602, 1618],
  [98, '聖約翰十五世', 'John XV', 1619, 1629],
  [99, '聖瑪太三世', 'Matthew III', 1631, 1646],
  [100, '聖瑪可六世', 'Mark VI', 1646, 1656],
  [101, '聖瑪太四世', 'Matthew IV', 1660, 1675],
  [102, '聖約翰十六世', 'John XVI', 1676, 1718],
  [103, '聖伯多祿六世', 'Peter VI', 1718, 1726],
  [104, '聖約翰十七世', 'John XVII', 1727, 1745],
  [105, '聖瑪可七世', 'Mark VII', 1745, 1769],
  [106, '聖約翰十八世', 'John XVIII', 1769, 1796],
  [107, '聖瑪可八世', 'Mark VIII', 1796, 1809],
  [108, '聖伯多祿七世', 'Peter VII', 1809, 1852],
  [109, '聖息羅四世', 'Cyril IV', 1854, 1861],
  [110, '聖德米特里二世', 'Demetrius II', 1862, 1870],
  [111, '聖息羅五世', 'Cyril V', 1874, 1927],
  [112, '聖約翰十九世', 'John XIX', 1928, 1942],
  [113, '聖瑪卡里三世', 'Macarius III', 1944, 1945],
  [114, '聖約撒柏', 'Yusab II', 1946, 1956],
  [115, '聖息羅六世', 'Cyril VI', 1959, 1971],
  // 117 已存在 = 沙努達三世
  [116, '聖沙努達三世', 'Shenouda III (full reign)', 1971, 2012],
  // 118 已存在 = 塔瓦德羅斯二世
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '亞歷山卓', '科普特正教', ${st}, ${ed}, '逝世', '正統', 'Coptic Orthodox Patriarchate of Alexandria official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Alexandria Coptic patriarchs (batch 2)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
