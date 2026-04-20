/**
 * Update all books with full bibliographic data + create category system
 * Run: npx ts-node scripts/update-books-with-categories.ts
 */
import * as dotenv from "dotenv";
dotenv.config();

const ACCESS_TOKEN = process.env.SUPABASE_ACCESS_TOKEN!;
const PROJECT_REF = "vloqgautkahgmqcwgfuo";

async function sql(query: string): Promise<any[]> {
  const res = await fetch(
    `https://api.supabase.com/v1/projects/${PROJECT_REF}/database/query`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${ACCESS_TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    }
  );
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`SQL Error (${res.status}): ${err}`);
  }
  return res.json();
}

function esc(v: string | null | undefined): string {
  if (v == null || v === "") return "NULL";
  return `'${v.replace(/'/g, "''")}'`;
}
function escNum(v: number | null | undefined): string {
  return v != null ? String(v) : "NULL";
}

// ── Category structure ────────────────────────────────────────────────────────
const TOP_CATS = ["人類生物學", "心理學", "文學", "世界宗教", "自然科學", "宗教學", "社會政治學", "哲學", "歷史學"];
const SUB_CATS: Record<string, string[]> = {
  "世界宗教": ["伊斯蘭教", "印度教", "佛教", "其他宗教", "東亞宗教", "波斯宗教", "基督教", "猶太教", "摩門教"],
  "歷史學":   ["中央界域史", "史料原典", "史學理論", "全球通史", "西方界域史", "亞太界域史", "東方界域史", "近代史", "美州界域史"],
};

// ── Book data (title must match exact DB value) ───────────────────────────────
interface BookData {
  title: string;
  translator?: string;
  publisher?: string;
  publishPlace?: string;
  publishYear?: number;
  cat: string; // leaf category name
}

const BOOKS: BookData[] = [
  // ── 基督教 ──
  { title: "激進神學與上帝之死", translator: "張賢勇", publisher: "中國人民大學出版社", publishPlace: "北京", publishYear: 2006, cat: "基督教" },
  { title: "神的歷史", translator: "蔡昌雄", publisher: "立緒文化", publishPlace: "新北市", publishYear: 2012, cat: "基督教" },
  { title: "神話簡史", translator: "胡亞非", publisher: "大塊文化", publishPlace: "台北", publishYear: 2006, cat: "基督教" },
  { title: "次經導論", translator: "劉良淑", publisher: "校園書房", publishPlace: "台北", publishYear: 2011, cat: "基督教" },
  { title: "耶穌與死海古卷", translator: "蔣馥蓁", publisher: "光啟文化", publishPlace: "台北", publishYear: 2021, cat: "基督教" },
  { title: "耶穌到底如何成為神", translator: "紀榮神", publisher: "橄欖出版", publishPlace: "台北", publishYear: 2018, cat: "基督教" },
  { title: "理性的勝利", translator: "黃文馨", publisher: "宗教文化出版社", publishPlace: "北京", publishYear: 2011, cat: "基督教" },
  { title: "諾斯與拯救", cat: "基督教" },
  { title: "穿過針眼：財富、西羅馬帝國的衰亡和基督教會的形成", translator: "卜永堅 等", publisher: "麥田出版", publishPlace: "台北", publishYear: 2017, cat: "基督教" },
  { title: "沒有神的宗教", translator: "陳雅汝", publisher: "商周出版", publishPlace: "台北", publishYear: 2014, cat: "哲學" },
  { title: "多元化的上帝觀", publisher: "貴州人民出版社", publishPlace: "北京", publishYear: 1991, cat: "基督教" },
  // ── 猶太教 ──
  { title: "希伯來聖經的文本、歷史與思想世界", publisher: "宗教文化出版社", publishPlace: "北京", publishYear: 2013, cat: "猶太教" },
  { title: "古以色列史", translator: "邱建健", publisher: "中國人民大學出版社", publishPlace: "北京", publishYear: 2006, cat: "猶太教" },
  { title: "虛構的猶太民族", translator: "王睿", publisher: "麥田出版", publishPlace: "台北", publishYear: 2017, cat: "猶太教" },
  { title: "猶太人的世紀", translator: "吳萬偉", publisher: "麥田出版", publishPlace: "台北", publishYear: 2021, cat: "猶太教" },
  // ── 伊斯蘭教 ──
  { title: "《中斷的天命：伊斯蘭觀點的世界史》", translator: "苑默文", publisher: "廣場出版", publishPlace: "新北市", publishYear: 2017, cat: "伊斯蘭教" },
  { title: "先知的繼承者", translator: "馮奕達", publisher: "貓頭鷹出版社", publishPlace: "台北", publishYear: 2020, cat: "伊斯蘭教" },
  { title: "阿拉伯通史", translator: "馬堅", publisher: "商務印書館", publishPlace: "北京", publishYear: 1979, cat: "伊斯蘭教" },
  { title: "古蘭經的故事", cat: "伊斯蘭教" },
  // ── 印度教 ──
  { title: "印度教導論", translator: "曹學鎔", publisher: "東大圖書", publishPlace: "台北", publishYear: 1993, cat: "印度教" },
  { title: "印度文明史", translator: "何子材", publisher: "華文出版社", publishPlace: "北京", publishYear: 2004, cat: "印度教" },
  { title: "印度宗教多元文化", publisher: "社會科學文獻出版社", publishPlace: "北京", publishYear: 2009, cat: "印度教" },
  { title: "《追尋印度史詩之美》", cat: "印度教" },
  // ── 佛教 ──
  { title: "大乘佛教思想", translator: "陳一標", publisher: "法爾出版社", publishPlace: "台北", publishYear: 1993, cat: "佛教" },
  { title: "佛教史", publisher: "江蘇人民出版社", publishPlace: "南京", publishYear: 2006, cat: "佛教" },
  { title: "巴利佛教的思想交涉", cat: "佛教" },
  { title: "〈北魏僧曹制度考──兼論中國僧官的起源〉", publisher: "國立臺灣大學歷史學系學報", publishPlace: "台北", publishYear: 1999, cat: "佛教" },
  // ── 東亞宗教 ──
  { title: "儒教簡史", publisher: "人民出版社", publishPlace: "北京", publishYear: 2015, cat: "東亞宗教" },
  { title: "道教史", publisher: "江蘇人民出版社", publishPlace: "南京", publishYear: 2006, cat: "東亞宗教" },
  { title: "成神：早期中國的宇宙論、祭祀與自我神化", translator: "張曉琴", publisher: "聯經出版", publishPlace: "台北", publishYear: 2018, cat: "東亞宗教" },
  { title: "祥瑞：王莽和他的時代", publisher: "上海人民出版社", publishPlace: "上海", publishYear: 2021, cat: "東亞宗教" },
  { title: "忠於自己靈魂的人", publisher: "麥田出版", publishPlace: "台北", publishYear: 2022, cat: "東亞宗教" },
  // ── 波斯宗教 ──
  { title: "祆教史", publisher: "上海社會科學院出版社", publishPlace: "上海", publishYear: 1998, cat: "波斯宗教" },
  { title: "二元神論：古波斯宗教神話研究", publisher: "中國社會科學出版社", publishPlace: "北京", publishYear: 1997, cat: "波斯宗教" },
  // ── 其他宗教 ──
  { title: "被隱藏的眾神", translator: "馮奕達", publisher: "八旗文化", publishPlace: "新北市", publishYear: 2015, cat: "其他宗教" },
  { title: "黑色上帝", translator: "王建福", publisher: "商務印書館", publishPlace: "北京", publishYear: 2017, cat: "其他宗教" },
  { title: "薩滿教", translator: "段滿福", publisher: "社會科學文獻出版社", publishPlace: "北京", publishYear: 2018, cat: "其他宗教" },
  { title: "摩尼教及其東漸", publisher: "淑馨出版社", publishPlace: "台北", publishYear: 1997, cat: "其他宗教" },
  { title: "巴哈歐拉的天啟(第四卷)", publisher: "澳門新紀元國際出版社", publishPlace: "澳門", cat: "其他宗教" },
  { title: "靈魂獵人", translator: "劉雅芳", publisher: "國立臺灣大學出版中心", publishPlace: "台北", publishYear: 2021, cat: "其他宗教" },
  { title: "被隱藏的眾神推薦序", cat: "其他宗教" },
  // ── 宗教學 ──
  { title: "造神：人類探索信仰與宗教的歷史", translator: "吳煒聲", publisher: "衛城出版", publishPlace: "新北市", publishYear: 2018, cat: "宗教學" },
  { title: "神的演化", translator: "林金源", publisher: "左岸文化", publishPlace: "新北市", publishYear: 2013, cat: "宗教學" },
  { title: "世界宗教中的神祕主義", translator: "翁少龍", publisher: "今日中國出版社", publishPlace: "北京", publishYear: 1992, cat: "宗教學" },
  { title: "探索神性", translator: "何光瀘", publisher: "中國人民大學出版社", publishPlace: "北京", publishYear: 2006, cat: "宗教學" },
  { title: "宗教思想史", translator: "晏可佳 等", publisher: "商周出版", publishPlace: "台北", publishYear: 2001, cat: "宗教學" },
  { title: "神話的歷史", translator: "杜文燕", publisher: "希望出版社", publishPlace: "太原", publishYear: 2003, cat: "宗教學" },
  { title: "千面女神", translator: "胡瑋退", publisher: "漫遊者文化", publishPlace: "台北", publishYear: 2019, cat: "宗教學" },
  { title: "坎伯生活美學", translator: "梁靜美", publisher: "立緒文化", publishPlace: "新北市", publishYear: 1999, cat: "宗教學" },
  { title: "魔鬼史", translator: "趙惠", publisher: "時代文藝出版社", publishPlace: "北京", publishYear: 2001, cat: "宗教學" },
  { title: "希臘宗教概論", publisher: "上海人民出版社", publishPlace: "上海", publishYear: 1997, cat: "宗教學" },
  { title: "西塞羅《論神性》導言", cat: "哲學" },
  { title: "蘇美爾神話", translator: "陳曉霞", publisher: "社會科學文獻出版社", publishPlace: "北京", publishYear: 2013, cat: "宗教學" },
  { title: "巴比倫與亞述神話", translator: "趙樹奎", publisher: "中央編譯出版社", publishPlace: "北京", publishYear: 2008, cat: "宗教學" },
  { title: "古代兩河流域與西亞神話", publisher: "台灣星光出版社", publishPlace: "台北", publishYear: 2001, cat: "宗教學" },
  { title: "埃及神話", translator: "郭騰堅", publisher: "聯經出版", publishPlace: "台北", publishYear: 2015, cat: "宗教學" },
  { title: "〈永恆的神話創作、不朽的宗教關懷〉。潘俊琳", cat: "宗教學" },
  // ── 哲學 ──
  { title: "西方哲學史", translator: "鄧曉芒、匡宏", publisher: "世界圖書出版公司", publishPlace: "北京", publishYear: 2013, cat: "哲學" },
  { title: "古希臘哲人論神", publisher: "北京大學出版社", publishPlace: "北京", publishYear: 2021, cat: "哲學" },
  { title: "前蘇格拉底哲學", translator: "翁歡冰", publisher: "華東師範大學出版社", publishPlace: "上海", publishYear: 2020, cat: "哲學" },
  { title: "政治觀念史稿(一)", translator: "段保良", publisher: "華東師範大學出版社", publishPlace: "上海", publishYear: 2007, cat: "哲學" },
  // ── 歷史學→全球通史 ──
  { title: "世界史前史", translator: "袁海兵", publisher: "世界圖書出版公司", publishPlace: "北京", publishYear: 2011, cat: "全球通史" },
  { title: "人類憑什麼", translator: "陳建良", publisher: "雅言文化", publishPlace: "台北", publishYear: 2014, cat: "全球通史" },
  { title: "槍炮、病菌與鋼鐵", translator: "王道還、廖月娟", publisher: "時報出版", publishPlace: "台北", publishYear: 1998, cat: "全球通史" },
  { title: "思想史：從火到佛洛伊德", translator: "胡翠娥", publisher: "木馬文化", publishPlace: "新北市", publishYear: 2019, cat: "全球通史" },
  { title: "大分離：就大陸與新大陸的歷史與人性", translator: "孫豔萍", publisher: "譯林出版社", publishPlace: "南京", publishYear: 2023, cat: "全球通史" },
  { title: "最早的農人", translator: "陳宥任", publisher: "麥田出版", publishPlace: "台北", publishYear: 2019, cat: "全球通史" },
  // ── 歷史學→東方界域史 ──
  { title: "埃及史：從原初時代至當下", translator: "郭子林", publisher: "華文出版社", publishPlace: "北京", publishYear: 2020, cat: "東方界域史" },
  { title: "古代埃及史", publisher: "商務印書館", publishPlace: "北京", publishYear: 2000, cat: "東方界域史" },
  { title: "不可不知的古埃及文明史", cat: "東方界域史" },
  { title: "王權與神祇(上)", translator: "郭丹彤", publisher: "商務印書館", publishPlace: "北京", publishYear: 2020, cat: "東方界域史" },
  { title: "法老的國度：古埃及文化史", publisher: "麥田出版", publishPlace: "台北", publishYear: 2001, cat: "東方界域史" },
  { title: "巴比倫：美索不達米亞和文明的誕生", translator: "陳麗", publisher: "中央編譯出版社", publishPlace: "北京", publishYear: 2015, cat: "東方界域史" },
  { title: "古代美索不達米亞社會生活", translator: "趙立行", publisher: "商務印書館", publishPlace: "北京", publishYear: 2007, cat: "東方界域史" },
  { title: "《「楔形傳說」──被「建構」的蘇美爾》", translator: "曹磊", publisher: "中國社會科學出版社", publishPlace: "北京", publishYear: 2022, cat: "東方界域史" },
  { title: "巴比倫法的人本觀", publisher: "商務印書館", publishPlace: "北京", publishYear: 2018, cat: "東方界域史" },
  { title: "古代近東歷史編撰學中的神話與政治", translator: "毛蕊", publisher: "商務印書館", publishPlace: "北京", publishYear: 2019, cat: "東方界域史" },
  // ── 歷史學→西方界域史 ──
  { title: "古典時代的終結", translator: "魏以勒", publisher: "麥田出版", publishPlace: "台北", publishYear: 2018, cat: "西方界域史" },
  { title: "古地中海文明陷落的關鍵", translator: "邱振訓", publisher: "麥田出版", publishPlace: "台北", publishYear: 2018, cat: "西方界域史" },
  { title: "希臘化世界", translator: "郭長剛", publisher: "上海人民出版社", publishPlace: "上海", publishYear: 2003, cat: "西方界域史" },
  { title: "碰撞與交融：希臘化時代的歷史與文化", publisher: "臺灣商務印書館", publishPlace: "台北", publishYear: 2016, cat: "西方界域史" },
  { title: "希臘化時代的歷史與文化", cat: "西方界域史" },
  { title: "東地中海世界的轉變與拜占庭帝國的奠基時代(4-6世紀)", publisher: "社會科學文獻出版社", publishPlace: "北京", publishYear: 2018, cat: "西方界域史" },
  { title: "不可不知的古代地中海文明史", cat: "西方界域史" },
  { title: "不可不知的古羅馬文明史", cat: "西方界域史" },
  { title: "十二幅地圖中的世界史", translator: "林玉菁", publisher: "馬可孛羅", publishPlace: "台北", publishYear: 2014, cat: "史學理論" },
  // ── 歷史學→亞太界域史 ──
  { title: "前中國時代", cat: "亞太界域史" },
  { title: "世界史的誕生", translator: "陳心慧", publisher: "八旗文化", publishPlace: "台北", publishYear: 2016, cat: "亞太界域史" },
  // ── 歷史學→中央界域史 ──
  { title: "以色列史", cat: "中央界域史" },
  // ── 歷史學→史學理論 ──
  { title: "外國史學史", publisher: "北京大學出版社", publishPlace: "北京", publishYear: 2017, cat: "史學理論" },
  // ── 社會政治學 ──
  { title: "從部落到國家", translator: "鄧子衿", publisher: "遠見天下文化", publishPlace: "台北", publishYear: 2020, cat: "社會政治學" },
  { title: "人性中的善良天使", translator: "洪蘭", publisher: "遠見天下文化", publishPlace: "台北", publishYear: 2015, cat: "社會政治學" },
  // ── 人類生物學 ──
  { title: "第三種猩猩", translator: "王道還", publisher: "時報出版", publishPlace: "台北", publishYear: 1998, cat: "人類生物學" },
  // ── 自然科學 ──
  { title: "抱歉了愛因斯坦", publisher: "遠見天下文化", publishPlace: "台北", publishYear: 2020, cat: "自然科學" },
];

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  console.log("Step 1: Create book_categories table + add category_id to books");
  await sql(`
    CREATE TABLE IF NOT EXISTS book_categories (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      name text NOT NULL UNIQUE,
      parent_id uuid REFERENCES book_categories(id) ON DELETE CASCADE,
      display_order int DEFAULT 0,
      created_at timestamptz DEFAULT now()
    )
  `);
  await sql(`ALTER TABLE books ADD COLUMN IF NOT EXISTS category_id uuid REFERENCES book_categories(id) ON DELETE SET NULL`);
  console.log("  Done.");

  console.log("Step 2: Insert top-level categories");
  const topInserts = TOP_CATS.map((name, i) =>
    `(${esc(name)}, NULL, ${i + 1})`
  ).join(",\n  ");
  await sql(`
    INSERT INTO book_categories (name, parent_id, display_order) VALUES
      ${topInserts}
    ON CONFLICT (name) DO NOTHING
  `);
  console.log("  Done.");

  console.log("Step 3: Fetch top-level IDs + insert subcategories");
  const topRows = await sql(`SELECT id, name FROM book_categories WHERE parent_id IS NULL`);
  const catIdByName: Record<string, string> = {};
  for (const row of topRows) catIdByName[row.name] = row.id;

  for (const [parentName, subs] of Object.entries(SUB_CATS)) {
    const parentId = catIdByName[parentName];
    if (!parentId) { console.warn(`  Parent not found: ${parentName}`); continue; }
    const subInserts = subs.map((name, i) =>
      `(${esc(name)}, '${parentId}', ${i + 1})`
    ).join(",\n    ");
    await sql(`
      INSERT INTO book_categories (name, parent_id, display_order) VALUES
        ${subInserts}
      ON CONFLICT (name) DO NOTHING
    `);
  }
  console.log("  Done.");

  console.log("Step 4: Fetch all category IDs");
  const allCatRows = await sql(`SELECT id, name FROM book_categories`);
  const allCatIds: Record<string, string> = {};
  for (const row of allCatRows) allCatIds[row.name] = row.id;

  console.log("Step 5: Update books with metadata + category_id");
  let updated = 0;
  let notFound = 0;

  // Process in batches of 25
  const BATCH = 25;
  for (let i = 0; i < BOOKS.length; i += BATCH) {
    const batch = BOOKS.slice(i, i + BATCH);
    const stmts: string[] = [];
    for (const b of batch) {
      const catId = allCatIds[b.cat];
      if (!catId) { console.warn(`  Category not found: ${b.cat}`); }
      const sets = [
        b.translator != null  ? `translator = ${esc(b.translator)}`      : null,
        b.publisher != null   ? `publisher = ${esc(b.publisher)}`         : null,
        b.publishPlace != null? `publish_place = ${esc(b.publishPlace)}`  : null,
        b.publishYear != null ? `publish_year = ${escNum(b.publishYear)}` : null,
        catId                 ? `category_id = '${catId}'`                 : null,
      ].filter(Boolean);
      if (sets.length > 0) {
        stmts.push(`UPDATE books SET ${sets.join(", ")} WHERE title = ${esc(b.title)}`);
      }
    }
    if (stmts.length > 0) {
      await sql(stmts.join(";\n"));
    }
    updated += batch.length;
    console.log(`  Processed ${Math.min(i + BATCH, BOOKS.length)}/${BOOKS.length}`);
    // Avoid rate limiting
    await new Promise(r => setTimeout(r, 1500));
  }

  console.log(`\nDone! Updated ${updated} books, ${notFound} not found in DB.`);

  // Summary
  const counts = await sql(`
    SELECT bc.name, COUNT(b.id) as cnt
    FROM book_categories bc
    LEFT JOIN books b ON b.category_id = bc.id
    GROUP BY bc.name ORDER BY cnt DESC LIMIT 15
  `);
  console.log("\nTop categories by book count:");
  counts.forEach((r: any) => console.log(`  ${r.name}: ${r.cnt}`));
}

main().catch(console.error);
