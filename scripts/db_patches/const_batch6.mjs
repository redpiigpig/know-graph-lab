/** Constantinople patriarchs batch 6: #268-#270 modern (1840-2025); fix #268 雅典納哥拉一世 year */
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

// First, fix the existing 雅典納哥拉一世 record
console.log("== Fix existing 雅典納哥拉一世 (was #268 1948-) — should be 1948-1972 ==");
console.log(await q(`
  UPDATE episcopal_succession
  SET succession_number = 286, start_year = 1948, end_year = 1972, end_reason = '逝世'
  WHERE see='君士坦丁堡' AND name_zh='雅典納哥拉一世' RETURNING name_zh, succession_number, start_year, end_year;
`));

// Then insert #268-#287
const items = [
  [268, '聖安提木四世', 'Anthimus IV', 1840, 1841],
  [269, '聖安提木五世', 'Anthimus V', 1841, 1842],
  [270, '聖該爾瑪諾六世', 'Germanus IV', 1842, 1845],
  [271, '聖默勒底', 'Meletius III', 1845, 1845],
  [272, '聖額我略七世', 'Anthimus VI', 1845, 1848],
  [273, '聖君士坦丁七世', 'Anthimus IV (restored)', 1848, 1852],
  [274, '聖該爾瑪諾(復位)', 'Germanus IV (restored)', 1852, 1853],
  [275, '聖安提木六世(三任)', 'Anthimus VI (3rd term)', 1853, 1855],
  [276, '聖息羅七世', 'Cyril VII', 1855, 1860],
  [277, '聖若亞撒(復位)', 'Joachim II', 1860, 1863],
  [278, '聖索弗洛尼三世', 'Sophronius III', 1863, 1866],
  [279, '聖額我略八世', 'Gregory VI (restored)', 1867, 1871],
  [280, '聖安提木(四任)', 'Anthimus VI (4th term)', 1871, 1873],
  [281, '聖若亞撒(復位二)', 'Joachim II (restored)', 1873, 1878],
  [282, '聖若亞撒三世', 'Joachim III', 1878, 1884],
  [283, '聖若亞撒四世', 'Joachim IV', 1884, 1886],
  [284, '聖底奧尼修五世', 'Dionysius V', 1887, 1891],
  [285, '聖尼弗倫八世', 'Neophytos VIII', 1891, 1894],
  // 286 already updated above (雅典納哥拉一世)
  [287, '德米特里一世', 'Demetrios I', 1972, 1991],
  [288, '巴爾多祿茂一世', 'Bartholomew I', 1991, null],
];

const valuesParts = items.map(p => {
  const [n, zh, en, st, ed] = p;
  const isCurrent = ed === null;
  return `(${n}, '${zh}', '${en}', '君士坦丁堡', '東正教', ${st}, ${ed === null ? 'NULL' : ed}, ${isCurrent ? 'NULL' : "'逝世'"}, '正統', 'Ecumenical Patriarchate official', NULL)`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`\n== Inserting ${items.length} Constantinople patriarchs (batch 6, modern) ==`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
