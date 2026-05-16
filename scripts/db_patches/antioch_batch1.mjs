/** Antioch Greek Orthodox patriarchs batch 1: #6-#80 (AD 273-799) */
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

// Existing: 1 聖伯多祿, 2 以沃迪烏斯, 3 聖依納爵, 4 海羅, 5 科爾涅利烏斯
const items = [
  [6,  '艾羅斯', 'Eros', 100, 127],
  [7,  '德奧菲洛', 'Theophilus', 169, 182],
  [8,  '聖瑪克西米諾', 'Maximinus I', 182, 191],
  [9,  '聖塞拉皮翁', 'Serapion', 191, 211],
  [10, '聖亞斯克列匹亞', 'Asclepiades the Confessor', 211, 220],
  [11, '聖斐萊圖', 'Philetus', 220, 231],
  [12, '聖左比諾', 'Zebinnus', 231, 237],
  [13, '聖巴比拉', 'Babylas', 237, 253],
  [14, '聖斐比烏斯', 'Fabius', 253, 256],
  [15, '聖德米特里', 'Demetrian', 256, 263],
  [16, '帕奧祿', 'Paul of Samosata', 260, 268],
  [17, '聖德謨諾', 'Domnus I', 268, 273],
  [18, '聖底摩泰', 'Timaeus', 273, 277],
  [19, '聖息羅', 'Cyril I', 277, 299],
  [20, '聖底連諾', 'Tyrannion', 299, 308],
  [21, '聖維塔利諾', 'Vitalius', 308, 314],
  [22, '聖斐羅特', 'Philogonius', 314, 324],
  [23, '聖優斯塔修', 'Eustathius', 324, 330],
  [24, '聖保利諾', 'Paulinus I', 330, 332],
  [25, '聖優拉里', 'Eulalius', 332, 333],
  [26, '聖優弗洛尼', 'Euphronius', 333, 334],
  [27, '聖弗拉切拉', 'Flacillus', 334, 342],
  [28, '聖斯德范', 'Stephen I', 342, 344],
  [29, '聖良提', 'Leontius', 344, 358],
  [30, '聖優多西', 'Eudoxius', 358, 360],
  [31, '聖默勒底', 'Meletius', 360, 381],
  [32, '聖弗拉維安', 'Flavian I', 381, 404],
  [33, '聖伯爾治羅', 'Porphyrius', 404, 412],
  [34, '聖亞歷山大', 'Alexander', 412, 417],
  [35, '聖德鐸德', 'Theodotus', 417, 428],
  [36, '聖約翰一世', 'John I', 428, 442],
  [37, '聖德謨諾二世', 'Domnus II', 442, 449],
  [38, '聖瑪克西穆', 'Maximus', 449, 455],
  [39, '聖巴西耳', 'Basil', 456, 459],
  [40, '聖亞加皮', 'Acacius', 459, 461],
  [41, '聖瑪丁', 'Martyrius', 461, 465],
  [42, '聖伯多祿', 'Peter the Fuller', 469, 471],
  [43, '聖朱利安', 'Julian', 471, 476],
  [44, '聖伯多祿(復位)', 'Peter the Fuller (restored)', 476, 477],
  [45, '聖約翰二世', 'John Codonatus', 477, 478],
  [46, '聖斯德范二世', 'Stephen II', 478, 481],
  [47, '聖斯德范三世', 'Stephen III', 481, 485],
  [48, '聖加蘭', 'Calandion', 485, 488],
  [49, '聖伯多祿(三任)', 'Peter the Fuller (3rd)', 488, 488],
  [50, '聖帕拉狄', 'Palladius', 488, 498],
  [51, '聖弗拉維安', 'Flavian II', 498, 512],
  [52, '聖塞維羅', 'Severus', 512, 518],
  [53, '聖保羅', 'Paul II', 518, 521],
  [54, '聖優弗拉西', 'Euphrasius', 521, 526],
  [55, '聖以法蓮', 'Ephraim of Antioch', 527, 545],
  [56, '聖德謨諾三世', 'Domnus III', 545, 559],
  [57, '聖亞納斯塔修', 'Anastasius I Sinaita', 559, 570],
  [58, '聖額我略', 'Gregory', 570, 593],
  [59, '聖亞納斯塔修(復位)', 'Anastasius I (restored)', 593, 599],
  [60, '聖亞納斯塔修二世', 'Anastasius II', 599, 609],
  [61, '聖額我略二世', 'Gregory II', 610, 620],
  [62, '聖亞納斯塔修三世', 'Anastasius III', 620, 628],
  [63, '聖瑪加略', 'Macarius', 628, 643],
  [64, '聖瑪加略二世', 'Macarius II', 643, 656],
  [65, '聖瑪加略三世', 'Macarius III', 656, 681],
  [66, '聖德奧法尼', 'Theophanes', 681, 687],
  [67, '聖塞巴斯', 'Sebastian', 687, 690],
  [68, '聖額我略三世', 'Gregory III', 690, 702],
  [69, '聖亞歷山大二世', 'Alexander II', 702, 707],
  [70, '聖斯德范四世', 'Stephen IV', 707, 715],
  [71, '聖德鐸德二世', 'Theodore II', 716, 750],
  [72, '聖德奧法克', 'Theodorus II', 750, 773],
  [73, '聖約翰四世', 'John IV', 779, 784],
  [74, '聖德奧多瑞', 'Theodoret', 784, 787],
  [75, '聖約伯', 'Job', 799, 833],
  [76, '聖尼古拉一世', 'Nicholas I', 847, 869],
  [77, '聖斯德范五世', 'Stephen V', 870, 880],
  [78, '聖德奧多西', 'Theodosius I', 887, 896],
  [79, '聖息羅二世', 'Simeon I', 896, 904],
  [80, '聖伊利亞', 'Elias I', 904, 934],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '安提阿', '未分裂教會', ${st}, ${ed}, '逝世', '正統', 'Greek Orthodox Patriarchate of Antioch official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Antioch GO patriarchs (batch 1)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
