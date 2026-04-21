const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SERVICE_KEY) {
  console.error("Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY");
  process.exit(1);
}

const headers = {
  apikey: SERVICE_KEY,
  Authorization: `Bearer ${SERVICE_KEY}`,
  "Content-Type": "application/json",
};

async function main() {
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/book_categories?select=id,name,parent_id&name=in.(人類生物學,人類學)`,
    { headers }
  );
  const rows = await res.json();
  const parent = rows.find((x) => x.name === "人類生物學");
  const child = rows.find((x) => x.name === "人類學");
  if (!parent || !child) {
    throw new Error(`Missing categories: ${JSON.stringify(rows)}`);
  }

  const patch = await fetch(`${SUPABASE_URL}/rest/v1/book_categories?id=eq.${child.id}`, {
    method: "PATCH",
    headers,
    body: JSON.stringify({ parent_id: parent.id }),
  });
  if (!patch.ok) {
    throw new Error(`Patch failed: ${patch.status} ${await patch.text()}`);
  }

  console.log(`✓ 人類學 (${child.id}) moved under 人類生物學 (${parent.id})`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
