/** Rome popes batch 2: #51-#100 (AD 498-872) */
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

const popes = [
  [51, '聖叙瑪克',           'Pope Symmachus',       498, 514, '逝世', null],
  [52, '聖何彌大',           'Pope Hormisdas',       514, 523, '逝世', '結束阿卡咎分裂'],
  [53, '聖若望一世',         'Pope John I',          523, 526, '殉道', '東哥德狄奧多里克下獄'],
  [54, '聖斐理斯四世',       'Pope Felix IV',        526, 530, '逝世', null],
  [55, '博尼法二世',         'Pope Boniface II',     530, 532, '逝世', null],
  [56, '若望二世',           'Pope John II',         533, 535, '逝世', '首位改名教宗（原名 Mercurius）'],
  [57, '聖亞加皮一世',       'Pope Agapetus I',      535, 536, '逝世', null],
  [58, '聖息維略',           'Pope Silverius',       536, 537, '流亡逝世', null],
  [59, '威吉理',             'Pope Vigilius',        537, 555, '逝世', '第二次君士坦丁堡大公會議'],
  [60, '貝拉吉一世',         'Pope Pelagius I',      556, 561, '逝世', null],
  [61, '若望三世',           'Pope John III',        561, 574, '逝世', null],
  [62, '本篤一世',           'Pope Benedict I',      575, 579, '逝世', null],
  [63, '貝拉吉二世',         'Pope Pelagius II',     579, 590, '逝世', null],
  // #64 額我略一世 already in DB
  [65, '撒比尼安',           'Pope Sabinian',        604, 606, '逝世', null],
  [66, '博尼法三世',         'Pope Boniface III',    607, 607, '逝世', null],
  [67, '聖博尼法四世',       'Pope Boniface IV',     608, 615, '逝世', null],
  [68, '聖德武德德',         'Pope Adeodatus I',     615, 618, '逝世', null],
  [69, '博尼法五世',         'Pope Boniface V',      619, 625, '逝世', null],
  [70, '何挪略一世',         'Pope Honorius I',      625, 638, '逝世', '後被定為一志論異端'],
  [71, '塞威林',             'Pope Severinus',       640, 640, '逝世', null],
  [72, '若望四世',           'Pope John IV',         640, 642, '逝世', null],
  [73, '德鐸一世',           'Pope Theodore I',      642, 649, '逝世', null],
  [74, '聖瑪爾定一世',       'Pope Martin I',        649, 655, '殉道', '反對一志論被流放克里米亞'],
  [75, '聖恩仁一世',         'Pope Eugene I',        654, 657, '逝世', null],
  [76, '聖維大利安',         'Pope Vitalian',        657, 672, '逝世', null],
  [77, '德武德德二世',       'Pope Adeodatus II',    672, 676, '逝世', null],
  [78, '多努',               'Pope Donus',           676, 678, '逝世', null],
  [79, '聖亞加多',           'Pope Agatho',          678, 681, '逝世', '第三次君士坦丁堡大公會議'],
  [80, '聖良二世',           'Pope Leo II',          682, 683, '逝世', null],
  [81, '聖本篤二世',         'Pope Benedict II',     684, 685, '逝世', null],
  [82, '若望五世',           'Pope John V',          685, 686, '逝世', null],
  [83, '科農',               'Pope Conon',           686, 687, '逝世', null],
  [84, '聖塞爾爵一世',       'Pope Sergius I',       687, 701, '逝世', null],
  [85, '若望六世',           'Pope John VI',         701, 705, '逝世', null],
  [86, '若望七世',           'Pope John VII',        705, 707, '逝世', null],
  [87, '西西尼',             'Pope Sisinnius',       708, 708, '逝世', null],
  [88, '君士坦丁',           'Pope Constantine',     708, 715, '逝世', null],
  [89, '聖額我略二世',       'Pope Gregory II',      715, 731, '逝世', '反對拜占庭破除聖像'],
  [90, '聖額我略三世',       'Pope Gregory III',     731, 741, '逝世', '末位希臘裔教宗'],
  [91, '聖匝加',             'Pope Zachary',         741, 752, '逝世', '末位拜占庭認可教宗'],
  [92, '斯德望二世',         'Pope Stephen II',      752, 757, '逝世', '與丕平訂立教皇國基礎'],
  [93, '聖保祿一世',         'Pope Paul I',          757, 767, '逝世', null],
  [94, '斯德望三世',         'Pope Stephen III',     768, 772, '逝世', null],
  [95, '哈德良一世',         'Pope Adrian I',        772, 795, '逝世', '第二次尼西亞大公會議'],
  [96, '聖良三世',           'Pope Leo III',         795, 816, '逝世', '加冕查理曼為皇帝（800）'],
  [97, '斯德望四世',         'Pope Stephen IV',      816, 817, '逝世', null],
  [98, '聖巴斯加一世',       'Pope Paschal I',       817, 824, '逝世', null],
  [99, '恩仁二世',           'Pope Eugene II',       824, 827, '逝世', null],
  [100, '瓦倫定',            'Pope Valentine',       827, 827, '逝世', null],
];

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

console.log(`Inserting ${popes.length} popes (batch 2)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records (skipped ${popes.length - res.length}):`);
for (const r of res) console.log(`  #${r.succession_number} ${r.name_zh}`);
