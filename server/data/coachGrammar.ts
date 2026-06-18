// ============================================================================
// 古典語文法「手工策展」課程（grc / la / hbo）— 2026-06-18
//   仿 enGrammar：syllabus 與每課內容（解說/例句/練習）全人工策展、預嵌 content，
//   grammar/index.get.ts 與 lesson.post.ts 偵測到這三語就直接回，**完全不走 AI**。
//   定向＝神學院初學版（Koine／教會拉丁／聖經希伯來），例句取自新約／武加大／BHS。
//   量表 ANCIENT（入門/初級/中級/進階）；目前鋪入門→初級，之後可續補。
// 加課：在對應語言陣列補一筆 GrammarTopic（含 content）即可。
// ============================================================================
import type { GrammarTopic } from "./enGrammar";

// ── 通用希臘文 Koine ────────────────────────────────────────────────────────
const GRC: GrammarTopic[] = [
  {
    id: "grc-alphabet",
    en: "Alphabet, Breathings & Accents",
    title: "希臘字母‧呼氣記號‧重音",
    levels: ["入門"],
    summary: "24 字母、母音前的呼氣記號（粗/柔）、三種重音與 σ/ς 寫法。",
    keywords: ["alphabet", "字母", "breathing", "呼氣", "accent", "重音", "sigma", "iota subscript"],
    content: {
      explanation:
        "希臘文有 24 個字母。母音（或字首 ρ）開頭的字一定帶**呼氣記號**：粗氣號 ( ῾ ) 發 h 音（如 ὁ = ho），柔氣號 ( ᾿ ) 不發音（如 ἐν = en）。\n重音有三種：銳 ( ´ )、抑 ( ` )、揚 ( ῀ )，初學先求讀對位置、不必背規則。\nσ 用在詞首與詞中，詞尾改寫成 ς（如 Ἰησοῦς）。母音下的小 ι（ᾳ ῃ ῳ）叫「下加 iota」，不發音但會影響字義。",
      examples: [
        { target: "ἀρχή", translation: "起初、太初", note: "柔氣號→不發 h；重音在尾音節" },
        { target: "ὁ", translation: "（陽性冠詞）這、那", note: "粗氣號→讀 ho" },
        { target: "Ἰησοῦς", translation: "耶穌", note: "詞尾 σ 寫成 ς；揚音 ῀" },
      ],
      practice: [
        { q: "ὁ 與 ἐν 各自的呼氣記號發不發 h 音？", answer: "ὁ 粗氣號發 h（ho）；ἐν 柔氣號不發（en）。" },
        { q: "σ 在詞尾要寫成什麼？舉一字。", answer: "寫成 ς，例：Ἰησοῦς、λόγος。" },
      ],
    },
  },
  {
    id: "grc-article-gender",
    en: "The Article & Three Genders",
    title: "冠詞與三種性",
    levels: ["入門"],
    summary: "ὁ（陽）／ἡ（陰）／τό（中），冠詞隨名詞的性‧數‧格變化。",
    keywords: ["article", "冠詞", "gender", "性", "ὁ ἡ τό", "定冠詞"],
    content: {
      explanation:
        "希臘文名詞有三種性：陽性、陰性、中性。定冠詞（相當於 the）主格單數為 ὁ（陽）／ἡ（陰）／τό（中）。\n希臘文沒有不定冠詞（a/an）；沒有冠詞時常譯為「一個」或不譯。\n冠詞與所修飾的名詞在**性、數、格**上一致，所以看冠詞就能判斷名詞的性與格——這是讀經很重要的線索。",
      examples: [
        { target: "ὁ λόγος", translation: "這道／話語", note: "陽性主格" },
        { target: "ἡ ἀγάπη", translation: "這愛", note: "陰性主格" },
        { target: "τὸ φῶς", translation: "這光", note: "中性主格（τό 在某些格寫作 τὸ）" },
      ],
      practice: [
        { q: "θεός（神）配哪個冠詞？", answer: "ὁ（陽性）→ ὁ θεός。" },
        { q: "希臘文有沒有「a/an」這種不定冠詞？", answer: "沒有；無冠詞時依文意譯為「一個」或不譯。" },
      ],
    },
  },
  {
    id: "grc-noun-cases",
    en: "Noun Cases (1st & 2nd Declension)",
    title: "名詞變格與五格的功能",
    levels: ["入門", "初級"],
    summary: "主／呼／賓／屬／與五格各司其職；先掌握第一、第二變格。",
    keywords: ["case", "格", "declension", "變格", "nominative", "genitive", "dative", "accusative"],
    content: {
      explanation:
        "希臘文靠**字尾（格）**標示語法角色，而非靠語序：\n‧主格＝主詞（λόγος）\n‧屬格＝所有/來源（of，λόγου）\n‧與格＝間接受詞/工具/處所（to/with/in，λόγῳ）\n‧賓格＝直接受詞（λόγον）\n‧呼格＝呼喚。\n第二變格陽性以 -ος 收尾（λόγος），第一變格陰性多以 -η/-α 收尾（ἀγάπη）。",
      examples: [
        { target: "ὁ λόγος τοῦ θεοῦ", translation: "神的道", note: "θεοῦ＝屬格『神的』" },
        { target: "ἐν ἀρχῇ", translation: "在起初", note: "ἀρχῇ＝與格（處所），下加 iota" },
        { target: "τὸν λόγον", translation: "（把）道（當受詞）", note: "賓格 -ον＝直接受詞" },
      ],
      practice: [
        { q: "「神的」用哪一格？寫出 θεός 的屬格。", answer: "屬格；θεοῦ。" },
        { q: "λόγος 當直接受詞時變成？", answer: "賓格 λόγον。" },
      ],
    },
  },
  {
    id: "grc-eimi-present",
    en: "εἰμί — Present Indicative",
    title: "繫詞 εἰμί（是）現在式",
    levels: ["入門"],
    summary: "最常見的不規則動詞「是」：εἰμί, εἶ, ἐστί(ν)…，兩端用主格。",
    keywords: ["εἰμί", "to be", "繫詞", "is", "copula", "present"],
    content: {
      explanation:
        "εἰμί（是）是最高頻動詞。現在直說：εἰμί（我是）／εἶ（你是）／ἐστί(ν)（他是）／ἐσμέν（我們是）／ἐστέ（你們是）／εἰσί(ν)（他們是）。\n它是**繫詞**，連接的主詞與述語**都用主格**（不像及物動詞用賓格）。\n字尾 -ν（活動鼻音）在母音或句末前出現，如 ἐστίν。",
      examples: [
        { target: "ὁ θεὸς ἀγάπη ἐστίν.", translation: "神是愛。", note: "兩端皆主格：θεός、ἀγάπη" },
        { target: "ἐγώ εἰμι.", translation: "我是。", note: "耶穌自稱常用語" },
        { target: "οὗτός ἐστιν ὁ υἱός.", translation: "這位是兒子。", note: "ἐστιν 第三人稱單數" },
      ],
      practice: [
        { q: "「他們是」希臘文怎麼說？", answer: "εἰσί(ν)。" },
        { q: "繫詞 εἰμί 兩端的名詞用什麼格？", answer: "都用主格。" },
      ],
    },
  },
  {
    id: "grc-verb-present-active",
    en: "Present Active Indicative (λύω)",
    title: "動詞現在主動直說（λύω）",
    levels: ["入門", "初級"],
    summary: "範式動詞 λύω 的六個人稱字尾：-ω, -εις, -ει, -ομεν, -ετε, -ουσι(ν)。",
    keywords: ["verb", "動詞", "present active", "現在式", "λύω", "conjugation", "變位"],
    content: {
      explanation:
        "規則動詞用範式 λύω（解開）學變位。現在主動直說＝動詞字幹 λυ- ＋人稱字尾：\nλύω（我）／λύεις（你）／λύει（他）／λύομεν（我們）／λύετε（你們）／λύουσι(ν)（他們）。\n希臘文動詞**本身含主詞**，所以常省略人稱代名詞。現在式可表正在或習慣的動作。",
      examples: [
        { target: "πιστεύω", translation: "我信", note: "πιστεύ- + ω" },
        { target: "γράφει", translation: "他寫", note: "第三人稱單數 -ει" },
        { target: "ἀκούουσιν τὸν λόγον.", translation: "他們聽這道。", note: "-ουσιν 第三人稱複數＋賓格受詞" },
      ],
      practice: [
        { q: "λύω 的『我們解開』是？", answer: "λύομεν。" },
        { q: "為什麼希臘文常不寫『我、你、他』等代名詞？", answer: "因為動詞字尾已標明人稱與數。" },
      ],
    },
  },
  {
    id: "grc-prepositions",
    en: "Prepositions & Their Cases",
    title: "介系詞與所搭配的格",
    levels: ["初級"],
    summary: "ἐν+與格、εἰς+賓格、ἐκ+屬格…；同一介系詞配不同格意思會變。",
    keywords: ["preposition", "介系詞", "ἐν", "εἰς", "ἐκ", "πρός", "case"],
    content: {
      explanation:
        "介系詞會「指定」後面名詞的格，意思隨格而變：\n‧ἐν ＋與格＝在…之內（ἐν ἀρχῇ）\n‧εἰς ＋賓格＝進入、朝向（εἰς τὸν κόσμον）\n‧ἐκ／ἐξ ＋屬格＝從…出來（ἐκ τοῦ θεοῦ）\n‧πρός ＋賓格＝向著、與…一起（πρὸς τὸν θεόν）。\n記介系詞時要連同它要求的格一起背。",
      examples: [
        { target: "ἐν ἀρχῇ ἦν ὁ λόγος", translation: "太初有道", note: "ἐν＋與格 ἀρχῇ" },
        { target: "ὁ λόγος ἦν πρὸς τὸν θεόν", translation: "道與神同在", note: "πρός＋賓格" },
        { target: "ἐκ τοῦ θεοῦ", translation: "出於神", note: "ἐκ＋屬格" },
      ],
      practice: [
        { q: "εἰς 後面接哪一格？意思是？", answer: "賓格；進入、朝向。" },
        { q: "ἐν 後接什麼格？", answer: "與格（dative）。" },
      ],
    },
  },
  {
    id: "grc-adjective-agreement",
    en: "Adjective Agreement",
    title: "形容詞與名詞一致",
    levels: ["初級"],
    summary: "形容詞在性‧數‧格上與名詞一致；位置決定『修飾』或『敘述』。",
    keywords: ["adjective", "形容詞", "agreement", "一致", "attributive", "predicate"],
    content: {
      explanation:
        "形容詞必須與所修飾名詞在**性、數、格**一致，如 ἅγιος（聖的）→ ἁγία（陰）／ἅγιον（中）。\n位置區分用法：\n‧修飾用法（冠詞後）：ὁ ἀγαθὸς λόγος＝這好的道。\n‧敘述用法（冠詞外）：ὁ λόγος ἀγαθός＝這道是好的（隱含 εἰμί）。",
      examples: [
        { target: "πνεῦμα ἅγιον", translation: "聖靈", note: "中性一致：ἅγιον" },
        { target: "ἡ ζωὴ αἰώνιος", translation: "永遠的生命", note: "陰性一致" },
        { target: "ὁ λόγος ἀληθής ἐστιν.", translation: "這道是真的。", note: "敘述用法（在冠詞外）" },
      ],
      practice: [
        { q: "「好的道」（修飾用法）冠詞與形容詞怎麼排？", answer: "ὁ ἀγαθὸς λόγος（形容詞在冠詞與名詞之間）。" },
        { q: "形容詞要跟名詞在哪三方面一致？", answer: "性、數、格。" },
      ],
    },
  },
  {
    id: "grc-aorist-intro",
    en: "Aorist Indicative & καί",
    title: "不定過去式入門與 καί 連句",
    levels: ["初級"],
    summary: "敘事主力時態 aorist：字首加 ἐ-（augment）；καί 串起敘事。",
    keywords: ["aorist", "不定過去式", "augment", "augment ε", "καί", "narrative"],
    content: {
      explanation:
        "**不定過去式（aorist）**是敘事最常用的過去時態，表「發生過」的單一動作。第一式 aorist 的標記：動詞前加 ἐ-（augment）＋字幹＋-σα- ＋字尾，如 ἔλυσα（我解開了）。\n讀福音書會大量看到以 καί（和、然後）開頭把一連串 aorist 串起來的敘事句（受希伯來文影響的風格）。",
      examples: [
        { target: "ἐπίστευσεν", translation: "他信了", note: "augment ἐ- ＋ πιστευ- ＋ -σεν" },
        { target: "ἐν ἀρχῇ ἐποίησεν ὁ θεὸς…", translation: "起初神創造了…", note: "ἐποίησεν＝aorist 第三人稱單數" },
        { target: "καὶ εἶπεν ὁ θεός", translation: "神說（然後神說）", note: "καί 起首的敘事句" },
      ],
      practice: [
        { q: "第一式 aorist 動詞字首常加什麼？", answer: "augment ἐ-（如 ἔλυσα、ἐπίστευσεν）。" },
        { q: "福音書敘事常用哪個連接詞把句子串起來？", answer: "καί。" },
      ],
    },
  },
];

// ── 教會拉丁文 Ecclesiastical ────────────────────────────────────────────────
const LA: GrammarTopic[] = [
  {
    id: "la-pronunciation",
    en: "Ecclesiastical Pronunciation",
    title: "教會式發音",
    levels: ["入門"],
    summary: "義大利式讀法：c/g 在 e,i 前軟化、ae=e、gn=ny、ti+母音=tsi。",
    keywords: ["pronunciation", "發音", "ecclesiastical", "教會式", "ae", "gn", "ti", "c g"],
    content: {
      explanation:
        "教會拉丁採義大利式發音（與古典式不同）：\n‧c 在 e, i, ae, oe 前讀 ch（如 caelum→『切』lum）；其餘讀 k。\n‧g 在 e, i 前讀 j（如 genus→『傑』nus）。\n‧ae、oe 都讀作 e（caelum≈celum）。\n‧gn 讀 ny（agnus→『阿尼ус』≈anyus）。\n‧ti＋母音讀 tsi（gratia→『格拉tsia』）。\n‧h 通常不發音。",
      examples: [
        { target: "caelum", translation: "天", note: "ae=e、c 在 ae 前讀 ch" },
        { target: "Agnus Dei", translation: "神的羔羊", note: "gn 讀 ny" },
        { target: "gratia", translation: "恩典", note: "ti＋a 讀 tsia" },
      ],
      practice: [
        { q: "caelum 的 ae 怎麼讀？", answer: "讀作 e（≈celum）。" },
        { q: "gratia 的 ti 怎麼讀？", answer: "ti＋母音讀 tsi（gra-tsia）。" },
      ],
    },
  },
  {
    id: "la-noun-decl",
    en: "Noun Declensions 1 & 2 + Cases",
    title: "第一、二變格與格的功能",
    levels: ["入門", "初級"],
    summary: "拉丁靠字尾標格：主/屬/與/賓/奪/呼；第一變格 -a、第二變格 -us。",
    keywords: ["declension", "變格", "case", "格", "nominative", "genitive", "ablative", "第一變格"],
    content: {
      explanation:
        "拉丁名詞靠**字尾（格）**表語法角色：\n‧主格＝主詞 ‧屬格＝所有(of) ‧與格＝間接受詞(to/for) ‧賓格＝直接受詞 ‧奪格＝by/with/from/in ‧呼格＝呼喚。\n第一變格多為陰性、單數主格 -a（gloria，屬格 -ae）；第二變格多為陽性 -us（dominus，屬格 -i）或中性 -um（verbum）。\n字典詞條給「主格, 屬格」即可判斷變格，如 gloria, -ae；dominus, -i。",
      examples: [
        { target: "gloria Dei", translation: "神的榮耀", note: "Dei＝Deus 的屬格『神的』" },
        { target: "verbum Domini", translation: "主的話", note: "Domini＝屬格；verbum 中性主格" },
        { target: "in nomine Patris", translation: "因父之名", note: "nomine＝奪格（in＋奪格）" },
      ],
      practice: [
        { q: "Deus（神）的屬格『神的』是？", answer: "Dei。" },
        { q: "『by/with/from/in』這類意思多用哪一格？", answer: "奪格（ablative）。" },
      ],
    },
  },
  {
    id: "la-sum-present",
    en: "sum — Present Tense",
    title: "繫詞 sum（是）現在式",
    levels: ["入門"],
    summary: "最高頻不規則動詞：sum, es, est, sumus, estis, sunt。",
    keywords: ["sum", "esse", "to be", "繫詞", "是", "present"],
    content: {
      explanation:
        "sum（我是）是拉丁最高頻動詞。現在式：sum（我）／es（你）／est（他）／sumus（我們）／estis（你們）／sunt（他們）。\n它是繫詞，連接的主詞與述語**都用主格**。動詞含主詞，故常省略人稱代名詞。",
      examples: [
        { target: "Deus caritas est.", translation: "神是愛。", note: "兩端主格；est 第三人稱單數" },
        { target: "Dominus vobiscum.", translation: "願主與你們同在。", note: "禮儀常用語（est 省略）" },
        { target: "ego sum", translation: "我是", note: "耶穌自稱（ego 可省）" },
      ],
      practice: [
        { q: "『他們是』拉丁文怎麼說？", answer: "sunt。" },
        { q: "繫詞 sum 兩端名詞用哪一格？", answer: "都用主格。" },
      ],
    },
  },
  {
    id: "la-verb-present",
    en: "Present Tense — Conjugations 1 & 2",
    title: "動詞現在式（第一、二變位）",
    levels: ["入門", "初級"],
    summary: "amō（第一變位 -āre）與 videō（第二變位 -ēre）的人稱字尾。",
    keywords: ["verb", "動詞", "conjugation", "變位", "amo", "video", "present"],
    content: {
      explanation:
        "拉丁動詞依不定式分變位。第一變位（-āre，如 amāre 愛）現在式：amō, amās, amat, amāmus, amātis, amant。\n第二變位（-ēre，如 vidēre 看）：videō, vidēs, videt, vidēmus, vidētis, vident。\n人稱字尾共通：-ō/-m（我）、-s（你）、-t（他）、-mus（我們）、-tis（你們）、-nt（他們）。動詞含主詞，常省略代名詞。",
      examples: [
        { target: "laudāmus te", translation: "我們讚美祢", note: "laudāre 第一變位，-mus 我們" },
        { target: "credo in Deum", translation: "我信神", note: "crēdere（第三變位）credo＝我信，信經首句" },
        { target: "videt", translation: "他看見", note: "vidēre 第二變位，-t 第三人稱單數" },
      ],
      practice: [
        { q: "amāre 的『他們愛』是？", answer: "amant。" },
        { q: "字尾 -mus 代表哪個人稱？", answer: "第一人稱複數『我們』。" },
      ],
    },
  },
  {
    id: "la-adjective-agreement",
    en: "Adjective Agreement",
    title: "形容詞與名詞一致",
    levels: ["初級"],
    summary: "形容詞隨名詞的性‧數‧格變化，如 bonus, -a, -um。",
    keywords: ["adjective", "形容詞", "agreement", "一致", "bonus", "sanctus"],
    content: {
      explanation:
        "形容詞與所修飾名詞在**性、數、格**一致。bonus（好的）三性：bonus（陽）／bona（陰）／bonum（中）。\nsanctus（聖的）同理：sanctus / sancta / sanctum。形容詞通常放在名詞之後（Spiritus Sanctus）。",
      examples: [
        { target: "Spiritus Sanctus", translation: "聖靈", note: "陽性一致：Sanctus" },
        { target: "vita aeterna", translation: "永生", note: "陰性一致：aeterna" },
        { target: "regnum caeleste", translation: "天國", note: "中性一致：caeleste" },
      ],
      practice: [
        { q: "把 sanctus 配陰性名詞 ecclesia（教會）。", answer: "ecclesia sancta（聖教會）。" },
        { q: "形容詞要與名詞在哪三方面一致？", answer: "性、數、格。" },
      ],
    },
  },
  {
    id: "la-prepositions",
    en: "Prepositions + Accusative / Ablative",
    title: "介系詞＋賓格／奪格",
    levels: ["初級"],
    summary: "in/sub 等配賓格表動向、配奪格表處所；cum/de/ex 恆配奪格。",
    keywords: ["preposition", "介系詞", "in", "cum", "de", "ex", "ad", "ablative", "accusative"],
    content: {
      explanation:
        "介系詞決定後面名詞的格：\n‧ad ＋賓格＝朝向；per ＋賓格＝經由。\n‧cum ＋奪格＝與…一起；de/ex(e) ＋奪格＝關於/從…出。\n‧in、sub 兩用：**＋賓格表動向**（in caelum＝進入天），**＋奪格表處所**（in caelo＝在天上）。",
      examples: [
        { target: "in caelo et in terra", translation: "在天上和在地上", note: "in＋奪格＝處所" },
        { target: "cum Spiritu Sancto", translation: "與聖靈同在", note: "cum＋奪格" },
        { target: "ex Maria Virgine", translation: "由童貞瑪利亞", note: "ex＋奪格＝從…出（信經）" },
      ],
      practice: [
        { q: "in caelum 與 in caelo 差在哪？", answer: "in＋賓格 caelum＝進入天（動向）；in＋奪格 caelo＝在天上（處所）。" },
        { q: "cum 後接哪一格？", answer: "奪格（ablative）。" },
      ],
    },
  },
  {
    id: "la-genitive-dative",
    en: "Uses of Genitive & Dative",
    title: "屬格與與格的用法",
    levels: ["初級"],
    summary: "屬格＝『的』(of)；與格＝『給/對』(to/for) 的間接受詞。",
    keywords: ["genitive", "屬格", "dative", "與格", "of", "to for"],
    content: {
      explanation:
        "**屬格**表所有或所屬（of）：filius Dei＝神的兒子；regnum caelorum＝諸天之國。\n**與格**表間接受詞或對象（to/for）：常見於『把 X 給 Y』『對 Y 而言』，如 da nobis（賜給我們）、gloria Patri（榮耀歸於父）。",
      examples: [
        { target: "filius Dei", translation: "神的兒子", note: "Dei＝屬格" },
        { target: "Gloria Patri et Filio", translation: "榮耀歸於父與子", note: "Patri、Filio＝與格『歸於』" },
        { target: "da nobis pacem", translation: "賜我們平安", note: "nobis＝與格『給我們』" },
      ],
      practice: [
        { q: "『歸於父』Patri 是哪一格？為什麼？", answer: "與格；表對象/歸屬（to/for）。" },
        { q: "『神的兒子』的『神的』用哪一格？", answer: "屬格 Dei。" },
      ],
    },
  },
  {
    id: "la-perfect-intro",
    en: "Perfect Tense (Intro)",
    title: "完成式入門",
    levels: ["初級"],
    summary: "表已完成的過去動作；用完成字幹＋-ī, -istī, -it…，如 amāvī。",
    keywords: ["perfect", "完成式", "amavi", "tense", "past"],
    content: {
      explanation:
        "完成式表「已經做了」的過去動作。用動詞的**完成字幹**（字典第三主要部分）＋字尾：-ī（我）／-istī（你）／-it（他）／-imus（我們）／-istis（你們）／-ērunt（他們）。\n例：amāre→完成字幹 amāv-→amāvī（我愛過）。crēdere→crēdidī（我信了）。",
      examples: [
        { target: "Verbum caro factum est", translation: "道成了肉身", note: "factum est＝完成被動（是…成了）" },
        { target: "credidi", translation: "我信了", note: "crēdere 的完成式" },
        { target: "fecit", translation: "他做了/造了", note: "facere 完成式第三人稱單數" },
      ],
      practice: [
        { q: "amāre 的『我愛過』完成式是？", answer: "amāvī。" },
        { q: "完成式第三人稱複數字尾是？", answer: "-ērunt（如 fēcērunt）。" },
      ],
    },
  },
];

// ── 聖經希伯來文 Biblical ────────────────────────────────────────────────────
const HBO: GrammarTopic[] = [
  {
    id: "hbo-alphabet-niqqud",
    en: "Alphabet, Vowel Points & Reading Direction",
    title: "字母‧母音點‧由右至左",
    levels: ["入門"],
    summary: "22 子音（5 個有詞尾形）＋母音點 niqqud；由右向左讀。",
    keywords: ["alphabet", "字母", "niqqud", "母音點", "RTL", "final letters", "sofit", "dagesh"],
    content: {
      explanation:
        "希伯來文**由右向左**書寫，22 個字母全是子音。母音以字母下/上的「點符（niqqud）」標示，如 ָ (a)、ֵ (e)、ִ (i)。\n5 個字母在詞尾改寫成「字尾形（sofit）」：כ→ך、מ→ם、נ→ן、פ→ף、צ→ץ。\n字母中的小點（dagesh）可加重子音或改變讀音（如 בּ=b / ב=v）。",
      examples: [
        { target: "אֱלֹהִים", translation: "神（複數形，作單數用）", note: "由右讀：alef-lamed-he-yod-mem" },
        { target: "שָׁלוֹם", translation: "平安", note: "ָ=a、וֹ=o；詞尾 ם" },
        { target: "מֶלֶךְ", translation: "王", note: "詞尾 ך（kaf sofit）" },
      ],
      practice: [
        { q: "希伯來文閱讀方向是？", answer: "由右向左。" },
        { q: "字母 מ 在詞尾要寫成？", answer: "ם（mem sofit）。" },
      ],
    },
  },
  {
    id: "hbo-article-noun",
    en: "Definite Article & Noun Gender/Number",
    title: "冠詞 הַ 與名詞性‧數",
    levels: ["入門"],
    summary: "定冠詞 הַ＋後字母加 dagesh；名詞分陽/陰，陰性多 -ָה 結尾。",
    keywords: ["article", "冠詞", "ha", "gender", "性", "number", "數", "plural"],
    content: {
      explanation:
        "定冠詞是前綴 הַ（ha＋下一字母重音點 dagesh），相當於 the，如 הָאָרֶץ＝這地。希伯來文沒有不定冠詞。\n名詞分陽性、陰性：陰性單數常以 -ָה（如 תּוֹרָה 律法）結尾。複數：陽性 -ִים（-im），陰性 -וֹת（-ot）。",
      examples: [
        { target: "הַשָּׁמַיִם", translation: "這天（諸天）", note: "הַ＋šamayim；ש 帶 dagesh" },
        { target: "הָאָרֶץ", translation: "這地", note: "喉音 א 前冠詞母音變長 הָ" },
        { target: "תּוֹרָה", translation: "律法（陰性）", note: "-ָה 陰性結尾" },
      ],
      practice: [
        { q: "希伯來文的定冠詞前綴是什麼？", answer: "הַ（ha-，並使後字母帶 dagesh）。" },
        { q: "陽性名詞複數常見字尾？", answer: "-ִים（-im）。" },
      ],
    },
  },
  {
    id: "hbo-prepositions-waw",
    en: "Conjunction ו & Inseparable Prepositions",
    title: "連接詞 וְ 與前綴介系詞 בְּ/לְ/כְּ",
    levels: ["入門", "初級"],
    summary: "וְ（和）、בְּ（在/用）、לְ（向/給）、כְּ（如）皆黏在字前；מִן＝從。",
    keywords: ["waw", "conjunction", "連接詞", "preposition", "介系詞", "be", "le", "min"],
    content: {
      explanation:
        "希伯來文有幾個**黏著前綴**：\n‧וְ＝和、然後（連接詞）\n‧בְּ＝在…裡/用/憑\n‧לְ＝向/給/為了\n‧כְּ＝如同。\n它們直接寫在下一個字前面（不分寫）。另有獨立介系詞 מִן＝從…（常縮為前綴 מִ＋dagesh）。\n加冠詞時前綴與冠詞會合併，如 בְּ＋הַ→בַּ。",
      examples: [
        { target: "בְּרֵאשִׁית", translation: "在起初", note: "בְּ（在）＋ rēšīt（起初）" },
        { target: "הַשָּׁמַיִם וְאֵת הָאָרֶץ", translation: "天和地", note: "וְ＝和（黏在 אֵת 前）" },
        { target: "לְדָוִד", translation: "（屬）大衛的／給大衛", note: "לְ＋大衛，詩篇標題常見" },
      ],
      practice: [
        { q: "『在起初』בְּרֵאשִׁית 的前綴 בְּ 是什麼意思？", answer: "在…裡（in）。" },
        { q: "『和』的前綴連接詞是？", answer: "וְ（we-/u-）。" },
      ],
    },
  },
  {
    id: "hbo-construct",
    en: "Construct Chain (smikhut)",
    title: "附屬連綴（construct chain）",
    levels: ["初級"],
    summary: "兩名詞相連表『X 的 Y』；前字取連綴形、冠詞只加在最後字。",
    keywords: ["construct", "連綴", "smikhut", "סמיכות", "of", "genitive"],
    content: {
      explanation:
        "希伯來文表「X 的 Y」用**連綴**：把兩個名詞並列，被擁有者在前（取『連綴形』、常縮短/變音），擁有者在後。整串只在**最後一個字**加冠詞。\n如 דְּבַר־יְהוָה＝『耶和華的話』（dəḇar＝dāḇār 的連綴形）。連綴形常用連字號（maqqef）連接。",
      examples: [
        { target: "דְּבַר יְהוָה", translation: "耶和華的話", note: "dāḇār→連綴形 dəḇar" },
        { target: "בֵּית אֱלֹהִים", translation: "神的家（殿）", note: "bayit→連綴形 bêt" },
        { target: "מֶלֶךְ יִשְׂרָאֵל", translation: "以色列的王", note: "前字連綴、後字為擁有者" },
      ],
      practice: [
        { q: "連綴鏈裡冠詞 הַ 加在哪個字上？", answer: "只加在最後（擁有者）那個字。" },
        { q: "『神的家』bayit 在連綴時變成什麼形？", answer: "連綴形 bêt（בֵּית）。" },
      ],
    },
  },
  {
    id: "hbo-pronoun-suffix",
    en: "Pronouns & Possessive Suffixes",
    title: "代名詞與所有詞尾",
    levels: ["初級"],
    summary: "獨立代名詞 אֲנִי/אַתָּה…；所有用詞尾黏名詞，如 -ִי=我的。",
    keywords: ["pronoun", "代名詞", "suffix", "詞尾", "possessive", "所有", "ani"],
    content: {
      explanation:
        "獨立人稱代名詞：אֲנִי（我）／אַתָּה（你，陽）／הוּא（他）／הִיא（她）等。\n「我的、你的…」不用獨立字，而是把**詞尾**黏在名詞後：-ִי（我的）、-ְךָ（你的，陽）、-וֹ（他的）。如 תּוֹרָתִי＝我的律法、דְּבָרוֹ＝他的話。同類詞尾也黏在介系詞與動詞上。",
      examples: [
        { target: "אֲנִי יְהוָה", translation: "我是耶和華", note: "אֲנִי＝我（繫詞常省略）" },
        { target: "תּוֹרָתוֹ", translation: "他的律法", note: "תּוֹרָה＋詞尾 -וֹ（他的）" },
        { target: "שְׁמוֹ", translation: "他的名", note: "šēm＋-ô" },
      ],
      practice: [
        { q: "『我的律法』怎麼構成？", answer: "תּוֹרָה ＋ 詞尾 -ִי → תּוֹרָתִי。" },
        { q: "獨立代名詞『我』是？", answer: "אֲנִי（也作 אָנֹכִי）。" },
      ],
    },
  },
  {
    id: "hbo-qal-perfect",
    en: "Qal Perfect (qatal)",
    title: "Qal 完成式（qatal）",
    levels: ["初級"],
    summary: "最基本動詞型 Qal 的完成貌：表已完成動作，字尾標人稱性數。",
    keywords: ["qal", "perfect", "完成式", "qatal", "binyan", "verb", "動詞"],
    content: {
      explanation:
        "希伯來動詞有七個「型（binyan）」，最基本的是 **Qal**。完成式（qatal/perfect）多表**已完成**的動作，用範式 קָטַל（殺，文法範例字）：\nקָטַל（他）／קָטְלָה（她）／קָטַלְתָּ（你陽）／קָטַלְתִּי（我）／קָטְלוּ（他們）。\n字根多為三子音（如 כ-ת-ב 寫、ש-מ-ר 守），母音套進範式即得各種動詞。",
      examples: [
        { target: "בָּרָא אֱלֹהִים", translation: "神創造了", note: "bārā＝Qal 完成 3 陽單" },
        { target: "כָּתַב", translation: "他寫了", note: "字根 כ-ת-ב 套入 qatal 範式" },
        { target: "שָׁמַרְתִּי", translation: "我守了", note: "字尾 -תִּי＝我" },
      ],
      practice: [
        { q: "最基本的動詞型（binyan）叫什麼？", answer: "Qal。" },
        { q: "qatal 完成式字尾 -תִּי 代表哪個人稱？", answer: "第一人稱單數『我』。" },
      ],
    },
  },
  {
    id: "hbo-qal-imperfect",
    en: "Qal Imperfect (yiqtol)",
    title: "Qal 未完成式（yiqtol）",
    levels: ["初級"],
    summary: "表未完成/未來/慣常動作；用前綴標人稱，如 יִקְטֹל=他將殺。",
    keywords: ["qal", "imperfect", "未完成式", "yiqtol", "prefix", "future"],
    content: {
      explanation:
        "Qal **未完成式（yiqtol/imperfect）**表未完成、未來或慣常的動作，特徵是用**前綴**（有時加字尾）標人稱：\nיִקְטֹל（他）／תִּקְטֹל（你陽/她）／אֶקְטֹל（我）／נִקְטֹל（我們）。\n與完成式（用字尾）相對：完成式≈已然，未完成式≈未然/反覆。",
      examples: [
        { target: "יִקְרָא", translation: "他將呼叫／他稱（為）", note: "yiqtol 3 陽單，前綴 יִ" },
        { target: "אֶשְׁמֹר", translation: "我將遵守", note: "前綴 אֶ＝我" },
        { target: "יְהִי אוֹר", translation: "要有光", note: "yəhî＝『願有』（祈使式，與未完成同源）" },
      ],
      practice: [
        { q: "未完成式靠什麼標人稱（相對完成式）？", answer: "靠前綴（如 יִ/תִּ/אֶ/נִ），完成式則靠字尾。" },
        { q: "『我將遵守』的前綴 אֶ 代表？", answer: "第一人稱單數『我』。" },
      ],
    },
  },
  {
    id: "hbo-waw-consecutive",
    en: "Waw-Consecutive Narrative",
    title: "waw 接續敘事",
    levels: ["初級"],
    summary: "敘事用 וַיִּקְטֹל（waw＋未完成）串連『接著他就…』。",
    keywords: ["waw consecutive", "敘事", "wayyiqtol", "narrative", "vav"],
    content: {
      explanation:
        "聖經敘事的骨幹是**敘述式 waw（wayyiqtol）**：在未完成式前加 וַ（waw＋後字母 dagesh），表過去連續動作『於是/接著他就…』。一連串 וַיֹּאמֶר…וַיַּעַשׂ… 把故事推進。\n看到 וַ＋帶前綴的動詞，多半就是在讀過去敘事，雖然動詞形式像未完成式，意義卻是過去。",
      examples: [
        { target: "וַיֹּאמֶר אֱלֹהִים", translation: "神說（於是神說）", note: "wayyōmer＝敘述式 waw" },
        { target: "וַיְהִי אוֹר", translation: "就有了光", note: "wayhî＝『就有』" },
        { target: "וַיַּרְא אֱלֹהִים כִּי טוֹב", translation: "神看著是好的", note: "wayyar＝接著神看" },
      ],
      practice: [
        { q: "敘述式 waw 形如 וַ＋動詞，意義是過去還是未來？", answer: "過去（敘事連續動作『於是…就』）。" },
        { q: "創世記反覆出現的 וַיֹּאמֶר 意思是？", answer: "（於是）神說。" },
      ],
    },
  },
];

export const COACH_GRAMMAR: Record<string, GrammarTopic[]> = { grc: GRC, la: LA, hbo: HBO };
export const CURATED_GRAMMAR_LANGS = new Set(Object.keys(COACH_GRAMMAR));

// 依量表級別過濾、帶入預嵌 content（lesson 端點直接回、不走 AI）
export function curatedGrammarSyllabus(language: string, level: string): any[] {
  const topics = COACH_GRAMMAR[language] || [];
  return topics
    .filter((t) => t.levels.includes(level))
    .map((t) => ({ id: t.id, title: t.title, summary: t.summary, content: t.content, done: false }));
}
