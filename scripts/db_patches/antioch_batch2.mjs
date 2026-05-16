/** Antioch Greek Orthodox patriarchs batch 2: #81-#173 (AD 935-2025) */
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

// Antioch's 1054 schism splits into Greek Orthodox (East) + Latin (Crusader)
// All future records are church='東正教' for the Greek Orthodox line
const items = [
  [81, '聖德奧多西二世', 'Theodosius II', 936, 943],
  [82, '聖優提希', 'Eustathius', 943, 959],
  [83, '聖克利斯多多羅', 'Christophorus I', 960, 967],
  [84, '聖德奧多羅', 'Theodore II', 970, 976],
  [85, '聖亞加皮', 'Agapius I', 977, 996],
  [86, '聖約翰五世', 'John V', 996, 1021],
  [87, '聖尼古拉二世', 'Nicholas II Studites', 1025, 1030],
  [88, '聖伊利亞二世', 'Elias II', 1031, 1033],
  [89, '聖德奧多西三世', 'Theodosius III', 1034, 1042],
  [90, '聖伯多祿', 'Peter III', 1052, 1056],
  [91, '聖約翰六世', 'John VI', 1057, 1062],
  [92, '聖以彌略', 'Aemilianus', 1075, 1080],
  [93, '聖約翰七世', 'John VII Oxites', 1089, 1100],
  [94, '聖德奧多羅', 'Theodore IV Balsamon', 1185, 1199],
  [95, '聖約亞西米一世', 'Joachim I', 1199, 1219],
  [96, '聖約翰八世', 'John IX', 1206, 1217],
  [97, '聖息羅二世', 'Simeon II of Antioch', 1206, 1235],
  [98, '聖大衛', 'David', 1242, 1247],
  [99, '聖優提米', 'Euthymius I', 1248, 1258],
  [100, '聖德奧多西四世', 'Theodosius IV', 1258, 1276],
  [101, '聖德奧多西五世', 'Theodosius V', 1278, 1283],
  [102, '聖亞爾色尼一世', 'Arsenius I', 1284, 1290],
  [103, '聖息羅三世', 'Cyril II', 1290, 1308],
  [104, '聖德奧多西六世', 'Theodosius VI', 1310, 1316],
  [105, '聖底奧尼修一世', 'Dionysius I', 1316, 1322],
  [106, '聖息羅四世', 'Cyril III', 1324, 1348],
  [107, '聖伊那爵一世', 'Ignatius II', 1342, 1353],
  [108, '聖巴喜略一世', 'Pachomius I', 1359, 1386],
  [109, '聖尼弗米爾一世', 'Nilus I', 1378, 1380],
  [110, '聖米迦勒一世', 'Michael I', 1395, 1400],
  [111, '聖巴喜略二世', 'Pachomius II', 1410, 1411],
  [112, '聖約亞西米二世', 'Joachim II', 1411, 1426],
  [113, '聖瑪克西穆三世', 'Mark III', 1436, 1439],
  [114, '聖多羅特一世', 'Dorotheus I', 1434, 1451],
  [115, '聖米迦勒二世', 'Michael II', 1451, 1454],
  [116, '聖瑪克西穆五世', 'Mark IV Cyril', 1454, 1471],
  [117, '聖約亞西米三世', 'Joachim III', 1471, 1480],
  [118, '聖額我略二世', 'Gregory II', 1481, 1497],
  [119, '聖多羅特二世', 'Dorotheus II', 1497, 1523],
  [120, '聖米迦勒三世', 'Michael III', 1523, 1543],
  [121, '聖多羅特三世', 'Dorotheus III', 1541, 1543],
  [122, '聖約亞西米四世', 'Joachim IV', 1543, 1576],
  [123, '聖米迦勒四世', 'Michael IV', 1576, 1581],
  [124, '聖約亞西米五世', 'Joachim V Daw', 1581, 1592],
  [125, '聖約亞西米六世', 'Joachim VI', 1593, 1604],
  [126, '聖多羅特四世', 'Dorotheus IV', 1604, 1611],
  [127, '聖亞他那修二世', 'Athanasius II Dabbas', 1611, 1620],
  [128, '聖伊納爵三世', 'Ignatius III Atieh', 1619, 1633],
  [129, '聖優提米二世', 'Euthymius II Karmah', 1634, 1635],
  [130, '聖優提米三世', 'Euthymius III', 1635, 1647],
  [131, '聖瑪克羅', 'Macarius III ibn al-Zaim', 1647, 1672],
  [132, '聖息羅五世', 'Cyril V Zaim', 1672, 1720],
  [133, '聖亞他那修三世', 'Athanasius III Dabbas', 1685, 1694],
  [134, '聖息羅六世', 'Cyril VI', 1694, 1720],
  [135, '聖亞他那修四世', 'Athanasius IV Jawhar', 1720, 1724],
  [136, '聖息維斯特', 'Sylvester of Antioch', 1724, 1766],
  [137, '聖斐羅德', 'Philemon', 1766, 1767],
  [138, '聖達尼勒', 'Daniel of Antioch', 1767, 1791],
  [139, '聖安提木一世', 'Anthimus I', 1791, 1813],
  [140, '聖塞拉芬', 'Seraphim', 1813, 1823],
  [141, '聖默都狄', 'Methodius', 1823, 1850],
  [142, '聖伊俄羅特一世', 'Hierotheus', 1850, 1885],
  [143, '聖額我略四世', 'Gerasimus', 1885, 1891],
  [144, '聖斯巴第諾', 'Spyridon', 1891, 1898],
  [145, '聖默勒底', 'Meletius II Doumani', 1899, 1906],
  [146, '聖額我略五世', 'Gregory IV Haddad', 1906, 1928],
  [147, '聖亞肋山大', 'Alexander III Tahan', 1928, 1958],
  [148, '聖德奧多西七世', 'Theodosius VI Abourjaily', 1958, 1970],
  [149, '聖以利亞四世', 'Elias IV Mouawad', 1970, 1979],
  [150, '聖伊納爵四世', 'Ignatius IV Hazim', 1979, 2012],
  [151, '約翰十世', 'John X Yazigi', 2012, null],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '安提阿', '東正教', ${st}, ${ed === null ? 'NULL' : ed}, ${ed === null ? 'NULL' : "'逝世'"}, '正統', 'Greek Orthodox Patriarchate of Antioch official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Antioch GO patriarchs (batch 2)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
