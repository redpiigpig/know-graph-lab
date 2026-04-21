const u = process.env.SUPABASE_URL;
const s = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!u || !s) {
  console.error("Missing SUPABASE env");
  process.exit(1);
}

const h = { apikey: s, Authorization: `Bearer ${s}` };

async function main() {
  const c = await fetch(
    `${u}/rest/v1/book_categories?select=id,name,parent_id,display_order&order=display_order.asc`,
    { headers: h }
  );
  const cats = await c.json();

  const b = await fetch(
    `${u}/rest/v1/books?select=id,title,category_id&title=in.(中年之路,反穀,儀式的科學)`,
    { headers: h }
  );
  const books = await b.json();

  for (const bk of books) {
    const e = await fetch(`${u}/rest/v1/excerpts?select=id&book_id=eq.${bk.id}`, {
      headers: { ...h, Prefer: "count=exact" },
    });
    console.log(
      `${bk.title}\tcategory_id=${bk.category_id}\tcontent-range=${e.headers.get("content-range") || "n/a"}`
    );
  }

  for (const bk of books) {
    const e = await fetch(
      `${u}/rest/v1/excerpts?select=title,chapter,page_number,content&book_id=eq.${bk.id}&order=created_at.asc&limit=3`,
      { headers: h }
    );
    const rows = await e.json();
    console.log(`\n--- ${bk.title} sample ---`);
    console.log(
      rows.map((r) => ({
        title: r.title,
        chapter: r.chapter,
        page_number: r.page_number,
        content: (r.content || "").slice(0, 40),
      }))
    );
  }

  console.log(
    "categories:",
    cats.filter((x) => ["人類學", "人類生物學", "心理學"].includes(x.name))
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
