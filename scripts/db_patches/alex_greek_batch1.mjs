/** Alexandria Greek Orthodox patriarchs batch 1: #6-#60 (AD 189-680) */
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

// Existing in DB: 1-5 (Mark, Anianus, Avilius, Kedron, Primus) church=未分裂教會
//                 25 狄奧斯科爾一世 (Dioscorus I, 444-451) — pre-schism
//                 38 班雅明一世 — Coptic only?
//                 117 本篤十六世·沙努達三世, 118 教宗塔瓦德羅斯二世 — Coptic
// Alexandria GO + Coptic share #1-#27, then split at Council of Chalcedon (451)
//   #28+ are different in each tradition
// We'll insert as church='未分裂教會' for #6-#27, then church='東正教' for GO from #28
const items = [
  [6,  '猶斯都', 'Justus', 118, 129],
  [7,  '優梅尼', 'Eumenes', 129, 142],
  [8,  '瑪可一世', 'Markianos', 142, 152],
  [9,  '塞拉皮翁', 'Celadion', 152, 166],
  [10, '亞加皮', 'Agrippinus', 167, 178],
  [11, '猶利安', 'Julian', 178, 189],
  [12, '聖德米特里一世', 'Demetrius I', 189, 232],
  [13, '聖希拉克拉', 'Heraclas', 232, 248],
  [14, '聖丟尼修', 'Dionysius', 248, 264],
  [15, '聖瑪可西穆', 'Maximus', 264, 282],
  [16, '聖德鐸納', 'Theonas', 282, 300],
  [17, '聖伯多祿一世', 'Peter I', 300, 311],
  [18, '聖亞基拉', 'Achillas', 312, 313],
  [19, '聖亞歷山大一世', 'Alexander I', 313, 326],
  [20, '聖亞他納修一世', 'Athanasius the Great', 326, 373],
  [21, '聖伯多祿二世', 'Peter II', 373, 380],
  [22, '聖底摩太一世', 'Timothy I', 381, 385],
  [23, '聖德鐸非洛', 'Theophilus I', 385, 412],
  [24, '聖息羅一世', 'Cyril I', 412, 444],
  // 25 狄奧斯科爾一世 already in DB
  [26, '聖普羅特里', 'Proterius', 451, 457],
  [27, '提摩太二世', 'Timothy II Aelurus', 457, 460],
  [28, '聖薩洛弗修', 'Salofaciolus', 460, 475],
  [29, '聖約翰一世', 'John I Talaia', 482, 482],
  [30, '聖伯多祿三世', 'Peter III Mongus', 482, 489],
  [31, '聖亞他納修二世', 'Athanasius II Keletes', 490, 496],
  [32, '聖約翰二世', 'John II', 496, 505],
  [33, '聖約翰三世', 'John III the Hemulah', 505, 516],
  [34, '聖底摩太三世', 'Timothy III', 517, 535],
  [35, '聖德鐸西亞', 'Theodosius I', 535, 537],
  [36, '聖加偯安', 'Gainas', 537, 540],
  [37, '聖斐連', 'Paul of Tabennese', 540, 541],
  [38, '聖斯米諾', 'Zoilus', 541, 551],
  [39, '聖亞坡里納', 'Apollinarius', 551, 570],
  [40, '聖約翰四世', 'John IV', 569, 579],
  [41, '聖優洛提', 'Eulogius', 580, 607],
  [42, '聖德鐸德', 'Theodore Scribo', 607, 609],
  [43, '聖若望', 'John V the Almoner', 609, 620],
  [44, '聖該爾瑪', 'George I', 621, 631],
  [45, '聖息祿', 'Cyrus', 631, 642],
  [46, '聖伯多祿四世', 'Peter IV', 642, 651],
  [47, '聖德鐸德二世', 'Theodore I', 666, 669],
  [48, '聖約翰六世', 'John VI', 669, 689],
  [49, '聖伊撒拉', 'Isaac', 689, 692],
  [50, '聖息羅二世', 'Cyril II of Alexandria', 692, 718],
  [51, '聖科斯馬', 'Cosmas I', 727, 768],
  [52, '聖玻黎優德', 'Polyeuctus', 770, 779],
  [53, '聖克里斯多多羅', 'Christophorus I', 805, 836],
  [54, '聖佐波利斯', 'Sophronius II', 836, 859],
  [55, '聖米迦勒一世', 'Michael I', 870, 903],
  [56, '聖克里斯多多羅二世', 'Christophorus II', 907, 932],
  [57, '聖優提希', 'Eutychius', 933, 940],
  [58, '聖索弗洛尼三世', 'Sophronius III', 941, 960],
  [59, '聖伊撒拉二世', 'Isaac II', 941, 954],
  [60, '聖約伯', 'Job', 954, 960],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  // pre-451 (Council of Chalcedon) church=未分裂教會, post-451 GO=東正教
  const church = n < 26 ? '未分裂教會' : '東正教';
  return `(${n}, '${zh}', '${en}', '亞歷山卓', '${church}', ${st}, ${ed}, '逝世', '正統', 'Greek Orthodox Patriarchate of Alexandria official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Alexandria GO patriarchs (batch 1)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
