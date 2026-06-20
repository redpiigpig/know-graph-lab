// ============================================================================
// 文字創造族譜（世界書寫系統演化 DAG）
// 用於 /genealogy/scripts。節點＝書寫系統，邊＝演化關係（parents[].kind）。
// era：約略起源年（負＝BCE）；coach：對應 /coach 語言代碼（可深連教練）。
// 學術依據：主流文字學共識（Daniels & Bright《世界書寫系統》等）；
// 有爭議的承襲（如婆羅米←亞蘭、諺文←八思巴）以 kind:"influenced" 標虛線並於 note 註明。
// ============================================================================

export type ScriptType =
  | "proto"          // 原型文字
  | "logographic"    // 語素（表意）文字
  | "logosyllabic"   // 語素音節文字
  | "syllabary"      // 音節文字
  | "abjad"          // 輔音音素文字（不標母音）
  | "abugida"        // 元音附標文字（子音帶固有母音）
  | "alphabet"       // 全音素字母
  | "featural"       // 特徵文字
  | "undeciphered";  // 未解讀

export type EdgeKind = "descendant" | "derived" | "adapted" | "influenced";

export interface ScriptParent { id: string; kind: EdgeKind; }
export interface ScriptNode {
  id: string;
  name: string;        // 中文名
  sample: string;      // 代表字符／字樣
  type: ScriptType;
  family: string;      // 大族（配色/篩選）
  era: number;         // 約略起源年（負=BCE）
  region: string;      // 地區
  status: "living" | "extinct" | "undeciphered";
  note: string;        // 一句話
  coach?: string;      // 對應 /coach 語言代碼
  parents: ScriptParent[];
}

// 大族（配色與圖例順序）
export const SCRIPT_FAMILIES: { key: string; label: string; color: string }[] = [
  { key: "cuneiform", label: "楔形文字系", color: "#b45309" },     // amber-700
  { key: "egyptian", label: "埃及／聖書體系", color: "#15803d" },   // green-700
  { key: "semitic", label: "閃語字母系", color: "#0e7490" },        // cyan-700
  { key: "european", label: "希臘‧拉丁‧歐洲系", color: "#1d4ed8" }, // blue-700
  { key: "brahmic", label: "婆羅米／印度系", color: "#a21caf" },     // fuchsia-700
  { key: "mongolic", label: "粟特‧回鶻‧蒙古系", color: "#7c3aed" }, // violet-600
  { key: "eastasian", label: "漢字系", color: "#dc2626" },          // red-600
  { key: "mesoamerican", label: "中美洲系", color: "#ca8a04" },     // yellow-600
  { key: "independent", label: "獨立／近代發明", color: "#475569" }, // slate-600
];

export const SCRIPT_NODES: ScriptNode[] = [
  // ── 獨立起源（根） ──
  { id: "proto-cuneiform", name: "原始楔形文字", sample: "𒀭", type: "proto", family: "cuneiform", era: -3400, region: "蘇美（烏魯克）", status: "extinct", note: "已知最早文字，烏魯克記帳泥板", parents: [] },
  { id: "egyptian", name: "埃及聖書體", sample: "𓂀", type: "logosyllabic", family: "egyptian", era: -3250, region: "古埃及", status: "extinct", note: "象形＋音符＋定符；亡靈書", coach: "egy", parents: [] },
  { id: "chinese-oracle", name: "甲骨文", sample: "龜", type: "logographic", family: "eastasian", era: -1250, region: "商代中國", status: "extinct", note: "占卜刻辭，漢字最早形態", parents: [] },
  { id: "indus", name: "印度河文字", sample: "𑀇", type: "undeciphered", family: "independent", era: -2600, region: "印度河流域", status: "undeciphered", note: "未解讀、無確定後裔", parents: [] },
  { id: "zapotec", name: "薩波特克文字", sample: "◆", type: "logosyllabic", family: "mesoamerican", era: -500, region: "中美洲", status: "extinct", note: "中美洲最早文字之一", parents: [] },

  // ── 楔形文字系 ──
  { id: "sumerian-cuneiform", name: "蘇美楔形文字", sample: "𒅴", type: "logosyllabic", family: "cuneiform", era: -3100, region: "蘇美", status: "extinct", note: "由原始楔形演成音節", parents: [{ id: "proto-cuneiform", kind: "descendant" }] },
  { id: "akkadian-cuneiform", name: "阿卡德楔形文字", sample: "𒀀", type: "logosyllabic", family: "cuneiform", era: -2350, region: "美索不達米亞", status: "extinct", note: "借蘇美楔形寫閃語", coach: "akk", parents: [{ id: "sumerian-cuneiform", kind: "adapted" }] },
  { id: "elamite-cuneiform", name: "埃蘭楔形文字", sample: "𒄿", type: "logosyllabic", family: "cuneiform", era: -2200, region: "埃蘭", status: "extinct", note: "改自阿卡德楔形", parents: [{ id: "akkadian-cuneiform", kind: "adapted" }] },
  { id: "hittite-cuneiform", name: "西臺楔形文字", sample: "𒈛", type: "logosyllabic", family: "cuneiform", era: -1650, region: "安那托利亞", status: "extinct", note: "印歐語最早楔形紀錄", parents: [{ id: "akkadian-cuneiform", kind: "adapted" }] },
  { id: "old-persian-cuneiform", name: "古波斯楔形文字", sample: "𐎠", type: "abugida", family: "cuneiform", era: -525, region: "阿契美尼德波斯", status: "extinct", note: "新創半音節楔形；貝希斯敦", coach: "peo", parents: [{ id: "akkadian-cuneiform", kind: "derived" }] },
  { id: "ugaritic", name: "烏加列文字", sample: "𒀀", type: "abjad", family: "cuneiform", era: -1400, region: "北敘利亞", status: "extinct", note: "楔形外觀的子音字母", coach: "uga", parents: [{ id: "akkadian-cuneiform", kind: "influenced" }, { id: "proto-sinaitic", kind: "influenced" }] },

  // ── 埃及系 ──
  { id: "hieratic", name: "僧侶體", sample: "𓏞", type: "logosyllabic", family: "egyptian", era: -2600, region: "古埃及", status: "extinct", note: "聖書體草寫", parents: [{ id: "egyptian", kind: "descendant" }] },
  { id: "demotic", name: "世俗體", sample: "𓊪", type: "logosyllabic", family: "egyptian", era: -650, region: "古埃及", status: "extinct", note: "僧侶體再簡化", parents: [{ id: "hieratic", kind: "descendant" }] },
  { id: "meroitic", name: "麥羅埃文字", sample: "𐦀", type: "abugida", family: "egyptian", era: -300, region: "庫施（努比亞）", status: "extinct", note: "取材聖書體/世俗體", parents: [{ id: "egyptian", kind: "derived" }, { id: "demotic", kind: "influenced" }] },
  { id: "proto-sinaitic", name: "原始西奈字母", sample: "𐤀", type: "abjad", family: "semitic", era: -1850, region: "西奈／迦南", status: "extinct", note: "取聖書體首音造字母（字母之祖）", parents: [{ id: "egyptian", kind: "derived" }] },

  // ── 閃語字母系 ──
  { id: "phoenician", name: "腓尼基字母", sample: "𐤀", type: "abjad", family: "semitic", era: -1050, region: "黎凡特海岸", status: "extinct", note: "22 子音；字母之母", coach: "phn", parents: [{ id: "proto-sinaitic", kind: "descendant" }] },
  { id: "south-arabian", name: "古南阿拉伯文字", sample: "𐩱", type: "abjad", family: "semitic", era: -900, region: "南阿拉伯", status: "extinct", note: "原始西奈另一支", parents: [{ id: "proto-sinaitic", kind: "descendant" }] },
  { id: "old-north-arabian", name: "古北阿拉伯文字", sample: "𐪀", type: "abjad", family: "semitic", era: -800, region: "北阿拉伯", status: "extinct", note: "南阿拉伯近親", parents: [{ id: "south-arabian", kind: "descendant" }] },
  { id: "geez", name: "吉茲文字", sample: "ግ", type: "abugida", family: "semitic", era: -100, region: "衣索比亞", status: "living", note: "南阿拉伯加母音成音節", coach: "gez", parents: [{ id: "south-arabian", kind: "descendant" }] },
  { id: "paleo-hebrew", name: "古希伯來字母", sample: "𐤀", type: "abjad", family: "semitic", era: -1000, region: "以色列／猶大", status: "extinct", note: "腓尼基直系", parents: [{ id: "phoenician", kind: "descendant" }] },
  { id: "aramaic", name: "亞蘭字母", sample: "𐡀", type: "abjad", family: "semitic", era: -900, region: "近東", status: "extinct", note: "近東通用語；多文字之源", coach: "arc", parents: [{ id: "phoenician", kind: "descendant" }] },
  { id: "hebrew-square", name: "方體希伯來字母", sample: "א", type: "abjad", family: "semitic", era: -250, region: "猶太", status: "living", note: "亞蘭字母演成猶太方體", coach: "hbo", parents: [{ id: "aramaic", kind: "descendant" }] },
  { id: "syriac", name: "敘利亞字母", sample: "ܐ", type: "abjad", family: "semitic", era: -100, region: "埃德薩", status: "living", note: "基督教亞蘭字母（景教）", coach: "syr", parents: [{ id: "aramaic", kind: "descendant" }] },
  { id: "palmyrene", name: "帕米拉字母", sample: "𐡠", type: "abjad", family: "semitic", era: -44, region: "帕米拉", status: "extinct", note: "亞蘭草書", parents: [{ id: "aramaic", kind: "descendant" }] },
  { id: "mandaic", name: "曼達字母", sample: "ࡀ", type: "abjad", family: "semitic", era: 200, region: "美索不達米亞南", status: "living", note: "曼達教諾斯底經典", coach: "mid", parents: [{ id: "aramaic", kind: "descendant" }] },
  { id: "nabataean", name: "納巴泰字母", sample: "𐢀", type: "abjad", family: "semitic", era: -150, region: "佩特拉", status: "extinct", note: "亞蘭草書→阿拉伯之源", parents: [{ id: "aramaic", kind: "descendant" }] },
  { id: "arabic", name: "阿拉伯字母", sample: "ا", type: "abjad", family: "semitic", era: 400, region: "阿拉伯", status: "living", note: "納巴泰連寫演成", coach: "ar", parents: [{ id: "nabataean", kind: "descendant" }] },
  { id: "pahlavi", name: "巴列維文字", sample: "𐭯", type: "abjad", family: "semitic", era: -250, region: "波斯", status: "extinct", note: "亞蘭字母寫中古波斯", parents: [{ id: "aramaic", kind: "descendant" }] },
  { id: "avestan", name: "阿維斯陀字母", sample: "𐬀", type: "alphabet", family: "semitic", era: 400, region: "波斯", status: "extinct", note: "巴列維加母音記祆教聖典", coach: "ae", parents: [{ id: "pahlavi", kind: "derived" }] },
  { id: "kharosthi", name: "佉盧文", sample: "𐨀", type: "abugida", family: "brahmic", era: -350, region: "犍陀羅", status: "extinct", note: "亞蘭字母右行演成", parents: [{ id: "aramaic", kind: "derived" }] },
  { id: "sogdian", name: "粟特字母", sample: "𐼀", type: "abjad", family: "mongolic", era: 100, region: "中亞", status: "extinct", note: "亞蘭草書；絲路通行", parents: [{ id: "aramaic", kind: "descendant" }] },

  // ── 希臘‧拉丁‧歐洲系 ──
  { id: "greek", name: "希臘字母", sample: "Α", type: "alphabet", family: "european", era: -800, region: "希臘", status: "living", note: "首個標母音的全音素字母", coach: "grc", parents: [{ id: "phoenician", kind: "adapted" }] },
  { id: "etruscan", name: "伊特拉斯坎字母", sample: "𐌀", type: "alphabet", family: "european", era: -700, region: "義大利", status: "extinct", note: "西希臘字母→拉丁之橋", parents: [{ id: "greek", kind: "adapted" }] },
  { id: "latin", name: "拉丁字母", sample: "A", type: "alphabet", family: "european", era: -650, region: "羅馬", status: "living", note: "全球最廣用字母", coach: "la", parents: [{ id: "etruscan", kind: "descendant" }] },
  { id: "runic", name: "盧恩字母", sample: "ᚠ", type: "alphabet", family: "european", era: 150, region: "北歐／日耳曼", status: "extinct", note: "古義大利字母北傳", parents: [{ id: "etruscan", kind: "derived" }] },
  { id: "ogham", name: "歐甘文", sample: "᚛", type: "alphabet", family: "european", era: 400, region: "愛爾蘭", status: "extinct", note: "刻劃線記愛爾蘭語", parents: [{ id: "latin", kind: "influenced" }] },
  { id: "coptic", name: "科普特字母", sample: "Ⲁ", type: "alphabet", family: "european", era: 300, region: "埃及", status: "living", note: "希臘字母＋7 世俗體字母", coach: "cop", parents: [{ id: "greek", kind: "adapted" }, { id: "demotic", kind: "derived" }] },
  { id: "gothic", name: "哥德字母", sample: "𐌰", type: "alphabet", family: "european", era: 350, region: "東日耳曼", status: "extinct", note: "烏斐拉據希臘造", parents: [{ id: "greek", kind: "derived" }] },
  { id: "armenian", name: "亞美尼亞字母", sample: "Ա", type: "alphabet", family: "european", era: 405, region: "亞美尼亞", status: "living", note: "馬什托茨創；受希臘序影響", coach: "hy", parents: [{ id: "greek", kind: "influenced" }] },
  { id: "georgian", name: "喬治亞字母", sample: "Ⴀ", type: "alphabet", family: "european", era: 430, region: "喬治亞", status: "living", note: "卡特韋利語系；序受希臘影響", coach: "ka", parents: [{ id: "greek", kind: "influenced" }] },
  { id: "glagolitic", name: "格拉哥里字母", sample: "Ⰰ", type: "alphabet", family: "european", era: 862, region: "大摩拉維亞", status: "extinct", note: "西里爾兄弟為斯拉夫語造", parents: [{ id: "greek", kind: "derived" }] },
  { id: "cyrillic", name: "西里爾字母", sample: "А", type: "alphabet", family: "european", era: 893, region: "保加利亞", status: "living", note: "希臘安色爾＋格拉哥里", coach: "chu", parents: [{ id: "greek", kind: "derived" }, { id: "glagolitic", kind: "influenced" }] },
  { id: "tifinagh", name: "提非納字母", sample: "ⵣ", type: "abjad", family: "semitic", era: 300, region: "北非（柏柏爾）", status: "living", note: "源自利比亞-柏柏爾字母", parents: [{ id: "phoenician", kind: "derived" }] },

  // ── 粟特‧回鶻‧蒙古系 ──
  { id: "old-uyghur", name: "回鶻字母", sample: "ﺍ", type: "abjad", family: "mongolic", era: 800, region: "中亞", status: "extinct", note: "粟特字母豎寫", parents: [{ id: "sogdian", kind: "descendant" }] },
  { id: "mongolian", name: "蒙古文字", sample: "ᠠ", type: "abjad", family: "mongolic", era: 1204, region: "蒙古", status: "living", note: "回鶻字母寫蒙古語", parents: [{ id: "old-uyghur", kind: "descendant" }] },
  { id: "manchu", name: "滿文", sample: "ᠠ", type: "abjad", family: "mongolic", era: 1599, region: "滿洲", status: "extinct", note: "蒙古文加圈點", parents: [{ id: "mongolian", kind: "adapted" }] },
  { id: "todo", name: "托忒文", sample: "ᡐ", type: "abjad", family: "mongolic", era: 1648, region: "衛拉特蒙古", status: "extinct", note: "蒙古文改良標母音", parents: [{ id: "mongolian", kind: "derived" }] },

  // ── 婆羅米／印度系 ──
  { id: "brahmi", name: "婆羅米文", sample: "𑀓", type: "abugida", family: "brahmic", era: -300, region: "印度", status: "extinct", note: "印度系字母之源（源出存爭議）", parents: [{ id: "aramaic", kind: "derived" }] },
  { id: "gupta", name: "笈多文", sample: "𑀓", type: "abugida", family: "brahmic", era: 350, region: "北印度", status: "extinct", note: "北方婆羅米演成", parents: [{ id: "brahmi", kind: "descendant" }] },
  { id: "siddham", name: "悉曇文", sample: "𑖀", type: "abugida", family: "brahmic", era: 600, region: "印度／東亞", status: "extinct", note: "漢傳密教真言用字", parents: [{ id: "gupta", kind: "descendant" }] },
  { id: "nagari", name: "那格利文", sample: "न", type: "abugida", family: "brahmic", era: 700, region: "北印度", status: "extinct", note: "天城體前身", parents: [{ id: "gupta", kind: "descendant" }] },
  { id: "sharada", name: "夏拉達文", sample: "𑆯", type: "abugida", family: "brahmic", era: 800, region: "喀什米爾", status: "extinct", note: "西北婆羅米支", parents: [{ id: "gupta", kind: "descendant" }] },
  { id: "devanagari", name: "天城體", sample: "अ", type: "abugida", family: "brahmic", era: 1000, region: "北印度", status: "living", note: "梵文/印地文；佛教大乘梵本", coach: "sa", parents: [{ id: "nagari", kind: "descendant" }] },
  { id: "gujarati", name: "古吉拉特文", sample: "અ", type: "abugida", family: "brahmic", era: 1592, region: "古吉拉特", status: "living", note: "天城體草書", parents: [{ id: "devanagari", kind: "descendant" }] },
  { id: "modi", name: "莫迪文", sample: "𑘀", type: "abugida", family: "brahmic", era: 1600, region: "馬哈拉施特拉", status: "extinct", note: "那格利草書", parents: [{ id: "nagari", kind: "descendant" }] },
  { id: "gurmukhi", name: "古木基文", sample: "ੳ", type: "abugida", family: "brahmic", era: 1539, region: "旁遮普", status: "living", note: "錫克教經典用字", parents: [{ id: "sharada", kind: "descendant" }] },
  { id: "bengali", name: "孟加拉-阿薩姆文", sample: "অ", type: "abugida", family: "brahmic", era: 1000, region: "孟加拉", status: "living", note: "悉曇東支（高迪）", parents: [{ id: "siddham", kind: "descendant" }] },
  { id: "odia", name: "歐迪亞文", sample: "ଅ", type: "abugida", family: "brahmic", era: 1050, region: "奧迪沙", status: "living", note: "圓弧因貝葉書寫", parents: [{ id: "siddham", kind: "descendant" }] },
  { id: "tibetan", name: "藏文", sample: "ཀ", type: "abugida", family: "brahmic", era: 650, region: "西藏", status: "living", note: "吞彌據印度文造；大藏經", coach: "bo", parents: [{ id: "gupta", kind: "derived" }] },
  { id: "phags-pa", name: "八思巴文", sample: "ꡀ", type: "abugida", family: "brahmic", era: 1269, region: "元朝", status: "extinct", note: "藏文豎寫，元帝國通用", parents: [{ id: "tibetan", kind: "derived" }] },
  { id: "lepcha", name: "雷布查文", sample: "ᰀ", type: "abugida", family: "brahmic", era: 1700, region: "錫金", status: "living", note: "藏文衍生", parents: [{ id: "tibetan", kind: "derived" }] },
  { id: "limbu", name: "林布文", sample: "ᤀ", type: "abugida", family: "brahmic", era: 1740, region: "尼泊爾東", status: "living", note: "藏文衍生", parents: [{ id: "tibetan", kind: "derived" }] },
  { id: "tamil-brahmi", name: "泰米爾-婆羅米", sample: "𑀓", type: "abugida", family: "brahmic", era: -200, region: "南印度", status: "extinct", note: "南方婆羅米支", parents: [{ id: "brahmi", kind: "descendant" }] },
  { id: "pallava", name: "帕拉瓦文", sample: "𑀓", type: "abugida", family: "brahmic", era: 400, region: "南印度", status: "extinct", note: "東南亞諸文字之源", parents: [{ id: "brahmi", kind: "descendant" }] },
  { id: "grantha", name: "古蘭塔文", sample: "𑌅", type: "abugida", family: "brahmic", era: 500, region: "泰米爾地區", status: "extinct", note: "南印書寫梵文", parents: [{ id: "pallava", kind: "descendant" }] },
  { id: "vatteluttu", name: "瓦特盧圖文", sample: "𑀓", type: "abugida", family: "brahmic", era: 500, region: "南印度", status: "extinct", note: "泰米爾古草書", parents: [{ id: "tamil-brahmi", kind: "descendant" }] },
  { id: "tamil", name: "泰米爾文", sample: "அ", type: "abugida", family: "brahmic", era: 700, region: "泰米爾納德", status: "living", note: "源古蘭塔/瓦特盧圖", parents: [{ id: "grantha", kind: "descendant" }] },
  { id: "malayalam", name: "馬拉雅拉姆文", sample: "അ", type: "abugida", family: "brahmic", era: 830, region: "喀拉拉", status: "living", note: "古蘭塔衍生", parents: [{ id: "grantha", kind: "descendant" }] },
  { id: "kannada", name: "卡納達文", sample: "ಕ", type: "abugida", family: "brahmic", era: 1500, region: "卡納塔卡", status: "living", note: "卡丹巴/遮婁其支", parents: [{ id: "brahmi", kind: "descendant" }] },
  { id: "telugu", name: "泰盧固文", sample: "అ", type: "abugida", family: "brahmic", era: 1100, region: "安得拉", status: "living", note: "與卡納達同源", parents: [{ id: "brahmi", kind: "descendant" }] },
  { id: "sinhala", name: "僧伽羅文", sample: "අ", type: "abugida", family: "brahmic", era: 700, region: "斯里蘭卡", status: "living", note: "婆羅米＋古蘭塔影響", parents: [{ id: "brahmi", kind: "descendant" }] },
  { id: "old-mon", name: "古孟文", sample: "𑄀", type: "abugida", family: "brahmic", era: 550, region: "下緬甸", status: "extinct", note: "帕拉瓦東傳", parents: [{ id: "pallava", kind: "descendant" }] },
  { id: "burmese", name: "緬甸文", sample: "က", type: "abugida", family: "brahmic", era: 1050, region: "緬甸", status: "living", note: "源古孟文", parents: [{ id: "old-mon", kind: "descendant" }] },
  { id: "khmer", name: "高棉文", sample: "ក", type: "abugida", family: "brahmic", era: 611, region: "柬埔寨", status: "living", note: "帕拉瓦東傳；泰寮之源", parents: [{ id: "pallava", kind: "descendant" }] },
  { id: "thai", name: "泰文", sample: "ก", type: "abugida", family: "brahmic", era: 1283, region: "泰國", status: "living", note: "蘭甘亨王據高棉造", parents: [{ id: "khmer", kind: "derived" }] },
  { id: "lao", name: "寮文", sample: "ກ", type: "abugida", family: "brahmic", era: 1350, region: "寮國", status: "living", note: "源高棉/泰文", parents: [{ id: "khmer", kind: "derived" }] },
  { id: "cham", name: "占文", sample: "ꨀ", type: "abugida", family: "brahmic", era: 700, region: "占婆（越南南）", status: "living", note: "帕拉瓦東傳", parents: [{ id: "pallava", kind: "descendant" }] },
  { id: "kawi", name: "卡維文（古爪哇）", sample: "ꦲ", type: "abugida", family: "brahmic", era: 750, region: "爪哇", status: "extinct", note: "南島諸文字之源", parents: [{ id: "pallava", kind: "descendant" }] },
  { id: "javanese", name: "爪哇文", sample: "ꦲ", type: "abugida", family: "brahmic", era: 1500, region: "爪哇", status: "living", note: "卡維文後裔", parents: [{ id: "kawi", kind: "descendant" }] },
  { id: "balinese", name: "峇里文", sample: "ᬅ", type: "abugida", family: "brahmic", era: 1000, region: "峇里", status: "living", note: "卡維文後裔", parents: [{ id: "kawi", kind: "descendant" }] },
  { id: "baybayin", name: "貝貝因文", sample: "ᜊ", type: "abugida", family: "brahmic", era: 1300, region: "菲律賓", status: "living", note: "他加祿古字母", parents: [{ id: "kawi", kind: "derived" }] },
  { id: "lontara", name: "望加錫文", sample: "ᨀ", type: "abugida", family: "brahmic", era: 1500, region: "蘇拉威西", status: "living", note: "布吉斯語用字", parents: [{ id: "kawi", kind: "derived" }] },
  { id: "batak", name: "巴塔克文", sample: "ᯀ", type: "abugida", family: "brahmic", era: 1300, region: "蘇門答臘", status: "living", note: "帕拉瓦南傳", parents: [{ id: "pallava", kind: "derived" }] },

  // ── 漢字系 ──
  { id: "seal-script", name: "篆書", sample: "篆", type: "logographic", family: "eastasian", era: -220, region: "秦中國", status: "extinct", note: "金文整理，小篆統一", parents: [{ id: "chinese-oracle", kind: "descendant" }] },
  { id: "clerical", name: "隸書", sample: "隸", type: "logographic", family: "eastasian", era: -200, region: "漢中國", status: "extinct", note: "篆書簡化，漢字定型", parents: [{ id: "seal-script", kind: "descendant" }] },
  { id: "hanzi", name: "楷書漢字", sample: "漢", type: "logographic", family: "eastasian", era: 200, region: "中國", status: "living", note: "文言文；佛道儒原典", coach: "lzh", parents: [{ id: "clerical", kind: "descendant" }] },
  { id: "kanji", name: "日文漢字", sample: "字", type: "logographic", family: "eastasian", era: 500, region: "日本", status: "living", note: "漢字傳日", parents: [{ id: "hanzi", kind: "adapted" }] },
  { id: "hiragana", name: "平假名", sample: "あ", type: "syllabary", family: "eastasian", era: 800, region: "日本", status: "living", note: "漢字草書成音節", coach: "ja", parents: [{ id: "kanji", kind: "derived" }] },
  { id: "katakana", name: "片假名", sample: "ア", type: "syllabary", family: "eastasian", era: 800, region: "日本", status: "living", note: "取漢字偏旁成音節", parents: [{ id: "kanji", kind: "derived" }] },
  { id: "hanja", name: "韓文漢字", sample: "韓", type: "logographic", family: "eastasian", era: 400, region: "韓國", status: "living", note: "漢字傳韓", parents: [{ id: "hanzi", kind: "adapted" }] },
  { id: "chu-nom", name: "喃字", sample: "𡨸", type: "logographic", family: "eastasian", era: 1200, region: "越南", status: "extinct", note: "據漢字造越南字", parents: [{ id: "hanzi", kind: "derived" }] },
  { id: "khitan", name: "契丹文", sample: "𘬞", type: "logosyllabic", family: "eastasian", era: 920, region: "遼", status: "extinct", note: "仿漢字造契丹字", parents: [{ id: "hanzi", kind: "derived" }] },
  { id: "jurchen", name: "女真文", sample: "𠴓", type: "logosyllabic", family: "eastasian", era: 1119, region: "金", status: "extinct", note: "據契丹/漢字造", parents: [{ id: "khitan", kind: "derived" }] },
  { id: "tangut", name: "西夏文", sample: "𗀀", type: "logographic", family: "eastasian", era: 1036, region: "西夏", status: "extinct", note: "仿漢字另造六千字", parents: [{ id: "hanzi", kind: "derived" }] },
  { id: "nushu", name: "女書", sample: "𛈁", type: "syllabary", family: "eastasian", era: 1500, region: "湖南江永", status: "extinct", note: "女性專用音節字", parents: [{ id: "hanzi", kind: "derived" }] },
  { id: "bopomofo", name: "注音符號", sample: "ㄅ", type: "syllabary", family: "eastasian", era: 1913, region: "中華民國", status: "living", note: "取漢字部件標音", parents: [{ id: "hanzi", kind: "derived" }] },
  { id: "yi", name: "彝文", sample: "ꀀ", type: "syllabary", family: "eastasian", era: 1500, region: "中國西南", status: "living", note: "古彝文（源出存爭議）", parents: [{ id: "hanzi", kind: "influenced" }] },

  // ── 中美洲系 ──
  { id: "epi-olmec", name: "地峽文字", sample: "◈", type: "logosyllabic", family: "mesoamerican", era: -500, region: "中美洲", status: "undeciphered", note: "奧爾梅克後續", parents: [{ id: "zapotec", kind: "influenced" }] },
  { id: "maya", name: "馬雅文字", sample: "𓀀", type: "logosyllabic", family: "mesoamerican", era: -250, region: "中美洲", status: "extinct", note: "美洲最完整文字（獨立）", parents: [{ id: "epi-olmec", kind: "influenced" }] },

  // ── 獨立／近代發明 ──
  { id: "hangul", name: "諺文（韓字）", sample: "한", type: "featural", family: "independent", era: 1443, region: "朝鮮", status: "living", note: "世宗創特徵文字（八思巴影響存爭議）", parents: [{ id: "phags-pa", kind: "influenced" }] },
  { id: "cherokee", name: "切羅基音節文字", sample: "Ꭰ", type: "syllabary", family: "independent", era: 1821, region: "北美", status: "living", note: "塞闊雅借拉丁字形、值自創", parents: [{ id: "latin", kind: "influenced" }] },
  { id: "canadian-syllabics", name: "加拿大原住民音節文字", sample: "ᐊ", type: "abugida", family: "independent", era: 1840, region: "加拿大", status: "living", note: "受天城體與速記啟發", parents: [{ id: "devanagari", kind: "influenced" }] },
  { id: "vai", name: "瓦伊音節文字", sample: "ꔀ", type: "syllabary", family: "independent", era: 1833, region: "賴比瑞亞", status: "living", note: "西非自創音節字", parents: [] },
  { id: "nko", name: "恩科字母", sample: "ߐ", type: "alphabet", family: "independent", era: 1949, region: "西非", status: "living", note: "曼丁語右行字母（受阿拉伯啟發）", parents: [{ id: "arabic", kind: "influenced" }] },
  { id: "adlam", name: "阿德拉姆字母", sample: "𞤀", type: "alphabet", family: "independent", era: 1989, region: "西非（富拉）", status: "living", note: "少年自創富拉字母", parents: [] },
  { id: "osmanya", name: "奧斯曼亞字母", sample: "𐒀", type: "alphabet", family: "independent", era: 1922, region: "索馬利亞", status: "extinct", note: "索馬利語自創字母", parents: [] },
];

// 工具：依 id 取節點
export function getScriptNode(id: string): ScriptNode | undefined {
  return SCRIPT_NODES.find((n) => n.id === id);
}
export const SCRIPT_TYPE_LABEL: Record<ScriptType, string> = {
  proto: "原型文字", logographic: "語素文字", logosyllabic: "語素音節", syllabary: "音節文字",
  abjad: "輔音字母", abugida: "元音附標", alphabet: "全音素字母", featural: "特徵文字", undeciphered: "未解讀",
};
export const EDGE_KIND_LABEL: Record<EdgeKind, string> = {
  descendant: "演化", derived: "據以創製", adapted: "改用", influenced: "影響（較鬆/有爭議）",
};
