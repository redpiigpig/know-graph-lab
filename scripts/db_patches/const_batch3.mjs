/** Constantinople patriarchs batch 3: #101-#160 (AD 1084-1380) */
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
  [101, '聖尼古拉三世', 'Nicholas III Grammatikos', 1084, 1111],
  [102, '聖若望九世', 'John IX Agapetos', 1111, 1134],
  [103, '聖良斯提巴提', 'Leo Styppes', 1134, 1143],
  [104, '聖米迦勒二世', 'Michael II Kourkouas', 1143, 1146],
  [105, '聖科斯馬二世', 'Cosmas II Atticus', 1146, 1147],
  [106, '聖尼古拉四世', 'Nicholas IV Mouzalon', 1147, 1151],
  [107, '聖德鐸二世', 'Theodotus II', 1151, 1153],
  [108, '聖尼弗倫一世', 'Neophytos I', 1153, 1154],
  [109, '聖君士坦丁四世', 'Constantine IV Chliarenos', 1154, 1157],
  [110, '聖盧加', 'Luke Chrysoberges', 1157, 1170],
  [111, '聖米迦勒三世', 'Michael III of Anchialus', 1170, 1178],
  [112, '聖卡里尼克二世', 'Charitonen', 1178, 1179],
  [113, '聖德鐸西亞', 'Theodosius I Borradiotes', 1179, 1183],
  [114, '聖巴西流二世', 'Basil II Kamateros', 1183, 1186],
  [115, '聖尼基塔二世', 'Nicetas II Mountanes', 1186, 1189],
  [116, '聖德鐸西亞二世', 'Theodosius II', 1189, 1190],
  [117, '聖德鐸德二世', 'Dositheos', 1189, 1191],
  [118, '聖該爾瑪諾二世', 'George II Xiphilinos', 1191, 1198],
  [119, '聖約翰十世', 'John X Kamateros', 1198, 1206],
  [120, '聖米迦勒四世', 'Michael IV Autoreianos', 1207, 1213],
  [121, '聖德鐸德三世', 'Theodore II Eirenikos', 1214, 1216],
  [122, '聖瑪西米二世', 'Maximus II', 1216, 1216],
  [123, '聖瑪努伊', 'Manuel I Sarantenos', 1217, 1222],
  [124, '聖該爾瑪諾三世', 'Germanus II', 1223, 1240],
  [125, '聖默都狄二世', 'Methodius II', 1240, 1240],
  [126, '聖瑪努伊二世', 'Manuel II', 1244, 1254],
  [127, '聖亞爾沙二世', 'Arsenios Autoreianos', 1255, 1260],
  [128, '聖尼基弗魯二世', 'Nikephoros II', 1260, 1261],
  [129, '聖亞爾沙(復位)', 'Arsenios (restored)', 1261, 1265],
  [130, '聖該爾瑪諾四世', 'Germanus III', 1265, 1266],
  [131, '聖若瑟一世', 'Joseph I', 1266, 1275],
  [132, '聖若望十一世', 'John XI Bekkos', 1275, 1282],
  [133, '聖若瑟一世(復位)', 'Joseph I (restored)', 1282, 1283],
  [134, '聖額我略二世', 'Gregory II of Cyprus', 1283, 1289],
  [135, '聖亞他納修一世', 'Athanasius I', 1289, 1293],
  [136, '聖若望十二世', 'John XII Kosmas', 1294, 1303],
  [137, '聖亞他納修一世(復位)', 'Athanasius I (restored)', 1303, 1309],
  [138, '聖尼弗倫一世', 'Niphon I', 1310, 1314],
  [139, '聖若望十三世', 'John XIII Glykys', 1315, 1319],
  [140, '聖伊撒拉二世', 'Gerasimos I', 1320, 1321],
  [141, '聖伊撒拉三世', 'Isaiah', 1323, 1334],
  [142, '聖若望十四世', 'John XIV Kalekas', 1334, 1347],
  [143, '聖伊西多一世', 'Isidore I', 1347, 1350],
  [144, '聖卡里斯都一世', 'Callistus I', 1350, 1353],
  [145, '聖斐羅德', 'Philotheos Kokkinos', 1353, 1354],
  [146, '聖卡里斯都一世(復位)', 'Callistus I (restored)', 1355, 1363],
  [147, '聖斐羅德(復位)', 'Philotheos (restored)', 1364, 1376],
  [148, '聖瑪加略一世', 'Macarius', 1376, 1379],
  [149, '聖尼祿一世', 'Neilos Kerameus', 1380, 1388],
  [150, '聖安東尼四世', 'Antony IV', 1389, 1390],
  [151, '聖瑪加略(復位)', 'Macarius (restored)', 1390, 1391],
  [152, '聖安東尼四世(復位)', 'Antony IV (restored)', 1391, 1397],
  [153, '聖卡里斯都二世', 'Callistus II Xanthopoulos', 1397, 1397],
  [154, '聖瑪太一世', 'Matthew I', 1397, 1410],
  [155, '聖優提米', 'Euthymius II', 1410, 1416],
  [156, '聖若瑟二世', 'Joseph II', 1416, 1439],
  [157, '聖默通', 'Metrophanes II', 1440, 1443],
  [158, '聖額我略三世', 'Gregory III Mammas', 1443, 1450],
  [159, '聖亞他納修二世', 'Athanasius II', 1450, 1453],
  [160, '聖根那弟二世', 'Gennadius II Scholarius', 1454, 1456],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '君士坦丁堡', '東正教', ${st}, ${ed}, '逝世', '正統', 'Patriarchate of Constantinople official records', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Constantinople patriarchs (batch 3, post-1054 schism)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
