/**
 * Methodist apostolic-succession anchor:
 *   約翰·波特 (Canterbury #83, 1737-1747) — already in DB
 *     → 約翰·衛斯理 (1728 ordained priest by Potter)
 *       → 多默·科克 (1784 ordained superintendent by Wesley)
 *         + 法蘭西斯·亞斯理 (1784 co-superintendent)
 *           → all American Methodist bishops
 *
 * Architectural choice (per user spec, accepting Methodist self-view):
 *   - Create see "巴爾的摩（衛理）" representing the 1784 Christmas Conference
 *   - Wesley/Coke/Asbury are bishops #1/2/3 of this see
 *   - parent_see_id → 坎特伯里·英格蘭教會 (so it shows as Canterbury side branch)
 *   - founded_year=1738 → API's findBishopAtYear lands on Potter (#83, 1737-47) ✓
 *   - Patch 9 existing 衛理宗 sees parent_see_id → 巴爾的摩(衛理)
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

// 1. Create see "巴爾的摩（衛理）" — 1784 Christmas Conference
console.log("== INSERT see 巴爾的摩（衛理）·美聯合衛理公會早期 ==");
console.log(await q(`
  INSERT INTO episcopal_sees
    (name_zh, name_en, see_zh, church, tradition, status, founded_year, location, parent_see_id, notes)
  VALUES (
    '巴爾的摩（衛理會早期）', 'Baltimore Christmas Conference / Methodist Episcopal Church',
    '巴爾的摩（衛理）', '衛理宗', '基督新教', '已廢除',
    1738, '美國馬里蘭州巴爾的摩',
    (SELECT id FROM episcopal_sees WHERE see_zh='坎特伯里' AND church='英格蘭教會'),
    '1738 衛斯理 Aldersgate 經歷後展開福音復興運動；1784 巴爾的摩聖誕大會正式成立美國衛理會（Methodist Episcopal Church），衛斯理派多默·科克按立法蘭西斯·亞斯理為共同總監督。'
  )
  ON CONFLICT (see_zh, church) DO NOTHING
  RETURNING id, see_zh, church, parent_see_id;
`));

// 2. Insert Wesley + Coke + Asbury
console.log("\n== INSERT Wesley + Coke + Asbury ==");
console.log(await q(`
  INSERT INTO episcopal_succession
    (name_zh, name_en, see, church, succession_number, start_year, end_year, end_reason, appointed_by, status, sources, notes)
  VALUES
    ('約翰·衛斯理', 'John Wesley', '巴爾的摩（衛理）', '衛理宗', 1, 1738, 1791, '逝世',
     '坎特伯里大主教約翰·波特（1728 按立為長老）', '正統',
     'Wesley, Journal; Tyerman, Life and Times of Rev. John Wesley',
     '1728 由牛津主教約翰·波特按立為英格蘭教會長老；1738/05/24 Aldersgate 經歷後開創福音復興運動；1784 自任主教權柄按立多默·科克為美國衛理會總監督。'),
    ('查爾斯·衛斯理', 'Charles Wesley', '巴爾的摩（衛理）', '衛理宗', NULL, 1738, 1788, '逝世',
     '英格蘭教會（與兄長同工）', '正統', 'Wesley, Journal',
     '約翰·衛斯理之弟，衛理宗共同創始人，作詞 6,000+ 首詩歌。'),
    ('多默·科克', 'Thomas Coke', '巴爾的摩（衛理）', '衛理宗', 2, 1784, 1814, '逝世',
     '約翰·衛斯理（1784/09/02 按立）', '正統',
     'Coke, Journal; Drew, Life of Thomas Coke',
     '1784/09/02 衛斯理在 Bristol 按立科克為美國衛理會 superintendent（後改稱 bishop）；1784/12 巴爾的摩聖誕大會宣告美國衛理會成立並按立亞斯理。'),
    ('法蘭西斯·亞斯理', 'Francis Asbury', '巴爾的摩（衛理）', '衛理宗', 3, 1784, 1816, '逝世',
     '多默·科克（1784/12/27 巴爾的摩聖誕大會按立）', '正統',
     'Asbury, Journal; Tipple, Francis Asbury, the Prophet of the Long Road',
     '美國衛理宗的「使徒」，1771 由衛斯理派往美國；1784 巴爾的摩聖誕大會被科克按立為主教；任內 32 年走遍美國拓荒，按立 4,000+ 牧師、培養 700+ 巡迴傳道。')
  ON CONFLICT DO NOTHING
  RETURNING id, name_zh, succession_number;
`));

// 3. Patch 9 existing 衛理宗 sees parent_see_id → 巴爾的摩（衛理）
//    The 9 sees:
//    費城(衛理) AME → 巴爾的摩
//    夏洛特(衛理) AMEZ → 巴爾的摩
//    孟菲斯(衛理) CME → 巴爾的摩
//    印第安納波利斯(衛理) Free Methodist → 巴爾的摩
//    納許維爾(衛理) UMC → 巴爾的摩
//    亞特蘭大(衛理) GMC → 納許維爾(衛理)（從 UMC 分裂）
//    首爾(衛理) Korean Methodist → 納許維爾(衛理)（UMC 派遣）
//    孟買(衛理) Indian Methodist → 納許維爾(衛理)
//    約翰尼斯堡(衛理) South African → 巴爾的摩
console.log("\n== PATCH 9 衛理宗 sees parent_see_id ==");
console.log(await q(`
  UPDATE episcopal_sees
  SET parent_see_id = (SELECT id FROM episcopal_sees WHERE see_zh='巴爾的摩（衛理）' LIMIT 1)
  WHERE see_zh IN ('費城（衛理）', '夏洛特（衛理）', '孟菲斯（衛理）', '印第安納波利斯（衛理）', '納許維爾（衛理）', '約翰尼斯堡（衛理）')
  RETURNING see_zh, church;
`));
console.log(await q(`
  UPDATE episcopal_sees
  SET parent_see_id = (SELECT id FROM episcopal_sees WHERE see_zh='納許維爾（衛理）' LIMIT 1)
  WHERE see_zh IN ('亞特蘭大（衛理）', '首爾（衛理）', '孟買（衛理）')
  RETURNING see_zh, church;
`));

// 4. Verify
console.log("\n== Verify final structure ==");
console.log(await q(`
  SELECT s.see_zh, s.church, s.founded_year, p.see_zh as parent_see, p.church as parent_church
  FROM episcopal_sees s LEFT JOIN episcopal_sees p ON p.id = s.parent_see_id
  WHERE s.see_zh LIKE '%衛理%'
  ORDER BY s.founded_year;
`));
