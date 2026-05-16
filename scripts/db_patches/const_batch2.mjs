/** Constantinople patriarchs batch 2: #40-#100 (AD 518-906) */
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
  [40, '聖若望二世', 'John II of Cappadocia', 518, 520],
  [41, '聖伊巴芬', 'Epiphanius', 520, 535],
  [42, '聖安提木一世', 'Anthimus I', 535, 536],
  [43, '聖梅納', 'Menas', 536, 552],
  [44, '聖優提希', 'Eutychius', 552, 565],
  [45, '聖若望三世', 'John III Scholasticus', 565, 577],
  [46, '聖優提希(復位)', 'Eutychius (restored)', 577, 582],
  [47, '聖若望四世', 'John IV Nesteutes', 582, 595],
  [48, '聖息黎安二世', 'Cyriacus II', 596, 606],
  [49, '聖多默', 'Thomas I', 607, 610],
  [50, '聖塞爾爵一世', 'Sergius I', 610, 638],
  [51, '皮羅斯', 'Pyrrhus', 638, 641],
  [52, '保羅二世', 'Paul II', 641, 653],
  [53, '皮羅斯(復位)', 'Pyrrhus (restored)', 654, 654],
  [54, '伯多祿', 'Peter', 654, 666],
  [55, '聖多默二世', 'Thomas II', 667, 669],
  [56, '聖若望五世', 'John V', 669, 675],
  [57, '聖君士坦丁一世', 'Constantine I', 675, 677],
  [58, '聖德鐸', 'Theodore I', 677, 679],
  [59, '聖額我略一世', 'George I', 679, 686],
  [60, '聖德鐸(復位)', 'Theodore I (restored)', 686, 687],
  [61, '聖保羅三世', 'Paul III', 687, 693],
  [62, '聖卡里尼克一世', 'Callinicus I', 693, 705],
  [63, '聖息黎安三世', 'Cyrus', 706, 712],
  [64, '若望六世', 'John VI', 712, 715],
  [65, '聖該爾瑪諾一世', 'Germanus I', 715, 730],
  [66, '亞納斯塔修', 'Anastasius', 730, 754],
  [67, '君士坦丁二世', 'Constantine II', 754, 766],
  [68, '尼基塔一世', 'Nicetas I', 766, 780],
  [69, '聖保羅四世', 'Paul IV', 780, 784],
  [70, '聖塔拉修', 'Tarasios', 784, 806],
  [71, '聖尼基弗魯一世', 'Nikephoros I', 806, 815],
  [72, '德鐸德', 'Theodotus I Kassiteras', 815, 821],
  [73, '安東尼一世', 'Antony I Kassymatas', 821, 836],
  [74, '若望七世', 'John VII Grammatikos', 837, 843],
  [75, '聖默都狄一世', 'Methodius I', 843, 847],
  [76, '聖伊納爵一世', 'Ignatius', 847, 858],
  [77, '聖佛提一世', 'Photios I (the Great)', 858, 867],
  [78, '聖伊納爵一世(復位)', 'Ignatius (restored)', 867, 877],
  [79, '聖佛提一世(復位)', 'Photios I (restored)', 877, 886],
  [80, '聖斯德望一世', 'Stephen I', 886, 893],
  [81, '聖安東尼二世', 'Antony II Kauleas', 893, 901],
  [82, '聖尼古拉一世', 'Nicholas I Mystikos', 901, 907],
  [83, '聖優梯米一世', 'Euthymius I', 907, 912],
  [84, '聖尼古拉一世(復位)', 'Nicholas I (restored)', 912, 925],
  [85, '聖斯德望二世', 'Stephen II of Amaseia', 925, 928],
  [86, '聖德里巴', 'Tryphon', 928, 931],
  [87, '聖德奧菲拉', 'Theophylact', 933, 956],
  [88, '聖玻黎優德', 'Polyeuctus', 956, 970],
  [89, '聖巴西流一世', 'Basil I Skamandrenos', 970, 974],
  [90, '聖安東尼三世', 'Antony III the Studite', 974, 980],
  [91, '尼古拉二世', 'Nicholas II Chrysoberges', 984, 996],
  [92, '息辛尼斯二世', 'Sisinnius II', 996, 998],
  [93, '聖塞爾爵二世', 'Sergius II', 1001, 1019],
  [94, '聖優思塔提', 'Eustathius', 1019, 1025],
  [95, '聖亞列克斯一世', 'Alexius I Stoudites', 1025, 1043],
  [96, '聖米迦勒一世', 'Michael I Cerularius', 1043, 1058],
  [97, '聖君士坦丁三世', 'Constantine III Leichoudes', 1059, 1063],
  [98, '聖若望八世', 'John VIII Xiphilinos', 1064, 1075],
  [99, '聖科斯馬一世', 'Cosmas I', 1075, 1081],
  [100, '聖優思特拉提', 'Eustratius Garidas', 1081, 1084],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '君士坦丁堡', '未分裂教會', ${st}, ${ed}, '逝世', '正統', 'Patriarchate of Constantinople official records', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Constantinople patriarchs (batch 2)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
