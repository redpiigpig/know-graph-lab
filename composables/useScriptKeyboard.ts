// ============================================================================
// 通用「轉寫鍵盤」工廠 — 打英文/羅馬字即時對照成目標文字（字母系文字，無狀態）
// 與 useGreekKeyboard / useHebrewKeyboard / useKanaKeyboard 並列，但這支是「資料驅動」：
//   給一份 Latin→目標字母的單鍵對照表（+ 可選的點選額外字母 / 附加符號），
//   就生出一個和希臘/希伯來鍵盤同介面的 handler（onKeydown / insert / palette…）。
// 適用「1 鍵 → 1 字」的字母系文字：西里爾、科普特、阿拉伯、敘利亞、亞美尼亞、喬治亞。
// 不適用 abugida/音節文字（天城體 sa/pra、藏文 bo、吉茲 gez）——那些需要有狀態的 IME，另議。
// ============================================================================

export interface ScriptKeyEntry {
  ch: string;       // 目標字
  latin?: string;   // 對照表顯示的鍵（點選額外字母可不填）
  label?: string;   // 對照表附註
}
export interface ScriptSpec {
  key: string;                       // = Coach.keyboard 值（cyrillic / coptic / arabic / syriac / armenian / georgian）
  label: string;                     // 工具列顯示名（如「西里爾鍵盤」）
  hint: string;                      // 工具列一行提示
  rtl?: boolean;                     // 由右至左（阿拉伯 / 敘利亞）
  bicameral?: boolean;              // 有大小寫：大寫鍵自動產生大寫字母（西里爾 / 科普特 / 亞美尼亞）
  caseSensitive?: boolean;          // 大寫鍵當成「不同字母鍵」直接查表（阿拉伯 / 敘利亞 / 喬治亞）
  map: Record<string, string>;       // 單鍵 Latin → 目標字（caseSensitive 時含大寫鍵）
  extras?: ScriptKeyEntry[];        // 點選插入的額外字母（無單鍵）
  marks?: { mark: string; label: string }[]; // 點選插入的附加符號（母音點 / harakat…）
}

// 目標字母（含結合附加符號）的偵測：用於游標前是否為字母
const COMBINING = /[̀-ͯ҃-҉֑-ׇؐ-ًؚ-ٰٟۖ-ܑۭܰ-݊॑-॔็-๎]/;
function isWordChar(ch: string): boolean {
  return !!ch && !/\s/.test(ch);
}

type SetValue = (value: string, cursor: number) => void;

export function makeScriptKeyboard(spec: ScriptSpec) {
  function targetFor(k: string): string | undefined {
    if (spec.caseSensitive) return spec.map[k];
    const lower = k.toLowerCase();
    const base = spec.map[lower];
    if (!base) return undefined;
    return spec.bicameral && k !== lower ? base.toLocaleUpperCase() : base;
  }

  function insert(el: HTMLTextAreaElement, text: string, setValue: SetValue) {
    const start = el.selectionStart ?? el.value.length;
    const end = el.selectionEnd ?? start;
    const before = el.value.slice(0, start) + text;
    setValue(before + el.value.slice(end), before.length);
  }

  // keydown 攔截：回傳 true 表示已處理（呼叫端視為已 preventDefault）
  function onKeydown(e: KeyboardEvent, el: HTMLTextAreaElement, setValue: SetValue): boolean {
    if (e.ctrlKey || e.metaKey || e.altKey) return false;
    const k = e.key;
    if (k.length !== 1) return false; // Enter/Backspace/方向鍵…照常
    const start = el.selectionStart ?? el.value.length;
    const end = el.selectionEnd ?? start;
    const head = el.value.slice(0, start);
    const tail = el.value.slice(end);

    const g = targetFor(k);
    if (g) {
      e.preventDefault();
      const head2 = head + g;
      setValue(head2 + tail, head2.length);
      return true;
    }
    if (k === " ") {
      e.preventDefault();
      const head2 = head + " ";
      setValue(head2 + tail, head2.length);
      return true;
    }
    return false;
  }

  // 對照表（單鍵字母 + 額外字母）
  const palette: ScriptKeyEntry[] = [
    ...Object.entries(spec.map).map(([latin, ch]) => ({ latin, ch })),
    ...(spec.extras ?? []),
  ];

  return {
    key: spec.key,
    label: spec.label,
    hint: spec.hint,
    rtl: !!spec.rtl,
    onKeydown,
    insert,
    palette,
    marks: spec.marks ?? [],
  };
}

// ════════════════════════════════════════════════════════════════════════════
//  各文字對照表（單鍵走最常見字母，其餘字母與符號放 extras/marks 點選）
// ════════════════════════════════════════════════════════════════════════════

// 西里爾（教會斯拉夫 chu 用；含教會斯拉夫古字母）
const cyrillic: ScriptSpec = {
  key: "cyrillic", label: "西里爾鍵盤", hint: "打 a→а、b→б、c→ц、j→й…；ж ч ш щ ю я 與古字母在對照表點選", bicameral: true,
  map: {
    a: "а", b: "б", v: "в", g: "г", d: "д", e: "е", z: "з", i: "и",
    j: "й", k: "к", l: "л", m: "м", n: "н", o: "о", p: "п", r: "р",
    s: "с", t: "т", u: "у", f: "ф", h: "х", c: "ц", y: "ы",
  },
  extras: [
    { ch: "ж", label: "zh" }, { ch: "ч", label: "ch" }, { ch: "ш", label: "sh" }, { ch: "щ", label: "shch" },
    { ch: "ю", label: "yu" }, { ch: "я", label: "ya" }, { ch: "э", label: "e" }, { ch: "ё", label: "yo" },
    { ch: "ъ", label: "硬音" }, { ch: "ь", label: "軟音" },
    { ch: "і", label: "十進 і" }, { ch: "ѣ", label: "yat ѣ" }, { ch: "ѡ", label: "omega ѡ" },
    { ch: "ѫ", label: "大yus ѫ" }, { ch: "ѧ", label: "小yus ѧ" }, { ch: "ѱ", label: "psi ѱ" },
    { ch: "ѯ", label: "ksi ѯ" }, { ch: "ѳ", label: "fita ѳ" }, { ch: "ѵ", label: "izhitsa ѵ" },
  ],
};

// 科普特（cop 用；希臘衍生 + 7 個世俗體字母）
const coptic: ScriptSpec = {
  key: "coptic", label: "科普特鍵盤", hint: "打 a→ⲁ、b→ⲃ、q→ⲑ、w→ⲱ…；7 個世俗體字母在對照表點選", bicameral: true,
  map: {
    a: "ⲁ", b: "ⲃ", g: "ⲅ", d: "ⲇ", e: "ⲉ", z: "ⲍ", h: "ⲏ", q: "ⲑ",
    i: "ⲓ", k: "ⲕ", l: "ⲗ", m: "ⲙ", n: "ⲛ", c: "ⲝ", o: "ⲟ", p: "ⲡ",
    r: "ⲣ", s: "ⲥ", t: "ⲧ", u: "ⲩ", f: "ⲫ", x: "ⲭ", y: "ⲯ", w: "ⲱ",
  },
  extras: [
    { ch: "ϣ", label: "shai ϣ" }, { ch: "ϥ", label: "fai ϥ" }, { ch: "ϧ", label: "khai ϧ" },
    { ch: "ϩ", label: "hori ϩ" }, { ch: "ϫ", label: "janja ϫ" }, { ch: "ϭ", label: "chima ϭ" },
    { ch: "ϯ", label: "ti ϯ" },
  ],
};

// 阿拉伯（ar 用；RTL，大寫鍵當不同字母）
const arabic: ScriptSpec = {
  key: "arabic", label: "阿拉伯鍵盤", hint: "打 a→ا、b→ب、c→ش、e→ع、x→خ；大寫 H ح S ص T ط…；母音符在對照表點選", rtl: true, caseSensitive: true,
  map: {
    a: "ا", b: "ب", t: "ت", v: "ث", j: "ج", H: "ح", x: "خ", d: "د",
    V: "ذ", r: "ر", z: "ز", s: "س", c: "ش", S: "ص", D: "ض", T: "ط",
    Z: "ظ", e: "ع", g: "غ", f: "ف", q: "ق", k: "ك", l: "ل", m: "م",
    n: "ن", h: "ه", w: "و", y: "ي",
  },
  extras: [
    { ch: "ء", label: "hamza ء" }, { ch: "أ", label: "أ" }, { ch: "إ", label: "إ" }, { ch: "آ", label: "آ" },
    { ch: "ة", label: "ta marbuta ة" }, { ch: "ى", label: "alif maqsura ى" },
    { ch: "ؤ", label: "ؤ" }, { ch: "ئ", label: "ئ" }, { ch: "لا", label: "لا" },
  ],
  marks: [
    { mark: "َ", label: "fatha ـَ" }, { mark: "ِ", label: "kasra ـِ" }, { mark: "ُ", label: "damma ـُ" },
    { mark: "ْ", label: "sukun ـْ" }, { mark: "ّ", label: "shadda ـّ" },
    { mark: "ً", label: "tanwin fath ـً" }, { mark: "ٍ", label: "tanwin kasr ـٍ" }, { mark: "ٌ", label: "tanwin damm ـٌ" },
  ],
};

// 敘利亞（syr 用；RTL，Estrangela 字母；大寫 T 當 teth）
const syriac: ScriptSpec = {
  key: "syriac", label: "敘利亞鍵盤", hint: "打 a→ܐ、b→ܒ、v→ܘ、x→ܚ、e→ܥ、w→ܫ；大寫 T→ܛ；母音點在對照表點選", rtl: true, caseSensitive: true,
  map: {
    a: "ܐ", b: "ܒ", g: "ܓ", d: "ܕ", h: "ܗ", v: "ܘ", z: "ܙ", x: "ܚ",
    T: "ܛ", y: "ܝ", k: "ܟ", l: "ܠ", m: "ܡ", n: "ܢ", s: "ܣ", e: "ܥ",
    p: "ܦ", c: "ܨ", q: "ܩ", r: "ܪ", w: "ܫ", t: "ܬ",
  },
  marks: [
    { mark: "ܰ", label: "ptaha ܰ" }, { mark: "ܶ", label: "rbasa ܶ" }, { mark: "ܺ", label: "hbasa ܺ" },
    { mark: "ܽ", label: "esasa ܽ" }, { mark: "̈", label: "syame ̈" },
  ],
};

// 亞美尼亞（hy 用；大小寫，核心字母走單鍵，其餘點選）
const armenian: ScriptSpec = {
  key: "armenian", label: "亞美尼亞鍵盤", hint: "打 a→ա、b→բ、g→գ…；其餘字母在對照表點選", bicameral: true,
  map: {
    a: "ա", b: "բ", g: "գ", d: "դ", e: "ե", z: "զ", t: "թ", i: "ի",
    l: "լ", k: "կ", h: "հ", m: "մ", y: "յ", n: "ն", s: "ս", o: "ո",
    p: "պ", r: "ր", v: "վ", x: "խ", c: "ց", j: "ջ", f: "ֆ",
  },
  extras: [
    { ch: "է", label: "ē է" }, { ch: "ը", label: "ə ը" }, { ch: "ժ", label: "ž ժ" }, { ch: "ծ", label: "c ծ" },
    { ch: "ձ", label: "j ձ" }, { ch: "ղ", label: "ł ղ" }, { ch: "ճ", label: "č ճ" }, { ch: "շ", label: "š շ" },
    { ch: "չ", label: "čʿ չ" }, { ch: "ռ", label: "ṙ ռ" }, { ch: "ւ", label: "w ւ" }, { ch: "փ", label: "pʿ փ" },
    { ch: "ք", label: "kʿ ք" }, { ch: "օ", label: "ō օ" }, { ch: "տ", label: "t տ" },
  ],
};

// 喬治亞（ka 用；unicase，大寫鍵當送氣/擠喉對立字母）
const georgian: ScriptSpec = {
  key: "georgian", label: "喬治亞鍵盤", hint: "打 a→ა、b→ბ…；大寫 T→ტ P→ფ K→ქ S→შ C→ჩ 等對立字母；其餘點選", caseSensitive: true,
  map: {
    a: "ა", b: "ბ", g: "გ", d: "დ", e: "ე", v: "ვ", z: "ზ", T: "თ",
    i: "ი", k: "კ", l: "ლ", m: "მ", n: "ნ", o: "ო", p: "პ", J: "ჟ",
    r: "რ", s: "ს", t: "ტ", u: "უ", P: "ფ", q: "ქ", R: "ღ", Q: "ყ",
    S: "შ", C: "ჩ", c: "ც", Z: "ძ", w: "წ", W: "ჭ", x: "ხ", j: "ჯ", h: "ჰ",
  },
};

export const SCRIPT_SPECS: Record<string, ScriptSpec> = {
  cyrillic, coptic, arabic, syriac, armenian, georgian,
};

export function getScriptKeyboard(key: string | undefined) {
  if (!key) return null;
  const spec = SCRIPT_SPECS[key];
  return spec ? makeScriptKeyboard(spec) : null;
}

// 給測試/UI 用：純函式版的「一鍵轉一字」（不含游標）
export function translitChar(specKey: string, k: string): string | undefined {
  const spec = SCRIPT_SPECS[specKey];
  if (!spec) return undefined;
  if (spec.caseSensitive) return spec.map[k];
  const lower = k.toLowerCase();
  const base = spec.map[lower];
  if (!base) return undefined;
  return spec.bicameral && k !== lower ? base.toLocaleUpperCase() : base;
}
