/** Alexandria Greek Orthodox patriarchs batch 2: #61-#117 (AD 960-2025) */
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
  [61, '聖伊利亞', 'Elias I', 964, 972],
  [62, '聖亞爾色尼一世', 'Arsenius I', 1000, 1010],
  [63, '聖德鐸非洛', 'Theophilus II', 1010, 1020],
  [64, '聖該爾瑪二世', 'Georgios II', 1021, 1051],
  [65, '聖良一世', 'Leontius', 1052, 1059],
  [66, '聖亞歷山大二世', 'Alexander II', 1059, 1062],
  [67, '聖約翰七世', 'John VII', 1062, 1100],
  [68, '聖卡里米克', 'Sabbas', 1100, 1117],
  [69, '聖德鐸德', 'Theodosius II', 1118, 1120],
  [70, '聖索弗洛', 'Sophronius IV', 1166, 1171],
  [71, '聖伊利亞二世', 'Elias II', 1171, 1175],
  [72, '聖瑪可', 'Mark III ibn Zur a', 1180, 1209],
  [73, '聖尼古拉', 'Nicholas I', 1210, 1243],
  [74, '聖亞他納修三世', 'Athanasius III', 1276, 1316],
  [75, '聖額我略二世', 'Gregory II', 1316, 1354],
  [76, '聖額我略三世', 'Gregory III', 1354, 1366],
  [77, '聖尼弗倫', 'Niphon', 1366, 1385],
  [78, '聖瑪可四世', 'Mark IV', 1385, 1389],
  [79, '聖尼古拉二世', 'Nicholas II', 1389, 1398],
  [80, '聖額我略四世', 'Gregory IV', 1398, 1412],
  [81, '聖尼古拉三世', 'Nicholas III', 1412, 1417],
  [82, '聖額我略五世', 'Gregory V', 1417, 1421],
  [83, '聖斐羅德', 'Philotheus I', 1435, 1459],
  [84, '聖瑪可五世', 'Mark V', 1459, 1484],
  [85, '聖額我略六世', 'Gregory VI', 1484, 1486],
  [86, '聖約翰八世', 'Joachim Pany of the Cyrene', 1486, 1567],
  [87, '聖息羅三世', 'Silvester', 1569, 1590],
  [88, '聖默勒底', 'Meletius I Pegas', 1590, 1601],
  [89, '聖息羅四世', 'Cyril III Lucaris', 1601, 1620],
  [90, '聖該爾瑪三世', 'Gerasimus I Spartaliotes', 1620, 1636],
  [91, '聖默都狄', 'Metrophanes Kritopoulos', 1636, 1639],
  [92, '聖尼基弗魯', 'Nikephoros Klaudas', 1639, 1645],
  [93, '聖若亞撒', 'Joannicius', 1645, 1657],
  [94, '聖巴喜略', 'Paisius', 1657, 1678],
  [95, '聖巴爾德尼', 'Parthenius I', 1678, 1688],
  [96, '聖該爾瑪四世', 'Gerasimus II Pallidas', 1688, 1710],
  [97, '聖息羅五世', 'Samuel Kapasoulis', 1710, 1723],
  [98, '聖科斯馬二世', 'Cosmas II', 1723, 1736],
  [99, '聖科斯馬三世', 'Cosmas III', 1737, 1746],
  [100, '聖默勒底二世', 'Matthew Psaltes', 1746, 1766],
  [101, '聖息普利亞諾', 'Cyprian', 1766, 1783],
  [102, '聖該爾瑪五世', 'Gerasimus III', 1783, 1788],
  [103, '聖巴爾德尼二世', 'Parthenius II', 1788, 1805],
  [104, '聖德鐸菲洛', 'Theophilus II Pankostas', 1805, 1825],
  [105, '聖希拉里', 'Hierotheos I', 1825, 1845],
  [106, '聖亞他納修四世', 'Artemios I', 1845, 1847],
  [107, '聖希拉里二世', 'Hierotheos II', 1847, 1858],
  [108, '聖卡里尼克', 'Callinicus', 1858, 1861],
  [109, '聖雅可巴', 'Iakovos', 1861, 1865],
  [110, '聖尼可萊', 'Nikanor', 1866, 1869],
  [111, '聖索弗洛五世', 'Sophronius IV', 1870, 1899],
  [112, '聖佛提一世', 'Photius I', 1900, 1925],
  [113, '聖默勒底三世', 'Meletius II Metaxakis', 1926, 1935],
  [114, '聖尼古拉五世', 'Nicholas V', 1935, 1939],
  [115, '聖克里斯多多羅', 'Christophorus II', 1939, 1966],
  [116, '聖尼古拉六世', 'Nicholas VI', 1968, 1986],
  [117, '聖巴爾德尼三世', 'Parthenios III', 1987, 1996],
  [118, '聖伯多祿七世', 'Petros VII', 1997, 2004],
  [119, '泰奧多羅斯二世', 'Theodore II', 2004, null],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '亞歷山卓', '東正教', ${st}, ${ed === null ? 'NULL' : ed}, ${ed === null ? 'NULL' : "'逝世'"}, '正統', 'Greek Orthodox Patriarchate of Alexandria official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Alexandria GO patriarchs (batch 2)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
