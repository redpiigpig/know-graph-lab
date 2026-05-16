/** Constantinople patriarchs batch 1: #2-#60 (AD 54-518) */
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

// Already in DB: #1 斯達基斯, #2 阿尼西莫, #3 波利加坡一世, #4 普路克, #16 美特羅法內斯一世
// Skip those.
const items = [
  // [succ_no, name_zh, name_en, start, end]
  [5,  '塞德基奧', 'Sedecion', 105, 114],
  [6,  '迪奧根尼', 'Diogenes', 114, 129],
  [7,  '艾留德流', 'Eleutherius', 129, 136],
  [8,  '腓力斯', 'Felix', 136, 141],
  [9,  '波利加坡二世', 'Polycarpus II', 141, 144],
  [10, '亞他諾多羅', 'Athenodorus', 144, 148],
  [11, '優善底', 'Euzois', 148, 154],
  [12, '勞倫斯', 'Laurence', 154, 166],
  [13, '亞利庇', 'Alypius', 166, 169],
  [14, '佩鐸里諾斯', 'Pertinax', 169, 187],
  [15, '聖奧林匹安', 'Olympianus', 187, 198],
  // #16 美特羅法內斯 already in DB (skip)
  [17, '聖亞力山大', 'Alexander', 314, 337],
  [18, '保羅一世', 'Paul I (the Confessor)', 337, 339],
  [19, '優西比烏', 'Eusebius of Nicomedia', 339, 341],
  [20, '馬其頓尼一世', 'Macedonius I', 342, 360],
  [21, '優德修', 'Eudoxius', 360, 370],
  [22, '德摩斐祿', 'Demophilus', 370, 380],
  [23, '聖額我略·納齊安', 'Gregory of Nazianzus', 379, 381],
  [24, '聖內克塔流', 'Nectarius', 381, 397],
  [25, '聖若望·屈梭多模', 'John Chrysostom', 398, 404],
  [26, '亞爾沙修', 'Arsacius', 404, 405],
  [27, '阿提庫', 'Atticus', 406, 425],
  [28, '息辛尼斯一世', 'Sisinnius I', 426, 427],
  [29, '聶斯多留', 'Nestorius', 428, 431],
  [30, '聖瑪西米安', 'Maximian', 431, 434],
  [31, '聖普羅克魯斯', 'Proclus', 434, 446],
  [32, '聖弗拉維安', 'Flavian', 446, 449],
  [33, '聖阿納托利', 'Anatolius', 449, 458],
  [34, '聖根那弟', 'Gennadius I', 458, 471],
  [35, '聖亞迦修', 'Acacius', 471, 489],
  [36, '弗拉維塔', 'Fravitta', 489, 490],
  [37, '聖優斐米', 'Euphemius', 490, 496],
  [38, '聖瑪克都尼二世', 'Macedonius II', 496, 511],
  [39, '提摩太一世', 'Timothy I', 511, 518],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '君士坦丁堡', '未分裂教會', ${st}, ${ed}, '逝世', '正統', 'Synaxarion of Constantinople; Patriarchate of Constantinople official records', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Constantinople patriarchs (batch 1)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
