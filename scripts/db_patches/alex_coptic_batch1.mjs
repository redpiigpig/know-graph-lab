/** Alexandria Coptic Orthodox patriarchs batch 1: #6-#60 (AD 118-768) */
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

// Already in DB: 1-5, 12, 24, 25, 38, 117, 118
const items = [
  [6,  '猶斯都', 'Justus', 118, 129],
  [7,  '優梅尼', 'Eumenes', 129, 142],
  [8,  '瑪可一世', 'Markianos', 142, 152],
  [9,  '塞拉皮翁', 'Celadion', 152, 166],
  [10, '亞加皮', 'Agrippinus', 167, 178],
  [11, '猶利安', 'Julian', 178, 189],
  // 12 已存在
  [13, '聖希拉克拉', 'Heraclas', 232, 248],
  [14, '聖丟尼修', 'Dionysius', 248, 264],
  [15, '聖瑪可西穆', 'Maximus', 264, 282],
  [16, '聖德鐸納', 'Theonas', 282, 300],
  [17, '聖伯多祿一世', 'Peter I', 300, 311],
  [18, '聖亞基拉', 'Achillas', 311, 312],
  [19, '聖亞歷山大一世', 'Alexander I', 312, 326],
  [20, '聖亞他納修一世', 'Athanasius the Great', 326, 373],
  [21, '聖伯多祿二世', 'Peter II', 373, 380],
  [22, '聖底摩太一世', 'Timothy I', 381, 385],
  [23, '聖德鐸非洛', 'Theophilus I', 385, 412],
  // 24, 25 already in DB
  [26, '聖底摩太二世', 'Timothy II Aelurus', 457, 477],
  [27, '聖伯多祿三世', 'Peter III Mongus', 477, 489],
  [28, '聖亞他納修二世', 'Athanasius II', 489, 496],
  [29, '聖約翰一世', 'John I', 496, 505],
  [30, '聖約翰二世', 'John II', 505, 516],
  [31, '聖底奧西', 'Dioscorus II', 516, 517],
  [32, '聖底摩太三世', 'Timothy III', 517, 535],
  [33, '聖德鐸西亞', 'Theodosius I', 535, 567],
  [34, '聖伯多祿四世', 'Peter IV', 567, 576],
  [35, '聖達米安', 'Damian', 576, 605],
  [36, '聖亞納斯塔修', 'Anastasius', 605, 616],
  [37, '聖安德魯尼', 'Andronicus', 616, 622],
  // 38 班雅明一世 already in DB
  [39, '聖亞加多', 'Agatho', 661, 677],
  [40, '聖約翰三世', 'John III', 677, 686],
  [41, '聖以撒', 'Isaac', 686, 689],
  [42, '聖息羅二世', 'Simon I', 689, 701],
  [43, '聖亞歷山大二世', 'Alexander II', 705, 730],
  [44, '聖科斯馬', 'Cosmas I', 730, 731],
  [45, '聖德鐸德', 'Theodore', 731, 743],
  [46, '聖米迦勒一世', 'Michael I', 743, 766],
  [47, '聖梅納', 'Mennas I', 766, 774],
  [48, '聖約翰四世', 'John IV', 776, 799],
  [49, '聖瑪可二世', 'Mark II', 799, 819],
  [50, '聖雅各', 'Jacob', 819, 830],
  [51, '聖息密', 'Simon II', 830, 830],
  [52, '聖約瑟', 'Joseph', 831, 849],
  [53, '聖米迦勒二世', 'Michael II', 849, 851],
  [54, '聖科斯馬二世', 'Cosmas II', 851, 858],
  [55, '聖薩努達一世', 'Shenouda I', 859, 880],
  [56, '聖米迦勒三世', 'Michael III', 880, 907],
  [57, '聖加百利一世', 'Gabriel I', 909, 920],
  [58, '聖科斯馬三世', 'Cosmas III', 920, 932],
  [59, '聖瑪可巴', 'Macarius I', 932, 952],
  [60, '聖德德', 'Theophanius', 952, 956],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '亞歷山卓', '科普特正教', ${st}, ${ed}, '逝世', '正統', 'Coptic Orthodox Patriarchate of Alexandria official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Alexandria Coptic patriarchs (batch 1)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
