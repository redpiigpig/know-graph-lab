// 三夷教研究資料 — 書目層
//
// `/research-data/sanyijiao`。祆教、摩尼教、（日後）景教三教的**二手研究**。
//
// ══════════ 為什麼研究資料合成一個 collection，經典卻分卡 ══════════
//
//   經典分卡（/avesta、日後的摩尼教經典區）：三教是三個獨立宗教，
//     而且編纂問題根本不同——祆教的正典還活著（火廟今天仍照亞斯納 72 章誦），
//     摩尼教的七部大經卻全佚，只能從科普特文、吐魯番殘卷、敦煌三經、
//     奧古斯丁的駁論引文與霞浦文書綴輯。體例合不到一起。
//
//   研究合卡（本檔）：研究文獻本來就大量跨教。林悟殊《中古三夷教辨證》
//     一本涵蓋三教，硬歸一教就會被切壞；林悟殊本人同時是祆教與摩尼教
//     兩條線的權威。故以 `religion` 欄標歸屬，跨教者標 'cross'。
//
// 🚨 **全文一律 file-backed，不進 DB。** 見 [[project_db_quota_rescue]]：
//    2026-07-08 Supabase 超量鎖站，定調新大內容表一律走檔案。
//    書目在本檔（進版控、看得見），全文與譯文在
//    public/content/research-data/sanyijiao/texts/{ref}.json。
//
// ══════════ 語言呈現規則（user 2026-09-06 定）══════════
//
//   「翻譯要雙語呈現，如果不是英文就要三語呈現，不能只有中譯」
//
//   原文是英文   → 兩欄：英文 ／ 繁中
//   原文非英文   → 三欄：原文 ／ 英文 ／ 繁中
//   原文是中文   → 一欄：原樣呈現（無翻譯，不生此問題）
//
//   理由是查證：只有中譯的對照沒有查證價值，讀者無從判斷譯得對不對。
//   reader 依 `lang` 自動決定欄數，見 columnsFor()。

/** 三夷教。cross＝一本涵蓋兩教以上（如《中古三夷教辨證》），不強行歸一教。 */
export type ZsReligion = 'zoroastrian' | 'manichaean' | 'nestorian' | 'cross'

export const RELIGION_META: Record<ZsReligion, { label: string; glyph: string; cls: string; desc: string }> = {
  zoroastrian: {
    label: '祆教', glyph: '🔥', cls: 'bg-orange-50 text-orange-800',
    desc: '瑣羅亞斯德教。唐代漢籍稱「祆」「火祆」，經典區見 /avesta。',
  },
  manichaean: {
    label: '摩尼教', glyph: '☀️', cls: 'bg-amber-50 text-amber-800',
    desc: '摩尼所創。入華後與民間宗教結合而有「明教」之名；霞浦文書 2008 年出土後重開新局。',
  },
  nestorian: {
    label: '景教', glyph: '✝️', cls: 'bg-sky-50 text-sky-800',
    desc: '東方教會（唐代稱景教）。本 collection 尚未收，列此以備。',
  },
  cross: {
    label: '三教通論', glyph: '🜂', cls: 'bg-stone-100 text-stone-700',
    desc: '一本涵蓋兩教以上者。三夷教同時入華、共用同一批粟特商旅網絡，研究上本難分割。',
  },
}

export type ZsKind = 'book' | 'article' | 'thesis' | 'reference' | 'chapter'

export const KIND_LABEL: Record<ZsKind, string> = {
  book: '專書',
  article: '期刊論文',
  thesis: '學位論文',
  reference: '工具書條目',
  chapter: '專書論文',
}

/** 全文取得狀態。與 /avesta 的三欄現況同一種誠實：說的是「拿不拿得到」。 */
export type ZsFulltext =
  | 'ready' // 已入庫並逐段對照
  | 'open' // 開放取用，待抓
  | 'library' // 需館藏／付費資料庫（華藝、CNKI、JSTOR）
  | 'print' // 僅紙本
  | 'none' // 查無電子全文

export const FULLTEXT_LABEL: Record<ZsFulltext, { zh: string; cls: string }> = {
  ready: { zh: '已上架', cls: 'bg-emerald-100 text-emerald-800' },
  open: { zh: '開放取用', cls: 'bg-sky-100 text-sky-800' },
  library: { zh: '需館藏', cls: 'bg-amber-100 text-amber-800' },
  print: { zh: '僅紙本', cls: 'bg-stone-100 text-stone-700' },
  none: { zh: '查無全文', cls: 'bg-gray-100 text-gray-500' },
}

/** 研究面向——三教共通的四條主線 */
export type ZsTheme = 'scripture' | 'homeland' | 'china' | 'modern'

export const THEME_META: Record<ZsTheme, { label: string; desc: string }> = {
  scripture: {
    label: '經典與語文',
    desc: '原典文獻學、校本、翻譯。祆教這一側是阿維斯陀語與巴列維文獻；'
      + '摩尼教這一側是科普特文、中古伊朗語吐魯番殘卷與敦煌漢文三經。'
      + '這一面向決定了經典區的取源可信度。',
  },
  homeland: {
    label: '本土與西方',
    desc: '伊朗本土的宗教史，以及摩尼教在羅馬帝國、中亞的傳布。三教東傳之前的樣貌。',
  },
  china: {
    label: '入華與華化',
    desc: '中古中國的三夷教：粟特移民、薩寶制度、圖像與墓葬、明教與大明國號之爭、霞浦文書。'
      + '**這一面向是中文學界的強項**，成果密度遠高於其他三項。',
  },
  modern: {
    label: '近現代與流散',
    desc: '帕西社群、近代改革、當代認同問題。',
  },
}

export interface ZsEntry {
  /** 檔名與路由用；全庫唯一 */
  ref: string
  /** 所屬宗教；跨教者用 'cross'，不強行歸一教 */
  religion: ZsReligion
  /** 標題（原文） */
  title: string
  /** 標題繁中（原文非中文者才有） */
  title_zh?: string
  authors: string
  year: number | string
  /** 刊名／出版社 */
  venue: string
  /** 原文語言：zh／en／ja／de／fr／fa… 決定 reader 的欄數 */
  lang: string
  kind: ZsKind
  theme: ZsTheme
  fulltext: ZsFulltext
  /** 全文取源網址 */
  url?: string
  /** 一句話說明它為什麼重要——書目不寫這個就只是一串書名 */
  note?: string
  /** 互見另一條目的 ref。用於必須並讀者（如吳晗與楊訥的大明國號之爭）。 */
  seealso?: string
}

/** 依原文語言決定 reader 要出哪幾欄（user 2026-09-06 定，見檔首）。 */
export function columnsFor(lang: string): Array<{ key: string; label: string }> {
  if (lang === 'zh') return [{ key: 'orig', label: '原文' }]
  if (lang === 'en') {
    return [{ key: 'orig', label: '英文原文' }, { key: 'zh', label: '繁體中文' }]
  }
  return [
    { key: 'orig', label: `${LANG_LABEL[lang] ?? lang}原文` },
    { key: 'en', label: '英譯' },
    { key: 'zh', label: '繁體中文' },
  ]
}

export const LANG_LABEL: Record<string, string> = {
  zh: '中文', en: '英文', ja: '日文', de: '德文', fr: '法文',
  fa: '波斯文', ru: '俄文', gu: '古吉拉特文',
}

// ════════════════════ 書目 ════════════════════
//
// 中文部分主要據絲綢之路網〈祆教研究中文書目〉與各書版權頁核對；
// 英文部分為該領域的標準著作。年份與出版社凡未親見者不臆造，寧可留空。

export const ENTRIES: ZsEntry[] = [
  // ────────── 經典與語文 ──────────
  {
    ref: 'yuan-wenqi-avesta',
    religion: 'zoroastrian',
    title: '阿維斯塔——瑣羅亞斯德教聖書',
    authors: '賈利爾‧杜斯特哈赫 選編；元文琪 譯',
    year: 2010, venue: '商務印書館', lang: 'zh', kind: 'book',
    theme: 'scripture', fulltext: 'library',
    note: '中文世界唯一成規模的《阿維斯陀》譯本，自波斯文選編本轉譯。'
      + '**本站經典區的篇名定譯即以此書為準**（伽薩／亞斯納／亞什特／萬迪達德／維斯帕拉德）；'
      + '但其譯文為選編、簡體且在版權內，故不作對照欄底本。',
  },
  {
    ref: 'yuan-wenqi-dualism',
    religion: 'zoroastrian',
    title: '二元神論：古波斯宗教神話研究',
    authors: '元文琪',
    year: 1997, venue: '中國社會科學出版社', lang: 'zh', kind: 'book',
    theme: 'scripture', fulltext: 'library',
    note: '譯者本人的研究專著，與其《阿維斯塔》譯本互為表裡。',
  },
  {
    ref: 'boyce-textual-sources',
    religion: 'zoroastrian',
    title: 'Textual Sources for the Study of Zoroastrianism',
    title_zh: '祆教研究文獻選輯',
    authors: 'Mary Boyce',
    year: 1984, venue: 'Manchester University Press', lang: 'en', kind: 'book',
    theme: 'scripture', fulltext: 'library',
    note: '把阿維斯陀、巴列維文獻、希臘羅馬旁證與帕西文獻的關鍵段落編成一冊並附英譯，'
      + '是入門與教學最常用的一本。',
  },
  {
    ref: 'skjaervo-spirit',
    religion: 'zoroastrian',
    title: 'The Spirit of Zoroastrianism',
    title_zh: '祆教的精神',
    authors: 'Prods Oktor Skjærvø',
    year: 2011, venue: 'Yale University Press', lang: 'en', kind: 'book',
    theme: 'scripture', fulltext: 'library',
    note: '當代阿維斯陀語文獻學第一人的選譯與導讀；其譯文常與達梅斯特舊譯出入甚大，'
      + '可用來檢驗本站以《東方聖書》為底本的譯文哪些地方已經過時。',
  },
  {
    ref: 'cantera-cab',
    religion: 'zoroastrian',
    title: 'Corpus Avesticum Berolinense: The Long Liturgy',
    title_zh: '柏林阿維斯陀語料庫：長祭典',
    authors: 'Alberto Cantera',
    year: '2019–', venue: 'Freie Universität Berlin', lang: 'en', kind: 'reference',
    theme: 'scripture', fulltext: 'open',
    url: 'https://www.geschkult.fu-berlin.de/en/e/iranistik/forschung/CAB/index.html',
    note: '首度按「祭典脈絡」而非按書重編阿維斯陀全集的新校本，仍在出版中。'
      + '本站若要開放阿維斯陀字母欄，霍夫曼式轉寫須取自此處或 TITUS。',
  },
  {
    ref: 'iranica-avesta',
    religion: 'zoroastrian',
    title: 'AVESTA (Encyclopaedia Iranica)',
    title_zh: '阿維斯陀（伊朗百科全書條目）',
    authors: 'Jean Kellens 等',
    year: 1987, venue: 'Encyclopaedia Iranica', lang: 'en', kind: 'reference',
    theme: 'scripture', fulltext: 'open',
    url: 'https://iranicaonline.org/articles/avesta-holy-book',
    note: '《伊朗百科全書》是本領域的標準工具書，條目由各題目的權威撰寫並附完整書目。'
      + '🚨 該站對機器直取回 403，須以瀏覽器管道取得。',
  },

  // ────────── 伊朗本土宗教史 ──────────
  {
    ref: 'gong-yan-xianjiaoshi',
    religion: 'zoroastrian',
    title: '祆教史',
    authors: '龔方震、晏可佳',
    year: 1998, venue: '上海社會科學院出版社', lang: 'zh', kind: 'book',
    theme: 'homeland', fulltext: 'library',
    note: '中文世界第一部通論性的祆教通史，自古伊朗宗教寫到近現代帕西社群，'
      + '中文學界的術語（阿胡拉‧馬茲達、安格拉‧曼紐、阿赫里曼）大半由此定型。',
  },
  {
    ref: 'boyce-history-1',
    religion: 'zoroastrian',
    title: 'A History of Zoroastrianism, Vol. I: The Early Period',
    title_zh: '祆教史 第一卷：早期',
    authors: 'Mary Boyce',
    year: 1975, venue: 'Brill', lang: 'en', kind: 'book',
    theme: 'homeland', fulltext: 'library',
    note: '本領域最重要的通史三卷本的第一卷。博伊斯主張祆教的連續性遠比一般設想的長，'
      + '此說至今仍是各家立論的基準點，即使反對者也須先處理她的論證。',
  },
  {
    ref: 'boyce-history-2',
    religion: 'zoroastrian',
    title: 'A History of Zoroastrianism, Vol. II: Under the Achaemenians',
    title_zh: '祆教史 第二卷：阿契美尼德時期',
    authors: 'Mary Boyce',
    year: 1982, venue: 'Brill', lang: 'en', kind: 'book',
    theme: 'homeland', fulltext: 'library',
    note: '本站《王室銘文》一藏「阿契美尼德算不算祆教」的爭議，主要材料出自此卷。',
  },
  {
    ref: 'boyce-zoroastrians',
    religion: 'zoroastrian',
    title: 'Zoroastrians: Their Religious Beliefs and Practices',
    title_zh: '祆教徒：信仰與實踐',
    authors: 'Mary Boyce',
    year: 1979, venue: 'Routledge', lang: 'en', kind: 'book',
    theme: 'homeland', fulltext: 'open',
    url: 'https://archive.org/details/zoroastriansthei0000boyc',
    note: '單卷本通論，比三卷本易讀，是英語世界最通行的入門書。Internet Archive 可借閱。',
  },
  {
    ref: 'boyce-selected-writings',
    religion: 'zoroastrian',
    title: 'Selected Writings of Mary Boyce, 1955–2005',
    title_zh: '博伊斯論文選集',
    authors: 'Mary Boyce',
    year: 2005, venue: '（論文彙編）', lang: 'en', kind: 'book',
    theme: 'homeland', fulltext: 'open',
    url: 'https://archive.org/details/boyce19552005selectedwritings',
    note: '264 頁可檢索 PDF，Internet Archive 全文開放。',
  },
  {
    ref: 'de-jong-traditions-magi',
    religion: 'zoroastrian',
    title: 'Traditions of the Magi: Zoroastrianism in Greek and Latin Literature',
    title_zh: '麻葛的傳統：希臘羅馬文獻中的祆教',
    authors: 'Albert de Jong',
    year: 1997, venue: 'Brill', lang: 'en', kind: 'book',
    theme: 'homeland', fulltext: 'library',
    note: '把希臘羅馬作家關於波斯宗教的記述逐條檢核，判定哪些可用、哪些是異國想像。'
      + '方法上與本站《希臘羅馬大藏經》處理「敵證」的作法同型。',
  },
  {
    ref: 'shaked-dualism',
    religion: 'zoroastrian',
    title: 'Dualism in Transformation: Varieties of Religion in Sasanian Iran',
    title_zh: '轉化中的二元論：薩珊伊朗的宗教樣態',
    authors: 'Shaul Shaked',
    year: 1994, venue: 'SOAS', lang: 'en', kind: 'book',
    theme: 'homeland', fulltext: 'library',
    note: '沙克德是巴列維文獻研究的權威，《丹卡爾德》第六卷英譯即出其手——'
      + '那正是本站英文欄補不上的兩個缺口之一。',
  },
  {
    ref: 'iranica-zoroastrianism-i',
    religion: 'zoroastrian',
    title: 'ZOROASTRIANISM i. Historical Review up to the Arab Conquest',
    title_zh: '祆教 一‧至阿拉伯征服為止的歷史回顧',
    authors: 'Encyclopaedia Iranica',
    year: 2000, venue: 'Encyclopaedia Iranica', lang: 'en', kind: 'reference',
    theme: 'homeland', fulltext: 'open',
    url: 'https://www.iranicaonline.org/articles/zoroastrianism-i-historical-review/',
    note: '通史性條目，附完整書目，適合作為各專題的入口。',
  },

  // ────────── 祆教入華（中文學界的強項）──────────
  {
    ref: 'chen-yuan-huoxianjiao',
    religion: 'zoroastrian',
    title: '火祆教入中國考',
    authors: '陳垣',
    year: 1923, venue: '《國學季刊》第 1 卷第 1 期', lang: 'zh', kind: 'article',
    theme: 'china', fulltext: 'open',
    note: '中文祆教研究的奠基之作，考定「祆」字的來歷、火祆祠的分布與薩寶制度。'
      + '此後百年的中文論著幾乎都自此文起手。1923 年刊出，已入公有領域。',
  },
  {
    ref: 'lin-wushu-bosi',
    religion: 'cross',
    title: '波斯拜火教與古代中國',
    authors: '林悟殊',
    year: 1995, venue: '新文豐出版公司（台北）', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '654 頁。台灣出版的祆教研究代表作，與摩尼教、景教合觀「三夷教」入華。',
  },
  {
    ref: 'lin-wushu-sanyijiao',
    religion: 'cross',
    title: '中古三夷教辨證',
    authors: '林悟殊',
    year: 2005, venue: '中華書局', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '祆教、摩尼教、景教三教入華的辨偽與考證；對敦煌文書真偽的判斷尤為關鍵。',
  },
  {
    ref: 'zhang-xiaogui-huahua',
    religion: 'zoroastrian',
    title: '中古華化祆教考述',
    authors: '張小貴',
    year: 2010, venue: '文物出版社', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '論唐宋祆祠分布、神祇崇拜的變形、拜火、婚俗與葬俗；'
      + '「華化」是本書的核心概念——入華的祆教已不等於伊朗本土的祆教。',
  },
  {
    ref: 'zhang-xiaogui-dongchuan',
    religion: 'zoroastrian',
    title: '中古祆教東傳及其華化研究',
    authors: '張小貴',
    year: '', venue: '', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '大量吸收國際伊朗學成果，強調據波斯文祆教經典分析，並結合考古材料；'
      + '在中文著作中對原典的處理最為紮實。',
  },
  {
    ref: 'jiang-boqin-art',
    religion: 'zoroastrian',
    title: '中國祆教藝術史研究',
    authors: '姜伯勤',
    year: 2004, venue: '三聯書店', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '以安伽墓、虞弘墓、史君墓的石刻圖像為中心；'
      + '圖像是祆教入華最直接的證據——中文文獻對祆教教義幾乎不記，圖像卻記了。',
  },
  {
    ref: 'rong-xinjiang-zhonggu',
    religion: 'cross',
    title: '中古中國與外來文明',
    authors: '榮新江',
    year: 2001, venue: '三聯書店', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '粟特移民聚落與薩寶制度的研究；祆教入華的社會史底層。',
  },
  {
    ref: 'cai-hongsheng-jiuxing',
    religion: 'cross',
    title: '唐代九姓胡與突厥文化',
    authors: '蔡鴻生',
    year: 1998, venue: '中華書局', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '九姓胡（粟特）是祆教入華的載體族群，本書是該題目的基礎研究。',
  },
  {
    ref: 'anjia-tomb',
    religion: 'zoroastrian',
    title: '西安北周安伽墓',
    authors: '陝西省考古研究所',
    year: 2003, venue: '文物出版社', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '2000 年出土，墓主為北周薩寶。圍屏石榻的祆教圖像是中國境內祆教考古的標誌性發現。',
  },
  {
    ref: 'yuhong-tomb',
    religion: 'zoroastrian',
    title: '太原隋虞弘墓',
    authors: '山西省考古研究所',
    year: 2005, venue: '文物出版社', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '與安伽墓並列的兩大祆教墓葬；石槨浮雕含明確的祭火與犬視（sagdīd）圖像。',
  },
  {
    ref: 'zhang-xiaogui-randeng',
    religion: 'zoroastrian',
    title: '敦煌文書所記「祆寺燃燈」考',
    authors: '張小貴',
    year: '', venue: '（期刊論文）', lang: 'zh', kind: 'article',
    theme: 'china', fulltext: 'open',
    url: 'https://nxkg.org.cn/index.php?a=show&c=index&catid=15&id=455&m=content',
    note: '據敦煌文書考祆祠的燃燈儀式；網路有全文。',
  },
  {
    ref: 'chen-ling-yicun',
    religion: 'zoroastrian',
    title: '中國境內祆教相關遺存考略',
    authors: '陳凌',
    year: '', venue: '（期刊論文）', lang: 'zh', kind: 'article',
    theme: 'china', fulltext: 'open',
    url: 'https://nxkg.org.cn/index.php?a=show&c=index&catid=15&id=463&m=content',
    note: '中國境內祆教遺存的清點；網路有全文。',
  },

  // ────────── 帕西社群與近現代 ──────────
  {
    ref: 'hinnells-parsis',
    religion: 'zoroastrian',
    title: 'The Zoroastrian Diaspora: Religion and Migration',
    title_zh: '祆教的流散：宗教與遷徙',
    authors: 'John R. Hinnells',
    year: 2005, venue: 'Oxford University Press', lang: 'en', kind: 'book',
    theme: 'modern', fulltext: 'library',
    note: '當代祆教社群的全球民族誌；本站《後期文獻》一藏所敘的遷徙史，其現代延續在此。',
  },
  {
    ref: 'stausberg-companion',
    religion: 'zoroastrian',
    title: 'The Wiley Blackwell Companion to Zoroastrianism',
    title_zh: '祆教研究指南',
    authors: 'Michael Stausberg & Yuhan Sohrab-Dinshaw Vevaina (eds.)',
    year: 2015, venue: 'Wiley Blackwell', lang: 'en', kind: 'book',
    theme: 'modern', fulltext: 'library',
    note: '最新的綜合性研究指南，四十餘章分別由各題目的專家撰寫，'
      + '是判斷「某個題目現在的定論是什麼」最快的一本。',
  },

  // ══════════════ 摩尼教 ══════════════

  // ────────── 經典與語文 ──────────
  {
    ref: 'gardner-lieu-texts',
    religion: 'manichaean',
    title: 'Manichaean Texts from the Roman Empire',
    title_zh: '羅馬帝國的摩尼教文獻',
    authors: 'Iain Gardner & Samuel N. C. Lieu (eds.)',
    year: 2004, venue: 'Cambridge University Press', lang: 'en', kind: 'book',
    theme: 'scripture', fulltext: 'library',
    note: '把科普特文、希臘文、拉丁文的摩尼教原典譯成英文編為一冊。'
      + '**摩尼教研究最麻煩的地方是原典散在六七種語言裡**，這種選輯因此格外要緊。',
  },
  {
    ref: 'klimkeit-silkroad',
    religion: 'manichaean',
    title: 'Gnosis on the Silk Road: Gnostic Texts from Central Asia',
    title_zh: '絲路上的諾斯底：中亞的諾斯底文獻',
    authors: 'Hans-Joachim Klimkeit',
    year: 1993, venue: 'HarperCollins', lang: 'en', kind: 'book',
    theme: 'scripture', fulltext: 'library',
    note: '吐魯番出土的中古波斯語、帕提亞語、粟特語摩尼教殘卷英譯；'
      + '與本站 /gnostic 的材料同屬一個光譜。',
  },
  {
    ref: 'cologne-mani-codex',
    religion: 'manichaean',
    title: 'The Cologne Mani Codex: Concerning the Origin of His Body',
    title_zh: '科隆摩尼古卷：論其身體的來歷',
    authors: 'Ludwig Koenen & Cornelia Römer (eds.)',
    year: 1988, venue: 'Scholars Press', lang: 'en', kind: 'book',
    theme: 'scripture', fulltext: 'library',
    note: '全世界最小的古卷（約 3.5×4.5 公分），記摩尼的生平與蒙召。'
      + '**摩尼生平的一手文獻**，1970 年才刊布，此前所知的摩尼傳記全出自敵手。',
  },

  // ────────── 本土與西方 ──────────
  {
    ref: 'lieu-roman-china',
    religion: 'manichaean',
    title: 'Manichaeism in the Later Roman Empire and Medieval China: A Historical Survey',
    title_zh: '晚期羅馬帝國與中古中國的摩尼教：歷史概覽',
    authors: 'Samuel N. C. Lieu',
    year: 1985, venue: 'Manchester University Press', lang: 'en', kind: 'book',
    theme: 'homeland', fulltext: 'ready',
    note: '**橫跨東西兩端的標準著作**。摩尼教是少數同時在羅馬與中國留下大量痕跡的宗教，'
      + '而多數研究只做一端；劉南強兼治兩端，故此書至今無可替代。',
  },
  {
    ref: 'lieu-central-asia',
    religion: 'manichaean',
    title: 'Manichaeism in Central Asia and China',
    title_zh: '中亞與中國的摩尼教',
    authors: 'Samuel N. C. Lieu',
    year: 1998, venue: 'Brill', lang: 'en', kind: 'book',
    theme: 'homeland', fulltext: 'library',
  },
  {
    ref: 'beduhn-body',
    religion: 'manichaean',
    title: 'The Manichaean Body: In Discipline and Ritual',
    title_zh: '摩尼教的身體：戒律與儀式',
    authors: 'Jason David BeDuhn',
    year: 2000, venue: 'Johns Hopkins University Press', lang: 'en', kind: 'book',
    theme: 'homeland', fulltext: 'library',
    note: '從飲食與齋戒切入摩尼教的宇宙論——選民不自行採食是因為採食會傷及光明分子。'
      + '把教義與身體實踐接起來的代表作。',
  },
  {
    ref: 'baker-brian-rediscovered',
    religion: 'manichaean',
    title: 'Manichaeism: An Ancient Faith Rediscovered',
    title_zh: '摩尼教：一個重見天日的古代信仰',
    authors: 'Nicholas J. Baker-Brian',
    year: 2011, venue: 'T&T Clark', lang: 'en', kind: 'book',
    theme: 'homeland', fulltext: 'library',
    note: '最新的英文入門通論。書名點出這個領域的處境：摩尼教一度被視為已死的異端，'
      + '直到二十世紀吐魯番與埃及的出土才「重見天日」。',
  },

  // ────────── 入華與華化（中文學界的強項）──────────
  {
    ref: 'chen-yuan-mani',
    religion: 'manichaean',
    title: '摩尼教入中國考',
    authors: '陳垣',
    year: 1923, venue: '《國學季刊》', lang: 'zh', kind: 'article',
    theme: 'china', fulltext: 'open',
    note: '與〈火祆教入中國考〉同年刊出，同為中文三夷教研究的奠基之作。1923 年，已入公有領域。',
  },
  {
    ref: 'lin-wushu-mani-dongjian',
    religion: 'manichaean',
    title: '摩尼教及其東漸',
    authors: '林悟殊',
    year: 1987, venue: '中華書局', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'ready',
    note: '**中文摩尼教研究的奠基專著**。林悟殊同時是祆教線的權威——'
      + '三夷教的研究在中文學界本來就由同一批人做，這也是本 collection 不按教別拆開的理由。',
  },
  {
    ref: 'wang-jianchuan-mingjiao',
    religion: 'manichaean',
    title: '從摩尼教到明教',
    authors: '王見川',
    year: 1992, venue: '新文豐出版公司（台北）', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '台灣出版的明教研究代表作。摩尼教入華後與民間宗教結合而成「明教」，'
      + '這個轉變是中國宗教史上外來宗教本土化最徹底的案例之一。',
  },
  {
    ref: 'wu-han-damingdiguo',
    religion: 'manichaean',
    title: '明教與大明帝國',
    authors: '吳晗',
    year: 1941, venue: '《清華學報》第 13 卷第 1 期', lang: 'zh', kind: 'article',
    theme: 'china', fulltext: 'open',
    note: '主張明朝國號「明」出自明教，據韓林兒稱「小明王」等證。'
      + '**此說影響極大但爭議未息**，須與下一條楊訥的反駁並讀——'
      + '只收一方等於把一場仍在進行的辯論寫成定論。',
    seealso: 'yang-ne-bailianjiao',
  },
  {
    ref: 'yang-ne-bailianjiao',
    religion: 'manichaean',
    title: '元代白蓮教研究',
    authors: '楊訥',
    year: '', venue: '', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '**反駁吳晗**：主張元末起事的宗教背景是白蓮教而非明教，「大明」國號與明教無關。'
      + '與上一條並收才成辯論。',
    seealso: 'wu-han-damingdiguo',
  },
  {
    ref: 'rui-chuanming-dongfang',
    religion: 'manichaean',
    title: '東方摩尼教研究',
    authors: '芮傳明',
    year: '', venue: '', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
  },
  {
    ref: 'yang-fuxue-huihu',
    religion: 'manichaean',
    title: '回鶻摩尼教研究',
    authors: '楊富學',
    year: '', venue: '', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '摩尼教在回鶻汗國被立為**國教**——這是摩尼教史上唯一一次取得國教地位，'
      + '也是它得以東傳入華的政治條件。',
  },
  {
    ref: 'ma-xiaohe-xiyu',
    religion: 'manichaean',
    title: '摩尼教與古代西域史研究',
    authors: '馬小鶴',
    year: '', venue: '', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
  },
  {
    ref: 'yang-fuxue-xiapu',
    religion: 'manichaean',
    title: '霞浦摩尼教研究',
    authors: '楊富學、彭曉靜、包朗',
    year: '', venue: '（國家社科基金項目）', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
    note: '2008 年福建霞浦發現大量摩尼教文書、文物與遺址，'
      + '**這是摩尼教研究近三十年最大的一次材料增長**，且是活的民間傳承而非考古死材料。'
      + '相關研究仍在快速累積，本條目需定期回頭補。',
  },
  {
    ref: 'ma-xiaohe-xiapu',
    religion: 'manichaean',
    title: '霞浦文書研究',
    authors: '馬小鶴',
    year: '', venue: '', lang: 'zh', kind: 'book',
    theme: 'china', fulltext: 'library',
  },
]

export function entriesByTheme(theme: ZsTheme): ZsEntry[] {
  return ENTRIES.filter(e => e.theme === theme)
}

export function entriesByReligion(religion: ZsReligion): ZsEntry[] {
  return ENTRIES.filter(e => e.religion === religion)
}

/** 某一教的條目，含跨教通論——跨教書對每一教都算數，不該只出現在一個分頁。 */
export function entriesFor(religion: ZsReligion): ZsEntry[] {
  return ENTRIES.filter(e => e.religion === religion || e.religion === 'cross')
}

export function tallyReligion(): Record<string, number> {
  const t: Record<string, number> = {}
  for (const e of ENTRIES) t[e.religion] = (t[e.religion] ?? 0) + 1
  return t
}

export function findEntry(ref: string): ZsEntry | undefined {
  return ENTRIES.find(e => e.ref === ref)
}

export function tallyFulltext(): Record<string, number> {
  const t: Record<string, number> = {}
  for (const e of ENTRIES) t[e.fulltext] = (t[e.fulltext] ?? 0) + 1
  return t
}
