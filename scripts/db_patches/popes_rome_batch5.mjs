/** Rome popes batch 5: #201-#266 (AD 1389-2025) */
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
  [201, '博尼法九世',         'Pope Boniface IX',       1389, 1404, '逝世', '西方大分裂期間羅馬系'],
  [202, '依諾增爵七世',       'Pope Innocent VII',      1404, 1406, '逝世', null],
  [203, '額我略十二世',       'Pope Gregory XII',       1406, 1415, '退位', '康斯坦茨大公會議解決大分裂'],
  [204, '瑪爾定五世',         'Pope Martin V',          1417, 1431, '逝世', '結束西方大分裂'],
  [205, '恩仁四世',           'Pope Eugene IV',         1431, 1447, '逝世', '佛羅倫薩大公會議'],
  [206, '尼古拉五世',         'Pope Nicholas V',        1447, 1455, '逝世', '文藝復興教宗、創梵蒂岡圖書館'],
  [207, '加里斯都三世',       'Pope Callixtus III',     1455, 1458, '逝世', '波吉亞家族'],
  [208, '庇護二世',           'Pope Pius II',           1458, 1464, '逝世', '人文主義學者'],
  [209, '保祿二世',           'Pope Paul II',           1464, 1471, '逝世', null],
  [210, '思道四世',           'Pope Sixtus IV',         1471, 1484, '逝世', '建西斯廷小堂'],
  [211, '依諾增爵八世',       'Pope Innocent VIII',     1484, 1492, '逝世', null],
  [212, '亞歷山大六世',       'Pope Alexander VI',      1492, 1503, '逝世', '波吉亞家族；新世界劃分'],
  [213, '庇護三世',           'Pope Pius III',          1503, 1503, '逝世', null],
  [214, '儒略二世',           'Pope Julius II',         1503, 1513, '逝世', '委託米開朗基羅'],
  [215, '良十世',             'Pope Leo X',             1513, 1521, '逝世', '宗教改革爆發；委託拉斐爾'],
  [216, '哈德良六世',         'Pope Adrian VI',         1522, 1523, '逝世', '末位非義大利籍教宗（直至若望保祿二世）'],
  [217, '克勉七世',           'Pope Clement VII',       1523, 1534, '逝世', '羅馬之劫；亨利八世離婚案'],
  [218, '保祿三世',           'Pope Paul III',          1534, 1549, '逝世', '召開特利騰大公會議'],
  [219, '儒略三世',           'Pope Julius III',        1550, 1555, '逝世', null],
  [220, '瑪策祿二世',         'Pope Marcellus II',      1555, 1555, '逝世', null],
  [221, '保祿四世',           'Pope Paul IV',           1555, 1559, '逝世', null],
  [222, '庇護四世',           'Pope Pius IV',           1559, 1565, '逝世', '結束特利騰大公會議'],
  [223, '聖庇護五世',         'Pope Pius V',            1566, 1572, '逝世', '勒班陀海戰；統一羅馬禮'],
  [224, '額我略十三世',       'Pope Gregory XIII',      1572, 1585, '逝世', '訂立額我略曆'],
  [225, '思道五世',           'Pope Sixtus V',          1585, 1590, '逝世', null],
  [226, '烏爾班七世',         'Pope Urban VII',         1590, 1590, '逝世', null],
  [227, '額我略十四世',       'Pope Gregory XIV',       1590, 1591, '逝世', null],
  [228, '依諾增爵九世',       'Pope Innocent IX',       1591, 1591, '逝世', null],
  [229, '克勉八世',           'Pope Clement VIII',      1592, 1605, '逝世', null],
  [230, '良十一世',           'Pope Leo XI',            1605, 1605, '逝世', null],
  [231, '保祿五世',           'Pope Paul V',            1605, 1621, '逝世', '伽利略事件'],
  [232, '額我略十五世',       'Pope Gregory XV',        1621, 1623, '逝世', null],
  [233, '烏爾班八世',         'Pope Urban VIII',        1623, 1644, '逝世', '伽利略受審'],
  [234, '依諾增爵十世',       'Pope Innocent X',        1644, 1655, '逝世', null],
  [235, '亞歷山大七世',       'Pope Alexander VII',     1655, 1667, '逝世', null],
  [236, '克勉九世',           'Pope Clement IX',        1667, 1669, '逝世', null],
  [237, '克勉十世',           'Pope Clement X',         1670, 1676, '逝世', null],
  [238, '真福依諾增爵十一世', 'Pope Innocent XI',       1676, 1689, '逝世', null],
  [239, '亞歷山大八世',       'Pope Alexander VIII',    1689, 1691, '逝世', null],
  [240, '依諾增爵十二世',     'Pope Innocent XII',      1691, 1700, '逝世', null],
  [241, '克勉十一世',         'Pope Clement XI',        1700, 1721, '逝世', '中國禮儀之爭'],
  [242, '依諾增爵十三世',     'Pope Innocent XIII',     1721, 1724, '逝世', null],
  [243, '本篤十三世',         'Pope Benedict XIII',     1724, 1730, '逝世', null],
  [244, '克勉十二世',         'Pope Clement XII',       1730, 1740, '逝世', null],
  [245, '本篤十四世',         'Pope Benedict XIV',      1740, 1758, '逝世', '學者教宗'],
  [246, '克勉十三世',         'Pope Clement XIII',      1758, 1769, '逝世', null],
  [247, '克勉十四世',         'Pope Clement XIV',       1769, 1774, '逝世', '解散耶穌會（1773）'],
  [248, '庇護六世',           'Pope Pius VI',           1775, 1799, '流亡逝世', '法國大革命；被拿破崙俘虜'],
  [249, '庇護七世',           'Pope Pius VII',          1800, 1823, '逝世', '加冕拿破崙；恢復耶穌會'],
  [250, '良十二世',           'Pope Leo XII',           1823, 1829, '逝世', null],
  [251, '庇護八世',           'Pope Pius VIII',         1829, 1830, '逝世', null],
  [252, '額我略十六世',       'Pope Gregory XVI',       1831, 1846, '逝世', '末位非主教當選教宗'],
  [253, '真福庇護九世',       'Pope Pius IX',           1846, 1878, '逝世', '梵一大公會議；教宗無謬論；任期最長'],
  [254, '良十三世',           'Pope Leo XIII',          1878, 1903, '逝世', '《新事》通諭奠定天主教社會訓導'],
  [255, '聖庇護十世',         'Pope Pius X',            1903, 1914, '逝世', '反現代主義'],
  [256, '本篤十五世',         'Pope Benedict XV',       1914, 1922, '逝世', '一戰期間'],
  [257, '庇護十一世',         'Pope Pius XI',           1922, 1939, '逝世', '簽訂拉特朗條約建立梵蒂岡國'],
  [258, '庇護十二世',         'Pope Pius XII',          1939, 1958, '逝世', '二戰期間'],
  [259, '聖若望二十三世',     'Pope John XXIII',        1958, 1963, '逝世', '召開梵二大公會議'],
  [260, '聖保祿六世',         'Pope Paul VI',           1963, 1978, '逝世', '結束梵二大公會議'],
  [261, '若望保祿一世',       'Pope John Paul I',       1978, 1978, '逝世', '在位 33 天'],
  [262, '聖若望保祿二世',     'Pope John Paul II',      1978, 2005, '逝世', '波蘭籍；任期第二長'],
  [263, '本篤十六世',         'Pope Benedict XVI',      2005, 2013, '退位', '近代首位主動退位教宗'],
  [264, '方濟各',             'Pope Francis',           2013, 2025, '逝世', '首位耶穌會、首位拉美籍教宗'],
  [265, '良十四世',           'Pope Leo XIV',           2025, null, null, '首位美國籍教宗（出生於芝加哥）；2025/05/08 當選'],
];

const valuesParts = popes.map(p => {
  const [n, zh, en, st, ed, reason, notes] = p;
  const safeNotes = notes ? notes.replace(/'/g, "''") : null;
  return `(${n}, '${zh}', '${en}', '羅馬', '天主教', ${st}, ${ed === null ? 'NULL' : ed}, ${reason ? `'${reason}'` : 'NULL'}, '正統', 'Annuario Pontificio', ${safeNotes ? `'${safeNotes}'` : 'NULL'})`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${popes.length} popes (batch 5, final)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
