/** Armenia Etchmiadzin catholicoi batch 2: #81-#132 (AD 1430-2025) */
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
  [81, '聖君士坦丁六世', 'Konstandin VI Vahkatsi', 1430, 1439],
  [82, '聖額我略九世', 'Grigor IX Musabegyants', 1439, 1441],
  [83, '聖基拉科斯', 'Kirakos I Virapetsi', 1441, 1443],
  [84, '聖額我略十世', 'Grigor X Jalalbegyants', 1443, 1465],
  [85, '聖亞坤特', 'Aristakes II Atorakal', 1465, 1469],
  [86, '聖薩奇斯', 'Sargis II', 1469, 1474],
  [87, '聖約翰七世', 'Hovhannes VII Ajakir', 1474, 1484],
  [88, '聖薩奇斯二世', 'Sargis III', 1484, 1515],
  [89, '聖薩奇斯三世', 'Zakaria II', 1515, 1520],
  [90, '聖薩奇斯四世', 'Sargis IV', 1520, 1536],
  [91, '聖額我略十一世', 'Grigor XI Byuzantatsi', 1536, 1542],
  [92, '聖斯德范六世', 'Stepanos V Salmastetsi', 1542, 1567],
  [93, '聖米迦勒一世', 'Mikayel I Sebastatsi', 1567, 1576],
  [94, '聖額我略十二世', 'Grigor XII Vakuetsi', 1576, 1587],
  [95, '聖大衛四世', 'Davit IV Vagharshapatetsi', 1587, 1629],
  [96, '聖摩西三世', 'Movses III Tatevatsi', 1629, 1632],
  [97, '聖斐利浦', 'Pilippos I Aghbaketsi', 1633, 1655],
  [98, '聖雅各四世', 'Hakob IV Jughayetsi', 1655, 1680],
  [99, '聖以利亞二世', 'Eghiazar I', 1681, 1691],
  [100, '聖納哈佩特', 'Nahapet I Edesatsi', 1691, 1705],
  [101, '聖亞歷山大一世', 'Aleksandr I Jughayetsi', 1706, 1714],
  [102, '聖亞斯特瓦察圖爾', 'Astvatsatur I Hamadanetsi', 1715, 1725],
  [103, '聖卡拉佩特二世', 'Karapet II Ulnetsi', 1726, 1729],
  [104, '聖亞伯拉罕二世', 'Abraham II Khoshabetsi', 1730, 1734],
  [105, '聖亞伯拉罕三世', 'Abraham III Kretatsi', 1734, 1737],
  [106, '聖拉撒勒', 'Ghazar I Jahketsi', 1737, 1751],
  [107, '聖米拿斯', 'Minas I Akntsi', 1751, 1753],
  [108, '聖亞歷山大二世', 'Aleksandr II Byuzantatsi', 1753, 1755],
  [109, '聖薩哈克五世', 'Sahak V Ahabetsi', 1755, 1759],
  [110, '聖雅各五世', 'Hakob V Shamakhetsi', 1759, 1763],
  [111, '聖西米恩', 'Simeon I Yerevantsi', 1763, 1780],
  [112, '聖盧加', 'Ghukas I Karnetsi', 1780, 1799],
  [113, '聖約瑟夫二世', 'Hovsep II Arghutyan', 1800, 1801],
  [114, '聖大衛五世', 'Davit V Enegetsi', 1801, 1804],
  [115, '聖達尼勒', 'Daniel I Surmaretsi', 1801, 1808],
  [116, '聖以法蓮', 'Yeprem I Dzoragehtsi', 1809, 1830],
  [117, '聖約翰八世', 'Hovhannes VIII Karbetsi', 1831, 1842],
  [118, '聖納薩斯五世', 'Nerses V Ashtaraketsi', 1843, 1857],
  [119, '聖瑪西耶四世', 'Matteos I Konstandnupolsetsi', 1858, 1865],
  [120, '聖喬治四世', 'Gevorg IV Konstandnupolsetsi', 1866, 1882],
  [121, '聖瑪格杜爾', 'Makar I Teghkurantsi', 1885, 1891],
  [122, '聖姆克爾蒂奇', 'Mkrtich I Khrimian', 1893, 1907],
  [123, '聖瑪太二世', 'Matteos II Izmirlyan', 1908, 1910],
  [124, '聖喬治五世', 'Gevorg V Surenyants', 1911, 1930],
  [125, '聖科林一世', 'Khoren I Muradbekian', 1932, 1938],
  [126, '聖喬治六世', 'Gevorg VI Chorekchian', 1945, 1954],
  [127, '聖瓦茲根一世', 'Vazgen I Palchian', 1955, 1994],
  [128, '聖嘎勒克一世', 'Garegin I Sarkissian', 1995, 1999],
  [129, '聖嘎勒克二世', 'Karekin II Nersisyan', 1999, null],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '埃奇米亞津', '亞美尼亞使徒教會', ${st}, ${ed === null ? 'NULL' : ed}, ${ed === null ? 'NULL' : "'逝世'"}, '正統', 'Mother See of Holy Etchmiadzin official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Armenia catholicoi (batch 2)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
