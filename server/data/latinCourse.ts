// ============================================================================
// 教會拉丁文課程（LINGVA LATINA PRO CATHOLICIS）逐課策展資料。
// 使用者實際在上的「教會拉丁文（一）· 羅梅洛班」課程，每週一份講義。
// 純策展、零 AI、零 DB —— 供 /coach/la/course 課程複習頁驅動：
//   母音子音複習 / 單字 / 認讀拼讀規則 / 聽寫 / 發音跟讀。
// 新增一課 = 在 LESSONS 加一筆 CourseLesson。目前只 la 有課程。
// 例句／中譯一律沿用講義本身（教會式發音、天主教用語、繁體中文）。
// ============================================================================

export interface CoursePhone {
  form: string;      // 字母／字母組合／拼讀情境（如 "c 在 e、i 前"、"ae"）
  sound: string;     // 讀音（IPA + 中文提示）
  rule?: string;     // 規則說明
  examples: string;  // 例字（空白分隔，取自講義）
}
export interface CourseVocab {
  latin: string;     // 拉丁文（單字或短語）
  zh: string;        // 繁體中文釋義
  note?: string;     // 補充（縮寫／出處／發音提示）
}
export interface CourseLesson {
  id: string;
  no: number;
  title: string;
  subtitle?: string;
  date?: string;
  vowels: CoursePhone[];      // 單母音
  diphthongs: CoursePhone[];  // 雙母音
  consonants: CoursePhone[];  // 子音與拼讀規則
  vocab: CourseVocab[];       // 單字／禮儀短語
}
export interface CourseSpec {
  language: string;
  title: string;
  intro: string;
  ttsLang: string;
  lessons: CourseLesson[];
}

// ── 第 1 課（第 1–2 堂）：字母、發音、音節、重音 ──────────────────────────────
const LESSON_1: CourseLesson = {
  id: "l1",
  no: 1,
  title: "字母與發音 · Litterae et Pronuntiatio",
  subtitle: "第 1–2 堂：字母、單雙母音、子音拼讀、音節與重音",
  date: "2026-07-01",
  vowels: [
    { form: "a", sound: "[a] 阿", examples: "papa a ab ad" },
    { form: "e", sound: "[e] 耶", examples: "et me te sed ex que ave" },
    { form: "i", sound: "[i] 伊", examples: "in hic ibi enim via vita" },
    { form: "o", sound: "[o] 喔", examples: "non do ego homo oro" },
    { form: "u", sound: "[u] 烏", examples: "cum tu manus" },
    { form: "y", sound: "[i] 伊（希臘外來字）", examples: "hymnus mysterium" },
    { form: "ae（Æ）", sound: "[e] 念 e", rule: "ae 合成一個 e 音", examples: "saeculum saepe Galilaea" },
    { form: "oe（Œ）", sound: "[e] 念 e", rule: "oe 合成一個 e 音", examples: "poena proelium" },
  ],
  diphthongs: [
    { form: "au", sound: "[au̯] ㄠ", examples: "aut laudo autem Paulus" },
    { form: "eu", sound: "[eu̯] ㄟㄨ", examples: "Europa seu heus euge" },
    { form: "ei", sound: "[ei̯] ㄟ", examples: "deinde" },
    { form: "ui", sound: "[ui̯]", examples: "cui hui huic" },
  ],
  consonants: [
    // 基本子音
    { form: "p", sound: "[p] ㄅ", rule: "不送氣", examples: "papa populus panis" },
    { form: "b", sound: "[b] ㆠ 濁音", rule: "如閩南語「肉 bah」", examples: "beatus bonus debita" },
    { form: "t", sound: "[t] ㄉ", rule: "不送氣", examples: "testamentum totus tuus terra" },
    { form: "t + i + 母音", sound: "[ts] ㄗ", rule: "ti 後接母音、且前面無 s/t/x", examples: "laetitia gratia potentia" },
    { form: "d", sound: "[d] 濁音", rule: "如日語「ときどき」", examples: "Deus Dominus de" },
    { form: "f", sound: "[f] ㄈ", examples: "filius filia festum feria" },
    { form: "m", sound: "[m] ㄇ", examples: "Maria enim familia missa" },
    { form: "n", sound: "[n] ㄋ", examples: "nam non mensa nomen" },
    { form: "l", sound: "[l] ㄌ", examples: "laudo culpa apostolus" },
    { form: "r", sound: "[r] 彈舌", rule: "練習：tl > tr > br/pr > gr", examples: "rosa gloria gratia pro per Petrus" },
    // c 的軟硬
    { form: "c（ca/co/cu、字尾）", sound: "[k] ㄍ", rule: "不送氣；後接 a/o/u 或在字尾", examples: "cum culpa coram nunc" },
    { form: "c 在 e、i 前", sound: "[tʃ]", rule: "後有 e/i（含 ae/oe），但前面無 s/x", examples: "cena caelum facio cibus dicit" },
    { form: "ch", sound: "[k] ㄍ", rule: "外來語居多", examples: "Christus chorus Pascha" },
    { form: "k", sound: "[k] ㄍ", rule: "極少，外來語", examples: "Kyrie kalendae" },
    { form: "qu", sound: "[kw]", rule: "後面必接母音", examples: "qui quoque aqua antiquus" },
    // g 的軟硬
    { form: "g（ga/go/gu）", sound: "[g] ㆣ 濁音", rule: "如閩南語「牛 gû」", examples: "gaudium gloria ergo frango" },
    { form: "g 在 e、i 前", sound: "[dʒ]", rule: "後接 e/i", examples: "ager angelus regina evangelium" },
    { form: "gn", sound: "[ɲ] ㄬ", rule: "想成 ng + [j]", examples: "agnus regnum magnus signum" },
    // sc 的軟硬
    { form: "sc（sca/sco/scu）", sound: "[sk] ㄙㄍ", examples: "episcopus discumbere" },
    { form: "sc 在 e、i 前", sound: "[ʃ]", rule: "後接 e/i（含 ae/oe/ei/eu）", examples: "scio discipulus nescio ascendit" },
    // s 的清濁
    { form: "s", sound: "[s] ㄙ", examples: "sine sum es est" },
    { form: "s 在母音之間", sound: "[z]", rule: "夾在兩母音中間濁化", examples: "causa ecclesia rosa Josephus" },
    // x
    { form: "x", sound: "[ks]", examples: "pax lex rex calix crux dextera" },
    { form: "x 在母音之間", sound: "[gz]", rule: "夾在兩母音中間濁化", examples: "dixit exaudio exemplum" },
    { form: "xc 在 e、i 前", sound: "[kʃ]", examples: "in excelsis excipio" },
    // v / j
    { form: "v / u（母音前）", sound: "[v] ㄪ", rule: "教會式念 v，非古典 w", examples: "vita voluntas servus" },
    { form: "j / i（母音前）", sound: "[j] ㄧ 子音", examples: "Jesus Jacobus justus" },
    // h 與外來語 ph/th
    { form: "h", sound: "不發音", examples: "hora hodie hic hymnus" },
    { form: "h 在 i 與 i 之間", sound: "[k] ㄍ", examples: "mihi nihil" },
    { form: "ph", sound: "[f] ㄈ", rule: "外來語", examples: "propheta Josephus philosophia" },
    { form: "th", sound: "[t] ㄉ", rule: "外來語", examples: "Thomas Sabaoth theologia" },
  ],
  vocab: [
    // 高頻單字
    { latin: "Deus", zh: "神／天主" },
    { latin: "Dominus", zh: "主／上主" },
    { latin: "Pater", zh: "父" },
    { latin: "Filius", zh: "子" },
    { latin: "Spiritus Sanctus", zh: "聖神" },
    { latin: "Iesus", zh: "耶穌", note: "亦寫 Jesus" },
    { latin: "Maria", zh: "瑪利亞" },
    { latin: "pax", zh: "平安" },
    { latin: "gloria", zh: "光榮" },
    { latin: "fides", zh: "信德" },
    { latin: "vita", zh: "生命" },
    { latin: "sanctus", zh: "聖的／聖哉" },
    { latin: "gratia", zh: "恩寵", note: "念 gra-tsia" },
    { latin: "ecclesia", zh: "教會", note: "s 母音間念 z" },
    { latin: "caelum", zh: "天", note: "c 念 [tʃ]，念 che-lum" },
    { latin: "agnus", zh: "羔羊", note: "gn 念 [ɲ]" },
    { latin: "amen", zh: "阿們" },
    // 禮儀短語（EXERCITATIO / APPENDIX）
    { latin: "In nomine Patris, et Filii, et Spiritus Sancti.", zh: "因父、及子、及聖神之名。", note: "聖號經" },
    { latin: "Gloria Patri, et Filio, et Spiritui Sancto.", zh: "光榮歸於父、及子、及聖神。", note: "聖三光榮經" },
    { latin: "sicut erat in principio, et nunc, et semper.", zh: "起初如何，今日亦然，直到永遠。", note: "光榮經續" },
    { latin: "in saecula saeculorum. Amen.", zh: "世世無窮。阿們。" },
    { latin: "panis angelicus", zh: "天使神糧" },
    { latin: "mysterium fidei", zh: "信德的奧蹟" },
    { latin: "Iesus Nazarenus Rex Iudaeorum", zh: "納匝肋人耶穌，猶太人的君王", note: "INRI" },
    { latin: "Ad maiorem Dei gloriam", zh: "愈顯主榮", note: "AMDG" },
    { latin: "Et cum spiritu tuo.", zh: "也與你的心靈同在。" },
    { latin: "Exaudi nos, Domine.", zh: "求主俯聽我們。" },
    { latin: "Kyrie, eleison.", zh: "上主，求禰垂憐。", note: "希臘文禮儀用語" },
    { latin: "Miserere nobis, Domine.", zh: "上主，求禰垂憐。" },
    { latin: "Ave!", zh: "萬福！／你好！" },
    { latin: "Salve!", zh: "你好！" },
  ],
};

const la: CourseSpec = {
  language: "la",
  title: "教會拉丁文（一）· 羅梅洛班",
  intro: "LINGVA LATINA PRO CATHOLICIS。跟著你實際上的課程逐課複習：字母與教會式發音、單雙母音、子音拼讀規則、禮儀單字。複習分五塊——母音子音、單字、認讀（拼讀規則）、聽寫、發音跟讀。",
  ttsLang: "it-IT",
  lessons: [LESSON_1],
};

const COURSES: Record<string, CourseSpec> = { la };

/** 回傳該語言的課程資料（無則 null）。 */
export function courseForClient(language: string): CourseSpec | null {
  return COURSES[language] ?? null;
}
