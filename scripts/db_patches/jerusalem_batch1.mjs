/** Jerusalem patriarchs batch 1: #6-#80 (AD 100-980) */
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

// Existing: #1 義人雅各伯, #2 西默盎, #3 猶斯都一世, #4 匝哈烏斯, #5 托比亞斯
const items = [
  [6,  '聖班雅明一世', 'Benjamin I', 117, 119],
  [7,  '聖約翰一世', 'John I', 119, 121],
  [8,  '聖瑪太一世', 'Matthias I', 121, 124],
  [9,  '聖斐力一世', 'Philip', 124, 130],
  [10, '聖塞尼加斯', 'Seneca', 130, 132],
  [11, '聖猶斯都二世', 'Justus II', 132, 134],
  [12, '聖良未', 'Levi', 134, 135],
  [13, '聖以法蓮一世', 'Ephraim I', 135, 137],
  [14, '聖約瑟', 'Joseph', 137, 140],
  [15, '聖猶大', 'Judas', 140, 142],
  [16, '聖瑪可', 'Mark', 142, 154],
  [17, '聖卡西', 'Cassianus', 154, 156],
  [18, '聖普布利', 'Publius', 156, 161],
  [19, '聖瑪克西穆', 'Maximus I', 161, 167],
  [20, '聖朱利安', 'Julian I', 167, 168],
  [21, '聖該約', 'Gaius I', 168, 175],
  [22, '聖息馬科', 'Symmachus', 175, 175],
  [23, '聖該約二世', 'Gaius II', 175, 177],
  [24, '聖朱利安二世', 'Julian II', 177, 185],
  [25, '聖卡皮托', 'Capito', 185, 196],
  [26, '聖瑪克西穆二世', 'Maximus II', 196, 198],
  [27, '聖安提木', 'Antoninus', 198, 199],
  [28, '聖瓦倫', 'Valens', 199, 211],
  [29, '聖納斯丁', 'Narcissus', 211, 213],
  [30, '聖度斯', 'Dius', 213, 220],
  [31, '聖額爾瑪諾', 'Germanus', 220, 230],
  [32, '聖戈爾狄', 'Gordius', 230, 231],
  [33, '聖納斯丁(復位)', 'Narcissus (restored)', 231, 250],
  [34, '聖亞歷山大', 'Alexander', 251, 251],
  [35, '聖瑪查那', 'Mazabanes', 251, 260],
  [36, '聖喜美奈', 'Hymenaeus', 260, 298],
  [37, '聖匝布達', 'Zabdas', 298, 300],
  [38, '聖以耳邁', 'Hermon', 300, 314],
  [39, '聖瑪加略', 'Macarius I', 314, 333],
  [40, '聖瑪克西穆三世', 'Maximus III', 333, 348],
  [41, '聖息利祿', 'Cyril I', 350, 386],
  [42, '聖約翰二世', 'John II', 386, 417],
  [43, '聖布雷西', 'Praylius', 417, 422],
  [44, '聖猶威納', 'Juvenal', 422, 458],
  [45, '聖亞納斯塔修一世', 'Anastasius I', 458, 478],
  [46, '聖瑪爾廷', 'Martyrius', 478, 486],
  [47, '聖息羅', 'Sallustius', 486, 494],
  [48, '聖伊里亞一世', 'Elias I', 494, 516],
  [49, '聖約翰三世', 'John III', 516, 524],
  [50, '聖伯多祿', 'Peter I', 524, 552],
  [51, '聖瑪加略二世', 'Macarius II', 552, 564],
  [52, '聖優托基', 'Eustochius', 564, 575],
  [53, '聖約翰四世', 'John IV', 575, 593],
  [54, '聖亞瑪斯', 'Amos', 594, 600],
  [55, '聖伊撒卡', 'Isaac', 601, 609],
  [56, '聖匝加', 'Zacharias', 609, 631],
  [57, '聖默勒底', 'Modestus', 631, 634],
  [58, '聖索弗洛尼一世', 'Sophronius I', 634, 638],
  [59, '聖德奧多里', 'Theodore I', 638, 653],
  [60, '聖約翰五世', 'John V', 706, 735],
  [61, '聖德奧多里二世', 'Theodore II', 735, 770],
  [62, '聖以利亞二世', 'Elias II', 770, 797],
  [63, '聖喬治', 'George', 797, 807],
  [64, '聖約翰六世', 'John VI', 807, 820],
  [65, '聖德奧多里三世', 'Theodore III', 820, 836],
  [66, '聖巴喜略', 'Basil', 836, 839],
  [67, '聖約翰七世', 'John VII', 839, 843],
  [68, '聖塞爾季', 'Sergius I', 843, 859],
  [69, '聖索羅米', 'Solomon', 860, 865],
  [70, '聖德奧多西', 'Theodosius', 867, 884],
  [71, '聖以利亞三世', 'Elias III', 879, 907],
  [72, '聖塞爾季二世', 'Sergius II', 908, 911],
  [73, '聖良提', 'Leontius I', 912, 929],
  [74, '聖阿塔納修一世', 'Athanasius I', 929, 937],
  [75, '聖克利斯多多羅', 'Christodulus', 937, 950],
  [76, '聖亞加多', 'Agathon', 950, 964],
  [77, '聖約翰八世', 'John VIII', 964, 966],
  [78, '聖克利斯多多羅二世', 'Christodulus II', 966, 969],
  [79, '聖德謨諾', 'Thomas I', 969, 977],
  [80, '聖約瑟二世', 'Joseph II', 980, 984],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  return `(${n}, '${zh}', '${en}', '耶路撒冷', '未分裂教會', ${st}, ${ed}, '逝世', '正統', 'Greek Orthodox Patriarchate of Jerusalem official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${items.length} Jerusalem patriarchs (batch 1)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
