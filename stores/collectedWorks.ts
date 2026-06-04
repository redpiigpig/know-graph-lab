/**
 * 全集（Collected Works）store
 *
 * 經典學者全集的「最外層」作家 hub 資料：學術貢獻簡介、肖像、生平學術年表、
 * 按類別與年分編排的完整著作目錄（含轉錄狀態）。
 *
 * - portal：/collected-works（列出所有作家）
 * - 作家 hub：/collected-works/[slug]（簡介＋肖像＋年表＋著作目錄）
 * - 單卷閱讀沿用既有 /ebook/[id] 多欄 reader（work.ebookId 連過去）
 *
 * 編輯方式：直接改本檔（沿用 stores/speech.ts、/works 的 repo-committed 模式）。
 * 肖像走 Wikimedia Commons 公有領域圖（Special:FilePath，?width= 取縮圖），不用 Supabase Storage。
 * 方法論與版權盡職調查見 .claude/skills/ebook-collected-works/。
 */
import { defineStore } from 'pinia'

/** 轉錄狀態 */
export type WorkStatus =
  | 'done' // 已轉錄上架，可進 reader
  | 'in-progress' // 轉錄中（pilot / 部分章節）
  | 'planned' // 已排入、尚未轉錄
  | 'copyright' // 受版權限制，待合法來源

export interface CwTimelineEntry {
  year: string // "1823"、"1846–1848"
  text: string // 事件（繁中）
}

export interface CwWork {
  title: string // 繁中書名
  titleOriginal?: string // 原文書名（英／德…）
  year: string // 出版年（顯示用，可為區間）
  yearSort: number // 排序用單一年分
  category: string // 類別／群組（hub 內分組依據）
  languages?: string[] // 可得來源語言 code，如 ['en','de']
  status: WorkStatus
  ebookId?: string // 已轉錄時連到 /ebook/[id]
  note?: string // 備註（版權、進度…）
}

export interface CwAuthor {
  slug: string
  name: string // 繁中全名
  nameEn?: string
  nameOriginal?: string
  lifespan: string // "1823–1900"
  discipline: string // 一句話定位（portal 卡片副標）
  fields: string[] // 領域標籤
  portraitUrl: string
  portraitCredit?: string
  color: string // tailwind 色（safelist 見 tailwind.config.ts）
  emoji: string
  contribution: string[] // 學術貢獻簡介（繁中，段落陣列）
  sourceNote?: string // 來源／語言策略一句話
  timeline: CwTimelineEntry[]
  works: CwWork[]
}

export const useCollectedWorksStore = defineStore('collectedWorks', () => {
  const authors = ref<CwAuthor[]>([
    // ────────────────────────────────────────────────────────────────
    // 弗里德里希‧馬克斯‧穆勒（宗教學開山祖）
    // ────────────────────────────────────────────────────────────────
    {
      slug: 'max-mueller',
      name: '弗里德里希‧馬克斯‧穆勒',
      nameEn: 'Friedrich Max Müller',
      nameOriginal: 'Friedrich Max Müller',
      lifespan: '1823–1900',
      discipline: '比較宗教學與比較語言學的奠基者，「宗教學（the science of religion）」一詞的倡立者',
      fields: ['宗教學', '比較神話學', '比較語言學', '印度學', '東方學'],
      portraitUrl:
        'https://commons.wikimedia.org/wiki/Special:FilePath/Friedrich%20Max%20M%C3%BCller,%201898.jpg?width=500',
      portraitCredit: '1898 年攝‧Wikimedia Commons（公有領域）',
      color: 'sky',
      emoji: '🕉️',
      contribution: [
        '弗里德里希‧馬克斯‧穆勒是十九世紀最具影響力的東方學者之一，公認為**比較宗教學（comparative religion）／宗教學（the science of religion）的開山祖師**。他 1870 年於倫敦皇家研究院講授的四場講座（1873 年成書《宗教學導論》），首次主張宗教可以、也應當以比較與科學的方法研究，為宗教學立下學科基礎。',
        '他借用歌德論語言的名言，鑄成宗教研究最著名的格言——**「只知其一，便一無所知（He who knows one, knows none）」**：唯有把基督宗教放回世界諸宗教的脈絡中比較，才能真正理解任一宗教。',
        '在神話學上，他提出**「神話是語言的疾病（a disease of language）」**之說，並發展出以日象解神話的「太陽神話論」；他也以印歐比較語言學的方法，論證吠陀天神 Dyaus（特尤斯）與希臘 Zeus、拉丁 Jupiter 同源，並提出**單一神教（henotheism）**這一描述吠陀宗教的概念。',
        '其最龐大的學術工程，是主編五十卷的**《東方聖書（Sacred Books of the East）》**，將印度教、佛教、祆教、耆那教、道教、儒家與伊斯蘭的核心經典系統英譯，奠定了現代東方學與宗教文獻學的基石。',
      ],
      sourceNote:
        '穆勒以英文寫作為主（牛津），故來源以英文原典為準；少數有他監修的平行德文版者（如《宗教學導論》＝德文《Einleitung》1874）做英／德／繁中三欄。卒於 1900，全部著作已進入公有領域。',
      timeline: [
        { year: '1823', text: '生於德國德紹（Dessau），父為浪漫派詩人威廉‧穆勒。' },
        { year: '1841', text: '入萊比錫大學，主修梵文與比較語言學。' },
        { year: '1844', text: '赴柏林，從謝林（Schelling）與波普（Bopp）問學。' },
        { year: '1846', text: '定居英國，受東印度公司委託校編《梨俱吠陀》及薩亞納註。' },
        { year: '1850', text: '任牛津現代歐洲語言副教授。' },
        { year: '1854', text: '任牛津泰勒講座教授（Taylorian Professor）。' },
        { year: '1856', text: '發表〈比較神話學〉，提出以語言學解神話的綱領。' },
        { year: '1860', text: '競選牛津梵文講座教授落敗（Monier-Williams 當選），轟動學界。' },
        { year: '1868', text: '出任牛津首任比較語言學教授。' },
        { year: '1870', text: '於皇家研究院講「宗教學」四講——宗教學作為一門學科的誕生。' },
        { year: '1873', text: '《宗教學導論》出版，學科奠基之作。' },
        { year: '1875', text: '起主編《東方聖書》五十卷（至身後續出）。' },
        { year: '1878', text: '主講希伯特講座《宗教起源與發展》。' },
        { year: '1888–1892', text: '主講格拉斯哥吉福德講座，成四卷宗教學鉅著。' },
        { year: '1896', text: '獲任樞密院顧問官（Right Honourable）。' },
        { year: '1900', text: '卒於牛津。' },
      ],
      works: [
        // 宗教學奠基
        {
          title: '宗教學導論',
          titleOriginal: 'Introduction to the Science of Religion',
          year: '1873',
          yearSort: 1873,
          category: '宗教學奠基',
          languages: ['en', 'de'],
          status: 'in-progress',
          ebookId: '33333333-3333-4333-8333-333333333333',
          note: '起手卷 ‧ 皇家研究院四講＋兩附論；英德同構，英／德／繁中三欄逐段對照（轉錄中）。',
        },
        {
          title: '宗教起源與發展講座',
          titleOriginal: 'Lectures on the Origin and Growth of Religion',
          year: '1878',
          yearSort: 1878,
          category: '宗教學奠基',
          languages: ['en'],
          status: 'planned',
          note: '希伯特講座（Hibbert Lectures）。',
        },
        // Gifford 四講
        {
          title: '自然宗教',
          titleOriginal: 'Natural Religion',
          year: '1888',
          yearSort: 1888,
          category: 'Gifford 講座（宗教學四部）',
          languages: ['en'],
          status: 'planned',
          note: 'Longmans《全集》第一卷。',
        },
        {
          title: '物質宗教',
          titleOriginal: 'Physical Religion',
          year: '1890',
          yearSort: 1890,
          category: 'Gifford 講座（宗教學四部）',
          languages: ['en'],
          status: 'planned',
        },
        {
          title: '人類學宗教',
          titleOriginal: 'Anthropological Religion',
          year: '1891',
          yearSort: 1891,
          category: 'Gifford 講座（宗教學四部）',
          languages: ['en'],
          status: 'planned',
        },
        {
          title: '心理宗教（神智學）',
          titleOriginal: 'Theosophy, or Psychological Religion',
          year: '1892',
          yearSort: 1892,
          category: 'Gifford 講座（宗教學四部）',
          languages: ['en'],
          status: 'planned',
        },
        // 語言與神話學
        {
          title: '比較神話學',
          titleOriginal: 'Comparative Mythology',
          year: '1856',
          yearSort: 1856,
          category: '語言與神話學',
          languages: ['en'],
          status: 'planned',
        },
        {
          title: '語言科學講座',
          titleOriginal: 'Lectures on the Science of Language',
          year: '1861',
          yearSort: 1861,
          category: '語言與神話學',
          languages: ['en'],
          status: 'planned',
          note: '兩卷。',
        },
        {
          title: '神話科學論集',
          titleOriginal: 'Contributions to the Science of Mythology',
          year: '1897',
          yearSort: 1897,
          category: '語言與神話學',
          languages: ['en'],
          status: 'planned',
          note: '兩卷。',
        },
        // 印度學
        {
          title: '古代梵文文學史',
          titleOriginal: 'A History of Ancient Sanskrit Literature',
          year: '1859',
          yearSort: 1859,
          category: '印度學',
          languages: ['en'],
          status: 'planned',
        },
        {
          title: '印度能教我們什麼？',
          titleOriginal: 'India: What Can It Teach Us?',
          year: '1883',
          yearSort: 1883,
          category: '印度學',
          languages: ['en'],
          status: 'planned',
        },
        {
          title: '印度哲學六派',
          titleOriginal: 'The Six Systems of Indian Philosophy',
          year: '1899',
          yearSort: 1899,
          category: '印度學',
          languages: ['en'],
          status: 'planned',
        },
        // 文集與譯著
        {
          title: '德國作坊雜記',
          titleOriginal: 'Chips from a German Workshop',
          year: '1867–1875',
          yearSort: 1867,
          category: '文集與回憶',
          languages: ['en'],
          status: 'planned',
          note: '全集重排為四／五卷。',
        },
        {
          title: '往日時光（憶往）',
          titleOriginal: 'Auld Lang Syne',
          year: '1898',
          yearSort: 1898,
          category: '文集與回憶',
          languages: ['en'],
          status: 'planned',
        },
        {
          title: '自傳片段',
          titleOriginal: 'My Autobiography: A Fragment',
          year: '1901',
          yearSort: 1901,
          category: '文集與回憶',
          languages: ['en'],
          status: 'planned',
        },
        {
          title: '東方聖書（主編）',
          titleOriginal: 'The Sacred Books of the East',
          year: '1879–1910',
          yearSort: 1879,
          category: '主編譯本集',
          languages: ['en'],
          status: 'planned',
          note: '五十卷東方經典英譯集；性質為譯本集，未來或獨立成 corpus。',
        },
      ],
    },

    // ────────────────────────────────────────────────────────────────
    // 卡爾‧古斯塔夫‧榮格（分析心理學）
    // ────────────────────────────────────────────────────────────────
    {
      slug: 'jung',
      name: '卡爾‧古斯塔夫‧榮格',
      nameEn: 'Carl Gustav Jung',
      nameOriginal: 'Carl Gustav Jung',
      lifespan: '1875–1961',
      discipline: '分析心理學創立者；以原型、集體無意識、個體化等概念貫通心理學與宗教、神話、煉金術',
      fields: ['分析心理學', '深層心理學', '宗教心理學', '煉金術研究'],
      portraitUrl: 'https://commons.wikimedia.org/wiki/Special:FilePath/CGJung.jpg?width=500',
      portraitCredit: 'Wikimedia Commons（公有領域）',
      color: 'rose',
      emoji: '🌀',
      contribution: [
        '卡爾‧古斯塔夫‧榮格是**分析心理學（analytical psychology）的創立者**。他早年與佛洛伊德密切合作、後因對力比多與無意識的理解分歧而決裂，自此發展出獨立的深層心理學體系。',
        '他提出**集體無意識（collective unconscious）與原型（archetype）**理論，主張人類心靈深處共享一層超越個人經驗的心理結構；並以**個體化（individuation）**描述人格整合、趨向**自性（das Selbst）**的歷程。阿尼瑪／阿尼姆斯、陰影、人格面具、共時性等概念亦由他鑄成。',
        '榮格對**宗教、神話與煉金術**投入畢生研究，視其為集體無意識的象徵語言，使分析心理學與宗教學、比較神話學深度交織——這也是本全集對宗教研究者格外重要之處。',
      ],
      sourceNote:
        '榮格卒於 1961，德文《全集》(GW) 與英文《Collected Works》(CW) 多數卷受版權保護至 2031；僅 1929 前早期著作有乾淨公有領域來源。本站三欄對照從《力比多的轉化與象徵》(1912 德／1916 英) 早期版起步。',
      timeline: [
        { year: '1875', text: '生於瑞士凱斯維爾（Kesswil）。' },
        { year: '1900', text: '入蘇黎世伯格霍茲利精神病院，師從布魯勒。' },
        { year: '1906', text: '與佛洛伊德開始通信合作。' },
        { year: '1912', text: '《力比多的轉化與象徵》出版，種下與佛洛伊德決裂之因。' },
        { year: '1913–1917', text: '與佛洛伊德決裂，經歷「與無意識對峙」時期（《紅書》）。' },
        { year: '1921', text: '《心理類型》出版，提出內傾／外傾與四功能。' },
        { year: '1944', text: '任巴塞爾大學醫學心理學教授。' },
        { year: '1948', text: '蘇黎世榮格研究院成立。' },
        { year: '1961', text: '卒於瑞士庫斯納赫特（Küsnacht）。' },
      ],
      works: [
        {
          title: '力比多的轉化與象徵（早期版）',
          titleOriginal: 'Wandlungen und Symbole der Libido / Psychology of the Unconscious',
          year: '1912',
          yearSort: 1912,
          category: '早期著作（公有領域）',
          languages: ['de', 'en'],
          status: 'in-progress',
          ebookId: '22222222-2222-4222-8222-222222222222',
          note: '德 1912 原典＋Hinkle 1916 英譯，德／英／繁中三欄試譯進行中（≠ CW 第五卷改寫本）。',
        },
        {
          title: '轉化的象徵（CW 5）',
          titleOriginal: 'Symbols of Transformation',
          year: '1952',
          yearSort: 1952,
          category: '《全集》各卷（CW / GW）',
          status: 'copyright',
          note: '1912 原典的大幅改寫本；受版權至 2031，待合法來源。',
        },
        {
          title: '心理類型（CW 6）',
          titleOriginal: 'Psychological Types',
          year: '1921',
          yearSort: 1921,
          category: '《全集》各卷（CW / GW）',
          status: 'copyright',
        },
        {
          title: '原型與集體無意識（CW 9i）',
          titleOriginal: 'The Archetypes and the Collective Unconscious',
          year: '1959',
          yearSort: 1959,
          category: '《全集》各卷（CW / GW）',
          status: 'copyright',
        },
        {
          title: '心理學與宗教：西方與東方（CW 11）',
          titleOriginal: 'Psychology and Religion: West and East',
          year: '1958',
          yearSort: 1958,
          category: '《全集》各卷（CW / GW）',
          status: 'copyright',
          note: '對宗教研究最相關。',
        },
        {
          title: '心理學與煉金術（CW 12）',
          titleOriginal: 'Psychology and Alchemy',
          year: '1944',
          yearSort: 1944,
          category: '《全集》各卷（CW / GW）',
          status: 'copyright',
        },
        {
          title: '神祕合體（CW 14）',
          titleOriginal: 'Mysterium Coniunctionis',
          year: '1955',
          yearSort: 1955,
          category: '《全集》各卷（CW / GW）',
          status: 'copyright',
        },
      ],
    },
  ])

  const bySlug = (slug: string) => authors.value.find((a) => a.slug === slug)

  return { authors, bySlug }
})
