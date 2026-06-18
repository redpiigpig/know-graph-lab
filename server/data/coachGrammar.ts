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

// ── 德文 Hochdeutsch（A1 初學）────────────────────────────────────────────────
const DE: GrammarTopic[] = [
  {
    id: "de-articles-gender",
    en: "Three Genders & Articles",
    title: "三性與冠詞 der/die/das",
    levels: ["A1"],
    summary: "名詞分陽/陰/中，定冠詞 der/die/das、不定冠詞 ein/eine；名詞一律大寫。",
    keywords: ["gender", "性", "der die das", "冠詞", "ein", "名詞大寫"],
    content: {
      explanation:
        "德文名詞有三種性：陽性 der、陰性 die、中性 das（複數一律 die）。性別常無邏輯可循，**背名詞要連冠詞一起背**。\n不定冠詞（a/an）：陽/中 ein、陰 eine。\n所有名詞**字首一律大寫**（der Tag, die Kirche, das Buch）。",
      examples: [
        { target: "der Mann", translation: "（那個）男人", note: "陽性" },
        { target: "die Kirche", translation: "教會／教堂", note: "陰性" },
        { target: "das Buch", translation: "書", note: "中性" },
      ],
      practice: [
        { q: "「ein」與「eine」分別配哪種性？", answer: "ein＝陽性/中性；eine＝陰性。" },
        { q: "德文名詞書寫有什麼特別規則？", answer: "字首一律大寫。" },
      ],
    },
  },
  {
    id: "de-cases",
    en: "The Four Cases",
    title: "四格 Nominativ/Akkusativ/Dativ/Genitiv",
    levels: ["A1"],
    summary: "德文靠格標角色：主格、賓格（受詞）、與格（間受）、屬格（所有）。",
    keywords: ["case", "格", "Nominativ", "Akkusativ", "Dativ", "Genitiv"],
    content: {
      explanation:
        "德文用**格**標語法角色，冠詞會隨格變化：\n‧主格（Nom.）＝主詞：der Mann。\n‧賓格（Akk.）＝直接受詞：陽性 der→den（den Mann）。\n‧與格（Dat.）＝間接受詞/某些介系詞後：der→dem、die→der、das→dem。\n‧屬格（Gen.）＝所有（of）。\n陰/中性在主格與賓格同形，先掌握陽性的 der→den→dem 變化最有感。",
      examples: [
        { target: "Der Mann liest das Buch.", translation: "這男人讀這本書。", note: "der＝主格、das Buch＝賓格" },
        { target: "Ich gebe dem Kind ein Buch.", translation: "我給這孩子一本書。", note: "dem Kind＝與格（間接受詞）" },
        { target: "das Wort Gottes", translation: "神的話", note: "Gottes＝屬格（神的）" },
      ],
      practice: [
        { q: "陽性 der 當直接受詞（賓格）時變成？", answer: "den。" },
        { q: "間接受詞『給某人』用哪一格？", answer: "與格 Dativ（如 dem Kind）。" },
      ],
    },
  },
  {
    id: "de-present",
    en: "Present Tense (regular verbs)",
    title: "動詞現在式變位",
    levels: ["A1"],
    summary: "去 -en 取字幹＋人稱字尾：-e, -st, -t, -en, -t, -en。",
    keywords: ["verb", "動詞", "present", "現在式", "conjugation", "變位", "machen"],
    content: {
      explanation:
        "規則動詞取不定式去 -en 的字幹＋人稱字尾。以 machen（做）為例：ich mache／du machst／er(sie/es) macht／wir machen／ihr macht／sie/Sie machen。\n德文現在式可表現在與近未來。Sie（大寫）是禮貌的『您』。",
      examples: [
        { target: "Ich glaube an Gott.", translation: "我信神。", note: "glauben→glaube" },
        { target: "Sie betet jeden Tag.", translation: "她每天禱告。", note: "第三人稱單數 -t：betet" },
        { target: "Wir singen.", translation: "我們唱歌。", note: "wir 用 -en" },
      ],
      practice: [
        { q: "machen 的『du（你）』形式是？", answer: "machst。" },
        { q: "第三人稱單數（er/sie/es）的字尾通常是？", answer: "-t（如 macht、betet）。" },
      ],
    },
  },
  {
    id: "de-sein-haben",
    en: "sein & haben",
    title: "sein（是）與 haben（有）",
    levels: ["A1"],
    summary: "兩個最重要的不規則動詞，務必背熟。",
    keywords: ["sein", "haben", "是", "有", "to be", "to have"],
    content: {
      explanation:
        "sein（是）：ich bin, du bist, er ist, wir sind, ihr seid, sie sind。\nhaben（有）：ich habe, du hast, er hat, wir haben, ihr habt, sie haben。\n兩者極高頻，也是日後構成完成式的助動詞。",
      examples: [
        { target: "Gott ist Liebe.", translation: "神是愛。", note: "ist＝第三人稱單數" },
        { target: "Ich bin müde.", translation: "我累了。", note: "bin＝我是" },
        { target: "Wir haben Zeit.", translation: "我們有時間。", note: "haben＝有" },
      ],
      practice: [
        { q: "『他是』德文怎麼說？", answer: "er ist。" },
        { q: "haben 的『du（你）』形式？", answer: "hast。" },
      ],
    },
  },
  {
    id: "de-word-order",
    en: "Word Order (V2)",
    title: "語序：動詞置第二位",
    levels: ["A1"],
    summary: "主句中變位動詞恆在第二位；句首放別的成分，主詞就退到動詞後。",
    keywords: ["word order", "語序", "V2", "verb second", "Inversion"],
    content: {
      explanation:
        "德文主句的鐵則：**變位動詞在第二位（V2）**。\n若句首不是主詞（而是時間/地點等），主詞就移到動詞之後（倒裝）：Heute **bete** ich.（今天我禱告。）\nyes/no 問句把動詞提到句首：Glaubst du?（你信嗎？）",
      examples: [
        { target: "Ich gehe heute in die Kirche.", translation: "我今天去教堂。", note: "正常語序：主詞-動詞" },
        { target: "Heute gehe ich in die Kirche.", translation: "今天我去教堂。", note: "句首放 heute→動詞仍第二位、主詞後移" },
        { target: "Liest du die Bibel?", translation: "你讀聖經嗎？", note: "yes/no 問句動詞句首" },
      ],
      practice: [
        { q: "把『Ich lese heute.』改成以 heute 開頭。", answer: "Heute lese ich.（動詞仍第二位）。" },
        { q: "德文主句變位動詞固定在第幾位？", answer: "第二位（V2）。" },
      ],
    },
  },
  {
    id: "de-negation",
    en: "Negation: nicht & kein",
    title: "否定 nicht 與 kein",
    levels: ["A1"],
    summary: "nicht 否定動詞/形容詞/整句；kein 否定帶不定冠詞或無冠詞的名詞。",
    keywords: ["negation", "否定", "nicht", "kein"],
    content: {
      explanation:
        "**nicht**：否定動詞、形容詞或整句（通常放句尾或被否定詞前）：Ich glaube **nicht**.\n**kein**：否定名詞（取代 ein 或無冠詞複數）：Ich habe **kein** Buch.（我沒有書。）kein 像 ein 一樣隨性、格變化（kein/keine…）。",
      examples: [
        { target: "Das ist nicht wahr.", translation: "那不是真的。", note: "nicht 否定形容詞" },
        { target: "Ich habe keine Zeit.", translation: "我沒有時間。", note: "keine＋陰性名詞 Zeit" },
        { target: "Er betet nicht.", translation: "他不禱告。", note: "nicht 否定動詞，放句尾" },
      ],
      practice: [
        { q: "『我沒有錢（Geld，中性）』怎麼說？", answer: "Ich habe kein Geld." },
        { q: "否定一個動詞用 nicht 還是 kein？", answer: "nicht。" },
      ],
    },
  },
  {
    id: "de-pronouns-possessive",
    en: "Pronouns & Possessives",
    title: "人稱代名詞與所有冠詞",
    levels: ["A1"],
    summary: "ich/du/er…；所有用 mein/dein/sein…，字尾隨名詞性與格。",
    keywords: ["pronoun", "代名詞", "possessive", "mein", "dein", "所有"],
    content: {
      explanation:
        "人稱代名詞（主格）：ich, du, er/sie/es, wir, ihr, sie/Sie。\n所有冠詞像 ein 一樣變化：mein（我的）、dein（你的）、sein（他的）、ihr（她的/他們的）、unser（我們的）。字尾隨被擁有名詞的性與格：mein Vater（我父）／meine Mutter（我母）。",
      examples: [
        { target: "mein Gott", translation: "我的神", note: "陽性→mein" },
        { target: "meine Kirche", translation: "我的教會", note: "陰性→meine" },
        { target: "Sie ist meine Schwester.", translation: "她是我的姊妹。", note: "meine＋陰性" },
      ],
      practice: [
        { q: "『你的（陰性名詞）』所有冠詞是？", answer: "deine（如 deine Mutter）。" },
        { q: "所有冠詞字尾依什麼變化？", answer: "依被擁有名詞的性與格。" },
      ],
    },
  },
  {
    id: "de-modals",
    en: "Modal Verbs (intro)",
    title: "情態動詞入門",
    levels: ["A1"],
    summary: "können/müssen/wollen…＋句尾原形動詞（框架結構）。",
    keywords: ["modal", "情態動詞", "können", "müssen", "wollen", "Satzklammer"],
    content: {
      explanation:
        "情態動詞表能力/必須/意願：können（能）、müssen（必須）、wollen（想要）、dürfen（可以）、sollen（應該）、mögen（喜歡）。\n用法：情態動詞變位放第二位，**主要動詞用原形放句尾**（句框 Satzklammer）：Ich **muss** heute **beten**.",
      examples: [
        { target: "Ich kann Deutsch lesen.", translation: "我能讀德文。", note: "kann（第二位）… lesen（句尾原形）" },
        { target: "Wir müssen gehen.", translation: "我們必須走。", note: "müssen＋gehen" },
        { target: "Sie will beten.", translation: "她想禱告。", note: "wollen→will" },
      ],
      practice: [
        { q: "情態動詞句中，主要動詞放哪裡、用什麼形式？", answer: "放句尾、用原形（不定式）。" },
        { q: "können 的『ich』形式？", answer: "kann。" },
      ],
    },
  },
];

// ── 法文 Parisien（A1 初學）──────────────────────────────────────────────────
const FR: GrammarTopic[] = [
  {
    id: "fr-gender-articles",
    en: "Gender & Articles",
    title: "陰陽性與冠詞 le/la、un/une",
    levels: ["A1"],
    summary: "名詞分陰陽性；定冠詞 le/la/les、不定冠詞 un/une/des。",
    keywords: ["gender", "性", "le la les", "un une", "冠詞", "article"],
    content: {
      explanation:
        "法文名詞分陽性、陰性。定冠詞：陽 le、陰 la、複數 les（母音前 le/la 縮為 l'）。\n不定冠詞：陽 un、陰 une、複數 des。\n**背名詞要連冠詞一起背**（le livre, la table）。",
      examples: [
        { target: "le Dieu", translation: "神", note: "陽性→le（一般說 Dieu 不加冠詞）" },
        { target: "la prière", translation: "禱告", note: "陰性→la" },
        { target: "l'église", translation: "教堂／教會", note: "母音前縮為 l'" },
      ],
      practice: [
        { q: "陰性名詞用哪個不定冠詞？", answer: "une。" },
        { q: "le/la 在母音開頭的字前會怎樣？", answer: "縮寫成 l'（如 l'église）。" },
      ],
    },
  },
  {
    id: "fr-etre-avoir",
    en: "être & avoir",
    title: "être（是）與 avoir（有）",
    levels: ["A1"],
    summary: "兩個最重要的不規則動詞，也是複合過去式的助動詞。",
    keywords: ["être", "avoir", "是", "有", "to be", "to have"],
    content: {
      explanation:
        "être（是）：je suis, tu es, il/elle est, nous sommes, vous êtes, ils/elles sont。\navoir（有）：j'ai, tu as, il a, nous avons, vous avez, ils ont。\n兩者極高頻，也用來構成複合過去式（passé composé）。",
      examples: [
        { target: "Dieu est amour.", translation: "神是愛。", note: "est＝第三人稱單數" },
        { target: "Je suis prêt.", translation: "我準備好了。", note: "suis＝我是" },
        { target: "Nous avons la foi.", translation: "我們有信心。", note: "avons＝我們有" },
      ],
      practice: [
        { q: "『他是』法文怎麼說？", answer: "il est。" },
        { q: "avoir 的『je（我）』形式（含縮寫）？", answer: "j'ai。" },
      ],
    },
  },
  {
    id: "fr-er-verbs",
    en: "-er Verbs (Present)",
    title: "第一組 -er 動詞現在式",
    levels: ["A1"],
    summary: "最大宗規則動詞：去 -er＋字尾 -e, -es, -e, -ons, -ez, -ent。",
    keywords: ["verb", "動詞", "-er", "present", "現在式", "parler"],
    content: {
      explanation:
        "-er 結尾的規則動詞（如 parler 說）最多。去 -er 取字幹＋字尾：je parle, tu parles, il parle, nous parlons, vous parlez, ils parlent。\n注意 -e/-es/-ent 結尾**都不發音**，三者聽起來一樣。",
      examples: [
        { target: "Je prie chaque jour.", translation: "我每天禱告。", note: "prier→prie" },
        { target: "Nous chantons.", translation: "我們唱歌。", note: "nous→-ons" },
        { target: "Ils adorent Dieu.", translation: "他們敬拜神。", note: "ils→-ent（不發音）" },
      ],
      practice: [
        { q: "parler 的『nous（我們）』形式？", answer: "parlons。" },
        { q: "-e、-es、-ent 三個字尾發音上有何特點？", answer: "都不發音，聽起來相同。" },
      ],
    },
  },
  {
    id: "fr-negation",
    en: "Negation: ne … pas",
    title: "否定 ne … pas",
    levels: ["A1"],
    summary: "把動詞夾在 ne 與 pas 之間；口語常省略 ne。",
    keywords: ["negation", "否定", "ne pas"],
    content: {
      explanation:
        "法文否定用**雙詞框** ne … pas，把變位動詞夾在中間：Je **ne** crois **pas**.（我不信。）ne 在母音前縮為 n'（Je n'ai pas）。\n口語裡 ne 常被省略（Je crois pas）。",
      examples: [
        { target: "Ce n'est pas vrai.", translation: "這不是真的。", note: "n'est pas（est 母音前 ne→n'）" },
        { target: "Je ne comprends pas.", translation: "我不懂。", note: "ne…pas 夾動詞" },
        { target: "Il ne prie pas.", translation: "他不禱告。", note: "prie 夾在 ne…pas 中" },
      ],
      practice: [
        { q: "把『Je parle.』改成否定。", answer: "Je ne parle pas." },
        { q: "ne 在母音前要怎麼變？", answer: "縮為 n'（如 n'est pas）。" },
      ],
    },
  },
  {
    id: "fr-adjectives",
    en: "Adjective Agreement & Position",
    title: "形容詞陰陽性與位置",
    levels: ["A1"],
    summary: "形容詞隨名詞陰陽/單複數變化；多數放名詞後。",
    keywords: ["adjective", "形容詞", "agreement", "一致", "position"],
    content: {
      explanation:
        "形容詞要與名詞在性、數一致：陰性常加 -e、複數加 -s（saint→sainte→saints→saintes）。\n**多數形容詞放在名詞之後**（l'esprit saint）；少數常用短詞（grand, petit, bon, beau…）放前面。",
      examples: [
        { target: "le Saint-Esprit", translation: "聖靈", note: "saint 在此固定搭配" },
        { target: "la vie éternelle", translation: "永生", note: "éternelle＝陰性一致，放名詞後" },
        { target: "une bonne nouvelle", translation: "好消息（福音）", note: "bonne 短詞放前、陰性化" },
      ],
      practice: [
        { q: "形容詞配陰性名詞通常加什麼字尾？", answer: "-e（如 saint→sainte）。" },
        { q: "法文形容詞一般放名詞前還是後？", answer: "多數放後（少數常用短詞放前）。" },
      ],
    },
  },
  {
    id: "fr-questions",
    en: "Asking Questions",
    title: "疑問句三種方式",
    levels: ["A1"],
    summary: "語調上揚／est-ce que 開頭／主謂倒裝。",
    keywords: ["question", "疑問句", "est-ce que", "inversion", "倒裝"],
    content: {
      explanation:
        "法文問句三法：\n①口語把陳述句語調上揚：Tu crois?\n②句首加 **Est-ce que**：Est-ce que tu crois?\n③主謂**倒裝**（較正式）：Crois-tu?\n疑問詞（qui 誰、que 什麼、où 哪裡、quand 何時、pourquoi 為何）放句首。",
      examples: [
        { target: "Est-ce que vous priez?", translation: "你們禱告嗎？", note: "est-ce que 中性問法" },
        { target: "Où est l'église?", translation: "教堂在哪裡？", note: "où＝哪裡" },
        { target: "Crois-tu en Dieu?", translation: "你信神嗎？", note: "倒裝 crois-tu" },
      ],
      practice: [
        { q: "用 est-ce que 問『你說法文嗎』。", answer: "Est-ce que tu parles français?" },
        { q: "『哪裡』的疑問詞是？", answer: "où。" },
      ],
    },
  },
  {
    id: "fr-possessive",
    en: "Possessive Adjectives",
    title: "所有形容詞 mon/ma/mes",
    levels: ["A1"],
    summary: "依被擁有名詞的性與數：mon/ma/mes、ton/ta/tes、son/sa/ses…",
    keywords: ["possessive", "所有形容詞", "mon", "ma", "mes"],
    content: {
      explanation:
        "所有形容詞隨**被擁有的名詞**性數變化（不是隨擁有者）：\n我的＝mon（陽）/ma（陰）/mes（複）；你的＝ton/ta/tes；他/她的＝son/sa/ses。\n注意：陰性名詞若以母音開頭，用 mon/ton/son（發音順）：mon âme（我的靈魂）。",
      examples: [
        { target: "mon père", translation: "我的父親", note: "陽性→mon" },
        { target: "ma mère", translation: "我的母親", note: "陰性→ma" },
        { target: "mon âme", translation: "我的靈魂", note: "陰性但母音開頭→用 mon" },
      ],
      practice: [
        { q: "『我的（陰性子音開頭名詞）』用哪個？", answer: "ma（如 ma mère）。" },
        { q: "son/sa/ses 是隨擁有者還是被擁有名詞變化？", answer: "隨被擁有的名詞（性數）。" },
      ],
    },
  },
  {
    id: "fr-prepositions-contraction",
    en: "à / de & Contractions",
    title: "介系詞 à/de 與縮合",
    levels: ["A1"],
    summary: "à＋le=au、à＋les=aux；de＋le=du、de＋les=des。",
    keywords: ["preposition", "介系詞", "à", "de", "au", "du", "縮合", "contraction"],
    content: {
      explanation:
        "à（到/在）與 de（的/從）碰到定冠詞 le/les 必須**縮合**：\nà＋le→au、à＋les→aux；de＋le→du、de＋les→des。（à la、de la 不縮。）\nde 也表所有：la parole de Dieu（神的話）。",
      examples: [
        { target: "Je vais à l'église.", translation: "我去教堂。", note: "à＋l'（母音前不縮）" },
        { target: "la maison de Dieu", translation: "神的家", note: "de＝的" },
        { target: "Il parle au prêtre.", translation: "他對神父說話。", note: "à＋le→au" },
      ],
      practice: [
        { q: "à＋les 縮合成？", answer: "aux。" },
        { q: "de＋le 縮合成？", answer: "du。" },
      ],
    },
  },
];

// ── 日文 關東標準語（N5 初學）────────────────────────────────────────────────
const JA: GrammarTopic[] = [
  {
    id: "ja-desu",
    en: "～は～です Sentence",
    title: "基本句型 〜は〜です",
    levels: ["N5"],
    summary: "「A は B です」＝A 是 B；は 是主題助詞（讀 wa）。",
    keywords: ["です", "は", "wa", "基本句型", "topic"],
    content: {
      explanation:
        "最基本句型：**〔主題〕は〔內容〕です**。は 當助詞時讀作「wa」。です 是禮貌的斷定（是）。\n否定：〜では ありません（口語 〜じゃ ありません）。疑問：句尾加 か。",
      examples: [
        { target: "わたしは 学生です。", translation: "我是學生。", note: "は 讀 wa；です＝是" },
        { target: "これは 神社です。", translation: "這是神社。", note: "これ＝這個" },
        { target: "学生では ありません。", translation: "（我）不是學生。", note: "否定 では ありません" },
      ],
      practice: [
        { q: "助詞 は 當主題標記時怎麼讀？", answer: "讀作 wa。" },
        { q: "『〜です』的否定形是？", answer: "〜では ありません（口語 じゃ ありません）。" },
      ],
    },
  },
  {
    id: "ja-particles",
    en: "Core Particles",
    title: "基本助詞 は/が/を/に/へ/で",
    levels: ["N5"],
    summary: "は主題、が主詞、を受詞、に時間/歸著、へ方向、で場所/手段。",
    keywords: ["particle", "助詞", "は", "が", "を", "に", "で", "へ"],
    content: {
      explanation:
        "助詞接在詞後標角色：\n‧は＝主題（wa）‧が＝主詞 ‧を＝直接受詞（o）\n‧に＝時間點/到達點/存在處 ‧へ＝方向（e）‧で＝動作場所或手段。\n例：神社で お参りを します。（在神社參拜。）",
      examples: [
        { target: "本を 読みます。", translation: "讀書。", note: "を＝受詞標記（讀 o）" },
        { target: "七時に 起きます。", translation: "七點起床。", note: "に＝時間點" },
        { target: "神社で お祭りが あります。", translation: "在神社有祭典。", note: "で＝場所、が＝主詞" },
      ],
      practice: [
        { q: "直接受詞用哪個助詞？怎麼讀？", answer: "を，讀作 o。" },
        { q: "表示動作發生的『場所』用哪個助詞？", answer: "で（如 神社で）。" },
      ],
    },
  },
  {
    id: "ja-verb-groups",
    en: "Verb Groups & ます-form",
    title: "動詞三類與 ます形",
    levels: ["N5"],
    summary: "動詞分三類；禮貌體用 ます（否定 ません、過去 ました）。",
    keywords: ["verb", "動詞", "ます", "groups", "三類", "ru-verb", "u-verb"],
    content: {
      explanation:
        "日語動詞分三類：①五段（u 動詞，如 読む）②一段（ru 動詞，如 食べる）③不規則（する、来る）。\n禮貌體 **ます形**：食べる→食べます、読む→読みます、する→します。否定 〜ません、過去 〜ました、過去否定 〜ませんでした。",
      examples: [
        { target: "お祈りを します。", translation: "（我）禱告／祈禱。", note: "する→します" },
        { target: "毎日 聖書を 読みます。", translation: "每天讀聖經。", note: "読む→読みます" },
        { target: "肉を 食べません。", translation: "（我）不吃肉。", note: "食べる→食べません（否定）" },
      ],
      practice: [
        { q: "『食べる』的禮貌否定形？", answer: "食べません。" },
        { q: "する 的 ます形？", answer: "します。" },
      ],
    },
  },
  {
    id: "ja-adjectives",
    en: "い-adjectives & な-adjectives",
    title: "形容詞 い形與 な形",
    levels: ["N5"],
    summary: "い形容詞直接接名詞；な形容詞接名詞要加 な。",
    keywords: ["adjective", "形容詞", "い形", "な形", "i-adjective", "na-adjective"],
    content: {
      explanation:
        "兩類形容詞：\n‧**い形容詞**（以い結尾，如 高い、楽しい）：直接修飾名詞（高い山），否定 〜くないです。\n‧**な形容詞**（如 静か、有名）：修飾名詞要加 な（静かな 神社），否定 〜では ありません。\n過去：い形 〜かったです；な形 〜でした。",
      examples: [
        { target: "高い 山。", translation: "高的山。", note: "い形容詞直接接名詞" },
        { target: "静かな 教会。", translation: "安靜的教會。", note: "な形容詞＋な" },
        { target: "この 話は おもしろいです。", translation: "這個故事很有趣。", note: "い形容詞當述語" },
      ],
      practice: [
        { q: "な形容詞修飾名詞時要加什麼？", answer: "加 な（如 静かな 神社）。" },
        { q: "い形容詞『楽しい』的禮貌否定？", answer: "楽しくないです。" },
      ],
    },
  },
  {
    id: "ja-demonstratives",
    en: "これ/それ/あれ & か",
    title: "指示詞 これ/それ/あれ 與疑問 か",
    levels: ["N5"],
    summary: "こ近/そ中/あ遠；句尾加 か變疑問。",
    keywords: ["これ", "それ", "あれ", "ko-so-a", "指示詞", "か", "疑問"],
    content: {
      explanation:
        "指示體系依距離：これ（這，近說話者）／それ（那，近聽者）／あれ（那，雙方都遠）。修飾名詞用 この/その/あの＋名詞。\n疑問句把 **か** 加在句尾（不必倒裝）：これは 何ですか。（這是什麼？）",
      examples: [
        { target: "これは 何ですか。", translation: "這是什麼？", note: "か＝疑問" },
        { target: "その 本を ください。", translation: "請給我那本書。", note: "その＋名詞" },
        { target: "あれは 神社です。", translation: "那（遠處）是神社。", note: "あれ＝遠指" },
      ],
      practice: [
        { q: "把『これは 本です』改成疑問句。", answer: "これは 本ですか。" },
        { q: "離說話者近的『這個』指示詞是？", answer: "これ（修飾名詞用 この）。" },
      ],
    },
  },
  {
    id: "ja-te-form",
    en: "て-form (intro)",
    title: "て形入門",
    levels: ["N5", "N4"],
    summary: "連接動作、請求（〜てください）、進行（〜ています）的萬用形。",
    keywords: ["て形", "te-form", "てください", "ています"],
    content: {
      explanation:
        "て形是日語樞紐形：連接句子（〜て、〜）、請求（〜て ください）、進行/狀態（〜て います）。\n變化依類別：食べる→食べて；読む→読んで；行く→行って；する→して；来る→来て。",
      examples: [
        { target: "聖書を 読んで ください。", translation: "請讀聖經。", note: "読む→読んで＋ください＝請求" },
        { target: "今 お祈りを して います。", translation: "現在正在禱告。", note: "して います＝進行" },
        { target: "教会へ 行って、祈ります。", translation: "去教會，然後禱告。", note: "て形連接動作" },
      ],
      practice: [
        { q: "『請吃』日文怎麼說？", answer: "食べて ください。" },
        { q: "『〜て います』表示什麼？", answer: "正在進行或持續的狀態。" },
      ],
    },
  },
  {
    id: "ja-past",
    en: "Past Tense",
    title: "過去式 〜ました/〜でした",
    levels: ["N5"],
    summary: "動詞 〜ました（否定 〜ませんでした）；名詞/な形 〜でした；い形 〜かったです。",
    keywords: ["past", "過去式", "ました", "でした", "かった"],
    content: {
      explanation:
        "禮貌體過去：\n‧動詞：〜ます→〜ました（否定 〜ませんでした）。\n‧名詞・な形容詞：です→でした（否定 では ありませんでした）。\n‧い形容詞：〜いです→〜かったです（おいしい→おいしかったです）。",
      examples: [
        { target: "お祭りに 行きました。", translation: "（我）去了祭典。", note: "行きます→行きました" },
        { target: "それは 神社でした。", translation: "那（曾）是神社。", note: "です→でした" },
        { target: "楽しかったです。", translation: "（那時）很開心。", note: "い形過去 〜かったです" },
      ],
      practice: [
        { q: "『読みます』的過去否定？", answer: "読みませんでした。" },
        { q: "い形容詞『おいしい』的過去式？", answer: "おいしかったです。" },
      ],
    },
  },
  {
    id: "ja-more-particles",
    en: "と / も / から / まで & Counters",
    title: "助詞 と/も/から/まで 與數量詞",
    levels: ["N5", "N4"],
    summary: "と和/も也/から從/まで到；數量詞依物品種類不同。",
    keywords: ["と", "も", "から", "まで", "助詞", "counter", "數量詞"],
    content: {
      explanation:
        "更多助詞：と＝和（A と B）／も＝也（私も）／から＝從（起點/原因）／まで＝到（終點）。\n數量詞依物品分類（人＝〜人、書本＝〜冊、細長物＝〜本…），常接動詞前：本を 三冊 読みます。",
      examples: [
        { target: "聖書と 賛美歌。", translation: "聖經和讚美詩。", note: "と＝和" },
        { target: "九時から 始まります。", translation: "九點開始。", note: "から＝從（起點）" },
        { target: "私も 行きます。", translation: "我也去。", note: "も＝也" },
      ],
      practice: [
        { q: "『從…到…』用哪兩個助詞？", answer: "から…まで。" },
        { q: "『我也』日文怎麼說？", answer: "私も。" },
      ],
    },
  },
];

export const COACH_GRAMMAR: Record<string, GrammarTopic[]> = { grc: GRC, la: LA, hbo: HBO, de: DE, fr: FR, ja: JA };
export const CURATED_GRAMMAR_LANGS = new Set(Object.keys(COACH_GRAMMAR));

// 依量表級別過濾、帶入預嵌 content（lesson 端點直接回、不走 AI）
export function curatedGrammarSyllabus(language: string, level: string): any[] {
  const topics = COACH_GRAMMAR[language] || [];
  return topics
    .filter((t) => t.levels.includes(level))
    .map((t) => ({ id: t.id, title: t.title, summary: t.summary, content: t.content, done: false }));
}
