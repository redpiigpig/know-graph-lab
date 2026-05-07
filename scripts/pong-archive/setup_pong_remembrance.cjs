// 建立 pong_remembrance 資料表並插入初始資料
require('dotenv').config()
const { createClient } = require('@supabase/supabase-js')

const SUPABASE_URL = process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL
const supabase = createClient(SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY)

// ── Create table via Management API ──────────────────────────────────────────

async function createTable() {
  const ref = SUPABASE_URL.split('//')[1].split('.')[0]
  const token = process.env.SUPABASE_ACCESS_TOKEN
  if (!token) throw new Error('SUPABASE_ACCESS_TOKEN 未設定')

  const sql = `
    CREATE TABLE IF NOT EXISTS pong_remembrance (
      id           SERIAL PRIMARY KEY,
      title        TEXT NOT NULL,
      author       TEXT,
      source       TEXT,
      source_url   TEXT,
      published_at DATE,
      category     TEXT NOT NULL DEFAULT 'tribute',
      content      TEXT,
      summary      TEXT,
      tags         TEXT[],
      sort_order   INTEGER DEFAULT 0,
      is_published BOOLEAN DEFAULT TRUE,
      created_at   TIMESTAMPTZ DEFAULT NOW()
    );
    ALTER TABLE pong_remembrance ADD COLUMN IF NOT EXISTS category TEXT NOT NULL DEFAULT 'tribute';
    ALTER TABLE pong_remembrance ADD COLUMN IF NOT EXISTS author TEXT;
    ALTER TABLE pong_remembrance ADD COLUMN IF NOT EXISTS source TEXT;
    ALTER TABLE pong_remembrance ADD COLUMN IF NOT EXISTS source_url TEXT;
    ALTER TABLE pong_remembrance ADD COLUMN IF NOT EXISTS published_at DATE;
    ALTER TABLE pong_remembrance ADD COLUMN IF NOT EXISTS content TEXT;
    ALTER TABLE pong_remembrance ADD COLUMN IF NOT EXISTS summary TEXT;
    ALTER TABLE pong_remembrance ADD COLUMN IF NOT EXISTS tags TEXT[];
    ALTER TABLE pong_remembrance ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;
    ALTER TABLE pong_remembrance ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT TRUE;
    CREATE INDEX IF NOT EXISTS idx_pong_remembrance_sort ON pong_remembrance(sort_order);
  `

  const r = await fetch(`https://api.supabase.com/v1/projects/${ref}/database/query`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: sql }),
  })
  const body = await r.text()
  if (!r.ok) throw new Error(`建表失敗 ${r.status}: ${body}`)
  console.log(`✅ pong_remembrance 建表完成（HTTP ${r.status}）`)

  // Reload PostgREST schema cache so new columns are visible to JS client
  await fetch(`https://api.supabase.com/v1/projects/${ref}/database/query`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: `NOTIFY pgrst, 'reload schema'` }),
  })
  console.log('✅ schema cache reload 已發送')
  // Give PostgREST a moment to pick up the change
  await new Promise(r => setTimeout(r, 3000))
}

// ── Articles ──────────────────────────────────────────────────────────────────

const ARTICLES = [
  {
    title: '念君華',
    author: '邢福增',
    source: '時代論壇',
    source_url: 'https://christiantimes.org.hk/Common/Reader/News/ShowNews.jsp?Nid=178826&Pid=104&Version=0&Cid=2053&Charset=big5_hkscs',
    published_at: '2026-01-16',
    category: 'tribute',
    tags: ['悼念', '緬懷', '時代論壇', '香港', '2026'],
    sort_order: 1,
    is_published: true,
    summary: '邢福增教授回憶與龐君華相識近四十年的情誼，從1987年香港崇基神學院到台北城中教會，記述其謙遜牧養、對衛理宗傳統的深厚委身，以茶道精神比喻其悠然品格。',
    content: `1987年，一位從台灣來香港崇基神學院修讀神學的年輕人來到安素堂實習，任青年團契導師，他的名字是龐君華。原來他在香港出生，所以通諳粵語。那年我剛從中文大學本科畢業，並繼續進修碩士。除了在安素堂外，我們也在中大校園接觸，很快便熟絡起來。

有一次（大概是1988），青團在烏溪沙退修，他在營內帶分組，記得他要我們在一張紙上，寫自己的墓誌銘。我已忘記自己寫了甚麼，大概是保羅「打美好的仗……走當跑的路」之類。沒想到，多年後，墓園與墓碑成為自己的愛好。退修營晚上最好是聊天。那年初蔣經國剛離世，他跟我們談台灣的政治，指繼任的李登輝具台籍背景，讓我這「香港人」明白外省政權與本省人的糾結與矛盾。他又跟我們講了一個有關李登輝為何能當副總統的政治笑話：有次，蔣經國開國民黨中常委會議，要眾人提名副總統人選。由於眾常委不知老總統心意，會議間一片靜寂，生怕說出不是蔣心目中的人選。剛好老人家要去如廁，說了一句：「你等一會」（ni deng yi hui），眾人聽成為「李登輝」（li deng hui），於是便出了首位本省籍的副總統了。笑話反映威權體制下，強人一錘定音的領導現象。後來，他又跟我們分析李登輝的政治手腕，如何在外省人主導的國民黨內，逐步站穩陣腳，令我聽得入神。君華是外省人，卻對台灣本土政治有所認識，並給我介紹鄉土及本土神學。這位青年團契導師，在信仰問題以外，竟成了我的台灣政治及本土神學的啟蒙老師。

君華當時住在神學樓。太太肇悅在循道衛理總議會文字事工部事奉，記得有幾次在灣仔總議會開完會後，晚上跟肇悅一起搭火車回中大。君華開車到火車站接太太時，我都可以搭順風車回研究院宿舍。有一年我當了青團團長，跟職員會到崇基退修，由於君華夫婦都剛好那天不在神樓，讓我們可以到其宿舍「屈蛇」。但不知為何神樓地下大門在週末上了鎖，最後，我是爬水渠上二樓，然後再打開大門讓眾人入內。幸好，沒有給人見到。

1992年君華神道學學士（BD）畢業，邀請我們出席神學日。記得他是學生致詞的代表。神學日後，就到神學樓大廳用餐。那年，我已辭去中學教席，回中大讀博士，君華也繼續進修神學碩士。1996至99年間，君華任基督教中國宗教文化研究社副社長，我常到旺角僑健大廈宗文社查看圖書館有關中國教會的資料（沒想到，後來我竟當上宗文社副社長及社長）。每次上去，君華都會泡茶跟我聊天，分享他關於台灣本土神學的研究，又提到之後繼續進修神學博士，或回台灣牧會的抉擇。最後，相信是出於對衛理公會的委身，他放棄讀博士。即或如此，其學養卻成就一位具人文社會關懷的牧者。

君華回衛理公會後，有段長時間在城中教會任主任牧師。因此，每次到台北時，都會到城中探他，聽其分享建立牧區的異象。2017至18年間，因安息年在台北研究寫作，較多機會到城中崇拜。他總在飯後請我留下，到他辦公室泡茶……他對重建衛理宗傳統有很大抱負，並送我他用心編撰的經課讀經靈修資料。同時，他又在衛理神學研究院事奉，邀我到衛神參觀及分享。2019至22年間，君華被選為會督，對於一位中風康復者而言，無疑是很大挑戰。不過，同樣是出於對衛理公會的委身，讓他毅然承擔重任。2022年9至12月，再次安息年訪台，有一次出席城中崇拜，剛好遇上教會為他預備的榮休感恩會。他卸下牧職，希望可以有更多時間投身神學教育……

2023年底提早退休移居台灣後，君華常關心我們一家。2024年5月神學院同學來台交流，跟在台校友重聚，濟濟一堂，好不熱鬧。君華以「大師兄」身份出席。那時剛好遇上立法院爭議及青鳥行動，他最後請眾人為台灣禱告，台灣民主正面對很大挑戰……最後一次見面，應是去年3月在城中，他特別跟我分享對衛理公會神學教育的想法（這是他多年未竟心願），並指希望衛神與東吳大學（衛理公會背景）可以有更好的合作（他以崇基與中大的關係作參照）。離開時，君華仍跟我說，日後要找我再談此事……

昨早在捷運收到君華離世的消息，委實難以接受。1987年認識至今，從香港到台北，相知相交近四十載。2019年時，出土了一張1989年的舊照，是君華與我，跟當年崇基畢業的Martin（陳崇榮）的合照。兩人是我當時最熟悉，也是對我影響最深的神學生。Martin畢業後，在循道衛理任宣教師，卻在1990年因病離世。君華委身事奉，至退休後仍不間斷。兩人都是我生命的導師，在世及事奉的長短不一，卻忠誠及真實地回應上主的召命。令我再想起電影「大濛」中「雲」與「霧」的借寓：有些水滴能聚集成雲，再變成雨水滋潤大地。不過，有些落在沙漠，卻始終無法改變乾旱的環境。又有些卡在半空，只能作白濛濛的一片濛霧。電影導演在分享時曾說：「不管是雲是霧， 我們不該忘記那一片風景」、「人會消失，但風景會留下」、「我們現在的風景，都是前人建立的，我們也應該建立很好的一片風景給後人。」我們的生命，有時是雲，有時是霧。不管如何，只要努力，都是一片風景。

君華已經盡力，每一位認識他的人都能見證，他以生命繪出天國的風景。讓我們仰望天空，想像他就在天國某個角落，端出他最喜受的茶盤及茶具，泡一壺熱水，悠然自得地品一口茶。他在靜觀我們的風景，並等待某日再為我們泡茶共聚。`,
  },
  {
    title: '世上該當還有龐君華',
    author: '莊新泉',
    source: '基督教論壇報',
    source_url: null,  // 從 pong_reports 抓取
    published_at: '2026-01-28',
    category: 'tribute',
    tags: ['悼念', '緬懷', '基督教論壇報', '2026'],
    sort_order: 2,
    is_published: true,
    summary: null,
    content: null,  // 從 pong_reports 複製
  },
]

// ── Insert helpers ────────────────────────────────────────────────────────────

async function insertOne(article) {
  // Check by source_url or title
  let query = supabase.from('pong_remembrance').select('id')
  if (article.source_url) {
    query = query.eq('source_url', article.source_url)
  } else {
    query = query.eq('title', article.title)
  }
  const { data: existing } = await query.maybeSingle()
  if (existing) {
    console.log(`⏭  已存在，跳過：${article.title}`)
    return
  }
  const { error } = await supabase.from('pong_remembrance').insert(article)
  if (error) {
    console.error(`❌ 新增失敗：${article.title}`, error.message)
  } else {
    console.log(`✅ 已插入：${article.title}`)
  }
}

// ── Copy content from pong_reports ───────────────────────────────────────────

async function copyFromReports(title) {
  const { data, error } = await supabase
    .from('pong_reports')
    .select('content, summary, source_url')
    .eq('title', title)
    .maybeSingle()
  if (error || !data) {
    console.warn(`⚠️  pong_reports 中找不到「${title}」，content 留 null`)
    return null
  }
  return { content: data.content, summary: data.summary, source_url: data.source_url }
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  await createTable()

  for (const article of ARTICLES) {
    // If content is null and title matches, try to copy from pong_reports
    if (!article.content && article.title === '世上該當還有龐君華') {
      const fromReports = await copyFromReports(article.title)
      if (fromReports) {
        article.content = fromReports.content
        article.summary = fromReports.summary
        if (!article.source_url && fromReports.source_url) {
          article.source_url = fromReports.source_url
        }
        console.log(`📋 已從 pong_reports 複製 content：${article.title}`)
      }
    }
    await insertOne(article)
  }

  // Verify
  const { data, error } = await supabase
    .from('pong_remembrance')
    .select('id, title, author, category, published_at, is_published')
    .order('sort_order')
  if (error) { console.error('驗證失敗', error.message); return }
  console.log('\n── 目前 pong_remembrance ──')
  for (const r of data) {
    console.log(`[${r.id}] ${r.category} | ${r.published_at ?? '日期未知'} | ${r.author ?? '?'} | ${r.title.slice(0, 35)}`)
  }
}

main().catch(err => { console.error(err); process.exit(1) })
