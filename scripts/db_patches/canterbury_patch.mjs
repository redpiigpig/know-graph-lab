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

// 1. Insert 額我略一世 (Gregory I) — Pope #64, 590-604
console.log("== Insert Pope Gregory I ==");
console.log(await q(`
  INSERT INTO episcopal_succession
    (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes)
  VALUES
    ('教宗額我略一世', 'Pope Gregory I (the Great)', '羅馬', '天主教', 64, 590, 604, '逝世',
     '羅馬聖職人員選舉', '正統',
     'Bede, Ecclesiastical History I.23; Gregory of Tours; Liber Pontificalis',
     '大額我略；590 年差遣聖奧斯定（Augustine of Canterbury）赴英格蘭傳教，建立坎特伯里大主教座（597）。')
  ON CONFLICT DO NOTHING
  RETURNING id, name_zh, see, succession_number;
`));

// 2. Patch Canterbury (medieval) parent_see_id → Rome
console.log("\n== Patch Canterbury parent_see_id → Rome ==");
console.log(await q(`
  UPDATE episcopal_sees
  SET parent_see_id = (SELECT id FROM episcopal_sees WHERE see_zh='羅馬' AND church='天主教' LIMIT 1)
  WHERE see_zh='坎特伯里' AND church='天主教'
  RETURNING id, name_zh, parent_see_id;
`));

// 3. Verify
console.log("\n== Verify Canterbury ==");
console.log(await q(`
  SELECT s.see_zh, s.church, s.founded_year, p.see_zh as parent_see, p.church as parent_church
  FROM episcopal_sees s LEFT JOIN episcopal_sees p ON p.id = s.parent_see_id
  WHERE s.see_zh = '坎特伯里';
`));
