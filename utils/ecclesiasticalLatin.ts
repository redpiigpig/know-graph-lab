// ============================================================================
// 教會拉丁文（羅馬式發音）→ 義大利語拼寫，供瀏覽器語音朗讀
//
// 沒有任何裝置內建拉丁文語音，但羅馬式教會發音本來就是照義大利語音韻讀拉丁文：
// c 在 e/i 前讀 [tʃ]、gn 讀 [ɲ]、sc 在 e/i 前讀 [ʃ]、h 不發音——這些義大利語聲線
// 全部天生正確。真正會讀錯的是**拼寫**：義大利文沒有 ae/oe/j/y/ph/th，而 ti+母音
// 在教會拉丁讀 [tsi]（gratia = 「gra-zia」），義大利語卻照字面讀 [ti]。
//
// 所以這裡不是音譯，是把拉丁文改寫成「同一個音的義大利文拼法」再交給語音引擎。
// 每條規則都對得上教會拉丁發音表；改寫後的字串只給 TTS，畫面上永遠是原拼寫。
// ============================================================================

/** 長音符號與尾註記號：詞表印 ā ē ī ō ū，語音引擎會讀成亂碼或整個放棄。 */
const MACRONS: Record<string, string> = {
  ā: "a", ē: "e", ī: "i", ō: "o", ū: "u", ȳ: "y",
  ă: "a", ĕ: "e", ĭ: "i", ŏ: "o", ŭ: "u",
  æ: "ae", œ: "oe", ë: "e", ï: "i", ö: "o", ü: "u",
};

/** 體例記號不是拉丁文，不該念出來。 */
const APPARATUS = /[†℣℟*]|\((\d+)\)|\[[^\]]*\]|^[VR]\.\s*/gu;

/**
 * 行首的節號／段號是版面，不是經文。留著的話義大利語聲線會在每一節前面唸
 * 「uno、due、tre」——聽起來像有人在拉丁文中間報數。
 */
const LEADING_NUMBER = /^\s*\d+[.、]?[\s　]+/u;

/**
 * 兩個中世紀既有的拼法就是這樣讀的：mihi 讀 [ˈmiki]、nihil 讀 [ˈnikil]，
 * 而 michi／nichil 正是中世紀抄本自己的寫法，義大利語的 chi = [ki] 剛好對上。
 */
const LEXICAL: Array<[RegExp, string]> = [
  [/\bmihi\b/gu, "michi"],
  [/\bnihil\b/gu, "nichil"],
  [/\bnihilo\b/gu, "nichilo"],
];

const RULES: Array<[RegExp, string]> = [
  // j 是子音性的 i，y 一律讀 [i]
  [/j/gu, "i"],
  [/y/gu, "i"],
  // 教會拉丁的 ae/oe 是單母音 [e]，義大利語會拆成兩個音節
  [/ae|oe/gu, "e"],
  // 希臘借字的送氣塞音在教會拉丁已失去送氣
  [/ph/gu, "f"],
  [/th/gu, "t"],
  [/rh/gu, "r"],
  // ch 一律 [k]。義大利語的 ch 只在 e/i 前才是 [k]，其餘位置（Christus 的 chr、
  // charitas 的 cha）都得改寫成 c，否則會讀成 [tʃ]。
  [/ch(?![ei])/gu, "c"],
  // xc 在 e/i 前是 [kʃ]：excelsis 讀 ek-SHEL-sis。義大利語的 sc+e/i 就是 [ʃ]，
  // 所以把 x 拆成 c+s，讓 sce 自己成立。單獨的 x 不動——義大利語讀 [ks] 已對。
  [/x(?=c[ei])/gu, "cs"],
  // ti + 母音讀 [tsi]，但前面是 s、t、x 時不變（hostia、Attius、mixtio）
  [/(^|[^stx])ti(?=[aeou])/gu, "$1zi"],
];

/** 一行拉丁文改寫成義大利語拼寫；畫面文字不受影響。 */
export function toEcclesiasticalSpeech(latin: string): string {
  if (!latin) return "";
  let text = latin.normalize("NFC").replace(APPARATUS, " ").replace(LEADING_NUMBER, "");
  text = text.replace(/[āēīōūȳăĕĭŏŭæœëïöü]/gu, (ch) => MACRONS[ch] || ch);
  // 大寫的人名（DEMETRIUS、TISSERANT）有些語音引擎會逐字母拼讀
  text = text.toLowerCase();
  // 剩下的組合附加符號（拉丁文本身不用，但來源檔偶爾帶著）
  text = text.normalize("NFD").replace(/[̀-ͯ]/gu, "");
  for (const [pattern, replacement] of LEXICAL) text = text.replace(pattern, replacement);
  for (const [pattern, replacement] of RULES) text = text.replace(pattern, replacement);
  return text.replace(/\s+/gu, " ").trim();
}

/**
 * 詞表印的是字典形（`ōrō, ōrāre, ōrāvī, ōrātus`），整串念出來像在念變化表。
 * 朗讀單字時只念第一個形式。
 */
export function headwordForSpeech(forms: string): string {
  return toEcclesiasticalSpeech(String(forms || "").split(",")[0]);
}
