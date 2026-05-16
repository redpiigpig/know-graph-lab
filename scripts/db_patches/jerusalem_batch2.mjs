/** Jerusalem patriarchs batch 2: #81-#141 (AD 984-2025) */
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
  [81, '聖奧里斯狄', 'Orestes', 984, 1005],
  [82, '聖德奧菲洛', 'Theophilus', 1012, 1020],
  [83, '聖尼基弗魯', 'Nicephorus I', 1020, 1048],
  [84, '聖約翰九世', 'John IX', 1048, 1065],
  [85, '聖索弗洛尼二世', 'Sophronius II', 1065, 1090],
  [86, '聖優提米', 'Euthymius', 1090, 1099],
  [87, '聖息馬翁', 'Symeon II', 1098, 1099],
  [88, '聖薩巴', 'Sabbas', 1117, 1141],
  [89, '聖尼科底默', 'Nicodemus I', 1146, 1150],
  [90, '聖約翰十世', 'John IX', 1156, 1166],
  [91, '聖尼基弗魯二世', 'Nicephorus II', 1166, 1170],
  [92, '聖良提二世', 'Leontius II', 1170, 1190],
  [93, '聖多西特', 'Dositheus', 1191, 1195],
  [94, '聖瑪爾克', 'Mark II', 1195, 1213],
  [95, '聖優提米二世', 'Euthymius II', 1223, 1241],
  [96, '聖亞他納修二世', 'Athanasius II', 1224, 1236],
  [97, '聖索弗洛尼三世', 'Sophronius III', 1236, 1244],
  [98, '聖額我略一世', 'Gregory I', 1283, 1298],
  [99, '聖塔拉斯', 'Tarasius', 1298, 1308],
  [100, '聖亞他那修三世', 'Athanasius III', 1313, 1334],
  [101, '聖額我略二世', 'Gregory II', 1332, 1342],
  [102, '聖拉撒祿', 'Lazarus', 1334, 1368],
  [103, '聖亞爾色尼', 'Arsenius', 1344, 1366],
  [104, '聖多羅特', 'Dorotheus I', 1376, 1417],
  [105, '聖德奧菲洛二世', 'Theophilus II', 1417, 1424],
  [106, '聖德奧多里二世', 'Theophanes I', 1417, 1424],
  [107, '聖約亞西米一世', 'Joachim', 1431, 1450],
  [108, '聖德奧多里三世', 'Theophanes II', 1450, 1452],
  [109, '聖亞他那修四世', 'Athanasius IV', 1452, 1460],
  [110, '聖雅各', 'James', 1460, 1468],
  [111, '聖亞伯拉罕', 'Abraham', 1468, 1469],
  [112, '聖額我略三世', 'Gregory III', 1469, 1475],
  [113, '聖瑪克西穆四世', 'Mark IV', 1503, 1505],
  [114, '聖多羅特二世', 'Dorotheus II', 1505, 1537],
  [115, '聖額我略四世', 'Germanus', 1537, 1579],
  [116, '聖索弗洛尼四世', 'Sophronius IV', 1579, 1608],
  [117, '聖德奧菲洛三世', 'Theophanes III', 1608, 1644],
  [118, '聖巴喜略二世', 'Paisius', 1645, 1660],
  [119, '聖內克塔流', 'Nectarius', 1661, 1669],
  [120, '聖多西特二世', 'Dositheus II Notaras', 1669, 1707],
  [121, '聖克利桑特', 'Chrysanthus Notaras', 1707, 1731],
  [122, '聖默勒底二世', 'Meletius', 1731, 1737],
  [123, '聖巴爾德尼', 'Parthenius', 1737, 1766],
  [124, '聖埃弗拉穆', 'Ephraim II', 1766, 1771],
  [125, '聖索弗洛尼五世', 'Sophronius V', 1771, 1775],
  [126, '聖亞布拉米', 'Abraham', 1775, 1787],
  [127, '聖普羅可比', 'Procopius I', 1787, 1788],
  [128, '聖安提木一世', 'Anthemus', 1788, 1808],
  [129, '聖玻利加坡', 'Polycarp', 1808, 1827],
  [130, '聖亞他那修五世', 'Athanasius V', 1827, 1845],
  [131, '聖息羅二世', 'Cyril II', 1845, 1872],
  [132, '聖普羅可比二世', 'Procopius II', 1872, 1875],
  [133, '聖伊洛特', 'Hierotheus', 1875, 1882],
  [134, '聖尼可德姆', 'Nicodemus', 1883, 1890],
  [135, '聖該爾瑪諾', 'Gerasimus', 1891, 1897],
  [136, '聖達米安', 'Damianus', 1897, 1931],
  [137, '聖底摩太一世', 'Timotheus', 1935, 1955],
  [138, '聖班奈狄克', 'Benediktos I', 1957, 1980],
  [139, '聖底奧多羅一世', 'Diodoros I', 1981, 2000],
  [140, '聖伊倫尼烏一世', 'Eirenaios', 2001, 2005],
  [141, '狄奧菲洛三世', 'Theophilos III', 2005, null],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '耶路撒冷', '東正教', ${st}, ${ed === null ? 'NULL' : ed}, ${ed === null ? 'NULL' : "'逝世'"}, '正統', 'Greek Orthodox Patriarchate of Jerusalem official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Jerusalem patriarchs (batch 2)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
