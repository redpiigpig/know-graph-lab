// ============================================================================
// 古典語「每日閱讀/聽力」策展短文庫（grc / la / hbo）— 2026-06-18
//   今日計畫的閱讀短文與聽力段落原本逐篇走 AI 生成；這三語改抽本庫，**完全不走 AI**。
//   取材＝公有領域經文原文（新約／七十士／武加大／BHS），逐篇附繁中摘要＋理解題。
//   daily.get 依「台北日期種子」每日輪替挑題（閱讀/聽力各取一組、種子加鹽分流）。
// 加題：在對應語言陣列補一筆 BankPassage 即可。
// ============================================================================
export interface BankQuestion {
  q: string;
  options: string[];
  answer: string; // 正解的選項全文（與 options 之一相符）
}
export interface BankPassage {
  id: string;
  level: string;     // 量表級別（入門/初級…）
  title: string;     // 標題（含出處）
  text: string;      // 原文短文（閱讀顯示／聽力由 TTS 朗讀）
  summary: string;   // 繁中一句摘要
  questions: BankQuestion[];
}

// ── 通用希臘文 Koine（新約／七十士）─────────────────────────────────────────
const GRC: BankPassage[] = [
  {
    id: "grc-jn1-1", level: "入門", title: "約翰福音 1:1",
    text: "Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ ὁ λόγος ἦν πρὸς τὸν θεόν, καὶ θεὸς ἦν ὁ λόγος.",
    summary: "太初有道，道與神同在，道就是神。",
    questions: [
      { q: "「ἐν ἀρχῇ」是什麼意思？", options: ["在起初", "在最後", "在地上", "在殿裡"], answer: "在起初" },
      { q: "「ὁ λόγος」指的是？", options: ["道（話語）", "光", "水", "律法"], answer: "道（話語）" },
    ],
  },
  {
    id: "grc-jn3-16", level: "初級", title: "約翰福音 3:16",
    text: "Οὕτως γὰρ ἠγάπησεν ὁ θεὸς τὸν κόσμον, ὥστε τὸν υἱὸν τὸν μονογενῆ ἔδωκεν.",
    summary: "神愛世人，甚至賜下祂的獨生子。",
    questions: [
      { q: "「ἠγάπησεν」這個動詞是？", options: ["愛（過去式）", "創造", "說", "差遣"], answer: "愛（過去式）" },
      { q: "神所愛的對象「τὸν κόσμον」是？", options: ["世界（世人）", "天使", "門徒", "祭司"], answer: "世界（世人）" },
    ],
  },
  {
    id: "grc-1jn4-8", level: "入門", title: "約翰一書 4:8",
    text: "ὁ μὴ ἀγαπῶν οὐκ ἔγνω τὸν θεόν, ὅτι ὁ θεὸς ἀγάπη ἐστίν.",
    summary: "不愛人的，就不認識神，因為神就是愛。",
    questions: [
      { q: "「ὁ θεὸς ἀγάπη ἐστίν」意思是？", options: ["神就是愛", "神是光", "神是靈", "神是王"], answer: "神就是愛" },
      { q: "句中繫詞「ἐστίν」的意思是？", options: ["是", "有", "來", "去"], answer: "是" },
    ],
  },
  {
    id: "grc-jn8-12", level: "初級", title: "約翰福音 8:12",
    text: "Ἐγώ εἰμι τὸ φῶς τοῦ κόσμου· ὁ ἀκολουθῶν ἐμοὶ οὐ μὴ περιπατήσῃ ἐν τῇ σκοτίᾳ.",
    summary: "我是世界的光，跟從我的就不在黑暗裡走。",
    questions: [
      { q: "「Ἐγώ εἰμι」是什麼意思？", options: ["我是", "你是", "他是", "我們是"], answer: "我是" },
      { q: "「τὸ φῶς」是？", options: ["光", "道", "生命", "門"], answer: "光" },
    ],
  },
  {
    id: "grc-mt5-3", level: "初級", title: "馬太福音 5:3（八福之一）",
    text: "Μακάριοι οἱ πτωχοὶ τῷ πνεύματι, ὅτι αὐτῶν ἐστιν ἡ βασιλεία τῶν οὐρανῶν.",
    summary: "虛心的人有福了，因為天國是他們的。",
    questions: [
      { q: "「Μακάριοι」意思是？", options: ["有福的", "貧窮的", "聖潔的", "智慧的"], answer: "有福的" },
      { q: "「ἡ βασιλεία τῶν οὐρανῶν」是？", options: ["天國（諸天的國）", "地上的城", "聖殿", "曠野"], answer: "天國（諸天的國）" },
    ],
  },
  {
    id: "grc-jn11-35", level: "入門", title: "約翰福音 11:35",
    text: "ἐδάκρυσεν ὁ Ἰησοῦς.",
    summary: "耶穌哭了。（全聖經最短的一節）",
    questions: [
      { q: "「ἐδάκρυσεν」的意思是？", options: ["哭了", "笑了", "說了", "去了"], answer: "哭了" },
      { q: "句子的主詞是誰？", options: ["耶穌", "彼得", "神", "馬大"], answer: "耶穌" },
    ],
  },
  {
    id: "grc-ps22-1", level: "初級", title: "詩篇 23:1（七十士譯本 22:1）",
    text: "Κύριος ποιμαίνει με, καὶ οὐδέν με ὑστερήσει.",
    summary: "主牧養我，我必不缺乏。",
    questions: [
      { q: "「Κύριος」指的是？", options: ["主", "牧人僕役", "君王", "先知"], answer: "主" },
      { q: "「ποιμαίνει」意思接近？", options: ["牧養", "審判", "創造", "醫治"], answer: "牧養" },
    ],
  },
  {
    id: "grc-1cor13-4", level: "進階", title: "哥林多前書 13:4",
    text: "Ἡ ἀγάπη μακροθυμεῖ, χρηστεύεται ἡ ἀγάπη, οὐ ζηλοῖ.",
    summary: "愛是恆久忍耐，又有恩慈；愛是不嫉妒。",
    questions: [
      { q: "本節反覆出現的主詞「ἡ ἀγάπη」是？", options: ["愛", "信", "望", "義"], answer: "愛" },
      { q: "「μακροθυμεῖ」描述愛的哪種特質？", options: ["恆久忍耐", "嫉妒", "誇張", "易怒"], answer: "恆久忍耐" },
    ],
  },
];

// ── 教會拉丁文（武加大／禮儀）──────────────────────────────────────────────
const LA: BankPassage[] = [
  {
    id: "la-gen1-1", level: "入門", title: "創世記 1:1（武加大）",
    text: "In principio creavit Deus caelum et terram.",
    summary: "起初，神創造天地。",
    questions: [
      { q: "「In principio」是什麼意思？", options: ["起初", "末了", "在殿中", "在曠野"], answer: "起初" },
      { q: "「creavit」這個動詞是？", options: ["創造了", "說了", "看了", "造了房"], answer: "創造了" },
    ],
  },
  {
    id: "la-jn1-1", level: "入門", title: "約翰福音 1:1（武加大）",
    text: "In principio erat Verbum, et Verbum erat apud Deum, et Deus erat Verbum.",
    summary: "太初有道，道與神同在，道就是神。",
    questions: [
      { q: "「Verbum」對應希臘文的 λόγος，意思是？", options: ["道（話語）", "光", "生命", "靈"], answer: "道（話語）" },
      { q: "「erat」是哪個動詞的形式？", options: ["sum（是）的過去", "creare（造）", "videre（看）", "dicere（說）"], answer: "sum（是）的過去" },
    ],
  },
  {
    id: "la-gen1-3", level: "初級", title: "創世記 1:3（武加大）",
    text: "Dixitque Deus: Fiat lux. Et facta est lux.",
    summary: "神說：要有光。就有了光。",
    questions: [
      { q: "「Fiat lux」意思是？", options: ["要有光", "光消失", "黑暗來臨", "神看光"], answer: "要有光" },
      { q: "「Dixit」這個動詞是？", options: ["說了", "造了", "去了", "愛了"], answer: "說了" },
    ],
  },
  {
    id: "la-1jn4-16", level: "入門", title: "約翰一書 4:16（武加大）",
    text: "Deus caritas est, et qui manet in caritate, in Deo manet.",
    summary: "神就是愛；住在愛裡的，就住在神裡面。",
    questions: [
      { q: "「Deus caritas est」意思是？", options: ["神就是愛", "神是光", "神是王", "神是靈"], answer: "神就是愛" },
      { q: "「manet」意思接近？", options: ["居住/住在", "創造", "審判", "差遣"], answer: "居住/住在" },
    ],
  },
  {
    id: "la-pater", level: "初級", title: "主禱文（Pater Noster）開頭",
    text: "Pater noster, qui es in caelis, sanctificetur nomen tuum.",
    summary: "我們在天上的父，願祢的名被尊為聖。",
    questions: [
      { q: "「Pater noster」是？", options: ["我們的父", "我們的王", "我們的主", "我們的神"], answer: "我們的父" },
      { q: "「in caelis」意思是？", options: ["在諸天上", "在地上", "在殿中", "在心裡"], answer: "在諸天上" },
    ],
  },
  {
    id: "la-ave", level: "初級", title: "聖母經（Ave Maria）開頭",
    text: "Ave Maria, gratia plena, Dominus tecum.",
    summary: "萬福瑪利亞，滿被聖寵者，主與你同在。",
    questions: [
      { q: "「gratia plena」意思是？", options: ["滿有恩寵", "滿有智慧", "滿有能力", "滿有財富"], answer: "滿有恩寵" },
      { q: "「Dominus tecum」是？", options: ["主與你同在", "主賜你平安", "主醫治你", "主差遣你"], answer: "主與你同在" },
    ],
  },
  {
    id: "la-magnificat", level: "進階", title: "尊主頌（Magnificat）開頭",
    text: "Magnificat anima mea Dominum, et exsultavit spiritus meus in Deo salutari meo.",
    summary: "我心尊主為大，我靈以神我的救主為樂。",
    questions: [
      { q: "「anima mea」是？", options: ["我的靈魂", "我的身體", "我的家", "我的話"], answer: "我的靈魂" },
      { q: "「Dominum」在句中是主格還是賓格？", options: ["賓格（受詞）", "主格（主詞）", "屬格", "與格"], answer: "賓格（受詞）" },
    ],
  },
  {
    id: "la-ps22-1", level: "初級", title: "詩篇 23:1（武加大 22:1）",
    text: "Dominus regit me, et nihil mihi deerit.",
    summary: "主牧養我，我必一無所缺。",
    questions: [
      { q: "「Dominus」是？", options: ["主", "牧人", "君王", "僕人"], answer: "主" },
      { q: "「nihil mihi deerit」意思接近？", options: ["我一無所缺", "我必富足", "我必得勝", "我必歡喜"], answer: "我一無所缺" },
    ],
  },
];

// ── 聖經希伯來文（BHS）──────────────────────────────────────────────────────
const HBO: BankPassage[] = [
  {
    id: "hbo-gen1-1", level: "入門", title: "創世記 1:1",
    text: "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ׃",
    summary: "起初，神創造天地。",
    questions: [
      { q: "「בְּרֵאשִׁית」意思是？", options: ["在起初", "在末了", "在殿中", "在曠野"], answer: "在起初" },
      { q: "「אֱלֹהִים」是？", options: ["神", "天", "地", "光"], answer: "神" },
    ],
  },
  {
    id: "hbo-gen1-3", level: "初級", title: "創世記 1:3",
    text: "וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר׃",
    summary: "神說：要有光。就有了光。",
    questions: [
      { q: "「יְהִי אוֹר」意思是？", options: ["要有光", "黑暗來到", "神看光", "光消失"], answer: "要有光" },
      { q: "「וַיֹּאמֶר」是敘事中的哪種動作？", options: ["（於是）說", "（於是）造", "（於是）走", "（於是）看"], answer: "（於是）說" },
    ],
  },
  {
    id: "hbo-shema", level: "初級", title: "申命記 6:4（Shema）",
    text: "שְׁמַע יִשְׂרָאֵל יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָד׃",
    summary: "以色列啊，你要聽！耶和華我們的神是獨一的耶和華。",
    questions: [
      { q: "「שְׁמַע」是什麼意思？", options: ["你要聽", "你要看", "你要說", "你要走"], answer: "你要聽" },
      { q: "「אֶחָד」意思是？", options: ["一（獨一）", "聖潔", "永恆", "大能"], answer: "一（獨一）" },
    ],
  },
  {
    id: "hbo-ps23-1", level: "初級", title: "詩篇 23:1",
    text: "יְהוָה רֹעִי לֹא אֶחְסָר׃",
    summary: "耶和華是我的牧者，我必不缺乏。",
    questions: [
      { q: "「רֹעִי」意思是？", options: ["我的牧者", "我的王", "我的父", "我的主"], answer: "我的牧者" },
      { q: "「לֹא אֶחְסָר」意思接近？", options: ["我必不缺乏", "我必歡喜", "我必得勝", "我必安息"], answer: "我必不缺乏" },
    ],
  },
  {
    id: "hbo-num6-24", level: "入門", title: "民數記 6:24（祭司祝福）",
    text: "יְבָרֶכְךָ יְהוָה וְיִשְׁמְרֶךָ׃",
    summary: "願耶和華賜福給你，保護你。",
    questions: [
      { q: "「יְבָרֶכְךָ」意思接近？", options: ["願祂賜福給你", "願祂審判你", "願祂差遣你", "願祂醫治你"], answer: "願祂賜福給你" },
      { q: "字尾「ךָ」表示？", options: ["你（陽性）", "我", "他", "我們"], answer: "你（陽性）" },
    ],
  },
  {
    id: "hbo-ps1-1", level: "進階", title: "詩篇 1:1",
    text: "אַשְׁרֵי הָאִישׁ אֲשֶׁר לֹא הָלַךְ בַּעֲצַת רְשָׁעִים׃",
    summary: "不從惡人計謀的，這人便為有福。",
    questions: [
      { q: "「אַשְׁרֵי」意思是？", options: ["有福啊（多麼有福）", "禍哉", "聖潔", "智慧"], answer: "有福啊（多麼有福）" },
      { q: "「הָאִישׁ」是？", options: ["這人", "這王", "這神", "這民"], answer: "這人" },
    ],
  },
  {
    id: "hbo-prov1-7", level: "進階", title: "箴言 1:7",
    text: "יִרְאַת יְהוָה רֵאשִׁית דָּעַת׃",
    summary: "敬畏耶和華是知識的開端。",
    questions: [
      { q: "「יִרְאַת יְהוָה」意思是？", options: ["敬畏耶和華", "認識耶和華", "讚美耶和華", "尋求耶和華"], answer: "敬畏耶和華" },
      { q: "「רֵאשִׁית」意思接近？", options: ["開端/起頭", "終結", "果效", "賞賜"], answer: "開端/起頭" },
    ],
  },
  {
    id: "hbo-gen12-1", level: "進階", title: "創世記 12:1",
    text: "וַיֹּאמֶר יְהוָה אֶל־אַבְרָם לֶךְ־לְךָ מֵאַרְצְךָ׃",
    summary: "耶和華對亞伯蘭說：你要離開本地。",
    questions: [
      { q: "「לֶךְ־לְךָ」意思接近？", options: ["你去吧（離開）", "你留下", "你回來", "你等候"], answer: "你去吧（離開）" },
      { q: "「מֵאַרְצְךָ」中的前綴「מֵ」表示？", options: ["從…（離開）", "在…裡", "向…", "如同…"], answer: "從…（離開）" },
    ],
  },
];

export const COACH_PASSAGES: Record<string, BankPassage[]> = { grc: GRC, la: LA, hbo: HBO };
export const CURATED_PASSAGE_LANGS = new Set(Object.keys(COACH_PASSAGES));

export function passageById(language: string, id: string): BankPassage | undefined {
  return (COACH_PASSAGES[language] || []).find((p) => p.id === id);
}

// 簡單字串雜湊（種子排序用，確定性）
function hash(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}

// 依種子（如台北日期＋鹽）確定性挑 n 篇；同種子穩定、換天/換鹽即換題。
export function pickDailyPassages(language: string, seedStr: string, n: number): BankPassage[] {
  const pool = COACH_PASSAGES[language] || [];
  return [...pool]
    .map((p) => ({ p, k: hash(seedStr + "|" + p.id) }))
    .sort((a, b) => a.k - b.k)
    .slice(0, Math.min(n, pool.length))
    .map((x) => x.p);
}
