/** Constantinople patriarchs batch 4: #161-#220 (AD 1456-1746, Ottoman period) */
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
  [161, '聖伊撒多二世', 'Isidore II Xanthopoulos', 1456, 1462],
  [162, '聖若亞撒一世', 'Joasaph I', 1462, 1463],
  [163, '聖索弗洛尼一世', 'Sophronius I', 1463, 1464],
  [164, '聖瑪可二世', 'Mark II Xylokarabes', 1466, 1466],
  [165, '聖息馬翁一世', 'Symeon I of Trebizond', 1466, 1471],
  [166, '聖底奧尼修一世', 'Dionysius I', 1467, 1471],
  [167, '聖拉法埃', 'Raphael I', 1475, 1476],
  [168, '聖瑪克西穆斯三世', 'Maximus III', 1476, 1481],
  [169, '聖息馬翁(復位)', 'Symeon I (restored)', 1482, 1486],
  [170, '聖尼弗倫二世', 'Niphon II', 1486, 1488],
  [171, '聖底奧尼修(復位)', 'Dionysius I (restored)', 1488, 1490],
  [172, '聖瑪克西穆斯四世', 'Maximus IV', 1491, 1497],
  [173, '聖尼弗倫(復位)', 'Niphon II (restored)', 1497, 1498],
  [174, '聖若亞撒二世', 'Joachim I', 1498, 1502],
  [175, '聖尼弗倫(三復位)', 'Niphon II (3rd term)', 1502, 1502],
  [176, '聖巴喜略', 'Pachomius I', 1503, 1504],
  [177, '聖若亞撒(復位)', 'Joachim I (restored)', 1504, 1504],
  [178, '聖巴喜略(復位)', 'Pachomius I (restored)', 1504, 1513],
  [179, '聖德鐸', 'Theoleptus I', 1513, 1522],
  [180, '聖耶利米一世', 'Jeremias I', 1522, 1545],
  [181, '聖若亞撒三世', 'Joannicius I', 1546, 1546],
  [182, '聖底奧尼修二世', 'Dionysius II', 1546, 1556],
  [183, '聖若亞撒四世', 'Joasaph II', 1556, 1565],
  [184, '聖默都狄三世', 'Metrophanes III', 1565, 1572],
  [185, '聖耶利米二世', 'Jeremias II Tranos', 1572, 1579],
  [186, '聖默都狄(復位)', 'Metrophanes III (restored)', 1579, 1580],
  [187, '聖耶利米(復位)', 'Jeremias II (restored)', 1580, 1584],
  [188, '聖巴喜略二世', 'Pachomius II', 1584, 1585],
  [189, '聖德鐸德', 'Theoleptus II', 1585, 1586],
  [190, '聖耶利米(三任)', 'Jeremias II (3rd term)', 1587, 1595],
  [191, '聖瑪太二世', 'Matthew II', 1596, 1596],
  [192, '聖加百列', 'Gabriel I', 1596, 1596],
  [193, '聖德鐸鐸', 'Theophanes I', 1597, 1597],
  [194, '聖瑪太(復位)', 'Matthew II (restored)', 1598, 1602],
  [195, '聖尼斐特', 'Neophytos II', 1602, 1603],
  [196, '聖瑪太(三任)', 'Matthew II (3rd term)', 1603, 1603],
  [197, '聖拉斐爾二世', 'Raphael II', 1603, 1607],
  [198, '聖尼弗倫(復位)', 'Neophytos II (restored)', 1607, 1612],
  [199, '聖息羅一世', 'Cyril I Loukaris', 1612, 1612],
  [200, '聖底摩太二世', 'Timothy II', 1612, 1620],
  [201, '聖息羅(復位)', 'Cyril I Loukaris (restored)', 1620, 1623],
  [202, '聖額我略四世', 'Gregory IV', 1623, 1623],
  [203, '聖安提木二世', 'Anthimus II', 1623, 1623],
  [204, '聖息羅(三任)', 'Cyril I Loukaris (3rd)', 1623, 1633],
  [205, '聖息羅二世', 'Cyril II Kontares', 1633, 1633],
  [206, '聖息羅一世(四任)', 'Cyril I Loukaris (4th)', 1633, 1634],
  [207, '聖亞他納修三世', 'Athanasius III Patelaros', 1634, 1635],
  [208, '聖息羅(五任)', 'Cyril I Loukaris (5th)', 1637, 1638],
  [209, '聖亞他納修(復位)', 'Athanasius III (restored)', 1652, 1653],
  [210, '聖巴喜列', 'Paisius I', 1652, 1655],
  [211, '聖若亞尼基烏一世', 'Ioannicius II', 1646, 1656],
  [212, '聖息羅三世', 'Cyril III Spanos', 1652, 1654],
  [213, '聖巴喜列(復位)', 'Paisius I (restored)', 1654, 1655],
  [214, '聖若亞尼基烏(復位)', 'Ioannicius II (restored)', 1655, 1656],
  [215, '聖巴爾納', 'Parthenius III', 1656, 1657],
  [216, '聖加百列二世', 'Gabriel II', 1657, 1657],
  [217, '聖巴爾德尼', 'Parthenius IV', 1657, 1662],
  [218, '聖底奧尼修三世', 'Dionysius III Vardalis', 1662, 1665],
  [219, '聖巴爾德尼(復位)', 'Parthenius IV (restored)', 1665, 1667],
  [220, '聖克勉', 'Clement', 1667, 1667],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '君士坦丁堡', '東正教', ${st}, ${ed}, '逝世', '正統', 'Patriarchate of Constantinople official records', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Constantinople patriarchs (batch 4, Ottoman early)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
