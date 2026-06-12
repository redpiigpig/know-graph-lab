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

export const ALPHABETS: Record<string, AlphabetSpec> = { de, fr, ja, grc, la, hbo };

/** 取某語言的字母表（無則 undefined；英文不提供，使用者已熟）。 */
export function alphabetForClient(language: string): AlphabetSpec | undefined {
  return ALPHABETS[language];
}
