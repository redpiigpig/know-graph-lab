/** Rename per user spec: 厄奇米亞津 → 埃奇米亞津, 亞歷山大 → 亞歷山卓 */
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

// 1. Rename 厄奇米亞津 → 埃奇米亞津 (Armenia)
console.log("== Rename Armenia 厄奇米亞津 → 埃奇米亞津 ==");
console.log(await q(`UPDATE episcopal_sees SET see_zh = '埃奇米亞津' WHERE see_zh = '厄奇米亞津' RETURNING id, see_zh, church;`));
const r1 = await q(`UPDATE episcopal_succession SET see = '埃奇米亞津' WHERE see = '厄奇米亞津' RETURNING id;`);
console.log(`updated ${r1.length} succession rows`);

// 2. Rename 亞歷山大 → 亞歷山卓 (Alexandria)
console.log("\n== Rename Alexandria 亞歷山大 → 亞歷山卓 ==");
console.log(await q(`UPDATE episcopal_sees SET see_zh = '亞歷山卓' WHERE see_zh = '亞歷山大' RETURNING id, see_zh, church;`));
const r2 = await q(`UPDATE episcopal_succession SET see = '亞歷山卓' WHERE see = '亞歷山大' RETURNING id;`);
console.log(`updated ${r2.length} succession rows`);

// 3. Verify
console.log("\n== Verify ==");
console.log(await q(`SELECT see_zh, church, count(*) as n FROM episcopal_sees WHERE see_zh IN ('埃奇米亞津','亞歷山卓') GROUP BY see_zh, church ORDER BY see_zh;`));
console.log(await q(`SELECT see, church, count(*) as n FROM episcopal_succession WHERE see IN ('埃奇米亞津','亞歷山卓') GROUP BY see, church ORDER BY see, church;`));
