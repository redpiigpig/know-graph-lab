// 建立 pong_reports 資料表並插入初始資料（使用 Supabase REST API）
require('dotenv').config()
const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  process.env.VITE_SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

// 四篇有完整全文；三篇僅有標題與連結，content 留空待補
const ARTICLES = [
  {
    sort_order: 1,
    title: '衛理公會龐君華會督：同志議題難達共識　分家是務實作法',
    source: '基督教論壇報',
    source_url: 'https://www.ct.org.tw/1380496',
    author: null,
    published_at: null,
    content: null,
    summary: null,
    tags: ['同志議題', '教會合一', '衛理公會'],
  },
  {
    sort_order: 2,
    title: '「不冷不熱」是教會大危機　龐君華會督卸任前提醒：找回起初的愛！',
    source: '基督教今日報',
    source_url: 'https://www.cdn-news.org/news/N2205200006',
    author: null,
    published_at: '2022-05-20',
    content: null,
    summary: null,
    tags: ['卸任', '屬靈危機', '起初的愛'],
  },
  {
    sort_order: 3,
    title: '【衛理公會新任會督】龐君華：成為「真實門徒」　從牧者及會友領袖先開始',
    source: '基督教論壇報',
    source_url: 'https://ct.org.tw/html/news/3-3.php?cat=12&article=1338027',
    author: '蔡明憲',
    published_at: '2019-02-22',
    content: `中華基督教衛理公會於2月22日舉行第五十六屆年議會，選出龐君華牧師為新任會督。現任會督陳建中與龐君華皆強調當前衛理公會最重要的任務是實踐「真實門徒的生命」。

龐牧師表示，「會督是『責任』，不是『權力』」，他將致力於推動門徒生命的實踐。他認為教會領袖應當率先示範信仰，強調「『生命』是一切事奉最重要的基礎」。

陳建中會督分享見證，說明基督徒信仰應當在生活中真實可見。他以約翰衛斯理的精神勉勵眾人，鼓勵信徒家庭承諾「事奉耶和華」。

新任團隊包括會友會長趙慧敏與牧職會長劉天惠牧師，將於五月正式上任。`,
    summary: '衛理公會年議會選出龐君華為新任會督，強調推動「真實門徒的生命」，認為會督是責任而非權力。',
    tags: ['就任', '真實門徒', '衛理公會', '2019'],
  },
  {
    sort_order: 4,
    title: '衛理公會新任會督就任　龐君華：活出「徹底的門徒」邀請世人加入門徒行列',
    source: '基督教論壇報',
    source_url: 'https://ct.org.tw/html/news/3-3.php?cat=12&article=1342933',
    author: '蔡明憲',
    published_at: '2019-05-25',
    content: `中華基督教衛理公會於5月25日在台北衛理堂舉行會督就任禮拜。新任會督龐君華在陳建中會督的主禮下正式就任。

龐君華會督表示將延續上屆「徹底的門徒」異象，作為牧養與宣教的目標。他強調：「若沒有真實的門徒，就沒有真正的教會。」他指出基督徒應當對耶穌的呼召「來跟從我」做出清楚回應，真正跟隨主的人自然會為主做見證，愛周圍的人。

龐會督提醒不應滿足於「差不多的基督徒」，而應追求活出聖潔生命的力量。他強調循道衛理運動的信念，認為救恩應透過門徒生活來實踐，用此邀請世人加入主的門徒行列。

新加坡衛理公會張振忠會督則以「忠僕良牧：餵養我的羊」為題證道，提醒傳道人應牧養主耶穌所交託的羊群。

會中並舉行按牧禮、同工就職與差派禮拜。`,
    summary: '龐君華正式就任衛理公會會督，延續「徹底的門徒」異象，強調真實門徒才有真正的教會。',
    tags: ['就任', '徹底的門徒', '衛理公會', '2019'],
  },
  {
    sort_order: 5,
    title: '深耕靈性培育關顧　衛理公會前會督龐君華牧師安息主懷',
    source: '基督教論壇報',
    source_url: 'https://ct.org.tw/html/news/3-3.php?cat=10&article=1403041',
    author: '李容珍',
    published_at: '2026-04-15',
    content: `中華基督教衛理公會前會督龐君華牧師因突發心肌梗塞安息主懷，享年68歲。

衛理神學研究院指出，龐牧師「長年在衛理公會以及衛理神學研究院的服事中，謙卑擺上、殷勤牧養，以生命影響生命」。聖公會三一書院取消了原定由龐牧師授課的「靈修初探與操練」課程。

龐牧師畢業於香港中文大學崇基學院神學組，主修系統神學。曾任香港基督教中國文化宗教研究社副社長，並在台灣校園福音團契投入學生工作。2001年起於衛理公會城中教會牧會，歷任多項重要職務。

他強調衛理精神在於成為「真實的門徒」，認為教會應強調質而非量的成長，牧者與領袖應先做見證，體現「福音改變我們的心，我們跟上帝一起改變這個世界」的信念。`,
    summary: '龐君華牧師因突發心肌梗塞安息主懷，享年68歲，各界追念其謙卑牧養與靈性培育的深遠影響。',
    tags: ['安息主懷', '訃告', '衛理公會', '2026'],
  },
  {
    sort_order: 6,
    title: '教界快訊／衛理公會前會督龐君華牧師安息主懷　「世界就是我的牧區」',
    source: '基督教今日報',
    source_url: 'https://cdn-news.org/News.aspx?EntityID=News&PK=00000000a482501fab32bddda7e82e4c9b2f19e5b397c12e',
    author: null,
    published_at: '2026-04-15',
    content: null,
    summary: null,
    tags: ['安息主懷', '訃告', '衛理公會', '2026'],
  },
  {
    sort_order: 7,
    title: '竹聖靈性教育課程　幫助牧者了解崇拜意義與教會節期',
    source: '台灣教會公報新聞網',
    source_url: 'https://tcnn.org.tw/archives/228953',
    author: '林宜瑩',
    published_at: '2025-01-16',
    content: `新竹聖經學院靈性教育研習所邀請衛理公會前會督龐君華於1月13、14日主講「禮拜與牧養：在基督裡的靈性節奏」課程，與30多位長老教會牧師分享崇拜的意義、節期與禮拜的關聯性。

龐君華表示，「崇拜是公共的祈禱，基督徒是在教會崇拜中被形塑的群體」。他強調崇拜就是事奉，為使人與上帝相遇，並指出崇拜以上帝為中心而非人為中心，是恩典的途徑。

在教會禮儀方面，龐君華說明「聖事」包含聖道與聖禮，崇拜的基本模式包含預備禮、聖道禮、回應、聖餐禮與差遣禮。他舉例說明各節期的代表顏色：待降節期與大齋節期使用紫色，聖誕與復活節期使用白色，聖靈降臨節主日則使用紅色。

「教會年」以待降節期為一年起點，龐君華指出教會年具雙重意義：帶領信徒記念耶穌的誕生、復活與聖靈降臨，同時讓信徒經歷主內一家。他認為復活節是教會年的高峰。

竹聖院長阮介民表示該課程旨在幫助在牧會中遇到瓶頸的牧者獲得靈性滋養與重新得力。`,
    summary: '龐君華於新竹聖經學院主講崇拜與教會節期課程，強調崇拜以上帝為中心，是信徒靈性形塑的核心場域。',
    tags: ['崇拜', '教會節期', '靈性教育', '2025'],
  },
]

async function createTable() {
  // 用 rpc 執行 DDL
  const { error } = await supabase.rpc('exec_sql', {
    sql: `
      CREATE TABLE IF NOT EXISTS pong_reports (
        id           SERIAL PRIMARY KEY,
        title        TEXT NOT NULL,
        source       TEXT,
        source_url   TEXT,
        author       TEXT,
        published_at DATE,
        content      TEXT,
        summary      TEXT,
        tags         TEXT[],
        sort_order   INTEGER DEFAULT 0,
        is_published BOOLEAN DEFAULT TRUE,
        created_at   TIMESTAMPTZ DEFAULT NOW()
      );
    `
  })
  if (error) throw new Error('建表 rpc 失敗：' + JSON.stringify(error))
  console.log('✅ pong_reports 資料表已建立（或已存在）')
}

async function main() {
  // 先嘗試用 REST API 建表（需要 exec_sql rpc 存在）
  // 若無 rpc 則直接 upsert（表若不存在會報錯，屆時手動建表）
  try {
    await createTable()
  } catch (e) {
    console.warn('⚠️  exec_sql rpc 不存在，將直接嘗試插入（若表不存在會失敗）')
    console.warn(e.message)
  }

  let inserted = 0
  for (const a of ARTICLES) {
    // 確認是否已存在
    const { data: existing } = await supabase
      .from('pong_reports')
      .select('id')
      .eq('source_url', a.source_url)
      .maybeSingle()

    if (existing) {
      console.log(`⏭  已存在，跳過：${a.title.slice(0, 35)}…`)
      continue
    }

    const { error } = await supabase.from('pong_reports').insert(a)
    if (error) {
      console.error(`❌ 插入失敗：${a.title.slice(0, 35)}`, error.message)
    } else {
      console.log(`✅ 已插入：${a.title.slice(0, 40)}…`)
      inserted++
    }
  }

  // 驗證
  const { data, error } = await supabase
    .from('pong_reports')
    .select('id, title, source, published_at, content')
    .order('sort_order')

  if (error) { console.error('驗證查詢失敗', error.message); return }

  console.log('\n── 目前 pong_reports 資料 ──')
  for (const r of data) {
    const hasContent = !!r.content
    console.log(`[${r.id}] ${r.source} | ${r.published_at ?? '日期未知'} | 全文:${hasContent ? '✅' : '❌'} | ${r.title.slice(0, 40)}`)
  }
  console.log(`\n共插入 ${inserted} 筆`)
}

main().catch(err => { console.error(err); process.exit(1) })
