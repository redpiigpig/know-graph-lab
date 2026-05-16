/** Rome popes batch 3: #101-#150 (AD 827-1145) */
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

const popes = [
  [101, '額我略四世',         'Pope Gregory IV',        827, 844, '逝世', null],
  [102, '塞爾爵二世',         'Pope Sergius II',        844, 847, '逝世', null],
  [103, '聖良四世',           'Pope Leo IV',            847, 855, '逝世', '抵禦撒拉森人'],
  [104, '本篤三世',           'Pope Benedict III',      855, 858, '逝世', null],
  [105, '聖尼古拉一世',       'Pope Nicholas I',        858, 867, '逝世', '加冕重要、推進教皇權'],
  [106, '哈德良二世',         'Pope Adrian II',         867, 872, '逝世', null],
  [107, '若望八世',           'Pope John VIII',         872, 882, '被謀殺', null],
  [108, '瑪利諾一世',         'Pope Marinus I',         882, 884, '逝世', null],
  [109, '聖哈德良三世',       'Pope Adrian III',        884, 885, '逝世', null],
  [110, '斯德望五世',         'Pope Stephen V',         885, 891, '逝世', null],
  [111, '福爾摩蘇',           'Pope Formosus',          891, 896, '逝世', '死後被「屍體公會」審判'],
  [112, '博尼法六世',         'Pope Boniface VI',       896, 896, '逝世', null],
  [113, '斯德望六世',         'Pope Stephen VI',        896, 897, '被廢黜後被勒死', '主導「屍體公會」'],
  [114, '羅馬諾',             'Pope Romanus',           897, 897, '逝世', null],
  [115, '德鐸二世',           'Pope Theodore II',       897, 897, '逝世', null],
  [116, '若望九世',           'Pope John IX',           898, 900, '逝世', null],
  [117, '本篤四世',           'Pope Benedict IV',       900, 903, '逝世', null],
  [118, '良五世',             'Pope Leo V',             903, 903, '被廢黜', null],
  [119, '塞爾爵三世',         'Pope Sergius III',       904, 911, '逝世', '「淫亂統治」開始'],
  [120, '亞納大削三世',       'Pope Anastasius III',    911, 913, '逝世', null],
  [121, '蘭多',               'Pope Lando',             913, 914, '逝世', null],
  [122, '若望十世',           'Pope John X',            914, 928, '被廢黜', null],
  [123, '良六世',             'Pope Leo VI',            928, 928, '逝世', null],
  [124, '斯德望七世',         'Pope Stephen VII',       928, 931, '逝世', null],
  [125, '若望十一世',         'Pope John XI',           931, 935, '逝世', null],
  [126, '良七世',             'Pope Leo VII',           936, 939, '逝世', null],
  [127, '斯德望八世',         'Pope Stephen VIII',      939, 942, '被謀殺', null],
  [128, '瑪利諾二世',         'Pope Marinus II',        942, 946, '逝世', null],
  [129, '亞加皮二世',         'Pope Agapetus II',       946, 955, '逝世', null],
  [130, '若望十二世',         'Pope John XII',          955, 964, '逝世', '加冕鄂圖一世為神聖羅馬皇帝'],
  [131, '良八世',             'Pope Leo VIII',          963, 965, '逝世', null],
  [132, '本篤五世',           'Pope Benedict V',        964, 966, '逝世', null],
  [133, '若望十三世',         'Pope John XIII',         965, 972, '逝世', null],
  [134, '本篤六世',           'Pope Benedict VI',       973, 974, '被謀殺', null],
  [135, '本篤七世',           'Pope Benedict VII',      974, 983, '逝世', null],
  [136, '若望十四世',         'Pope John XIV',          983, 984, '被謀殺', null],
  [137, '若望十五世',         'Pope John XV',           985, 996, '逝世', null],
  [138, '額我略五世',         'Pope Gregory V',         996, 999, '逝世', '首位德裔教宗'],
  [139, '西爾維斯特二世',     'Pope Sylvester II',      999, 1003, '逝世', '首位法國裔教宗、博學'],
  [140, '若望十七世',         'Pope John XVII',         1003, 1003, '逝世', null],
  [141, '若望十八世',         'Pope John XVIII',        1003, 1009, '退休', null],
  [142, '塞爾爵四世',         'Pope Sergius IV',        1009, 1012, '逝世', null],
  [143, '本篤八世',           'Pope Benedict VIII',     1012, 1024, '逝世', null],
  [144, '若望十九世',         'Pope John XIX',          1024, 1032, '逝世', null],
  [145, '本篤九世',           'Pope Benedict IX',       1032, 1044, '被廢黜', '三任三廢'],
  [146, '西爾維斯特三世',     'Pope Sylvester III',     1045, 1045, '被廢黜', null],
  [147, '額我略六世',         'Pope Gregory VI',        1045, 1046, '退位', null],
  [148, '克勉二世',           'Pope Clement II',        1046, 1047, '逝世', null],
  [149, '達瑪穌二世',         'Pope Damasus II',        1048, 1048, '逝世', null],
  [150, '聖良九世',           'Pope Leo IX',            1049, 1054, '逝世', '東西教會大分裂（1054）'],
];

const valuesParts = popes.map(p => {
  const [n, zh, en, st, ed, reason, notes] = p;
  const safeNotes = notes ? notes.replace(/'/g, "''") : null;
  return `(${n}, '${zh}', '${en}', '羅馬', '未分裂教會', ${st}, ${ed}, ${reason ? `'${reason}'` : 'NULL'}, '正統', 'Liber Pontificalis; Catholic Encyclopedia', ${safeNotes ? `'${safeNotes}'` : 'NULL'})`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${popes.length} popes (batch 3)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
