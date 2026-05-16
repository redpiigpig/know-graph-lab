/** Improve cross-link: link to bishops via known aliases */
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

// Map teaching name → bishop name in DB
const aliases = [
  ['彼得',     '聖伯多祿',           '羅馬'],
  ['彼得',     '聖伯多祿',           '安提阿'],
  ['羅馬克勉一世', '聖克雷孟一世',     '羅馬'],
  ['約翰',     null, null],   // John apostle not in DB as bishop
  ['坡旅甲',   null, null],   // not in DB
  ['希拉克拉', '聖希拉克拉',          '亞歷山卓'],
  ['第尼修亞歷山大', '聖丟尼修',     '亞歷山卓'],
  ['巴西流',   null, null],   // not yet in episcopal_succession
  ['額我略·尼撒', null, null],
  ['約翰·屈梭多模', '聖若望·屈梭多模', '君士坦丁堡'],
  ['西利祿',   '聖息羅一世',         '亞歷山卓'],
  ['西奧菲洛', '聖德鐸非洛',         '亞歷山卓'],  // theophilus
  ['安波羅修', null, null],
  ['奧古斯丁', null, null],
  ['大額我略', '教宗額我略一世',     '羅馬'],
  ['奧斯定·坎特伯里', null, null],
  ['蘭法蘭克', null, null],
  ['安瑟倫·坎特伯里', null, null],
  ['亞勒伯多·瑪格努', null, null],
  ['多瑪斯·阿奎那', null, null],
  ['約翰·波特', '約翰·波特',         '坎特伯里'],
  ['約翰·衛斯理', '約翰·衛斯理',     '巴爾的摩（衛理）'],
  ['多默·科克', '多默·科克',         '巴爾的摩（衛理）'],
  ['法蘭西斯·亞斯理', '法蘭西斯·亞斯理', '巴爾的摩（衛理）'],
];

let teacherUpdates = 0, studentUpdates = 0;

for (const [teaching_name, db_name, see] of aliases) {
  if (!db_name || !see) continue;
  // Update teacher_bishop_id where teacher_name_zh = teaching_name
  const r1 = await q(`
    UPDATE church_teachings t
    SET teacher_bishop_id = b.id
    FROM episcopal_succession b
    WHERE t.teacher_name_zh = '${teaching_name}'
      AND t.teacher_bishop_id IS NULL
      AND b.name_zh = '${db_name}'
      AND b.see = '${see}'
    RETURNING t.id;
  `);
  teacherUpdates += r1.length;
  // Update student_bishop_id where student_name_zh = teaching_name
  const r2 = await q(`
    UPDATE church_teachings t
    SET student_bishop_id = b.id
    FROM episcopal_succession b
    WHERE t.student_name_zh = '${teaching_name}'
      AND t.student_bishop_id IS NULL
      AND b.name_zh = '${db_name}'
      AND b.see = '${see}'
    RETURNING t.id;
  `);
  studentUpdates += r2.length;
}

console.log(`Linked ${teacherUpdates} teacher fields, ${studentUpdates} student fields.`);

console.log("\n== Final stats ==");
console.log(await q(`
  SELECT count(*) as total,
    count(teacher_bishop_id) as with_teacher_link,
    count(student_bishop_id) as with_student_link,
    count(*) FILTER (WHERE teacher_bishop_id IS NOT NULL AND student_bishop_id IS NOT NULL) as both_linked
  FROM church_teachings;
`));
