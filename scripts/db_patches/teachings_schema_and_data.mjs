/**
 * Create church_teachings table + insert 55 well-attested teacher-disciple pairs.
 * Also: cross-link to existing episcopal_succession bishops where applicable.
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
  const txt = await res.text(); if (!res.ok) { console.error("FAIL:", txt); process.exit(1); } return JSON.parse(txt);
}

// 1. Create schema
console.log("== Create table church_teachings ==");
console.log(await q(`
  CREATE TABLE IF NOT EXISTS church_teachings (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_name_zh text NOT NULL,
    teacher_name_en text,
    student_name_zh text NOT NULL,
    student_name_en text,
    period_year     int,
    relationship    text DEFAULT '門徒',
    source          text,
    notes           text,
    teacher_bishop_id uuid REFERENCES episcopal_succession(id) ON DELETE SET NULL,
    student_bishop_id uuid REFERENCES episcopal_succession(id) ON DELETE SET NULL,
    created_at      timestamptz DEFAULT now()
  );
  CREATE INDEX IF NOT EXISTS church_teachings_teacher_idx ON church_teachings(teacher_name_zh);
  CREATE INDEX IF NOT EXISTS church_teachings_student_idx ON church_teachings(student_name_zh);
`));

// 2. Insert pairs.
// Format: [teacher_zh, teacher_en, student_zh, student_en, period_year, relationship, source, notes]
const pairs = [
  // ── 一、使徒時期 ──
  ['耶穌',     'Jesus Christ', '彼得',         'Peter',          30, '門徒', 'Mt 4:18', '十二使徒之一'],
  ['耶穌',     'Jesus Christ', '安得烈',       'Andrew',         30, '門徒', 'Mt 4:18', null],
  ['耶穌',     'Jesus Christ', '雅各（西庇太之子）', 'James, son of Zebedee', 30, '門徒', 'Mt 4:21', null],
  ['耶穌',     'Jesus Christ', '約翰',         'John',           30, '門徒', 'Mt 4:21', '愛徒'],
  ['耶穌',     'Jesus Christ', '腓力',         'Philip',         30, '門徒', 'Jn 1:43', null],
  ['耶穌',     'Jesus Christ', '巴多羅買',     'Bartholomew',    30, '門徒', 'Mt 10:3', null],
  ['耶穌',     'Jesus Christ', '馬太',         'Matthew',        30, '門徒', 'Mt 9:9', null],
  ['耶穌',     'Jesus Christ', '多馬',         'Thomas',         30, '門徒', 'Mt 10:3', null],
  ['耶穌',     'Jesus Christ', '雅各（亞勒腓之子）', 'James, son of Alphaeus', 30, '門徒', 'Mt 10:3', null],
  ['耶穌',     'Jesus Christ', '達太',         'Thaddaeus',      30, '門徒', 'Mt 10:3', null],
  ['耶穌',     'Jesus Christ', '西門（奮銳黨）', 'Simon the Zealot', 30, '門徒', 'Mt 10:4', null],
  ['耶穌',     'Jesus Christ', '馬提亞',       'Matthias',       33, '門徒', '徒 1:26', '取代猶大'],
  ['耶穌',     'Jesus Christ', '保羅',         'Paul',           34, '門徒', '徒 9; 林前 15:8', '復活後顯現'],
  ['耶穌',     'Jesus Christ', '義人雅各',     'James the Just', 30, '兄弟+門徒', '加 1:19', '主的兄弟'],
  ['彼得',     'Peter',        '馬可',         'Mark',           45, '屬靈父子', '彼前 5:13; Eus HE 2.15', '我兒馬可'],
  ['彼得',     'Peter',        '羅馬克勉一世', 'Pope Clement I', 60, '門徒', 'Eus HE 3.15; Tertullian', '#4 教宗'],
  ['保羅',     'Paul',         '提摩太',       'Timothy',        50, '屬靈父子', '提後 1:2', null],
  ['保羅',     'Paul',         '提多',         'Titus',          50, '屬靈父子', '多 1:4', null],
  ['保羅',     'Paul',         '路加',         'Luke',           50, '同工', 'Phlm 24', '醫生路加'],
  ['保羅',     'Paul',         '西拉',         'Silvanus',       50, '同工', '徒 15:40', null],
  ['保羅',     'Paul',         '阿尼西母',     'Onesimus',       60, '屬靈父子', '腓利門書', null],
  ['保羅',     'Paul',         '亞居拉',       'Aquila',         52, '同工', '徒 18:2', null],
  ['保羅',     'Paul',         '百基拉',       'Priscilla',      52, '同工', '徒 18:2', null],
  ['約翰',     'John',         '坡旅甲',       'Polycarp of Smyrna', 80, '門徒', 'Eus HE 5.20; Adv Haer 3.3.4', '士每拿主教'],
  ['約翰',     'John',         '帕皮亞',       'Papias of Hierapolis', 90, '門徒', 'Eus HE 3.39', '希拉波立主教'],
  ['巴拿巴',   'Barnabas',     '馬可',         'Mark',           45, '表兄+同工', '徒 13:5; 西 4:10', null],

  // ── 二、亞使徒時期（2 世紀）──
  ['坡旅甲',   'Polycarp',     '愛任紐',       'Irenaeus of Lyons', 135, '門徒', 'Adv Haer 3.3.4', '愛任紐自述兒時聽道'],
  ['游斯丁',   'Justin Martyr', '達提安',      'Tatian',         150, '門徒', 'Eus HE 4.16', '羅馬學派'],
  ['潘代諾',   'Pantaenus',    '革利免亞歷山大', 'Clement of Alexandria', 180, '門徒', 'Eus HE 5.10', '亞歷山大要理學校'],
  ['革利免亞歷山大', 'Clement of Alexandria', '俄利根', 'Origen', 200, '門徒', 'Eus HE 6.6', null],
  ['俄利根',   'Origen',       '希拉克拉',     'Heraclas',       220, '門徒+繼任', 'Eus HE 6.26', '亞歷山大 #13 主教'],
  ['俄利根',   'Origen',       '額我略·神蹟者', 'Gregory Thaumaturgus', 233, '門徒', 'Greg Thaum, Panegyric', null],
  ['俄利根',   'Origen',       '第尼修亞歷山大', 'Dionysius of Alexandria', 230, '門徒', 'Eus HE 6.29', '亞歷山大 #14'],

  // ── 三、卡帕多西亞 / 安提阿學派（4 世紀）──
  ['馬克莉娜（祖母）', 'Macrina the Elder', '巴西流', 'Basil the Great', 340, '撫養+教導', 'Greg Nyssa, Vita Macrinae', '聖巴西流之祖母'],
  ['馬克莉娜（祖母）', 'Macrina the Elder', '額我略·尼撒', 'Gregory of Nyssa', 345, '撫養+教導', 'Greg Nyssa, Vita Macrinae', null],
  ['巴西流',   'Basil the Great', '額我略·尼撒', 'Gregory of Nyssa', 365, '兄+神學師', 'Cappadocian corpus', null],
  ['戴奧多若', 'Diodore of Tarsus', '約翰·屈梭多模', 'John Chrysostom', 370, '門徒', 'Sozomen HE 8.2', '安提阿學派'],
  ['戴奧多若', 'Diodore of Tarsus', '摩普綏提亞德奧多若', 'Theodore of Mopsuestia', 375, '門徒', 'Antiochene school', null],
  ['摩普綏提亞德奧多若', 'Theodore of Mopsuestia', '聶斯多留', 'Nestorius', 410, '門徒', 'Cyril of Alex letters', '聶派由此衍出'],
  ['西奧菲洛', 'Theophilus of Alexandria', '西利祿', 'Cyril of Alexandria', 400, '叔父+繼任', 'Coptic tradition', '亞歷山大 #23→#24'],

  // ── 四、西方教父（4-5 世紀）──
  ['希拉里·普瓦捷', 'Hilary of Poitiers', '馬丁·都爾', 'Martin of Tours', 360, '門徒', 'Sulp Sev, Vita Martini', null],
  ['安波羅修', 'Ambrose of Milan', '奧古斯丁', 'Augustine of Hippo', 387, '老師+施洗', 'Conf 9.6.14', '387 復活節受洗'],
  ['耶柔米',   'Jerome',       '寶拉',         'Paula of Rome',  385, '神學指導', 'Jerome Letters', '伯利恆修會'],
  ['耶柔米',   'Jerome',       '優思託',       'Eustochium',     385, '神學指導', 'Jerome Letters', '寶拉之女'],
  ['奧古斯丁', 'Augustine of Hippo', '阿利庇', 'Alypius of Thagaste', 388, '同伴+門徒', 'Conf 9', '同受洗'],
  ['奧古斯丁', 'Augustine of Hippo', '普羅斯佩', 'Prosper of Aquitaine', 425, '神學追隨者', 'Prosper writings', '奧古斯丁主義'],
  ['約翰·加西安', 'John Cassian', '拉冷的奧諾拉', 'Honoratus of Lerins', 410, '修道指導', 'Cassian, Conferences', '西方修道'],

  // ── 五、東方修道與中世紀（4-13 世紀）──
  ['安條尼·大', 'Antony the Great', '帕克米烏', 'Pachomius', 320, '修道傳承', 'Vita Antonii; Vita Pachomii', '隱修→共修'],
  ['大額我略', 'Pope Gregory I', '奧斯定·坎特伯里', 'Augustine of Canterbury', 596, '派遣建立', 'Bede HE 1.23', '597 抵英'],
  ['西緬·新神學家', 'Symeon the New Theologian', '尼基塔·斯泰塔托斯', 'Niketas Stethatos', 1000, '門徒+傳記', 'Nik Steth, Vita Symeonis', '聖山傳統'],
  ['蘭法蘭克', 'Lanfranc of Bec', '安瑟倫·坎特伯里', 'Anselm of Canterbury', 1060, '門徒', 'Vita Anselmi by Eadmer', '貝克修院'],
  ['伯爾納·克勒窩', 'Bernard of Clairvaux', '威廉·聖蒂里', 'William of Saint-Thierry', 1115, '屬靈父子', 'William, Vita Bernardi', null],
  ['雨果·聖維克托', 'Hugh of Saint Victor', '理查·聖維克托', 'Richard of Saint Victor', 1135, '門徒', 'St Victor school tradition', '巴黎神秘主義'],
  ['亞勒伯多·瑪格努', 'Albertus Magnus', '多瑪斯·阿奎那', 'Thomas Aquinas', 1245, '老師', 'William of Tocco, Vita Thomae', '巴黎+科隆'],
  ['多瑪斯·阿奎那', 'Thomas Aquinas', '雷吉納德·皮佩諾', 'Reginald of Piperno', 1265, '秘書+門徒', 'Vita Thomae', '神學大全口述'],

  // ── 六、東正教晚期 + 改革時期 ──
  ['額我略·帕拉瑪', 'Gregory Palamas', '尼古拉·卡巴西拉', 'Nicholas Cabasilas', 1340, '神學影響', 'Hesychast tradition', '靜修運動'],
  ['約翰·波特', 'John Potter', '約翰·衛斯理', 'John Wesley', 1728, '按立', 'Wesley Journal', '時任牛津主教，按立 priest'],
  ['約翰·衛斯理', 'John Wesley', '多默·科克', 'Thomas Coke', 1784, '按立', 'Coke Journal', 'Bristol 按立 superintendent'],
  ['約翰·衛斯理', 'John Wesley', '法蘭西斯·亞斯理', 'Francis Asbury', 1771, '派遣+屬靈父子', 'Asbury Journal', '派往美國'],
  ['多默·科克', 'Thomas Coke', '法蘭西斯·亞斯理', 'Francis Asbury', 1784, '按立', '巴爾的摩聖誕大會', '正式按 bishop'],
  ['路德',     'Martin Luther', '梅蘭希通',    'Philip Melanchthon', 1520, '同工', 'Wittenberg circle', '威登堡神學夥伴'],
  ['加爾文',   'John Calvin',  '貝札',         'Theodore Beza',  1550, '門徒+繼任', 'Beza, Vita Calvini', '日內瓦繼任'],
];

// Build INSERT
const valuesParts = pairs.map(p => {
  const [tzh, ten, szh, sen, year, rel, source, notes] = p;
  const safe = (s) => s == null ? 'NULL' : `'${s.replace(/'/g, "''")}'`;
  return `(${safe(tzh)}, ${safe(ten)}, ${safe(szh)}, ${safe(sen)}, ${year ?? 'NULL'}, ${safe(rel)}, ${safe(source)}, ${safe(notes)})`;
}).join(',\n  ');

const sql = `INSERT INTO church_teachings (teacher_name_zh, teacher_name_en, student_name_zh, student_name_en, period_year, relationship, source, notes) VALUES ${valuesParts} RETURNING id, teacher_name_zh, student_name_zh;`;
console.log(`\n== Inserting ${pairs.length} teaching pairs ==`);
const res = await q(sql);
console.log(`Inserted ${res.length} pairs.`);

// 3. Cross-link teacher_bishop_id / student_bishop_id where bishop record exists
console.log("\n== Cross-link to episcopal_succession ==");
const linked = await q(`
  WITH match_teacher AS (
    UPDATE church_teachings t
    SET teacher_bishop_id = b.id
    FROM episcopal_succession b
    WHERE t.teacher_bishop_id IS NULL
      AND b.name_zh = t.teacher_name_zh
      AND (t.period_year IS NULL OR (b.start_year IS NULL OR ABS(b.start_year - t.period_year) < 50))
    RETURNING t.id
  ),
  match_student AS (
    UPDATE church_teachings t
    SET student_bishop_id = b.id
    FROM episcopal_succession b
    WHERE t.student_bishop_id IS NULL
      AND b.name_zh = t.student_name_zh
      AND (t.period_year IS NULL OR (b.start_year IS NULL OR ABS(b.start_year - t.period_year) < 50))
    RETURNING t.id
  )
  SELECT
    (SELECT count(*) FROM match_teacher) as teachers_linked,
    (SELECT count(*) FROM match_student) as students_linked;
`);
console.log(linked);

// 4. Stats
console.log("\n== Final stats ==");
console.log(await q(`
  SELECT count(*) as total,
    count(teacher_bishop_id) as with_teacher_link,
    count(student_bishop_id) as with_student_link
  FROM church_teachings;
`));
