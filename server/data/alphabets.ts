// ============================================================================
// 各語言「字母教學 + 字母測驗」策展資料（英文除外，使用者已熟英文字母）。
// 純策展、無 AI：教學頁顯示字母卡（字形／名稱／讀音／例字），測驗頁從同一份資料
// 出選擇題（看字形選讀音 / 看讀音選字形）。新增/修字母就改這個檔。
//
// 每語言一份 AlphabetSpec，內含若干 group（如日文：平假名／濁音／拗音／片假名；
// 希伯來：子音／字尾形／母音點）。字形 `char` 為主要展示字、`name` 字母名、
// `sound` 繁中讀音提示、`example`/`gloss` 例字與繁中義。`tts` 可覆寫朗讀文字
// （預設念 example，沒有就念 char）。
// 對應頁 `/coach/[lang]/alphabet`、端點 `/api/lang/alphabet`。
// ============================================================================

export interface AlphaLetter {
  char: string;       // 主要展示字形（測驗題面）
  upper?: string;     // 另外展示的大寫（希臘／拉丁）
  name: string;       // 字母名稱
  sound: string;      // 繁中讀音提示（測驗答案之一）
  example?: string;   // 該語言例字
  gloss?: string;     // 例字繁中義
  tts?: string;       // 覆寫朗讀文字（預設 example || char）
}
export interface AlphaGroup {
  key: string;
  label: string;
  note?: string;
  letters: AlphaLetter[];
}
export interface AlphabetSpec {
  language: string;
  title: string;
  intro: string;
  rtl?: boolean;      // 希伯來文由右至左
  groups: AlphaGroup[];
}

// ── 德文 de ────────────────────────────────────────────────────────────────
const de: AlphabetSpec = {
  language: "de",
  title: "德文字母 · Das Alphabet",
  intro: "德文用 26 個拉丁字母，外加 3 個變音字母 Ä Ö Ü 與 ß（Eszett）。重點在「字母名稱怎麼念」與變音字母的發音。",
  groups: [
    {
      key: "base", label: "26 個基本字母",
      letters: [
        { char: "a", upper: "A", name: "A", sound: "阿（ah）", example: "Apfel", gloss: "蘋果" },
        { char: "b", upper: "B", name: "Be", sound: "貝（beh）", example: "Buch", gloss: "書" },
        { char: "c", upper: "C", name: "Ce", sound: "切（tseh）", example: "Computer", gloss: "電腦" },
        { char: "d", upper: "D", name: "De", sound: "德（deh）", example: "danke", gloss: "謝謝" },
        { char: "e", upper: "E", name: "E", sound: "耶（eh）", example: "Engel", gloss: "天使" },
        { char: "f", upper: "F", name: "Ef", sound: "艾夫（eff）", example: "Frau", gloss: "女士" },
        { char: "g", upper: "G", name: "Ge", sound: "格（geh）", example: "gut", gloss: "好" },
        { char: "h", upper: "H", name: "Ha", sound: "哈（hah）", example: "Haus", gloss: "房子" },
        { char: "i", upper: "I", name: "I", sound: "伊（ih）", example: "Insel", gloss: "島" },
        { char: "j", upper: "J", name: "Jot", sound: "約特（yot，子音同 y）", example: "ja", gloss: "是" },
        { char: "k", upper: "K", name: "Ka", sound: "卡（kah）", example: "Kirche", gloss: "教堂" },
        { char: "l", upper: "L", name: "El", sound: "艾爾（ell）", example: "Liebe", gloss: "愛" },
        { char: "m", upper: "M", name: "Em", sound: "艾姆（emm）", example: "Mutter", gloss: "母親" },
        { char: "n", upper: "N", name: "En", sound: "艾恩（enn）", example: "nein", gloss: "不" },
        { char: "o", upper: "O", name: "O", sound: "喔（oh）", example: "Obst", gloss: "水果" },
        { char: "p", upper: "P", name: "Pe", sound: "沛（peh）", example: "Papier", gloss: "紙" },
        { char: "q", upper: "Q", name: "Ku", sound: "庫（kuh，恆接 u）", example: "Quelle", gloss: "泉源" },
        { char: "r", upper: "R", name: "Er", sound: "艾爾（err，小舌音）", example: "rot", gloss: "紅" },
        { char: "s", upper: "S", name: "Es", sound: "艾斯（ess）", example: "Sonne", gloss: "太陽" },
        { char: "t", upper: "T", name: "Te", sound: "特（teh）", example: "Tag", gloss: "日子" },
        { char: "u", upper: "U", name: "U", sound: "烏（uh）", example: "und", gloss: "和" },
        { char: "v", upper: "V", name: "Vau", sound: "法烏（fau，多念 f）", example: "Vater", gloss: "父親" },
        { char: "w", upper: "W", name: "We", sound: "維（veh，發 v）", example: "Wasser", gloss: "水" },
        { char: "x", upper: "X", name: "Ix", sound: "伊克斯（iks）", example: "Hexe", gloss: "女巫" },
        { char: "y", upper: "Y", name: "Ypsilon", sound: "宇普希龍（üpsilon）", example: "Symbol", gloss: "象徵" },
        { char: "z", upper: "Z", name: "Zett", sound: "賜特（tsett，發 ts）", example: "Zeit", gloss: "時間" },
      ],
    },
    {
      key: "umlaut", label: "變音字母與 ß",
      note: "Ä Ö Ü 是 a/o/u 的變音；ß 念清音 s，只出現在長母音/雙母音之後。",
      letters: [
        { char: "ä", upper: "Ä", name: "A-Umlaut", sound: "近開口的 e（如 fair）", example: "Äpfel", gloss: "蘋果（複數）" },
        { char: "ö", upper: "Ö", name: "O-Umlaut", sound: "圓唇的 e", example: "schön", gloss: "美麗" },
        { char: "ü", upper: "Ü", name: "U-Umlaut", sound: "圓唇的 i", example: "über", gloss: "在…之上" },
        { char: "ß", name: "Eszett / scharfes S", sound: "清音 s（不振動）", example: "Straße", gloss: "街道" },
      ],
    },
  ],
};

// ── 法文 fr ────────────────────────────────────────────────────────────────
const fr: AlphabetSpec = {
  language: "fr",
  title: "法文字母 · L'alphabet",
  intro: "法文用 26 個拉丁字母，外加重音符號（accent）與連字。重點在字母名稱與各重音符號改變的發音。",
  groups: [
    {
      key: "base", label: "26 個基本字母",
      letters: [
        { char: "a", upper: "A", name: "a", sound: "阿（a）", example: "ami", gloss: "朋友" },
        { char: "b", upper: "B", name: "bé", sound: "貝（bé）", example: "bon", gloss: "好" },
        { char: "c", upper: "C", name: "cé", sound: "塞（cé）", example: "ciel", gloss: "天空" },
        { char: "d", upper: "D", name: "dé", sound: "得（dé）", example: "dieu", gloss: "神" },
        { char: "e", upper: "E", name: "e", sound: "(ə) 輕音的呃", example: "église", gloss: "教堂" },
        { char: "f", upper: "F", name: "effe", sound: "艾夫（effe）", example: "foi", gloss: "信仰" },
        { char: "g", upper: "G", name: "gé", sound: "瑞（gé，軟音同 j）", example: "grâce", gloss: "恩典" },
        { char: "h", upper: "H", name: "ache", sound: "啞許（ache，不發音）", example: "homme", gloss: "人" },
        { char: "i", upper: "I", name: "i", sound: "伊（i）", example: "île", gloss: "島" },
        { char: "j", upper: "J", name: "ji", sound: "日（ji）", example: "jour", gloss: "日子" },
        { char: "k", upper: "K", name: "ka", sound: "卡（ka）", example: "kilo", gloss: "公斤" },
        { char: "l", upper: "L", name: "elle", sound: "艾爾（elle）", example: "livre", gloss: "書" },
        { char: "m", upper: "M", name: "emme", sound: "艾姆（emme）", example: "mère", gloss: "母親" },
        { char: "n", upper: "N", name: "enne", sound: "艾恩（enne）", example: "non", gloss: "不" },
        { char: "o", upper: "O", name: "o", sound: "喔（o）", example: "or", gloss: "金" },
        { char: "p", upper: "P", name: "pé", sound: "沛（pé）", example: "père", gloss: "父親" },
        { char: "q", upper: "Q", name: "ku", sound: "庫（ku）", example: "qui", gloss: "誰" },
        { char: "r", upper: "R", name: "erre", sound: "艾爾（erre，小舌音）", example: "roi", gloss: "王" },
        { char: "s", upper: "S", name: "esse", sound: "艾斯（esse）", example: "saint", gloss: "聖" },
        { char: "t", upper: "T", name: "té", sound: "特（té）", example: "temps", gloss: "時間" },
        { char: "u", upper: "U", name: "u", sound: "（圓唇的 i）", example: "un", gloss: "一" },
        { char: "v", upper: "V", name: "vé", sound: "維（vé）", example: "vie", gloss: "生命" },
        { char: "w", upper: "W", name: "double vé", sound: "杜布勒維（double vé）", example: "wagon", gloss: "車廂" },
        { char: "x", upper: "X", name: "iks", sound: "伊克斯（iks）", example: "voix", gloss: "聲音" },
        { char: "y", upper: "Y", name: "i grec", sound: "伊格瑞克（i grec）", example: "yeux", gloss: "眼睛" },
        { char: "z", upper: "Z", name: "zède", sound: "瑞德（zède）", example: "zèle", gloss: "熱忱" },
      ],
    },
    {
      key: "accent", label: "重音符號與連字",
      note: "重音符號會改變字母發音或區分同音字；ç 軟化 c；œ/æ 為連字。",
      letters: [
        { char: "é", name: "e accent aigu", sound: "閉口的 e（如 day）", example: "été", gloss: "夏天" },
        { char: "è", name: "e accent grave", sound: "開口的 e（如 fair）", example: "père", gloss: "父親" },
        { char: "ê", name: "e accent circonflexe", sound: "拉長的開口 e", example: "être", gloss: "是／存在" },
        { char: "ë", name: "e tréma", sound: "分音：與前母音分開念", example: "Noël", gloss: "聖誕" },
        { char: "à", name: "a accent grave", sound: "阿（區分 a/à）", example: "là", gloss: "那裡" },
        { char: "â", name: "a accent circonflexe", sound: "拉長的 a", example: "âme", gloss: "靈魂" },
        { char: "ç", name: "c cédille", sound: "軟音 s（在 a/o/u 前）", example: "ça", gloss: "這個" },
        { char: "î", name: "i circonflexe", sound: "拉長的 i", example: "dîner", gloss: "晚餐" },
        { char: "ï", name: "i tréma", sound: "分音：單獨念 i", example: "maïs", gloss: "玉米" },
        { char: "ô", name: "o circonflexe", sound: "閉口的長 o", example: "hôtel", gloss: "旅館" },
        { char: "û", name: "u circonflexe", sound: "拉長的 u", example: "sûr", gloss: "確定的" },
        { char: "ù", name: "u accent grave", sound: "u（區分 ou/où）", example: "où", gloss: "哪裡" },
        { char: "œ", name: "e dans l'o", sound: "連字 œ（如 cœur）", example: "cœur", gloss: "心" },
        { char: "æ", name: "e dans l'a", sound: "連字 æ（拉丁外來語）", example: "et cætera", gloss: "等等" },
      ],
    },
  ],
};

// ── 日文 ja ────────────────────────────────────────────────────────────────
const ja: AlphabetSpec = {
  language: "ja",
  title: "日文假名 · ひらがな・カタカナ",
  intro: "日文有兩套音節文字：平假名（和語/助詞）與片假名（外來語）。先熟清音五十音，再加濁音、半濁音、拗音。讀音以羅馬字標示。",
  groups: [
    {
      key: "hira", label: "平假名 · 清音（五十音）",
      letters: [
        { char: "あ", name: "あ", sound: "a" }, { char: "い", name: "い", sound: "i" }, { char: "う", name: "う", sound: "u" }, { char: "え", name: "え", sound: "e" }, { char: "お", name: "お", sound: "o" },
        { char: "か", name: "か", sound: "ka" }, { char: "き", name: "き", sound: "ki" }, { char: "く", name: "く", sound: "ku" }, { char: "け", name: "け", sound: "ke" }, { char: "こ", name: "こ", sound: "ko" },
        { char: "さ", name: "さ", sound: "sa" }, { char: "し", name: "し", sound: "shi" }, { char: "す", name: "す", sound: "su" }, { char: "せ", name: "せ", sound: "se" }, { char: "そ", name: "そ", sound: "so" },
        { char: "た", name: "た", sound: "ta" }, { char: "ち", name: "ち", sound: "chi" }, { char: "つ", name: "つ", sound: "tsu" }, { char: "て", name: "て", sound: "te" }, { char: "と", name: "と", sound: "to" },
        { char: "な", name: "な", sound: "na" }, { char: "に", name: "に", sound: "ni" }, { char: "ぬ", name: "ぬ", sound: "nu" }, { char: "ね", name: "ね", sound: "ne" }, { char: "の", name: "の", sound: "no" },
        { char: "は", name: "は", sound: "ha" }, { char: "ひ", name: "ひ", sound: "hi" }, { char: "ふ", name: "ふ", sound: "fu" }, { char: "へ", name: "へ", sound: "he" }, { char: "ほ", name: "ほ", sound: "ho" },
        { char: "ま", name: "ま", sound: "ma" }, { char: "み", name: "み", sound: "mi" }, { char: "む", name: "む", sound: "mu" }, { char: "め", name: "め", sound: "me" }, { char: "も", name: "も", sound: "mo" },
        { char: "や", name: "や", sound: "ya" }, { char: "ゆ", name: "ゆ", sound: "yu" }, { char: "よ", name: "よ", sound: "yo" },
        { char: "ら", name: "ら", sound: "ra" }, { char: "り", name: "り", sound: "ri" }, { char: "る", name: "る", sound: "ru" }, { char: "れ", name: "れ", sound: "re" }, { char: "ろ", name: "ろ", sound: "ro" },
        { char: "わ", name: "わ", sound: "wa" }, { char: "を", name: "を", sound: "wo" }, { char: "ん", name: "ん", sound: "n" },
      ],
    },
    {
      key: "hira_daku", label: "平假名 · 濁音／半濁音",
      letters: [
        { char: "が", name: "が", sound: "ga" }, { char: "ぎ", name: "ぎ", sound: "gi" }, { char: "ぐ", name: "ぐ", sound: "gu" }, { char: "げ", name: "げ", sound: "ge" }, { char: "ご", name: "ご", sound: "go" },
        { char: "ざ", name: "ざ", sound: "za" }, { char: "じ", name: "じ", sound: "ji" }, { char: "ず", name: "ず", sound: "zu" }, { char: "ぜ", name: "ぜ", sound: "ze" }, { char: "ぞ", name: "ぞ", sound: "zo" },
        { char: "だ", name: "だ", sound: "da" }, { char: "ぢ", name: "ぢ", sound: "ji" }, { char: "づ", name: "づ", sound: "zu" }, { char: "で", name: "で", sound: "de" }, { char: "ど", name: "ど", sound: "do" },
        { char: "ば", name: "ば", sound: "ba" }, { char: "び", name: "び", sound: "bi" }, { char: "ぶ", name: "ぶ", sound: "bu" }, { char: "べ", name: "べ", sound: "be" }, { char: "ぼ", name: "ぼ", sound: "bo" },
        { char: "ぱ", name: "ぱ", sound: "pa" }, { char: "ぴ", name: "ぴ", sound: "pi" }, { char: "ぷ", name: "ぷ", sound: "pu" }, { char: "ぺ", name: "ぺ", sound: "pe" }, { char: "ぽ", name: "ぽ", sound: "po" },
      ],
    },
    {
      key: "hira_yoon", label: "平假名 · 拗音",
      letters: [
        { char: "きゃ", name: "きゃ", sound: "kya" }, { char: "きゅ", name: "きゅ", sound: "kyu" }, { char: "きょ", name: "きょ", sound: "kyo" },
        { char: "しゃ", name: "しゃ", sound: "sha" }, { char: "しゅ", name: "しゅ", sound: "shu" }, { char: "しょ", name: "しょ", sound: "sho" },
        { char: "ちゃ", name: "ちゃ", sound: "cha" }, { char: "ちゅ", name: "ちゅ", sound: "chu" }, { char: "ちょ", name: "ちょ", sound: "cho" },
        { char: "にゃ", name: "にゃ", sound: "nya" }, { char: "にゅ", name: "にゅ", sound: "nyu" }, { char: "にょ", name: "にょ", sound: "nyo" },
        { char: "ひゃ", name: "ひゃ", sound: "hya" }, { char: "ひゅ", name: "ひゅ", sound: "hyu" }, { char: "ひょ", name: "ひょ", sound: "hyo" },
        { char: "みゃ", name: "みゃ", sound: "mya" }, { char: "みゅ", name: "みゅ", sound: "myu" }, { char: "みょ", name: "みょ", sound: "myo" },
        { char: "りゃ", name: "りゃ", sound: "rya" }, { char: "りゅ", name: "りゅ", sound: "ryu" }, { char: "りょ", name: "りょ", sound: "ryo" },
        { char: "ぎゃ", name: "ぎゃ", sound: "gya" }, { char: "ぎゅ", name: "ぎゅ", sound: "gyu" }, { char: "ぎょ", name: "ぎょ", sound: "gyo" },
        { char: "じゃ", name: "じゃ", sound: "ja" }, { char: "じゅ", name: "じゅ", sound: "ju" }, { char: "じょ", name: "じょ", sound: "jo" },
        { char: "びゃ", name: "びゃ", sound: "bya" }, { char: "びゅ", name: "びゅ", sound: "byu" }, { char: "びょ", name: "びょ", sound: "byo" },
        { char: "ぴゃ", name: "ぴゃ", sound: "pya" }, { char: "ぴゅ", name: "ぴゅ", sound: "pyu" }, { char: "ぴょ", name: "ぴょ", sound: "pyo" },
      ],
    },
    {
      key: "kata", label: "片假名 · 清音（五十音）",
      letters: [
        { char: "ア", name: "ア", sound: "a" }, { char: "イ", name: "イ", sound: "i" }, { char: "ウ", name: "ウ", sound: "u" }, { char: "エ", name: "エ", sound: "e" }, { char: "オ", name: "オ", sound: "o" },
        { char: "カ", name: "カ", sound: "ka" }, { char: "キ", name: "キ", sound: "ki" }, { char: "ク", name: "ク", sound: "ku" }, { char: "ケ", name: "ケ", sound: "ke" }, { char: "コ", name: "コ", sound: "ko" },
        { char: "サ", name: "サ", sound: "sa" }, { char: "シ", name: "シ", sound: "shi" }, { char: "ス", name: "ス", sound: "su" }, { char: "セ", name: "セ", sound: "se" }, { char: "ソ", name: "ソ", sound: "so" },
        { char: "タ", name: "タ", sound: "ta" }, { char: "チ", name: "チ", sound: "chi" }, { char: "ツ", name: "ツ", sound: "tsu" }, { char: "テ", name: "テ", sound: "te" }, { char: "ト", name: "ト", sound: "to" },
        { char: "ナ", name: "ナ", sound: "na" }, { char: "ニ", name: "ニ", sound: "ni" }, { char: "ヌ", name: "ヌ", sound: "nu" }, { char: "ネ", name: "ネ", sound: "ne" }, { char: "ノ", name: "ノ", sound: "no" },
        { char: "ハ", name: "ハ", sound: "ha" }, { char: "ヒ", name: "ヒ", sound: "hi" }, { char: "フ", name: "フ", sound: "fu" }, { char: "ヘ", name: "ヘ", sound: "he" }, { char: "ホ", name: "ホ", sound: "ho" },
        { char: "マ", name: "マ", sound: "ma" }, { char: "ミ", name: "ミ", sound: "mi" }, { char: "ム", name: "ム", sound: "mu" }, { char: "メ", name: "メ", sound: "me" }, { char: "モ", name: "モ", sound: "mo" },
        { char: "ヤ", name: "ヤ", sound: "ya" }, { char: "ユ", name: "ユ", sound: "yu" }, { char: "ヨ", name: "ヨ", sound: "yo" },
        { char: "ラ", name: "ラ", sound: "ra" }, { char: "リ", name: "リ", sound: "ri" }, { char: "ル", name: "ル", sound: "ru" }, { char: "レ", name: "レ", sound: "re" }, { char: "ロ", name: "ロ", sound: "ro" },
        { char: "ワ", name: "ワ", sound: "wa" }, { char: "ヲ", name: "ヲ", sound: "wo" }, { char: "ン", name: "ン", sound: "n" },
      ],
    },
  ],
};

// ── 通用希臘文 grc ─────────────────────────────────────────────────────────
const grc: AlphabetSpec = {
  language: "grc",
  title: "希臘字母 · Τὸ ἀλφάβητον",
  intro: "24 個希臘字母（大寫／小寫）。例字取自新約／七十士譯本常見詞。σ 在詞中、ς 在詞尾。另有呼氣記號與重音，見最後一組。",
  groups: [
    {
      key: "letters", label: "24 個字母",
      letters: [
        { char: "α", upper: "Α", name: "alpha 阿爾法", sound: "a", example: "ἀρχή", gloss: "起初／太初" },
        { char: "β", upper: "Β", name: "bēta 貝塔", sound: "b", example: "βίβλος", gloss: "書卷" },
        { char: "γ", upper: "Γ", name: "gamma 伽瑪", sound: "g（硬音）", example: "γῆ", gloss: "地" },
        { char: "δ", upper: "Δ", name: "delta 德爾塔", sound: "d", example: "δόξα", gloss: "榮耀" },
        { char: "ε", upper: "Ε", name: "epsilon 厄普西隆", sound: "短 e", example: "ἐγώ", gloss: "我" },
        { char: "ζ", upper: "Ζ", name: "zēta 澤塔", sound: "z／dz", example: "ζωή", gloss: "生命" },
        { char: "η", upper: "Η", name: "ēta 厄塔", sound: "長 e（近 i）", example: "ἡμέρα", gloss: "日子" },
        { char: "θ", upper: "Θ", name: "thēta 西塔", sound: "th（無聲）", example: "θεός", gloss: "神" },
        { char: "ι", upper: "Ι", name: "iōta 約塔", sound: "i", example: "Ἰησοῦς", gloss: "耶穌" },
        { char: "κ", upper: "Κ", name: "kappa 卡帕", sound: "k", example: "κύριος", gloss: "主" },
        { char: "λ", upper: "Λ", name: "lambda 拉姆達", sound: "l", example: "λόγος", gloss: "道／話語" },
        { char: "μ", upper: "Μ", name: "mu 繆", sound: "m", example: "μήτηρ", gloss: "母親" },
        { char: "ν", upper: "Ν", name: "nu 紐", sound: "n", example: "νόμος", gloss: "律法" },
        { char: "ξ", upper: "Ξ", name: "xi 克西", sound: "x（ks）", example: "ξύλον", gloss: "木頭" },
        { char: "ο", upper: "Ο", name: "omicron 奧密克戎", sound: "短 o", example: "ὁδός", gloss: "道路" },
        { char: "π", upper: "Π", name: "pi 派", sound: "p", example: "πνεῦμα", gloss: "靈" },
        { char: "ρ", upper: "Ρ", name: "rhō 柔", sound: "r", example: "ῥῆμα", gloss: "話語" },
        { char: "σ", upper: "Σ", name: "sigma 西格瑪", sound: "s（詞尾作 ς）", example: "σάρξ", gloss: "肉體" },
        { char: "τ", upper: "Τ", name: "tau 陶", sound: "t", example: "τέλος", gloss: "終結" },
        { char: "υ", upper: "Υ", name: "upsilon 宇普西隆", sound: "ü／u", example: "υἱός", gloss: "兒子" },
        { char: "φ", upper: "Φ", name: "phi 斐", sound: "ph／f", example: "φῶς", gloss: "光" },
        { char: "χ", upper: "Χ", name: "chi 希", sound: "ch（喉擦）", example: "χάρις", gloss: "恩典" },
        { char: "ψ", upper: "Ψ", name: "psi 普西", sound: "ps", example: "ψυχή", gloss: "魂" },
        { char: "ω", upper: "Ω", name: "ōmega 奧米伽", sound: "長 o", example: "ὥρα", gloss: "時刻" },
      ],
    },
    {
      key: "marks", label: "呼氣記號與重音",
      note: "母音／ρ 起首要標呼氣記號；重音標在重讀母音上。",
      letters: [
        { char: "ἁ", name: "粗氣記號 (dasia)", sound: "起首加 h 音", example: "ἅγιος", gloss: "聖潔的" },
        { char: "ἀ", name: "柔氣記號 (psili)", sound: "不加 h", example: "ἀγάπη", gloss: "愛" },
        { char: "ά", name: "銳音 (oxia)", sound: "重讀此母音", example: "ἀγάπη", gloss: "愛" },
        { char: "ᾶ", name: "揚抑音 (perispomeni)", sound: "長母音的升降調", example: "γῆ", gloss: "地" },
        { char: "ῳ", name: "ι 下標 (ypogegrammeni)", sound: "不發音的 iota", example: "λόγῳ", gloss: "在道裡" },
      ],
    },
  ],
};

// ── 教會拉丁文 la ──────────────────────────────────────────────────────────
const la: AlphabetSpec = {
  language: "la",
  title: "拉丁字母與教會式發音 · Alphabetum",
  intro: "字母與英文相同（古典無 J/U/W）。重點在「教會式（義大利式）發音」與字母組合：C/G 在 e、i、ae、oe 前軟化，V 念 v，AE/OE 念 e。",
  groups: [
    {
      key: "base", label: "字母與教會式讀音",
      letters: [
        { char: "a", upper: "A", name: "a", sound: "阿（a）", example: "ave", gloss: "萬福／你好" },
        { char: "b", upper: "B", name: "be", sound: "b", example: "bonus", gloss: "好的" },
        { char: "c", upper: "C", name: "ce", sound: "k；在 e/i/ae/oe 前軟化成 ch", example: "caelum", gloss: "天（念 che-lum）" },
        { char: "d", upper: "D", name: "de", sound: "d", example: "Deus", gloss: "神" },
        { char: "e", upper: "E", name: "e", sound: "耶（e）", example: "et", gloss: "和" },
        { char: "f", upper: "F", name: "ef", sound: "f", example: "fides", gloss: "信德" },
        { char: "g", upper: "G", name: "ge", sound: "硬 g；在 e/i 前軟化成 j（dʒ）", example: "genu", gloss: "膝（念 je-nu）" },
        { char: "h", upper: "H", name: "ha", sound: "多半不發音", example: "homo", gloss: "人" },
        { char: "i", upper: "I", name: "i", sound: "伊；母音前作子音 y", example: "in", gloss: "在…裡" },
        { char: "j", upper: "J", name: "iota", sound: "子音 i（y），中世紀才寫成 j", example: "Jesus", gloss: "耶穌" },
        { char: "k", upper: "K", name: "ka", sound: "k（極罕用）", example: "Kalendae", gloss: "朔日" },
        { char: "l", upper: "L", name: "el", sound: "l", example: "lux", gloss: "光" },
        { char: "m", upper: "M", name: "em", sound: "m", example: "mater", gloss: "母親" },
        { char: "n", upper: "N", name: "en", sound: "n", example: "nomen", gloss: "名" },
        { char: "o", upper: "O", name: "o", sound: "喔（o）", example: "oremus", gloss: "我們祈禱" },
        { char: "p", upper: "P", name: "pe", sound: "p", example: "pax", gloss: "平安" },
        { char: "q", upper: "Q", name: "qu", sound: "k（恆接 u，念 kw）", example: "qui", gloss: "誰" },
        { char: "r", upper: "R", name: "er", sound: "彈舌 r", example: "rex", gloss: "王" },
        { char: "s", upper: "S", name: "es", sound: "s（母音間可濁化 z）", example: "sanctus", gloss: "聖哉" },
        { char: "t", upper: "T", name: "te", sound: "t；ti+母音念 tsi", example: "terra", gloss: "地" },
        { char: "u", upper: "U", name: "u", sound: "烏（u）", example: "unus", gloss: "一" },
        { char: "v", upper: "V", name: "ve", sound: "v（教會式，非古典 w）", example: "Verbum", gloss: "道／聖言" },
        { char: "x", upper: "X", name: "ix", sound: "ks", example: "pax", gloss: "平安" },
        { char: "y", upper: "Y", name: "ypsilon", sound: "i（希臘外來字）", example: "hymnus", gloss: "讚美詩" },
        { char: "z", upper: "Z", name: "zeta", sound: "dz", example: "zelus", gloss: "熱忱" },
      ],
    },
    {
      key: "combos", label: "字母組合與發音規則",
      note: "這些組合是教會拉丁誦讀最關鍵處。",
      letters: [
        { char: "ae", name: "ae", sound: "念 e（=英 e）", example: "caelum", gloss: "天" },
        { char: "oe", name: "oe", sound: "念 e", example: "poena", gloss: "刑罰" },
        { char: "gn", name: "gn", sound: "念 ny（如義 ny）", example: "agnus", gloss: "羔羊（a-nyus）" },
        { char: "sc", name: "sc", sound: "在 e/i 前念 sh", example: "descendit", gloss: "降下（de-shen-）" },
        { char: "ti", name: "ti + 母音", sound: "念 tsi", example: "gratia", gloss: "恩典（gra-tsia）" },
        { char: "ch", name: "ch", sound: "念 k", example: "cherubim", gloss: "革魯賓" },
        { char: "ph", name: "ph", sound: "念 f", example: "propheta", gloss: "先知" },
        { char: "th", name: "th", sound: "念 t", example: "catholica", gloss: "大公的" },
      ],
    },
  ],
};

// ── 聖經希伯來文 hbo ───────────────────────────────────────────────────────
const hbo: AlphabetSpec = {
  language: "hbo",
  title: "希伯來字母 · הָאָלֶף־בֵּית",
  intro: "22 個子音，由右至左書寫。5 個字母在詞尾有「字尾形（sofit）」。母音由「母音點（niqqud）」標在子音下／旁。讀音為學術轉寫。",
  rtl: true,
  groups: [
    {
      key: "consonants", label: "22 個子音",
      letters: [
        { char: "א", name: "alef 阿萊夫", sound: "ʾ（喉塞／不發音）", example: "אָב", gloss: "父" },
        { char: "ב", name: "bet 貝特", sound: "b／v（無點時）", example: "בַּיִת", gloss: "家／殿" },
        { char: "ג", name: "gimel 吉梅爾", sound: "g", example: "גָּדוֹל", gloss: "大的" },
        { char: "ד", name: "dalet 達萊特", sound: "d", example: "דָּבָר", gloss: "話語／事" },
        { char: "ה", name: "he 黑", sound: "h", example: "הַר", gloss: "山" },
        { char: "ו", name: "vav 瓦夫", sound: "v；亦作母音 o／u", example: "וְ", gloss: "和（連接詞）" },
        { char: "ז", name: "zayin 札因", sound: "z", example: "זֶרַע", gloss: "種子／後裔" },
        { char: "ח", name: "chet 黑特", sound: "kh（喉擦音）", example: "חַיִּים", gloss: "生命" },
        { char: "ט", name: "tet 泰特", sound: "t", example: "טוֹב", gloss: "好" },
        { char: "י", name: "yod 約德", sound: "y", example: "יָד", gloss: "手" },
        { char: "כ", name: "kaf 卡夫", sound: "k／kh", example: "כֹּהֵן", gloss: "祭司" },
        { char: "ל", name: "lamed 拉梅德", sound: "l", example: "לֵב", gloss: "心" },
        { char: "מ", name: "mem 梅姆", sound: "m", example: "מַיִם", gloss: "水" },
        { char: "נ", name: "nun 努恩", sound: "n", example: "נֶפֶשׁ", gloss: "魂／生命" },
        { char: "ס", name: "samek 撒梅克", sound: "s", example: "סֵפֶר", gloss: "書卷" },
        { char: "ע", name: "ayin 阿因", sound: "ʿ（濁喉音）", example: "עַיִן", gloss: "眼／泉" },
        { char: "פ", name: "pe 佩", sound: "p／f", example: "פֶּה", gloss: "口" },
        { char: "צ", name: "tsade 察德", sound: "ts", example: "צֶדֶק", gloss: "公義" },
        { char: "ק", name: "qof 科夫", sound: "q（小舌 k）", example: "קֹדֶשׁ", gloss: "聖" },
        { char: "ר", name: "resh 雷什", sound: "r", example: "רֹאשׁ", gloss: "頭／首" },
        { char: "שׁ", name: "shin／sin 辛", sound: "sh（右點）／s（左點）", example: "שָׁלוֹם", gloss: "平安" },
        { char: "ת", name: "tav 塔夫", sound: "t", example: "תּוֹרָה", gloss: "妥拉／律法" },
      ],
    },
    {
      key: "finals", label: "字尾形（sofit）",
      note: "這 5 個字母出現在詞尾時換成字尾形。",
      letters: [
        { char: "ך", name: "kaf sofit", sound: "kh（詞尾）", example: "לְךָ", gloss: "給你" },
        { char: "ם", name: "mem sofit", sound: "m（詞尾）", example: "שָׁלוֹם", gloss: "平安" },
        { char: "ן", name: "nun sofit", sound: "n（詞尾）", example: "בֵּן", gloss: "兒子" },
        { char: "ף", name: "pe sofit", sound: "f（詞尾）", example: "כֶּסֶף", gloss: "銀子" },
        { char: "ץ", name: "tsade sofit", sound: "ts（詞尾）", example: "אֶרֶץ", gloss: "地" },
      ],
    },
    {
      key: "niqqud", label: "母音點（niqqud）",
      note: "母音點標在子音下方／旁；以子音 בּ 示範位置。",
      letters: [
        { char: "בָ", name: "qamats", sound: "a（長）", example: "בָּא", gloss: "他來" },
        { char: "בַ", name: "patach", sound: "a（短）", example: "בַּת", gloss: "女兒" },
        { char: "בֵ", name: "tsere", sound: "e（長）", example: "בֵּן", gloss: "兒子" },
        { char: "בֶ", name: "segol", sound: "e（短）", example: "אֶרֶץ", gloss: "地" },
        { char: "בִ", name: "hiriq", sound: "i", example: "אִישׁ", gloss: "男人" },
        { char: "בֹ", name: "holam", sound: "o", example: "טוֹב", gloss: "好" },
        { char: "בֻ", name: "qubuts", sound: "u", example: "שֻׁלְחָן", gloss: "桌子" },
        { char: "בְ", name: "shva", sound: "ə／無聲", example: "בְּרֵאשִׁית", gloss: "起初" },
      ],
    },
  ],
};

// ── 古典希臘文 att（與通用希臘文同 24 字母，重用 grc）────────────────────────
const att: AlphabetSpec = {
  ...grc,
  language: "att",
  title: "古典希臘字母 · Τὸ ἀλφάβητον（Attic）",
  intro: "古典（雅典）希臘文與通用希臘文用同一套 24 字母與呼氣記號、重音。例字取自荷馬與柏拉圖常見詞。",
};

// ── 亞蘭文 arc（方體字，與希伯來文同字母，重用 hbo）──────────────────────────
const arc: AlphabetSpec = {
  ...hbo,
  language: "arc",
  title: "亞蘭文字母（方體字）· אָלֶף־בֵּית אֲרָמִי",
  intro: "聖經亞蘭文與塔古姆用與希伯來文相同的方體字（22 子音、5 字尾形、母音點），由右至左。學過希伯來文可直接上手。",
};

// ── 教會斯拉夫文 chu（西里爾字母 + 古字母）──────────────────────────────────
const chu: AlphabetSpec = {
  language: "chu",
  title: "西里爾字母 · Кѷрїллица",
  intro: "教會斯拉夫文用西里爾字母（非現代俄文）。下方先列通用字母，再列教會斯拉夫特有的古字母。例字取自禮儀與聖經。",
  groups: [
    {
      key: "letters", label: "西里爾字母",
      letters: [
        { char: "а", upper: "А", name: "az 阿茲", sound: "a", example: "азъ", gloss: "我" },
        { char: "б", upper: "Б", name: "buky 布基", sound: "b", example: "Богъ", gloss: "神" },
        { char: "в", upper: "В", name: "vědi 韋季", sound: "v", example: "вода", gloss: "水" },
        { char: "г", upper: "Г", name: "glagoli", sound: "g", example: "глаголъ", gloss: "話語" },
        { char: "д", upper: "Д", name: "dobro", sound: "d", example: "духъ", gloss: "靈" },
        { char: "е", upper: "Е", name: "jest", sound: "e", example: "есть", gloss: "是" },
        { char: "ж", upper: "Ж", name: "živěte", sound: "zh（如 vision）", example: "животъ", gloss: "生命" },
        { char: "з", upper: "З", name: "zemlja", sound: "z", example: "земля", gloss: "地" },
        { char: "и", upper: "И", name: "iže", sound: "i", example: "имя", gloss: "名" },
        { char: "і", upper: "І", name: "i（十進）", sound: "i（用於母音前）", example: "Іисусъ", gloss: "耶穌" },
        { char: "к", upper: "К", name: "kako", sound: "k", example: "крестъ", gloss: "十字架" },
        { char: "л", upper: "Л", name: "ljudije", sound: "l", example: "любы", gloss: "愛" },
        { char: "м", upper: "М", name: "myslite", sound: "m", example: "миръ", gloss: "和平／世界" },
        { char: "н", upper: "Н", name: "našь", sound: "n", example: "небо", gloss: "天" },
        { char: "о", upper: "О", name: "onъ", sound: "o", example: "отецъ", gloss: "父" },
        { char: "п", upper: "П", name: "pokoj", sound: "p", example: "пророкъ", gloss: "先知" },
        { char: "р", upper: "Р", name: "rьci", sound: "r", example: "рабъ", gloss: "僕人" },
        { char: "с", upper: "С", name: "slovo", sound: "s", example: "слово", gloss: "道／話語" },
        { char: "т", upper: "Т", name: "tvrьdo", sound: "t", example: "Троица", gloss: "三位一體" },
        { char: "у", upper: "У", name: "ukъ", sound: "u", example: "умъ", gloss: "心智" },
        { char: "ф", upper: "Ф", name: "frьtъ", sound: "f", example: "фарисей", gloss: "法利賽人" },
        { char: "х", upper: "Х", name: "xěrъ", sound: "kh（喉擦）", example: "Христосъ", gloss: "基督" },
        { char: "ц", upper: "Ц", name: "ci", sound: "ts", example: "царь", gloss: "君王" },
        { char: "ч", upper: "Ч", name: "črьvь", sound: "ch", example: "человѣкъ", gloss: "人" },
        { char: "ш", upper: "Ш", name: "ša", sound: "sh", example: "шестъ", gloss: "六" },
        { char: "щ", upper: "Щ", name: "šta", sound: "shch", example: "пища", gloss: "食物" },
        { char: "ъ", name: "jerъ（硬音）", sound: "弱化的後母音／硬音記號", example: "сынъ", gloss: "兒子" },
        { char: "ы", upper: "Ы", name: "jery", sound: "y（後高母音）", example: "сынъ", gloss: "兒子" },
        { char: "ь", name: "jerь（軟音）", sound: "弱化的前母音／軟音記號", example: "день", gloss: "日" },
        { char: "ю", upper: "Ю", name: "ju", sound: "yu", example: "юница", gloss: "母牛" },
        { char: "я", upper: "Я", name: "ja", sound: "ya", example: "языкъ", gloss: "語言／民族" },
      ],
    },
    {
      key: "archaic", label: "教會斯拉夫古字母",
      note: "這些字母現代俄文已不用，但教會斯拉夫文獻常見。",
      letters: [
        { char: "ѣ", upper: "Ѣ", name: "jať 雅季", sound: "ě（近 ye）", example: "вѣра", gloss: "信德" },
        { char: "ѡ", upper: "Ѡ", name: "ōt（omega）", sound: "o", example: "ѡтецъ", gloss: "父" },
        { char: "ѧ", upper: "Ѧ", name: "malyj jus（小尤斯）", sound: "鼻化 e（ę）", example: "ѧзыкъ", gloss: "語言" },
        { char: "ѫ", upper: "Ѫ", name: "bolьšoj jus（大尤斯）", sound: "鼻化 o（ǫ）", example: "рѫка", gloss: "手" },
        { char: "ѱ", upper: "Ѱ", name: "psi", sound: "ps", example: "ѱаломъ", gloss: "詩篇" },
        { char: "ѯ", upper: "Ѯ", name: "ksi", sound: "ks", example: "Алеѯандръ", gloss: "亞歷山大" },
        { char: "ѳ", upper: "Ѳ", name: "fita", sound: "f／th（希臘 θ）", example: "Ѳома", gloss: "多馬" },
        { char: "ѵ", upper: "Ѵ", name: "ižica", sound: "i／v", example: "мѵро", gloss: "聖膏油" },
        { char: "ѕ", upper: "Ѕ", name: "dzělo", sound: "dz", example: "ѕвѣзда", gloss: "星" },
      ],
    },
  ],
};

// ── 古典阿拉伯文 ar（28 字母 + 母音符號）─────────────────────────────────────
const ar: AlphabetSpec = {
  language: "ar",
  title: "阿拉伯字母 · الأبجدية العربية",
  intro: "28 個輔音字母，由右至左、依位置連寫變形（此處列獨立形）。母音與其他發音用上下標的「母音符號（ḥarakāt）」。例字取自古蘭與宗教詞。",
  rtl: true,
  groups: [
    {
      key: "letters", label: "28 個字母",
      letters: [
        { char: "ا", name: "alif", sound: "ā／長 a（亦作母音座）", example: "الله", gloss: "真主" },
        { char: "ب", name: "bāʾ", sound: "b", example: "باب", gloss: "門" },
        { char: "ت", name: "tāʾ", sound: "t", example: "كتاب", gloss: "書" },
        { char: "ث", name: "thāʾ", sound: "th（無聲，如 think）", example: "ثلاثة", gloss: "三" },
        { char: "ج", name: "jīm", sound: "j（dʒ）", example: "جنة", gloss: "樂園" },
        { char: "ح", name: "ḥāʾ", sound: "ḥ（咽擦音）", example: "حق", gloss: "真理" },
        { char: "خ", name: "khāʾ", sound: "kh（喉擦）", example: "خبز", gloss: "麵包" },
        { char: "د", name: "dāl", sound: "d", example: "دين", gloss: "宗教" },
        { char: "ذ", name: "dhāl", sound: "dh（濁，如 this）", example: "ذكر", gloss: "記念／誦念" },
        { char: "ر", name: "rāʾ", sound: "r（彈舌）", example: "رب", gloss: "主" },
        { char: "ز", name: "zāy", sound: "z", example: "زكاة", gloss: "天課" },
        { char: "س", name: "sīn", sound: "s", example: "سلام", gloss: "平安" },
        { char: "ش", name: "shīn", sound: "sh", example: "شمس", gloss: "太陽" },
        { char: "ص", name: "ṣād", sound: "ṣ（重音 s）", example: "صلاة", gloss: "禮拜" },
        { char: "ض", name: "ḍād", sound: "ḍ（重音 d）", example: "رمضان", gloss: "齋月" },
        { char: "ط", name: "ṭāʾ", sound: "ṭ（重音 t）", example: "طريق", gloss: "道路" },
        { char: "ظ", name: "ẓāʾ", sound: "ẓ（重音 dh）", example: "ظلم", gloss: "不義" },
        { char: "ع", name: "ʿayn", sound: "ʿ（濁咽音）", example: "علم", gloss: "知識" },
        { char: "غ", name: "ghayn", sound: "gh（濁喉擦）", example: "غفور", gloss: "至赦的" },
        { char: "ف", name: "fāʾ", sound: "f", example: "فجر", gloss: "黎明" },
        { char: "ق", name: "qāf", sound: "q（小舌 k）", example: "قرآن", gloss: "古蘭" },
        { char: "ك", name: "kāf", sound: "k", example: "كتاب", gloss: "書" },
        { char: "ل", name: "lām", sound: "l", example: "ليل", gloss: "夜" },
        { char: "م", name: "mīm", sound: "m", example: "مسجد", gloss: "清真寺" },
        { char: "ن", name: "nūn", sound: "n", example: "نور", gloss: "光" },
        { char: "ه", name: "hāʾ", sound: "h", example: "هدى", gloss: "引導" },
        { char: "و", name: "wāw", sound: "w／長 ū", example: "وحي", gloss: "啟示" },
        { char: "ي", name: "yāʾ", sound: "y／長 ī", example: "يوم", gloss: "日子" },
      ],
    },
    {
      key: "harakat", label: "母音符號（ḥarakāt）",
      note: "短母音與其他發音標在輔音上下；以 ب 示範。",
      letters: [
        { char: "بَ", name: "fatḥa", sound: "a（短）", example: "بَ", gloss: "ba" },
        { char: "بِ", name: "kasra", sound: "i（短）", example: "بِ", gloss: "bi" },
        { char: "بُ", name: "ḍamma", sound: "u（短）", example: "بُ", gloss: "bu" },
        { char: "بْ", name: "sukūn", sound: "無母音", example: "بْ", gloss: "b" },
        { char: "بّ", name: "shadda", sound: "輔音加倍", example: "بّ", gloss: "bb" },
        { char: "بً", name: "tanwīn（fatḥa）", sound: "-an（不定）", example: "كتابًا", gloss: "一本書（受格）" },
      ],
    },
  ],
};

// ── 古典敘利亞文 syr（Estrangela 22 子音）────────────────────────────────────
const syr: AlphabetSpec = {
  language: "syr",
  title: "敘利亞字母 · ܐܠܦ ܒܝܬ（Estrangela）",
  intro: "22 個輔音，由右至左、連寫（此處列獨立形）。以最古老的 Estrangela 字體教學。母音用點或上下標（東/西兩傳統不同）。例字取自 Peshitta。",
  rtl: true,
  groups: [
    {
      key: "consonants", label: "22 個子音",
      letters: [
        { char: "ܐ", name: "ālaph", sound: "ʾ（喉塞／母音座）", example: "ܐܠܗܐ", gloss: "神" },
        { char: "ܒ", name: "bēth", sound: "b／v", example: "ܒܪܐ", gloss: "子" },
        { char: "ܓ", name: "gāmal", sound: "g", example: "ܓܒܪܐ", gloss: "人" },
        { char: "ܕ", name: "dālath", sound: "d／dh", example: "ܕܗܒܐ", gloss: "金" },
        { char: "ܗ", name: "hē", sound: "h", example: "ܗܘ", gloss: "他" },
        { char: "ܘ", name: "waw", sound: "w／長 u/o", example: "ܘ", gloss: "和" },
        { char: "ܙ", name: "zayn", sound: "z", example: "ܙܒܢܐ", gloss: "時間" },
        { char: "ܚ", name: "ḥēth", sound: "ḥ（咽擦）", example: "ܚܝܐ", gloss: "活的" },
        { char: "ܛ", name: "ṭēth", sound: "ṭ（重音 t）", example: "ܛܒܐ", gloss: "好" },
        { char: "ܝ", name: "yodh", sound: "y／長 i", example: "ܝܫܘܥ", gloss: "耶穌" },
        { char: "ܟ", name: "kāph", sound: "k／kh", example: "ܟܗܢܐ", gloss: "祭司" },
        { char: "ܠ", name: "lāmadh", sound: "l", example: "ܠܒܐ", gloss: "心" },
        { char: "ܡ", name: "mīm", sound: "m", example: "ܡܫܝܚܐ", gloss: "彌賽亞" },
        { char: "ܢ", name: "nūn", sound: "n", example: "ܢܘܪܐ", gloss: "火" },
        { char: "ܣ", name: "semkath", sound: "s", example: "ܣܦܪܐ", gloss: "書卷" },
        { char: "ܥ", name: "ʿē", sound: "ʿ（濁咽）", example: "ܥܡܐ", gloss: "民" },
        { char: "ܦ", name: "pē", sound: "p／f", example: "ܦܘܡܐ", gloss: "口" },
        { char: "ܨ", name: "ṣādhē", sound: "ṣ（重音 s）", example: "ܨܠܘܬܐ", gloss: "禱告" },
        { char: "ܩ", name: "qōph", sound: "q（小舌 k）", example: "ܩܕܝܫܐ", gloss: "聖" },
        { char: "ܪ", name: "rēsh", sound: "r", example: "ܪܘܚܐ", gloss: "靈" },
        { char: "ܫ", name: "shīn", sound: "sh", example: "ܫܠܡܐ", gloss: "平安" },
        { char: "ܬ", name: "taw", sound: "t／th", example: "ܬܘܪܐ", gloss: "山" },
      ],
    },
  ],
};

// ── 科普特文 cop（希臘衍生 + 7 世俗體字母）──────────────────────────────────
const cop: AlphabetSpec = {
  language: "cop",
  title: "科普特字母 · ⲧⲙⲛⲧⲣⲙⲛⲕⲏⲙⲉ",
  intro: "前 24 字母源自希臘大寫，末 7 字母取自世俗體（記希臘無的音）。以薩希德方言讀音為準。例字取自科普特聖經與納戈瑪第文獻。",
  groups: [
    {
      key: "greek", label: "希臘衍生字母",
      letters: [
        { char: "ⲁ", upper: "Ⲁ", name: "alpha", sound: "a", example: "ⲁⲅⲅⲉⲗⲟⲥ", gloss: "天使" },
        { char: "ⲃ", upper: "Ⲃ", name: "bēta（vida）", sound: "b／v", example: "ⲃⲱⲕ", gloss: "去" },
        { char: "ⲅ", upper: "Ⲅ", name: "gamma", sound: "g", example: "ⲅⲉⲛⲟⲥ", gloss: "族類" },
        { char: "ⲇ", upper: "Ⲇ", name: "delta", sound: "d", example: "ⲇⲓⲕⲁⲓⲟⲥ", gloss: "義人" },
        { char: "ⲉ", upper: "Ⲉ", name: "ei", sound: "短 e", example: "ⲉⲓⲱⲧ", gloss: "父" },
        { char: "ⲍ", upper: "Ⲍ", name: "zēta", sound: "z", example: "ⲍⲱⲏ", gloss: "生命" },
        { char: "ⲏ", upper: "Ⲏ", name: "ēta", sound: "長 e", example: "ⲏⲓ", gloss: "房子" },
        { char: "ⲑ", upper: "Ⲑ", name: "thēta", sound: "th", example: "ⲑⲉⲟⲥ", gloss: "神（希臘借詞）" },
        { char: "ⲓ", upper: "Ⲓ", name: "iōta", sound: "i", example: "ⲓⲱⲧ", gloss: "父" },
        { char: "ⲕ", upper: "Ⲕ", name: "kappa", sound: "k", example: "ⲕⲁϩ", gloss: "地" },
        { char: "ⲗ", upper: "Ⲗ", name: "laula", sound: "l", example: "ⲗⲁⲥ", gloss: "舌" },
        { char: "ⲙ", upper: "Ⲙ", name: "mē", sound: "m", example: "ⲙⲁⲁⲩ", gloss: "母" },
        { char: "ⲛ", upper: "Ⲛ", name: "nē", sound: "n", example: "ⲛⲟⲩⲧⲉ", gloss: "神" },
        { char: "ⲝ", upper: "Ⲝ", name: "ksi", sound: "ks", example: "ⲝⲩⲗⲟⲛ", gloss: "木" },
        { char: "ⲟ", upper: "Ⲟ", name: "o", sound: "短 o", example: "ⲟⲩⲟⲉⲓⲛ", gloss: "光" },
        { char: "ⲡ", upper: "Ⲡ", name: "pi", sound: "p", example: "ⲡⲛⲁ", gloss: "靈" },
        { char: "ⲣ", upper: "Ⲣ", name: "rō", sound: "r", example: "ⲣⲱⲙⲉ", gloss: "人" },
        { char: "ⲥ", upper: "Ⲥ", name: "sēmma", sound: "s", example: "ⲥⲱⲙⲁ", gloss: "身體" },
        { char: "ⲧ", upper: "Ⲧ", name: "tau", sound: "t", example: "ⲧⲱⲣⲉ", gloss: "手" },
        { char: "ⲩ", upper: "Ⲩ", name: "ué", sound: "u／y", example: "ⲯⲩⲭⲏ", gloss: "魂" },
        { char: "ⲫ", upper: "Ⲫ", name: "phi", sound: "ph／f", example: "ⲫⲱⲥ", gloss: "光（希臘借詞）" },
        { char: "ⲭ", upper: "Ⲭ", name: "khi", sound: "kh", example: "ⲭⲣⲓⲥⲧⲟⲥ", gloss: "基督" },
        { char: "ⲯ", upper: "Ⲯ", name: "psi", sound: "ps", example: "ⲯⲩⲭⲏ", gloss: "魂" },
        { char: "ⲱ", upper: "Ⲱ", name: "ōou", sound: "長 o", example: "ⲱⲛϩ", gloss: "生命" },
      ],
    },
    {
      key: "demotic", label: "世俗體字母",
      note: "希臘字母無法表達的科普特音，借自埃及世俗體。",
      letters: [
        { char: "ϣ", upper: "Ϣ", name: "šai", sound: "sh", example: "ϣⲏⲣⲉ", gloss: "兒子" },
        { char: "ϥ", upper: "Ϥ", name: "fai", sound: "f", example: "ϥⲧⲟⲟⲩ", gloss: "四" },
        { char: "ϧ", upper: "Ϧ", name: "khai（波海里）", sound: "kh", example: "ϧⲉⲛ", gloss: "在…裡" },
        { char: "ϩ", upper: "Ϩ", name: "hori", sound: "h", example: "ϩⲟⲟⲩ", gloss: "日" },
        { char: "ϫ", upper: "Ϫ", name: "djandja", sound: "j（dʒ）", example: "ϫⲟⲉⲓⲥ", gloss: "主" },
        { char: "ϭ", upper: "Ϭ", name: "tšima", sound: "tsh／c", example: "ϭⲟⲙ", gloss: "能力" },
        { char: "ϯ", upper: "Ϯ", name: "ti", sound: "ti（音節）", example: "ϯⲙⲉ", gloss: "村" },
      ],
    },
  ],
};

// ── 古典亞美尼亞文 hy（39 字母 Grabar）───────────────────────────────────────
const hy: AlphabetSpec = {
  language: "hy",
  title: "亞美尼亞字母 · Հայոց այբուբեն",
  intro: "梅斯羅普‧馬什托茨（405 年）所創，古典 Grabar 有 36 個原始字母（後增 3）。讀音用古典轉寫。例字取自亞美尼亞文聖經。",
  groups: [
    {
      key: "letters", label: "字母",
      letters: [
        { char: "ա", upper: "Ա", name: "ayb", sound: "a", example: "Աստուած", gloss: "神" },
        { char: "բ", upper: "Բ", name: "ben", sound: "b", example: "բան", gloss: "話語／道" },
        { char: "գ", upper: "Գ", name: "gim", sound: "g", example: "գիրք", gloss: "書" },
        { char: "դ", upper: "Դ", name: "da", sound: "d", example: "դուռն", gloss: "門" },
        { char: "ե", upper: "Ե", name: "ech", sound: "e／ye", example: "եկեղեցի", gloss: "教會" },
        { char: "զ", upper: "Զ", name: "za", sound: "z", example: "զօր", gloss: "力量" },
        { char: "է", upper: "Է", name: "ē", sound: "ē（長 e）", example: "էություն", gloss: "本質／存有" },
        { char: "ը", upper: "Ը", name: "ət", sound: "ə（schwa）", example: "ընդ", gloss: "與／在" },
        { char: "թ", upper: "Թ", name: "tʿo", sound: "tʿ（送氣 t）", example: "թագաւոր", gloss: "君王" },
        { char: "ժ", upper: "Ժ", name: "že", sound: "ž（zh）", example: "ժամ", gloss: "時辰" },
        { char: "ի", upper: "Ի", name: "ini", sound: "i", example: "իմաստ", gloss: "智慧／義" },
        { char: "լ", upper: "Լ", name: "liwn", sound: "l", example: "լոյս", gloss: "光" },
        { char: "խ", upper: "Խ", name: "xe", sound: "x（喉擦）", example: "խաչ", gloss: "十字架" },
        { char: "ծ", upper: "Ծ", name: "ca", sound: "c（ts，不送氣）", example: "ծնունդ", gloss: "誕生" },
        { char: "կ", upper: "Կ", name: "ken", sound: "k", example: "կեանք", gloss: "生命" },
        { char: "հ", upper: "Հ", name: "ho", sound: "h", example: "հաւատ", gloss: "信德" },
        { char: "ձ", upper: "Ձ", name: "ja", sound: "j（dz）", example: "ձայն", gloss: "聲音" },
        { char: "ղ", upper: "Ղ", name: "łat", sound: "ł（喉 l／gh）", example: "աղօթք", gloss: "禱告" },
        { char: "ճ", upper: "Ճ", name: "čē", sound: "č（不送氣 tš）", example: "ճշմարիտ", gloss: "真實" },
        { char: "մ", upper: "Մ", name: "men", sound: "m", example: "մարդ", gloss: "人" },
        { char: "յ", upper: "Յ", name: "yi", sound: "y", example: "յոյս", gloss: "盼望" },
        { char: "ն", upper: "Ն", name: "nu", sound: "n", example: "նոր", gloss: "新" },
        { char: "շ", upper: "Շ", name: "ša", sound: "š（sh）", example: "շնորհ", gloss: "恩典" },
        { char: "ո", upper: "Ո", name: "vo", sound: "o／vo", example: "ոգի", gloss: "靈" },
        { char: "չ", upper: "Չ", name: "čʿa", sound: "čʿ（送氣 tš）", example: "չար", gloss: "惡" },
        { char: "պ", upper: "Պ", name: "pe", sound: "p", example: "պատկեր", gloss: "形像" },
        { char: "ջ", upper: "Ջ", name: "ǰe", sound: "ǰ（dž）", example: "ջուր", gloss: "水" },
        { char: "ռ", upper: "Ռ", name: "ṙa", sound: "ṙ（強 r）", example: "առաքեալ", gloss: "使徒" },
        { char: "ս", upper: "Ս", name: "se", sound: "s", example: "սուրբ", gloss: "聖" },
        { char: "վ", upper: "Վ", name: "vew", sound: "v", example: "վկայ", gloss: "見證／殉道者" },
        { char: "տ", upper: "Տ", name: "tiwn", sound: "t", example: "տէր", gloss: "主" },
        { char: "ր", upper: "Ր", name: "re", sound: "r", example: "րաբունի", gloss: "拉比" },
        { char: "ց", upper: "Ց", name: "cʿo", sound: "cʿ（送氣 ts）", example: "ցորեն", gloss: "麥" },
        { char: "ւ", upper: "Ւ", name: "yiwn", sound: "w／u", example: "իւղ", gloss: "油" },
        { char: "փ", upper: "Փ", name: "pʿiwr", sound: "pʿ（送氣 p）", example: "փառք", gloss: "榮耀" },
        { char: "ք", upper: "Ք", name: "kʿe", sound: "kʿ（送氣 k）", example: "քահանայ", gloss: "祭司" },
        { char: "օ", upper: "Օ", name: "ō", sound: "ō（長 o）", example: "օր", gloss: "日" },
        { char: "ֆ", upper: "Ֆ", name: "fe", sound: "f", example: "ֆիլոն", gloss: "斐羅（外來音）" },
      ],
    },
  ],
};

// ── 古典喬治亞文 ka（33 字母 Mkhedruli）─────────────────────────────────────
const ka: AlphabetSpec = {
  language: "ka",
  title: "喬治亞字母 · ქართული ანბანი",
  intro: "現用 Mkhedruli 體 33 字母，無大小寫、一字一音、拼讀規律。讀音用古典轉寫。例字取自喬治亞文聖經與宗教詞。",
  groups: [
    {
      key: "letters", label: "33 個字母",
      letters: [
        { char: "ა", name: "an", sound: "a", example: "ღმერთი", gloss: "神" },
        { char: "ბ", name: "ban", sound: "b", example: "ბაგე", gloss: "唇" },
        { char: "გ", name: "gan", sound: "g", example: "გული", gloss: "心" },
        { char: "დ", name: "don", sound: "d", example: "დედა", gloss: "母" },
        { char: "ე", name: "en", sound: "e", example: "ეკლესია", gloss: "教會" },
        { char: "ვ", name: "vin", sound: "v", example: "ვაზი", gloss: "葡萄樹" },
        { char: "ზ", name: "zen", sound: "z", example: "ზეცა", gloss: "天" },
        { char: "თ", name: "tan", sound: "t（送氣）", example: "თავი", gloss: "頭" },
        { char: "ი", name: "in", sound: "i", example: "იესო", gloss: "耶穌" },
        { char: "კ", name: "kan", sound: "kʼ（擠喉 k）", example: "კაცი", gloss: "人" },
        { char: "ლ", name: "las", sound: "l", example: "ლოცვა", gloss: "禱告" },
        { char: "მ", name: "man", sound: "m", example: "მამა", gloss: "父" },
        { char: "ნ", name: "nar", sound: "n", example: "ნათელი", gloss: "光" },
        { char: "ო", name: "on", sound: "o", example: "ოქრო", gloss: "金" },
        { char: "პ", name: "par", sound: "pʼ（擠喉 p）", example: "პური", gloss: "餅" },
        { char: "ჟ", name: "žan", sound: "ž（zh）", example: "ჟამი", gloss: "時辰" },
        { char: "რ", name: "rae", sound: "r", example: "რწმენა", gloss: "信德" },
        { char: "ს", name: "san", sound: "s", example: "სული", gloss: "靈" },
        { char: "ტ", name: "tar", sound: "tʼ（擠喉 t）", example: "ტაძარი", gloss: "聖殿" },
        { char: "უ", name: "un", sound: "u", example: "უფალი", gloss: "主" },
        { char: "ფ", name: "par", sound: "p（送氣）", example: "ფერი", gloss: "色" },
        { char: "ქ", name: "kan", sound: "k（送氣）", example: "ქართული", gloss: "喬治亞語" },
        { char: "ღ", name: "ghan", sound: "ɣ（濁喉擦）", example: "ღმერთი", gloss: "神" },
        { char: "ყ", name: "qar", sound: "qʼ（擠喉小舌）", example: "ყანა", gloss: "田" },
        { char: "შ", name: "šin", sound: "š（sh）", example: "შვილი", gloss: "孩子" },
        { char: "ჩ", name: "čin", sound: "č（送氣 tš）", example: "ჩემი", gloss: "我的" },
        { char: "ც", name: "can", sound: "c（送氣 ts）", example: "ცა", gloss: "天" },
        { char: "ძ", name: "ʒil", sound: "ʒ（dz）", example: "ძე", gloss: "子" },
        { char: "წ", name: "cʼil", sound: "cʼ（擠喉 ts）", example: "წმინდა", gloss: "聖" },
        { char: "ჭ", name: "čʼar", sound: "čʼ（擠喉 tš）", example: "ჭეშმარიტი", gloss: "真實" },
        { char: "ხ", name: "xan", sound: "x（喉擦）", example: "ხელი", gloss: "手" },
        { char: "ჯ", name: "ǰan", sound: "ǰ（dž）", example: "ჯვარი", gloss: "十字架" },
        { char: "ჰ", name: "hae", sound: "h", example: "ჰაერი", gloss: "空氣" },
      ],
    },
  ],
};

// ── 梵文 sa（天城體：母音 + 子音）────────────────────────────────────────────
const sa: AlphabetSpec = {
  language: "sa",
  title: "天城體 · देवनागरी",
  intro: "梵文用天城體：母音有「獨立形」（字首）與「母音記號」（接子音）；子音帶固有母音 a。讀音用 IAST 轉寫。例字含佛教與印度教常見詞。",
  groups: [
    {
      key: "vowels", label: "母音（獨立形）",
      letters: [
        { char: "अ", name: "a", sound: "短 a", example: "अहम्", gloss: "我" },
        { char: "आ", name: "ā", sound: "長 a", example: "आत्मन्", gloss: "自我／神我" },
        { char: "इ", name: "i", sound: "短 i", example: "इति", gloss: "如是" },
        { char: "ई", name: "ī", sound: "長 i", example: "ईश्वर", gloss: "自在天／主" },
        { char: "उ", name: "u", sound: "短 u", example: "उप", gloss: "近" },
        { char: "ऊ", name: "ū", sound: "長 u", example: "भू", gloss: "地" },
        { char: "ऋ", name: "ṛ", sound: "捲舌母音 r", example: "ऋषि", gloss: "仙人" },
        { char: "ए", name: "e", sound: "e", example: "एक", gloss: "一" },
        { char: "ऐ", name: "ai", sound: "ai", example: "ऐश्वर्य", gloss: "威德" },
        { char: "ओ", name: "o", sound: "o", example: "ओम्", gloss: "唵（聖音）" },
        { char: "औ", name: "au", sound: "au", example: "औषध", gloss: "藥" },
        { char: "अं", name: "ṃ（anusvara）", sound: "鼻化", example: "संघ", gloss: "僧伽" },
        { char: "अः", name: "ḥ（visarga）", sound: "氣音 h", example: "दुःख", gloss: "苦" },
      ],
    },
    {
      key: "consonants", label: "子音（帶固有母音 a）",
      note: "依發音部位排列（喉/顎/捲舌/齒/唇＋半母音與擦音）。",
      letters: [
        { char: "क", name: "ka", sound: "k", example: "कर्म", gloss: "業" },
        { char: "ख", name: "kha", sound: "kh（送氣）", example: "खग", gloss: "鳥" },
        { char: "ग", name: "ga", sound: "g", example: "गुरु", gloss: "上師" },
        { char: "घ", name: "gha", sound: "gh（送氣）", example: "घट", gloss: "瓶" },
        { char: "ङ", name: "ṅa", sound: "ng（喉鼻）", example: "अङ्ग", gloss: "支分" },
        { char: "च", name: "ca", sound: "c（ch，不送氣）", example: "चित्त", gloss: "心" },
        { char: "छ", name: "cha", sound: "ch（送氣）", example: "छाया", gloss: "影" },
        { char: "ज", name: "ja", sound: "j", example: "जन्म", gloss: "生" },
        { char: "झ", name: "jha", sound: "jh（送氣）", example: "झष", gloss: "魚" },
        { char: "ञ", name: "ña", sound: "ny（顎鼻）", example: "ज्ञान", gloss: "智" },
        { char: "ट", name: "ṭa", sound: "ṭ（捲舌）", example: "पट", gloss: "布" },
        { char: "ठ", name: "ṭha", sound: "ṭh（捲舌送氣）", example: "मठ", gloss: "寺院" },
        { char: "ड", name: "ḍa", sound: "ḍ（捲舌）", example: "दण्ड", gloss: "杖／罰" },
        { char: "ढ", name: "ḍha", sound: "ḍh（捲舌送氣）", example: "गूढ", gloss: "隱密" },
        { char: "ण", name: "ṇa", sound: "ṇ（捲舌鼻）", example: "गुण", gloss: "德／屬性" },
        { char: "त", name: "ta", sound: "t（齒）", example: "तत्त्व", gloss: "真實／諦" },
        { char: "थ", name: "tha", sound: "th（齒送氣）", example: "रथ", gloss: "車" },
        { char: "द", name: "da", sound: "d（齒）", example: "देव", gloss: "天／神" },
        { char: "ध", name: "dha", sound: "dh（齒送氣）", example: "धर्म", gloss: "法／達磨" },
        { char: "न", name: "na", sound: "n", example: "नाम", gloss: "名" },
        { char: "प", name: "pa", sound: "p", example: "पद्म", gloss: "蓮花" },
        { char: "फ", name: "pha", sound: "ph（送氣）", example: "फल", gloss: "果" },
        { char: "ब", name: "ba", sound: "b", example: "बुद्ध", gloss: "佛陀" },
        { char: "भ", name: "bha", sound: "bh（送氣）", example: "भगवत्", gloss: "世尊" },
        { char: "म", name: "ma", sound: "m", example: "मन्त्र", gloss: "真言" },
        { char: "य", name: "ya", sound: "y", example: "योग", gloss: "瑜伽" },
        { char: "र", name: "ra", sound: "r", example: "राज", gloss: "王" },
        { char: "ल", name: "la", sound: "l", example: "लोक", gloss: "世間" },
        { char: "व", name: "va", sound: "v／w", example: "वेद", gloss: "吠陀" },
        { char: "श", name: "śa", sound: "ś（顎 sh）", example: "शून्य", gloss: "空" },
        { char: "ष", name: "ṣa", sound: "ṣ（捲舌 sh）", example: "ऋषि", gloss: "仙人" },
        { char: "स", name: "sa", sound: "s", example: "सत्य", gloss: "真諦" },
        { char: "ह", name: "ha", sound: "h", example: "हृदय", gloss: "心要" },
      ],
    },
  ],
};

const pra: AlphabetSpec = {
  ...sa,
  language: "pra",
  title: "天城體（半摩揭陀俗語）· देवनागरी",
  intro: "半摩揭陀俗語的耆那聖典常以天城體轉寫。字母同梵文天城體；俗語音變使複輔音簡化、長音較少。例字仍以天城體示意。",
};

// ── 藏文 bo（30 子音 + 母音記號）────────────────────────────────────────────
const bo: AlphabetSpec = {
  language: "bo",
  title: "藏文字母 · བོད་ཡིག",
  intro: "30 個基本子音（帶固有母音 a），4 個母音記號標在子音上下。讀音用 Wylie 轉寫。例字取自佛教詞。音節間以音節點 ་ 分隔。",
  groups: [
    {
      key: "consonants", label: "30 個子音",
      letters: [
        { char: "ཀ", name: "ka", sound: "k（不送氣）", example: "ཀུན", gloss: "一切" },
        { char: "ཁ", name: "kha", sound: "kh（送氣）", example: "ཁ", gloss: "口" },
        { char: "ག", name: "ga", sound: "g", example: "གསེར", gloss: "金" },
        { char: "ང", name: "nga", sound: "ng", example: "ངག", gloss: "語" },
        { char: "ཅ", name: "ca", sound: "c（ch 不送氣）", example: "ཅི", gloss: "何" },
        { char: "ཆ", name: "cha", sound: "ch（送氣）", example: "ཆོས", gloss: "法（達磨）" },
        { char: "ཇ", name: "ja", sound: "j", example: "ཇོ", gloss: "尊者" },
        { char: "ཉ", name: "nya", sound: "ny", example: "ཉི", gloss: "日" },
        { char: "ཏ", name: "ta", sound: "t（不送氣）", example: "ཏིང", gloss: "定" },
        { char: "ཐ", name: "tha", sound: "th（送氣）", example: "ཐར", gloss: "解脫" },
        { char: "ད", name: "da", sound: "d", example: "དགེ", gloss: "善" },
        { char: "ན", name: "na", sound: "n", example: "ནང", gloss: "內" },
        { char: "པ", name: "pa", sound: "p（不送氣）", example: "པད", gloss: "蓮" },
        { char: "ཕ", name: "pha", sound: "ph（送氣）", example: "ཕྱག", gloss: "敬禮" },
        { char: "བ", name: "ba", sound: "b", example: "བོད", gloss: "西藏" },
        { char: "མ", name: "ma", sound: "m", example: "མ", gloss: "母" },
        { char: "ཙ", name: "tsa", sound: "ts（不送氣）", example: "ཙནྡན", gloss: "栴檀" },
        { char: "ཚ", name: "tsha", sound: "tsh（送氣）", example: "ཚེ", gloss: "壽" },
        { char: "ཛ", name: "dza", sound: "dz", example: "རྫོགས", gloss: "圓滿" },
        { char: "ཝ", name: "wa", sound: "w", example: "ཝ", gloss: "狐" },
        { char: "ཞ", name: "zha", sound: "zh", example: "ཞི", gloss: "寂" },
        { char: "ཟ", name: "za", sound: "z", example: "ཟླ", gloss: "月" },
        { char: "འ", name: "'a", sound: "ʼa（濁喉／a 座）", example: "འགྲོ", gloss: "眾生" },
        { char: "ཡ", name: "ya", sound: "y", example: "ཡི", gloss: "之" },
        { char: "ར", name: "ra", sound: "r", example: "རིན", gloss: "寶" },
        { char: "ལ", name: "la", sound: "l", example: "ལས", gloss: "業" },
        { char: "ཤ", name: "sha", sound: "sh", example: "ཤེས", gloss: "知／智" },
        { char: "ས", name: "sa", sound: "s", example: "སངས", gloss: "覺（淨）" },
        { char: "ཧ", name: "ha", sound: "h", example: "ཧཱུྃ", gloss: "吽（種子字）" },
        { char: "ཨ", name: "a", sound: "a（母音座）", example: "ཨོཾ", gloss: "唵" },
      ],
    },
    {
      key: "vowels", label: "母音記號",
      note: "標在子音上／下；無記號＝固有母音 a。以 ཀ 示範。",
      letters: [
        { char: "ཀི", name: "gigu", sound: "i", example: "རིན", gloss: "寶" },
        { char: "ཀུ", name: "zhabkyu", sound: "u", example: "གུ", gloss: "九" },
        { char: "ཀེ", name: "drengbu", sound: "e", example: "སེམས", gloss: "心" },
        { char: "ཀོ", name: "naro", sound: "o", example: "བོད", gloss: "西藏" },
      ],
    },
  ],
};

// ── 吉茲文 gez（fidäl：33 子音基字 + 7 母音階）──────────────────────────────
const gez: AlphabetSpec = {
  language: "gez",
  title: "吉茲音節文字 · ፊደል",
  intro: "吉茲用「音節文字 fidäl」：每個子音基字（1 階 ä）依母音變 7 階。下方先列 33 個子音基字，再以 ሰ(s) 示範 7 個母音階。讀音用學術轉寫。",
  groups: [
    {
      key: "consonants", label: "子音基字（1 階 ä）",
      letters: [
        { char: "ሀ", name: "hä", sound: "h", example: "ሀገር", gloss: "國" },
        { char: "ለ", name: "lä", sound: "l", example: "ልብ", gloss: "心" },
        { char: "ሐ", name: "ḥä", sound: "ḥ（咽擦）", example: "ሕግ", gloss: "律法" },
        { char: "መ", name: "mä", sound: "m", example: "ማይ", gloss: "水" },
        { char: "ሠ", name: "śä", sound: "ś", example: "ሠናይ", gloss: "善" },
        { char: "ረ", name: "rä", sound: "r", example: "ርእስ", gloss: "頭" },
        { char: "ሰ", name: "sä", sound: "s", example: "ሰላም", gloss: "平安" },
        { char: "ሸ", name: "šä", sound: "š（sh）", example: "ሺ", gloss: "千" },
        { char: "ቀ", name: "qä", sound: "q（擠喉 k）", example: "ቅዱስ", gloss: "聖" },
        { char: "በ", name: "bä", sound: "b", example: "ቤት", gloss: "家／殿" },
        { char: "ተ", name: "tä", sound: "t", example: "ትምህርት", gloss: "教導" },
        { char: "ቸ", name: "čä", sound: "č（tš）", example: "ቸር", gloss: "慈" },
        { char: "ኀ", name: "ḫä", sound: "ḫ（喉擦）", example: "ኃይል", gloss: "力量" },
        { char: "ነ", name: "nä", sound: "n", example: "ነቢይ", gloss: "先知" },
        { char: "ኘ", name: "ñä", sound: "ñ（ny）", example: "ኘ", gloss: "ña" },
        { char: "አ", name: "ʾä", sound: "ʾ（喉塞／母音座）", example: "አብ", gloss: "父" },
        { char: "ከ", name: "kä", sound: "k", example: "ካህን", gloss: "祭司" },
        { char: "ኸ", name: "ḵä", sound: "ḵ（喉擦 k）", example: "ኸ", gloss: "ḵa" },
        { char: "ወ", name: "wä", sound: "w", example: "ወልድ", gloss: "子" },
        { char: "ዐ", name: "ʿä", sound: "ʿ（濁咽）", example: "ዐይን", gloss: "眼" },
        { char: "ዘ", name: "zä", sound: "z", example: "ዘመን", gloss: "時代" },
        { char: "ዠ", name: "žä", sound: "ž（zh）", example: "ዠ", gloss: "ža" },
        { char: "የ", name: "yä", sound: "y", example: "የสוስ", gloss: "耶穌" },
        { char: "ደ", name: "dä", sound: "d", example: "ድንግል", gloss: "童貞" },
        { char: "ጀ", name: "ǧä", sound: "ǧ（dž）", example: "ጀ", gloss: "ǧa" },
        { char: "ገ", name: "gä", sound: "g", example: "ገነት", gloss: "樂園" },
        { char: "ጠ", name: "ṭä", sound: "ṭ（擠喉 t）", example: "ጥበብ", gloss: "智慧" },
        { char: "ጨ", name: "č̣ä", sound: "č̣（擠喉 tš）", example: "ጨ", gloss: "č̣a" },
        { char: "ጰ", name: "ṗä", sound: "ṗ（擠喉 p）", example: "ጴጥሮስ", gloss: "彼得" },
        { char: "ጸ", name: "ṣä", sound: "ṣ（擠喉 s）", example: "ጸሎት", gloss: "禱告" },
        { char: "ፀ", name: "ṣ́ä", sound: "ṣ́（另一擠喉 s）", example: "ፀሐይ", gloss: "太陽" },
        { char: "ፈ", name: "fä", sound: "f", example: "ፍቅር", gloss: "愛" },
        { char: "ፐ", name: "pä", sound: "p", example: "ፓ", gloss: "pa" },
      ],
    },
    {
      key: "orders", label: "7 個母音階（以 ሰ s 示範）",
      note: "每個子音都依此 7 階變化（codepoint 連續位移）。",
      letters: [
        { char: "ሰ", name: "1 階 sä", sound: "sä", example: "ሰላም", gloss: "平安" },
        { char: "ሱ", name: "2 階 su", sound: "su", example: "ሱባኤ", gloss: "守齋" },
        { char: "ሲ", name: "3 階 si", sound: "si", example: "ሲና", gloss: "西奈" },
        { char: "ሳ", name: "4 階 sa", sound: "sa", example: "ሳህል", gloss: "盤" },
        { char: "ሴ", name: "5 階 se", sound: "se", example: "ሴት", gloss: "女" },
        { char: "ስ", name: "6 階 sə", sound: "sə／s（無母音）", example: "ስም", gloss: "名" },
        { char: "ሶ", name: "7 階 so", sound: "so", example: "ሶርያ", gloss: "敘利亞" },
      ],
    },
  ],
};

// ── 曼達文 mid（22 子音）────────────────────────────────────────────────────
const mid: AlphabetSpec = {
  language: "mid",
  title: "曼達字母 · ࡀࡁࡂࡀࡃࡀ",
  intro: "曼達教的東亞蘭語字母，由右至左，特點是母音也寫出（含 a/i/u 字母）。讀音用學術轉寫。例字取自曼達教文獻。",
  rtl: true,
  groups: [
    {
      key: "letters", label: "字母",
      letters: [
        { char: "ࡀ", name: "halqa", sound: "a", example: "ࡀࡁࡀ", gloss: "父" },
        { char: "ࡁ", name: "ba", sound: "b", example: "ࡁࡉࡕ", gloss: "家" },
        { char: "ࡂ", name: "ga", sound: "g", example: "ࡂࡀࡁࡓࡀ", gloss: "人" },
        { char: "ࡃ", name: "da", sound: "d", example: "ࡃࡀࡄࡁࡀ", gloss: "金" },
        { char: "ࡄ", name: "ha", sound: "h", example: "ࡄࡉࡉࡀ", gloss: "活的" },
        { char: "ࡅ", name: "wa（ushenna）", sound: "w／u／o", example: "ࡅ", gloss: "和" },
        { char: "ࡆ", name: "za", sound: "z", example: "ࡆࡉࡃࡒࡀ", gloss: "義" },
        { char: "ࡇ", name: "eh", sound: "ḥ（咽擦）", example: "ࡇࡉࡉࡀ", gloss: "生命" },
        { char: "ࡈ", name: "ṭa", sound: "ṭ（重音 t）", example: "ࡈࡀࡁ", gloss: "好" },
        { char: "ࡉ", name: "yodh", sound: "y／i", example: "ࡉࡀࡅࡀࡓ", gloss: "光界" },
        { char: "ࡊ", name: "ka", sound: "k", example: "ࡊࡅࡔࡈࡀ", gloss: "真實" },
        { char: "ࡋ", name: "la", sound: "l", example: "ࡋࡉࡁࡀ", gloss: "心" },
        { char: "ࡌ", name: "ma", sound: "m", example: "ࡌࡀࡍࡃࡀ", gloss: "知識（曼達）" },
        { char: "ࡍ", name: "na", sound: "n", example: "ࡍࡅࡓࡀ", gloss: "火" },
        { char: "ࡎ", name: "sa", sound: "s", example: "ࡎࡀࡁࡀ", gloss: "長老" },
        { char: "ࡏ", name: "ʿ（in）", sound: "ʿ／e", example: "ࡏࡍࡀ", gloss: "眼／泉" },
        { char: "ࡐ", name: "pa", sound: "p／f", example: "ࡐࡅࡌࡀ", gloss: "口" },
        { char: "ࡑ", name: "ṣa（ṣadi）", sound: "ṣ（重音 s）", example: "ࡑࡀࡃࡒࡀ", gloss: "義" },
        { char: "ࡒ", name: "qa", sound: "q（小舌 k）", example: "ࡒࡀࡃࡀ", gloss: "聖" },
        { char: "ࡓ", name: "ra", sound: "r", example: "ࡓࡁࡀ", gloss: "大" },
        { char: "ࡔ", name: "ša", sound: "sh", example: "ࡔࡅࡌࡀ", gloss: "名" },
        { char: "ࡕ", name: "ta", sound: "t", example: "ࡕࡅࡓࡀ", gloss: "山" },
      ],
    },
  ],
};

export const ALPHABETS: Record<string, AlphabetSpec> = {
  de, fr, ja, grc, la, hbo,
  att, arc, chu, ar, syr, cop, hy, ka, sa, pra, bo, gez, mid,
};

/** 取某語言的字母表（無則 undefined；英文不提供，使用者已熟）。 */
export function alphabetForClient(language: string): AlphabetSpec | undefined {
  return ALPHABETS[language];
}
