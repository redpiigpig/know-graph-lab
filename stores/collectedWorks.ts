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
  externalUrl?: string // 連到獨立 corpus／portal（如東方聖書），優先於 ebookId
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
          status: 'done',
          ebookId: '33333333-3333-4333-8333-333333333333',
          note: '起手卷 ‧ 皇家研究院四講＋兩附論；**英／德／繁中三欄逐段對照（自譯本）**，全書竣約 21.5 萬繁中字。另有他人專業中譯本（陳觀勝、李培榮譯，上海人民出版社 1988）收於 /ebook 圖書館，兩本並存、用途不同。',
        },
        {
          title: '宗教起源與發展講座',
          titleOriginal: 'Lectures on the Origin and Growth of Religion',
          ebookId: '44444445-4444-4444-8444-444444444444',
          year: '1878',
          yearSort: 1878,
          category: '宗教學奠基',
          languages: ['en'],
          status: 'done',
          note: '希伯特講座（Hibbert Lectures）。',
        },
        // Gifford 四講
        {
          title: '自然宗教',
          titleOriginal: 'Natural Religion',
          ebookId: '44444441-4444-4444-8444-444444444444',
          year: '1888',
          yearSort: 1888,
          category: 'Gifford 講座（宗教學四部）',
          languages: ['en'],
          status: 'done',
          note: 'Longmans《全集》第一卷。',
        },
        {
          title: '物質宗教',
          titleOriginal: 'Physical Religion',
          ebookId: '44444442-4444-4444-8444-444444444444',
          year: '1890',
          yearSort: 1890,
          category: 'Gifford 講座（宗教學四部）',
          languages: ['en'],
          status: 'done',
        },
        {
          title: '人類學宗教',
          titleOriginal: 'Anthropological Religion',
          ebookId: '44444443-4444-4444-8444-444444444444',
          year: '1891',
          yearSort: 1891,
          category: 'Gifford 講座（宗教學四部）',
          languages: ['en'],
          status: 'done',
        },
        {
          title: '心理宗教（神智學）',
          titleOriginal: 'Theosophy, or Psychological Religion',
          ebookId: '44444444-4444-4444-8444-444444444444',
          year: '1892',
          yearSort: 1892,
          category: 'Gifford 講座（宗教學四部）',
          languages: ['en'],
          status: 'done',
        },
        // 語言與神話學
        {
          title: '比較神話學',
          titleOriginal: 'Comparative Mythology',
          ebookId: '4444444b-4444-4444-8444-444444444444',
          year: '1856',
          yearSort: 1856,
          category: '語言與神話學',
          languages: ['en'],
          status: 'done',
        },
        {
          title: '語言科學講座',
          titleOriginal: 'Lectures on the Science of Language',
          ebookId: '44444446-4444-4444-8444-444444444444',
          year: '1861',
          yearSort: 1861,
          category: '語言與神話學',
          languages: ['en'],
          status: 'done',
          note: '兩卷。',
        },
        {
          title: '神話科學論集',
          titleOriginal: 'Contributions to the Science of Mythology',
          ebookId: '4444444c-4444-4444-8444-444444444444',
          year: '1897',
          yearSort: 1897,
          category: '語言與神話學',
          languages: ['en'],
          status: 'done',
          note: '兩卷。',
        },
        // 印度學
        {
          title: '古代梵文文學史',
          titleOriginal: 'A History of Ancient Sanskrit Literature',
          ebookId: '4444444e-4444-4444-8444-444444444444',
          year: '1859',
          yearSort: 1859,
          category: '印度學',
          languages: ['en'],
          status: 'in-progress',
          note: '英文可讀；繁中逐段翻譯進行中。',
        },
        {
          title: '印度能教我們什麼？',
          titleOriginal: 'India: What Can It Teach Us?',
          ebookId: '44444449-4444-4444-8444-444444444444',
          year: '1883',
          yearSort: 1883,
          category: '印度學',
          languages: ['en'],
          status: 'done',
        },
        {
          title: '印度哲學六派',
          titleOriginal: 'The Six Systems of Indian Philosophy',
          ebookId: '4444444a-4444-4444-8444-444444444444',
          year: '1899',
          yearSort: 1899,
          category: '印度學',
          languages: ['en'],
          status: 'done',
        },
        // 文集與譯著
        {
          title: '德國作坊雜記',
          titleOriginal: 'Chips from a German Workshop',
          ebookId: '44444448-4444-4444-8444-444444444444',
          year: '1867–1875',
          yearSort: 1867,
          category: '文集與回憶',
          languages: ['en'],
          status: 'done',
          note: '全集重排為四／五卷。',
        },
        {
          title: '往日時光（憶往）',
          titleOriginal: 'Auld Lang Syne',
          ebookId: '4444444f-4444-4444-8444-444444444444',
          year: '1898',
          yearSort: 1898,
          category: '文集與回憶',
          languages: ['en'],
          status: 'in-progress',
          note: '英文可讀；繁中逐段翻譯進行中。',
        },
        {
          title: '自傳片段',
          titleOriginal: 'My Autobiography: A Fragment',
          ebookId: '44444450-4444-4444-8444-444444444444',
          year: '1901',
          yearSort: 1901,
          category: '文集與回憶',
          languages: ['en'],
          status: 'in-progress',
          note: '英文可讀；繁中逐段翻譯進行中。',
        },
        {
          title: '東方聖書（主編）',
          titleOriginal: 'The Sacred Books of the East',
          externalUrl: '/sacred-books-east',
          year: '1879–1910',
          yearSort: 1879,
          category: '主編譯本集',
          languages: ['en'],
          status: 'in-progress',
          note: '五十卷東方經典英譯集；性質為譯本集，已獨立成 corpus → 點此進入專屬目錄。',
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
        // 精神醫學與實驗心理學（早期）
        {
          title: '精神醫學研究',
          titleOriginal: 'Psychiatric Studies',
          year: '1902–07',
          yearSort: 1,
          category: '精神醫學與實驗心理學（早期）',
          status: 'copyright',
          note: '全集 CW 1 ＝ GW 1。德文原典 1929 前出版部分屬公有領域；Hull 英譯仍受版權。',
        },
        {
          title: '實驗研究（字詞聯想）',
          titleOriginal: 'Experimental Researches',
          year: '1904–10',
          yearSort: 2,
          category: '精神醫學與實驗心理學（早期）',
          status: 'copyright',
          note: '全集 CW 2 ＝ GW 2。德文原典 1929 前出版部分屬公有領域；Hull 英譯仍受版權。',
        },
        {
          title: '精神疾病的心理成因',
          titleOriginal: 'The Psychogenesis of Mental Disease',
          year: '1907–58',
          yearSort: 3,
          category: '精神醫學與實驗心理學（早期）',
          status: 'copyright',
          note: '全集 CW 3 ＝ GW 3。含 1907《早發性癡呆心理學》（德文原典公有領域）。',
        },
        // 精神分析與力比多理論
        {
          title: '佛洛伊德與精神分析',
          titleOriginal: 'Freud and Psychoanalysis',
          year: '1906–16',
          yearSort: 4,
          category: '精神分析與力比多理論',
          status: 'copyright',
          note: '全集 CW 4 ＝ GW 4。部分早期德文論文 1929 前公有領域；Hull 英譯仍受版權。',
        },
        {
          title: '轉化的象徵',
          titleOriginal: 'Symbols of Transformation',
          year: '1952',
          yearSort: 5,
          category: '精神分析與力比多理論',
          status: 'copyright',
          note: '全集 CW 5 ＝ GW 5。1912《力比多的轉化與象徵》的大幅改寫本；受版權至 2031，待合法來源（早期版見上「早期著作」）。',
        },
        // 分析心理學核心理論
        {
          title: '心理類型',
          titleOriginal: 'Psychological Types',
          year: '1921',
          yearSort: 6,
          category: '分析心理學核心理論',
          status: 'copyright',
          note: '全集 CW 6 ＝ GW 6。',
        },
        {
          title: '分析心理學二論',
          titleOriginal: 'Two Essays on Analytical Psychology',
          year: '1917／28',
          yearSort: 7,
          category: '分析心理學核心理論',
          status: 'copyright',
          note: '全集 CW 7 ＝ GW 7。',
        },
        {
          title: '心靈的結構與動力',
          titleOriginal: 'The Structure and Dynamics of the Psyche',
          year: '1916–52',
          yearSort: 8,
          category: '分析心理學核心理論',
          status: 'copyright',
          note: '全集 CW 8 ＝ GW 8。含〈論心靈能量〉〈共時性〉。',
        },
        // 原型與集體無意識
        {
          title: '原型與集體無意識',
          titleOriginal: 'The Archetypes and the Collective Unconscious',
          year: '1934–55',
          yearSort: 9.1,
          category: '原型與集體無意識',
          status: 'copyright',
          note: '全集 CW 9 第一分冊 ＝ GW 9/1。對宗教研究高度相關（原型、母親原型、曼陀羅）。',
        },
        {
          title: '伊雍',
          titleOriginal: 'Aion: Researches into the Phenomenology of the Self',
          year: '1951',
          yearSort: 9.2,
          category: '原型與集體無意識',
          status: 'copyright',
          note: '全集 CW 9 第二分冊 ＝ GW 9/2。對宗教研究高度相關（基督象徵、自性、雙魚座時代）。',
        },
        // 文明與宗教
        {
          title: '轉變中的文明',
          titleOriginal: 'Civilization in Transition',
          year: '1918–59',
          yearSort: 10,
          category: '文明與宗教',
          status: 'copyright',
          note: '全集 CW 10 ＝ GW 10。',
        },
        {
          title: '心理學與宗教：西方與東方',
          titleOriginal: 'Psychology and Religion: West and East',
          year: '1932–52',
          yearSort: 11,
          category: '文明與宗教',
          status: 'copyright',
          note: '全集 CW 11 ＝ GW 11。對宗教研究最相關。',
        },
        // 煉金術三部曲
        {
          title: '心理學與煉金術',
          titleOriginal: 'Psychology and Alchemy',
          year: '1944',
          yearSort: 12,
          category: '煉金術三部曲',
          status: 'copyright',
          note: '全集 CW 12 ＝ GW 12。煉金術三部之一。',
        },
        {
          title: '煉金術研究',
          titleOriginal: 'Alchemical Studies',
          year: '1929–54',
          yearSort: 13,
          category: '煉金術三部曲',
          status: 'copyright',
          note: '全集 CW 13 ＝ GW 13。煉金術三部之一（含《金花的祕密》評註、佐西默斯異象）。',
        },
        {
          title: '神祕合體',
          titleOriginal: 'Mysterium Coniunctionis',
          year: '1955–56',
          yearSort: 14,
          category: '煉金術三部曲',
          status: 'copyright',
          note: '全集 CW 14 ＝ GW 14。煉金術三部之一；榮格晚年集大成。',
        },
        // 藝術、治療與人格
        {
          title: '人、藝術與文學中的精神',
          titleOriginal: 'The Spirit in Man, Art, and Literature',
          year: '1922–41',
          yearSort: 15,
          category: '藝術、治療與人格',
          status: 'copyright',
          note: '全集 CW 15 ＝ GW 15。',
        },
        {
          title: '心理治療實務',
          titleOriginal: 'The Practice of Psychotherapy',
          year: '1921–51',
          yearSort: 16,
          category: '藝術、治療與人格',
          status: 'copyright',
          note: '全集 CW 16 ＝ GW 16。',
        },
        {
          title: '人格的發展',
          titleOriginal: 'The Development of Personality',
          year: '1910–25',
          yearSort: 17,
          category: '藝術、治療與人格',
          status: 'copyright',
          note: '全集 CW 17 ＝ GW 17。',
        },
        {
          title: '象徵的生命',
          titleOriginal: 'The Symbolic Life: Miscellaneous Writings',
          year: '1939–55',
          yearSort: 18,
          category: '藝術、治療與人格',
          status: 'copyright',
          note: '全集 CW 18 ＝ GW 18。雜文與短篇彙編。',
        },
        // 工具卷（書目與索引）
        {
          title: '總書目',
          titleOriginal: 'General Bibliography of C. G. Jung’s Writings',
          year: '1979',
          yearSort: 19,
          category: '工具卷（書目與索引）',
          status: 'copyright',
          note: '全集 CW 19（無 GW 對應）。工具卷（書目）。',
        },
        {
          title: '總索引',
          titleOriginal: 'General Index to the Collected Works',
          year: '1979',
          yearSort: 20,
          category: '工具卷（書目與索引）',
          status: 'copyright',
          note: '全集 CW 20（無 GW 對應）。工具卷（索引）。',
        },
      ],
    },

    // ────────────────────────────────────────────────────────────────
    // 雷蒙‧潘尼卡（宗教間／宗教內對話、宇宙神人共融）
    // ────────────────────────────────────────────────────────────────
    {
      slug: 'panikkar',
      name: '雷蒙‧潘尼卡',
      nameEn: 'Raimon Panikkar',
      nameOriginal: 'Raimon Panikkar',
      lifespan: '1918–2010',
      discipline:
        '宗教間／宗教內對話與跨文化哲學巨擘；天主教神父，提出「宇宙神人共融」與《印度教中未識的基督》',
      fields: ['比較神學', '宗教哲學', '宗教間對話', '印度學', '三一神學'],
      portraitUrl:
        'https://commons.wikimedia.org/wiki/Special:FilePath/Raimon%20Panikkar.jpg?width=500',
      portraitCredit: 'Milena Carrara 攝‧2007‧Wikimedia Commons（CC0 公有領域）',
      color: 'indigo',
      emoji: '🪷',
      contribution: [
        '雷蒙‧潘尼卡是二十世紀**宗教間對話、比較神學與跨文化哲學**最具影響力的思想家之一。他生於巴塞隆納，父為印度馬拉雅利的印度教徒、母為加泰隆尼亞的天主教徒，一身兼具兩大宗教傳統；領有哲學、化學、神學三個博士學位，並於 1946 年領受天主教神父聖秩。他常以一句話自述這趟思想旅程——**「我以基督徒出發，發現自己是印度教徒，回來時成了佛教徒，卻未曾不再是基督徒。」**',
        '他最著名的著作《**印度教中未識的基督（The Unknown Christ of Hinduism）**》（1964／1981 修訂）主張：基督並非基督宗教的專利，而是在印度教深處早已隱然臨在的「全基督（the whole Christ）」。由此他發展出**「宗教內對話（intrareligious dialogue）」**——真正的宗教相遇不是兩個教派代表的外部協商，而是發生在「我自己內部」、在信仰者心靈深處的內在朝聖；以別於一般的**「宗教間對話（interreligious dialogue）」**。',
        '他鑄造**「宇宙神人共融（cosmotheandric）」**直觀，主張一切實在恆是**宇宙、神、人**三維不可分割的共融，並以印度吠檀多的**「不二（advaita）」**重新詮釋基督宗教的**三位一體**，視三一為實在的根本結構。其方法論貢獻——**同構等價（homeomorphic equivalence）**與**跨地詮釋學（diatopical hermeneutics）**——成為跨文化宗教比較的重要工具。',
        '其畢生著述由 Milena Carrara Pavan 主編、與塔維爾泰特維瓦里翁基金會合作，整理為按主題重編的 **12 卷《全集（Opera Omnia）》**（Jaca Book 義大利文版／Orbis Books 英文版，2010–2022 完成）。1989 年的愛丁堡**吉福德講座**結集為《存在的韻律（The Rhythm of Being）》，是其思想的哲學總結。',
      ],
      sourceNote:
        '潘尼卡卒於 2010，全部著作受版權保護至約 2080；網路無乾淨合法公有領域全文，第三方中譯本一律不入庫。採 English-first：私人站非公有領域來源可用，英文先輸入、繁中逐步補。他以多語（加泰隆／西／義／英／德）原創，《全集》為主題重編；起手卷《印度教中未識的基督》原文即英文，先英／繁中雙語，個別文本日後若得平行原文版再升三欄。',
      timeline: [
        { year: '1918', text: '11 月 2 日生於巴塞隆納；父為印度教徒、母為天主教徒。' },
        { year: '1946', text: '獲馬德里大學哲學博士，並領受天主教神父聖秩。' },
        { year: '1954', text: '首度赴印度，深入研習梵文、吠陀與印度哲學。' },
        { year: '1958', text: '獲化學博士。' },
        { year: '1961', text: '於羅馬拉特朗宗座大學獲神學博士。' },
        { year: '1964', text: '《印度教中未識的基督》出版，奠定其宗教對話思想。' },
        { year: '1966', text: '任哈佛神學院客座教授。' },
        { year: '1972', text: '任加州大學聖塔芭芭拉分校宗教研究教授。' },
        { year: '1977', text: '《吠陀經驗（The Vedic Experience）》出版。' },
        { year: '1987', text: '於加泰隆尼亞塔維爾泰特創立維瓦里翁基金會，隱居著述。' },
        { year: '1989', text: '主講愛丁堡吉福德講座，後成《存在的韻律》。' },
        { year: '2010', text: '8 月 26 日卒於塔維爾泰特，享壽 91。' },
      ],
      works: [
        // 代表作 ‧ 起手卷
        {
          title: '印度教中未識的基督',
          titleOriginal: 'The Unknown Christ of Hinduism',
          year: '1964／1981',
          yearSort: 1964,
          category: '印度教與基督宗教（卷七）',
          languages: ['en'],
          status: 'planned',
          note: '起手卷 ‧ 潘尼卡最著名代表作。英／繁中雙語逐段對照（自譯本）pipeline 已就緒（scripts/panikkar_build.py），受版權待英文來源檔到位即開譯；原文即英文，西班牙文版日後可升英／西／繁中三欄。',
        },
        // 全集 12 卷（受版權，待合法來源）
        {
          title: '神祕：生命的圓滿',
          titleOriginal: 'Mysticism: The Fullness of Life (Opera Omnia I.1)',
          year: '全集 I.1',
          yearSort: 1,
          category: '神祕與靈性（卷一）',
          status: 'copyright',
        },
        {
          title: '靈性：生命之道',
          titleOriginal: 'Spirituality: The Way of Life (Opera Omnia I.2)',
          year: '全集 I.2',
          yearSort: 2,
          category: '神祕與靈性（卷一）',
          status: 'copyright',
        },
        {
          title: '宗教與諸宗教',
          titleOriginal: 'Religion and Religions (Opera Omnia II)',
          year: '全集 II',
          yearSort: 3,
          category: '宗教與諸宗教（卷二）',
          status: 'copyright',
        },
        {
          title: '基督宗教：基督宗教傳統',
          titleOriginal: 'Christianity: The Christian Tradition (Opera Omnia III.1)',
          year: '全集 III.1',
          yearSort: 4,
          category: '基督宗教（卷三）',
          status: 'copyright',
        },
        {
          title: '基督宗教：基督顯現',
          titleOriginal: 'Christianity: A Christophany (Opera Omnia III.2)',
          year: '全集 III.2',
          yearSort: 5,
          category: '基督宗教（卷三）',
          status: 'copyright',
          note: 'Christophany（基督顯現）為潘尼卡自鑄概念。',
        },
        {
          title: '印度教：吠陀經驗',
          titleOriginal: 'Hinduism: The Vedic Experience (Opera Omnia IV.1)',
          year: '全集 IV.1（原 1977）',
          yearSort: 6,
          category: '印度教（卷四）',
          status: 'copyright',
          note: '即《The Vedic Experience / Mantramañjarī》，吠陀選譯與冥想。',
        },
        {
          title: '印度教：印度的達磨',
          titleOriginal: 'Hinduism: The Dharma of India (Opera Omnia IV.2)',
          year: '全集 IV.2',
          yearSort: 7,
          category: '印度教（卷四）',
          status: 'copyright',
        },
        {
          title: '佛教',
          titleOriginal: 'Buddhism (Opera Omnia V)',
          year: '全集 V',
          yearSort: 8,
          category: '佛教（卷五）',
          status: 'copyright',
        },
        {
          title: '文化與宗教的對話：多元論與跨文化性',
          titleOriginal:
            'Cultures and Religions in Dialogue: Pluralism and Interculturality (Opera Omnia VI.1)',
          year: '全集 VI.1',
          yearSort: 9,
          category: '文化與宗教的對話（卷六）',
          status: 'copyright',
        },
        {
          title: '文化與宗教的對話：跨文化與宗教間對話',
          titleOriginal:
            'Cultures and Religions in Dialogue: Intercultural and Interreligious Dialogue (Opera Omnia VI.2)',
          year: '全集 VI.2',
          yearSort: 10,
          category: '文化與宗教的對話（卷六）',
          status: 'copyright',
        },
        {
          title: '印度教與基督宗教',
          titleOriginal: 'Hinduism and Christianity (Opera Omnia VII)',
          year: '全集 VII',
          yearSort: 11,
          category: '印度教與基督宗教（卷七）',
          status: 'copyright',
          note: '收錄《印度教中未識的基督》及相關文稿（起手卷即出於此主題）。',
        },
        {
          title: '三一與宇宙神人共融觀',
          titleOriginal: 'Trinitarian and Cosmotheandric Vision (Opera Omnia VIII)',
          year: '全集 VIII',
          yearSort: 12,
          category: '三一與宇宙神人共融（卷八）',
          status: 'copyright',
          note: 'cosmotheandric（宇宙神人共融）招牌概念的總成。',
        },
        {
          title: '奧祕與詮釋學：神話、象徵與禮儀',
          titleOriginal: 'Mystery and Hermeneutics: Myth, Symbol, and Ritual (Opera Omnia IX.1)',
          year: '全集 IX.1',
          yearSort: 13,
          category: '奧祕與詮釋學（卷九）',
          status: 'copyright',
        },
        {
          title: '奧祕與詮釋學：信仰、詮釋與道言',
          titleOriginal: 'Mystery and Hermeneutics: Faith, Hermeneutics, and Word (Opera Omnia IX.2)',
          year: '全集 IX.2',
          yearSort: 14,
          category: '奧祕與詮釋學（卷九）',
          status: 'copyright',
        },
        {
          title: '哲學與神學：存在的韻律（吉福德講座）',
          titleOriginal:
            'Philosophy and Theology: The Rhythm of Being — The Gifford Lectures (Opera Omnia X.1)',
          year: '全集 X.1（1989 講座）',
          yearSort: 15,
          category: '哲學與神學（卷十）',
          status: 'copyright',
          note: '1989 愛丁堡吉福德講座，思想的哲學總結。',
        },
        {
          title: '哲學與神學（下）',
          titleOriginal: 'Philosophy and Theology — Part Two (Opera Omnia X.2)',
          year: '全集 X.2',
          yearSort: 16,
          category: '哲學與神學（卷十）',
          status: 'copyright',
        },
        {
          title: '神聖的世俗性',
          titleOriginal: 'Sacred Secularity (Opera Omnia XI)',
          year: '全集 XI',
          yearSort: 17,
          category: '神聖的世俗性與科學（卷十一‧十二）',
          status: 'copyright',
        },
        {
          title: '空間、時間與科學',
          titleOriginal: 'Space, Time, and Science (Opera Omnia XII)',
          year: '全集 XII',
          yearSort: 18,
          category: '神聖的世俗性與科學（卷十一‧十二）',
          status: 'copyright',
        },
      ],
    },
  ])

  const bySlug = (slug: string) => authors.value.find((a) => a.slug === slug)

  return { authors, bySlug }
})
