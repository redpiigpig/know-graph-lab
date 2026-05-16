/**
 * Rome popes — batch 1 of 6 (popes #6-#50, covers AD 107-498)
 *
 * Names follow Taiwan/HK Catholic 中譯 conventions (preferred when officially published);
 * otherwise standard 大公教 transliteration. Source: 教廷年鑑、天主教中文 wiki、Liber Pontificalis.
 * Using ON CONFLICT DO NOTHING so re-runs are idempotent.
 *
 * Strategy: only insert succession_number > 5 OR != 64 to avoid duplicating
 * existing rows.
 */
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
  const txt = await res.text();
  if (!res.ok) { console.error("FAIL:", txt); process.exit(1); }
  return JSON.parse(txt);
}

// Each entry: [succ_no, name_zh, name_en, start, end, end_reason, notes_short]
const popes = [
  [6,  '聖亞歷山大一世',     'Pope Alexander I',     107, 115, '殉道', null],
  [7,  '聖息斯篤一世',       'Pope Sixtus I',        115, 125, '殉道', null],
  [8,  '聖德肋斯福魯',       'Pope Telesphorus',     125, 136, '殉道', null],
  [9,  '聖修今',             'Pope Hyginus',         136, 140, '殉道', null],
  [10, '聖庇護一世',         'Pope Pius I',          140, 155, '殉道', null],
  [11, '聖盎日道',           'Pope Anicetus',        155, 166, '殉道', null],
  [12, '聖蘇德爾',           'Pope Soter',           166, 175, '殉道', null],
  [13, '聖艾流德祿斯',       'Pope Eleutherius',     175, 189, '逝世', null],
  [14, '聖維克托一世',       'Pope Victor I',        189, 199, '殉道', '北非首位拉丁語教宗'],
  [15, '聖則斐林諾',         'Pope Zephyrinus',      199, 217, '逝世', null],
  [16, '聖加里斯都一世',     'Pope Callixtus I',     217, 222, '殉道', null],
  [17, '聖烏爾班一世',       'Pope Urban I',         222, 230, '逝世', null],
  [18, '聖龐弟亞諾',         'Pope Pontian',         230, 235, '退位後殉道', '首位主動退位教宗'],
  [19, '聖安泰魯斯',         'Pope Anterus',         235, 236, '殉道', null],
  [20, '聖法比盎',           'Pope Fabian',          236, 250, '殉道', '德西鳥斯逼害下殉道'],
  [21, '聖科爾乃略',         'Pope Cornelius',       251, 253, '殉道', '與對立教宗諾窪天爭'],
  [22, '聖路修一世',         'Pope Lucius I',        253, 254, '殉道', null],
  [23, '聖斯德望一世',       'Pope Stephen I',       254, 257, '殉道', null],
  [24, '聖息斯篤二世',       'Pope Sixtus II',       257, 258, '殉道', '瓦肋良逼害'],
  [25, '聖丟尼修一世',       'Pope Dionysius',       259, 268, '逝世', null],
  [26, '聖斐理斯一世',       'Pope Felix I',         269, 274, '逝世', null],
  [27, '聖歐底其雅諾',       'Pope Eutychian',       275, 283, '逝世', null],
  [28, '聖加約斯',           'Pope Caius',           283, 296, '逝世', null],
  [29, '聖瑪策林',           'Pope Marcellinus',     296, 304, '殉道', '戴克里仙逼害'],
  [30, '聖瑪爾賽琉一世',     'Pope Marcellus I',     308, 309, '逝世', null],
  [31, '聖恩西比',           'Pope Eusebius',        309, 309, '流亡逝世', null],
  [32, '聖默基亞德',         'Pope Miltiades',       311, 314, '逝世', '米蘭詔書時期'],
  [33, '聖西維斯特一世',     'Pope Sylvester I',     314, 335, '逝世', '尼西亞大公會議；君士坦丁皈依時期'],
  [34, '聖瑪爾谷',           'Pope Mark',            336, 336, '逝世', null],
  [35, '聖儒略一世',         'Pope Julius I',        337, 352, '逝世', null],
  [36, '利貝里',             'Pope Liberius',        352, 366, '逝世', null],
  [37, '聖達瑪穌一世',       'Pope Damasus I',       366, 384, '逝世', '委託耶柔米譯武加大本'],
  [38, '聖西利修',           'Pope Siricius',        384, 399, '逝世', '首位以「教宗」自稱者'],
  [39, '聖亞納大削一世',     'Pope Anastasius I',    399, 401, '逝世', null],
  [40, '聖依諾增爵一世',     'Pope Innocent I',      401, 417, '逝世', '羅馬被哥德人攻陷時'],
  [41, '聖佐西睦',           'Pope Zosimus',         417, 418, '逝世', null],
  [42, '聖博尼法一世',       'Pope Boniface I',      418, 422, '逝世', null],
  [43, '聖塞肋斯定一世',     'Pope Celestine I',     422, 432, '逝世', '以弗所大公會議'],
  [44, '聖思道三世',         'Pope Sixtus III',      432, 440, '逝世', null],
  [45, '聖大良一世',         'Pope Leo I (the Great)', 440, 461, '逝世', '迦克墩大公會議；阻退匈奴'],
  [46, '聖義拉略',           'Pope Hilarius',        461, 468, '逝世', null],
  [47, '聖辛普利修',         'Pope Simplicius',      468, 483, '逝世', '西羅馬帝國滅亡 (476)'],
  [48, '聖斐理斯三世',       'Pope Felix III',       483, 492, '逝世', null],
  [49, '聖嘉修西',           'Pope Gelasius I',      492, 496, '逝世', null],
  [50, '亞納大削二世',       'Pope Anastasius II',   496, 498, '逝世', null],
];

// Build INSERT statement
const valuesParts = popes.map(p => {
  const [n, zh, en, st, ed, reason, notes] = p;
  const safeNotes = notes ? notes.replace(/'/g, "''") : null;
  return `(${n}, '${zh}', '${en}', '羅馬', '未分裂教會', ${st}, ${ed}, ${reason ? `'${reason}'` : 'NULL'}, '正統', 'Liber Pontificalis; Catholic Encyclopedia', ${safeNotes ? `'${safeNotes}'` : 'NULL'})`;
}).join(',\n  ');

const sql = `
  INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes)
  VALUES ${valuesParts}
  ON CONFLICT DO NOTHING
  RETURNING succession_number, name_zh;
`;

console.log(`Inserting ${popes.length} popes...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records:`);
for (const r of res) console.log(`  #${r.succession_number} ${r.name_zh}`);
