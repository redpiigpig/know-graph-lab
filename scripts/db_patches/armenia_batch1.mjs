/** Armenia (埃奇米亞津) catholicoi batch 1: #3-#80 (AD 333-1100) */
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

// Existing in DB:
// #1 聖額我略·啟蒙者 301-325, #2 阿里斯塔科斯 325-333,
// #4 涅爾塞斯一世 353-373, #8 聖撒哈克一世 387-438
const items = [
  [3,  '弗爾塔尼斯', 'Vrtanes', 333, 341],
  // 4 already in DB
  [5,  '聖薩哈克(早期)', 'Hovsep I', 341, 348],
  [6,  '聖納薩斯', 'Husik I', 348, 359],
  [7,  '聖法倫', 'Pharen I', 359, 367],
  // 8 already
  [9,  '聖伯斯陶斯', 'Brkisho', 442, 465],
  [10, '聖梅萊蒂', 'Shmuel I', 465, 475],
  [11, '聖默薩斯', 'Mushe I', 475, 484],
  [12, '聖巴布根一世', 'Babgen I', 490, 516],
  [13, '聖薩繆爾一世', 'Samuel I', 516, 526],
  [14, '聖穆薩', 'Mushe II', 526, 534],
  [15, '聖薩克一世', 'Sahak II', 534, 539],
  [16, '聖克里斯多福', 'Christopher I', 539, 545],
  [17, '聖奈爾塞斯二世', 'Nerses II', 548, 557],
  [18, '聖約翰二世', 'Hovhannes II', 557, 574],
  [19, '聖摩西二世', 'Movses II', 574, 604],
  [20, '聖亞伯拉罕一世', 'Abraham I', 607, 615],
  [21, '聖科米塔斯', 'Komitas I', 615, 628],
  [22, '聖克里斯多福二世', 'Christopher II', 628, 630],
  [23, '聖艾澤爾一世', 'Ezr I', 630, 641],
  [24, '聖納薩斯三世', 'Nerses III the Builder', 641, 661],
  [25, '聖阿納斯塔', 'Anastas I', 661, 667],
  [26, '聖伊利亞', 'Israel I', 667, 677],
  [27, '聖薩哈克三世', 'Sahak III', 677, 703],
  [28, '聖以利亞一世', 'Yeghia I', 703, 717],
  [29, '聖約翰三世', 'Hovhannes III Odznetsi', 717, 728],
  [30, '聖大衛一世', 'David I', 728, 741],
  [31, '聖崔達特一世', 'Trdat I', 741, 764],
  [32, '聖崔達特二世', 'Trdat II', 764, 767],
  [33, '聖息馬翁', 'Sion I', 767, 775],
  [34, '聖艾澤爾', 'Esayi I', 775, 788],
  [35, '聖斯德范一世', 'Stepanos I', 788, 790],
  [36, '聖約亞伯', 'Hovab I', 790, 791],
  [37, '聖所羅門一世', 'Soghomon I', 791, 792],
  [38, '聖喬治一世', 'Gevorg I', 792, 795],
  [39, '聖約瑟一世', 'Hovsep II', 795, 806],
  [40, '聖大衛二世', 'David II', 806, 833],
  [41, '聖約翰四世', 'Hovhannes IV', 833, 855],
  [42, '聖薩哈克四世', 'Zakaria I', 855, 877],
  [43, '聖喬治二世', 'Gevorg II', 877, 897],
  [44, '聖瑪斯托', 'Mashtots I', 897, 898],
  [45, '聖約翰五世', 'Hovhannes V', 899, 929],
  [46, '聖斯德范二世', 'Stepanos II', 929, 930],
  [47, '聖德奧多里', 'Theodoros I', 930, 941],
  [48, '聖艾澤爾三世', 'Eghishe I', 941, 946],
  [49, '聖阿納尼亞', 'Ananias I Mokatsi', 946, 968],
  [50, '聖瓦罕', 'Vahan I', 968, 969],
  [51, '聖斯德范三世', 'Stepanos III', 969, 972],
  [52, '聖科米塔斯二世', 'Khachik I', 972, 992],
  [53, '聖薩哈克五世', 'Sargis I', 992, 1019],
  [54, '聖伯多祿一世', 'Petros I Getadardz', 1019, 1058],
  [55, '聖科米塔斯三世', 'Khachik II', 1058, 1065],
  [56, '聖額我略二世', 'Grigor II Vkayaser', 1066, 1105],
  [57, '聖巴蘇基', 'Barseg I Anetsi', 1105, 1113],
  [58, '聖額我略三世', 'Grigor III Pahlavuni', 1113, 1166],
  [59, '聖內爾塞斯四世', 'Nerses IV Shnorhali', 1166, 1173],
  [60, '聖額我略四世', 'Grigor IV Tgha', 1173, 1193],
  [61, '聖額我略五世', 'Grigor V Karavezh', 1193, 1194],
  [62, '聖額我略六世', 'Grigor VI Apirat', 1194, 1203],
  [63, '聖約翰六世', 'Hovhannes VI Ssetsi', 1203, 1221],
  [64, '聖君士坦丁一世', 'Konstandin I Bardzraberdtsi', 1221, 1267],
  [65, '聖雅各一世', 'Hakob I Klayetsi', 1268, 1286],
  [66, '聖君士坦丁二世', 'Konstandin II Pronagortz', 1286, 1289],
  [67, '聖斯德范五世', 'Stepanos IV Hromklayetsi', 1290, 1293],
  [68, '聖額我略七世', 'Grigor VII Anavarzetsi', 1293, 1307],
  [69, '聖君士坦丁三世', 'Konstandin III Kesaratsi', 1307, 1322],
  [70, '聖君士坦丁四世', 'Konstandin IV Lambronatsi', 1322, 1326],
  [71, '聖雅各二世', 'Hakob II', 1327, 1341],
  [72, '聖梅基塔', 'Mkhitar I Grnertsi', 1341, 1355],
  [73, '聖梅西亞', 'Mesrop I Artazetsi', 1359, 1372],
  [74, '聖君士坦丁五世', 'Konstandin V Sisetsi', 1372, 1374],
  [75, '聖玻嘔斯', 'Poghos I Sisetsi', 1374, 1382],
  [76, '聖德奧多魯', 'Teodoros II Kilikietsi', 1382, 1392],
  [77, '聖卡拉佩特', 'Karapet I Keghetsi', 1393, 1404],
  [78, '聖雅各三世', 'Hakob III Sisetsi', 1404, 1411],
  [79, '聖額我略八世', 'Grigor VIII Khantsoghats', 1411, 1418],
  [80, '聖玻烏', 'Poghos II Garnetsi', 1418, 1430],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '埃奇米亞津', '亞美尼亞使徒教會', ${st}, ${ed}, '逝世', '正統', 'Mother See of Holy Etchmiadzin official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Armenia catholicoi (batch 1)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
