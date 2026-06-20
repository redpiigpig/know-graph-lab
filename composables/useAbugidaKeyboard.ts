// ============================================================================
// Abugida / 音節文字「鍵盤」 — 天城體(梵/俗語)、吉茲(fidäl)、藏文
// 這些文字非「1 鍵 1 字」（子音帶固有母音、母音以記號結合、有疊寫/音節階），
// 故不能用 useScriptKeyboard 的無狀態工廠。本檔用「整詞 roman 緩衝 + 逐鍵重轉寫」：
//   每打一鍵 → 把目前這個詞的 roman 緩衝整串丟給純函式 translit() → 重算目標文字 →
//   用新結果取代螢幕上「這個詞」舊的那段（記 outLen）。遇空白/標點/Enter 就 commit 清緩衝。
// 純 translit 函式可單測（test/coach/abugida-keyboard.spec.ts）。
// ============================================================================

type SetValue = (value: string, cursor: number) => void;

// ── 工具：longest-match 斷詞器（給定 key 集合，回最長命中的 key）──
function longest(keys: string[], s: string, i: number): string | null {
  for (const k of keys) if (s.startsWith(k, i)) return k;
  return null;
}
function byLenDesc(obj: Record<string, unknown>): string[] {
  return Object.keys(obj).sort((a, b) => b.length - a.length);
}

// ════════════════════════════════════════════════════════════════════════════
//  1) 天城體 Devanāgarī（梵 sa／半摩揭陀俗語 pra）— ITRANS 風格
// ════════════════════════════════════════════════════════════════════════════
const DV_VOWELS: Record<string, [string, string]> = { // [獨立, 母音記號 matra]
  a: ["अ", ""], aa: ["आ", "ा"], A: ["आ", "ा"], i: ["इ", "ि"], ii: ["ई", "ी"], I: ["ई", "ी"],
  u: ["उ", "ु"], uu: ["ऊ", "ू"], U: ["ऊ", "ू"], R: ["ऋ", "ृ"], e: ["ए", "े"], ai: ["ऐ", "ै"],
  o: ["ओ", "ो"], au: ["औ", "ौ"],
};
const DV_CONS: Record<string, string> = {
  k: "क", kh: "ख", g: "ग", gh: "घ", G: "ङ", ch: "च", c: "च", Ch: "छ", chh: "छ", j: "ज", jh: "झ", J: "ञ",
  T: "ट", Th: "ठ", D: "ड", Dh: "ढ", N: "ण", t: "त", th: "थ", d: "द", dh: "ध", n: "न",
  p: "प", ph: "फ", f: "फ", b: "ब", bh: "भ", m: "म", y: "य", r: "र", l: "ल", v: "व", w: "व",
  sh: "श", z: "श", Sh: "ष", S: "ष", s: "स", h: "ह", L: "ळ", x: "क्ष", GY: "ज्ञ",
};
const DV_SPECIAL: Record<string, string> = { M: "ं", H: "ः", "~": "ँ", OM: "ॐ" };
const DV_VIRAMA = "्";
const DV_KEYS = byLenDesc({ ...DV_CONS, ...DV_VOWELS, ...DV_SPECIAL });

export function translitDevanagari(roman: string): string {
  let out = "", i = 0, prevCons = false;
  while (i < roman.length) {
    const key = longest(DV_KEYS, roman, i);
    if (!key) { out += roman[i]; i++; prevCons = false; continue; }
    i += key.length;
    if (key in DV_CONS) {
      if (prevCons) out += DV_VIRAMA;          // 子音接子音 → 中間插虛音符成合字
      out += DV_CONS[key];
      prevCons = true;
    } else if (key in DV_VOWELS) {
      const [indep, matra] = DV_VOWELS[key];
      out += prevCons ? matra : indep;         // 子音後 → 母音記號；否則獨立母音
      prevCons = false;
    } else {                                   // 特殊符號（anusvara/visarga/OM）
      out += DV_SPECIAL[key];
      prevCons = false;
    }
  }
  return out;
}

// ════════════════════════════════════════════════════════════════════════════
//  2) 吉茲 Gəʿəz / fidäl（gez）— 音節 = 子音基 + 母音階（codepoint 位移 0–6）
// ════════════════════════════════════════════════════════════════════════════
// SERA 慣例：子音基字＝1 階(ä)的 codepoint；母音鍵決定階 e→0(ä) u→1 i→2 a→3 E→4 o→6；
// 無母音的孤立子音＝6 階(ə，offset 5)——這樣詞尾/輔音叢自然，且詞形拼寫正確（如 selam→ሰላም）。
const GZ_BASE: Record<string, string> = {
  h: "ሀ", l: "ለ", H: "ሐ", m: "መ", sx: "ሠ", r: "ረ", s: "ሰ", x: "ሸ", q: "ቀ", b: "በ",
  t: "ተ", c: "ቸ", hx: "ኀ", n: "ነ", N: "ኘ", "'": "አ", k: "ከ", kx: "ኸ", w: "ወ",
  "`": "ዐ", z: "ዘ", Z: "ዠ", y: "የ", d: "ደ", j: "ጀ", g: "ገ", T: "ጠ", C: "ጨ", P: "ጰ",
  S: "ጸ", Sx: "ፀ", f: "ፈ", p: "ፐ",
};
const GZ_VOWEL: Record<string, number> = { e: 0, u: 1, i: 2, a: 3, E: 4, o: 6 }; // SERA：e=ä(1階)
const GZ_BARE_OFFSET = 5; // 無母音的孤立子音 → 6 階(ə)
const GZ_KEYS = byLenDesc(GZ_BASE);
const GZ_GLOTTAL = "አ"; // 字首母音用 ʾ(አ) 系列承載

export function translitGeez(roman: string): string {
  let out = "", i = 0;
  while (i < roman.length) {
    const cons = longest(GZ_KEYS, roman, i);
    if (cons) {
      i += cons.length;
      let off = GZ_BARE_OFFSET;
      const v = roman[i];
      if (v !== undefined && GZ_VOWEL[v] !== undefined) { off = GZ_VOWEL[v]; i++; }
      out += String.fromCodePoint(GZ_BASE[cons].codePointAt(0)! + off);
      continue;
    }
    const v = roman[i];
    if (v !== undefined && GZ_VOWEL[v] !== undefined) { // 字首獨立母音
      out += String.fromCodePoint(GZ_GLOTTAL.codePointAt(0)! + GZ_VOWEL[v]); i++; continue;
    }
    out += roman[i]; i++;
  }
  return out;
}

// ════════════════════════════════════════════════════════════════════════════
//  3) 藏文 Tibetan（bo）— Wylie；疊寫用顯式 "+"（簡化版，複雜疊字以 + 手動堆）
// ════════════════════════════════════════════════════════════════════════════
const TB_CONS: Record<string, string> = {
  kh: "ཁ", k: "ཀ", g: "ག", ng: "ང", ch: "ཆ", c: "ཅ", j: "ཇ", ny: "ཉ",
  th: "ཐ", t: "ཏ", d: "ད", n: "ན", ph: "ཕ", p: "པ", b: "བ", m: "མ",
  tsh: "ཚ", ts: "ཙ", dz: "ཛ", w: "ཝ", zh: "ཞ", z: "ཟ", "'": "འ", y: "ཡ",
  r: "ར", l: "ལ", sh: "ཤ", s: "ས", h: "ཧ",
};
const TB_VOWEL: Record<string, string> = { i: "ི", u: "ུ", e: "ེ", o: "ོ" }; // a = 固有母音
const TB_KEYS = byLenDesc(TB_CONS);
const TB_SUBJOIN_OFFSET = 0x50; // 全形子音 U+0F40.. → 後加（疊寫）子音 U+0F90..
const tbSubjoin = (ch: string) => String.fromCodePoint(ch.codePointAt(0)! + TB_SUBJOIN_OFFSET);

// 藏文正字疊寫規則（自動找字根 ming gzhi）
const TB_PREFIX = new Set(["g", "d", "b", "m", "'"]);            // 前加字 sngon 'jug
const TB_SUPER: Record<string, Set<string>> = {                  // 上加字 mgo can → 可帶的字根
  r: new Set(["k", "g", "ng", "j", "ny", "t", "d", "n", "b", "m", "ts", "dz"]),
  l: new Set(["k", "g", "ng", "c", "j", "t", "d", "p", "b", "h"]),
  s: new Set(["k", "g", "ng", "ny", "t", "d", "n", "p", "b", "m", "ts"]),
};
const TB_SUB: Record<string, Set<string>> = {                    // 下加字 'dogs can → 可附的字根
  y: new Set(["k", "kh", "g", "p", "ph", "b", "m"]),
  r: new Set(["k", "kh", "g", "t", "th", "d", "n", "p", "ph", "b", "m", "s", "h"]),
  l: new Set(["k", "g", "b", "r", "s", "z"]),
  w: new Set(["k", "kh", "g", "c", "ny", "t", "d", "ts", "tsh", "zh", "z", "r", "l", "sh", "s", "h"]),
};
interface TbOnset { prefix?: string; super?: string; root: string; sub?: string; }
function parseTbOnset(cs: string[]): TbOnset {
  if (cs.length === 1) return { root: cs[0] };
  if (cs.length === 2) {
    const [a, b] = cs;
    if (TB_SUB[b]?.has(a)) return { root: a, sub: b };       // 字根 + 下加字（如 ky, gr）
    if (TB_SUPER[a]?.has(b)) return { super: a, root: b };   // 上加字 + 字根（如 rk, sg）
    return { prefix: a, root: b };                            // 前加字 + 字根（如 bg）
  }
  // 3+ 個：有前加字就剝掉再遞迴；否則 上加+字根+下加
  const [a, ...rest] = cs;
  if (TB_PREFIX.has(a)) return { prefix: a, ...parseTbOnset(rest) };
  const [s, r, sub] = cs;
  return { super: s, root: r, sub };
}
function renderTbOnset(cs: string[]): string {
  if (!cs.length) return "";
  const p = parseTbOnset(cs);
  let out = "";
  if (p.prefix) out += TB_CONS[p.prefix];
  out += p.super ? TB_CONS[p.super] + tbSubjoin(TB_CONS[p.root]) : TB_CONS[p.root];
  if (p.sub) out += tbSubjoin(TB_CONS[p.sub]);
  return out;
}

// 顯式疊寫模式（buffer 含 "+"）：每個子音全形，"+" 把下一個子音變後加形（梵文/不規則疊字用）
function translitTibetanManual(roman: string): string {
  let out = "", i = 0, prevCons = false, subjoinNext = false;
  while (i < roman.length) {
    if (roman[i] === "+") { subjoinNext = true; i++; continue; }
    const cons = longest(TB_KEYS, roman, i);
    if (cons) { i += cons.length; out += subjoinNext ? tbSubjoin(TB_CONS[cons]) : TB_CONS[cons]; subjoinNext = false; prevCons = true; continue; }
    const v = roman[i];
    if (v === "a") { if (!prevCons) out += "ཨ"; i++; prevCons = false; continue; }
    if (TB_VOWEL[v] !== undefined) { out += TB_VOWEL[v]; i++; prevCons = false; continue; }
    out += roman[i]; i++; prevCons = false;
  }
  return out;
}

// 自動疊寫（一個 buffer = 一個音節，由 tsheg/空白分隔）：解析 前加/上加/字根/下加 + 母音 + 後加字
export function translitTibetan(roman: string): string {
  if (roman.includes("+")) return translitTibetanManual(roman); // 顯式模式（梵文等不規則疊字）
  const onset: string[] = [], suffix: string[] = [];
  let vowel: string | null = null, sawVowel = false, tail = "", i = 0;
  while (i < roman.length) {
    const c = longest(TB_KEYS, roman, i);
    if (c) { i += c.length; (sawVowel ? suffix : onset).push(c); continue; }
    const ch = roman[i]; i++;
    if ("aiueo".includes(ch)) {
      if (!sawVowel) { vowel = ch; sawVowel = true; }
      else if (ch !== "a") tail += TB_VOWEL[ch] ?? "";        // 罕見的第二母音
    } else tail += ch;                                         // 未知字元原樣
  }
  let out = renderTbOnset(onset);
  if (sawVowel) {
    if (!onset.length) out += "ཨ";                            // 字首獨立母音用 ཨ 承載
    if (vowel && vowel !== "a") out += TB_VOWEL[vowel];
  }
  for (const s of suffix) out += TB_CONS[s];                   // 後加字＝全形
  return out + tail;
}

// ════════════════════════════════════════════════════════════════════════════
//  有狀態鍵盤工廠（整詞 roman 緩衝 + 逐鍵重轉寫 + commit）
// ════════════════════════════════════════════════════════════════════════════
export interface AbugidaSpec {
  key: string;
  label: string;
  hint: string;
  translit: (roman: string) => string;
  bufRe: RegExp;                 // 哪些單鍵併入 roman 緩衝
  wordSep?: string;              // 空白鍵插入的分隔字（藏文＝tsheg ་）
  palette?: { ch: string; latin?: string; label?: string }[];
  marks?: { mark: string; label: string }[];
}

export function makeAbugidaKeyboard(spec: AbugidaSpec) {
  let roman = "";
  let outLen = 0;
  function reset() { roman = ""; outLen = 0; }

  function render(el: HTMLTextAreaElement, setValue: SetValue, newRoman: string) {
    roman = newRoman;
    const newOut = spec.translit(roman);
    const ss = el.selectionStart ?? el.value.length;
    const head = el.value.slice(0, Math.max(0, ss - outLen));
    const tail = el.value.slice(ss);
    outLen = newOut.length;
    setValue(head + newOut + tail, (head + newOut).length);
  }

  function insert(el: HTMLTextAreaElement, text: string, setValue: SetValue) {
    const ss = el.selectionStart ?? el.value.length;
    const se = el.selectionEnd ?? ss;
    reset();
    const head = el.value.slice(0, ss);
    setValue(head + text + el.value.slice(se), (head + text).length);
  }

  function onKeydown(e: KeyboardEvent, el: HTMLTextAreaElement, setValue: SetValue): boolean {
    if (e.ctrlKey || e.metaKey || e.altKey || (e as any).isComposing || e.key === "Process") return false;
    const k = e.key;
    if (k.length === 1 && spec.bufRe.test(k)) {
      e.preventDefault();
      render(el, setValue, roman + k);
      return true;
    }
    if (k === "Backspace") {
      if (roman.length > 0) { e.preventDefault(); render(el, setValue, roman.slice(0, -1)); return true; }
      reset(); return false;
    }
    if (k === " ") {
      e.preventDefault();
      const sep = spec.wordSep ?? " ";
      const ss = el.selectionStart ?? el.value.length;
      const head = el.value.slice(0, ss);
      reset();
      setValue(head + sep + el.value.slice(ss), (head + sep).length);
      return true;
    }
    reset(); // Enter／標點等：commit，交給呼叫端預設處理
    return false;
  }

  return {
    key: spec.key, label: spec.label, hint: spec.hint, rtl: false,
    onKeydown, insert, reset, palette: spec.palette ?? [], marks: spec.marks ?? [],
  };
}

// 各 spec
const devanagari: AbugidaSpec = {
  key: "devanagari", label: "天城體鍵盤", translit: translitDevanagari, bufRe: /[a-zA-Z~]/,
  hint: "ITRANS：打 dharma→धर्म、namaste→नमस्ते；長音 aa/ii/uu，捲舌 T Th D N，鼻音 M，止韻 H",
  palette: [
    { ch: "अ", latin: "a" }, { ch: "आ", latin: "aa" }, { ch: "इ", latin: "i" }, { ch: "ई", latin: "ii" },
    { ch: "उ", latin: "u" }, { ch: "ऊ", latin: "uu" }, { ch: "ऋ", latin: "R" }, { ch: "ए", latin: "e" },
    { ch: "ऐ", latin: "ai" }, { ch: "ओ", latin: "o" }, { ch: "औ", latin: "au" }, { ch: "ॐ", latin: "OM" },
  ],
  marks: [{ mark: "ं", label: "anusvara ं (M)" }, { mark: "ः", label: "visarga ः (H)" }, { mark: "ँ", label: "candrabindu ँ (~)" }, { mark: "्", label: "virama ्" }],
};
const geez: AbugidaSpec = {
  key: "geez", label: "吉茲鍵盤", translit: translitGeez, bufRe: /[a-zA-Z'`]/,
  hint: "SERA：子音＝6階(ə)；接 e→1階(ä) u i a E o 換階（selam→ሰላም）；ś=sx ḫ=hx ḵ=kx ḥ=H ṣ=S ʾ=' ʿ=`",
  palette: [
    { ch: "ሀ", latin: "he" }, { ch: "ለ", latin: "le" }, { ch: "መ", latin: "me" }, { ch: "ረ", latin: "re" },
    { ch: "ሰ", latin: "se" }, { ch: "ቀ", latin: "qe" }, { ch: "በ", latin: "be" }, { ch: "ተ", latin: "te" },
    { ch: "ነ", latin: "ne" }, { ch: "አ", latin: "'e" }, { ch: "ከ", latin: "ke" }, { ch: "ወ", latin: "we" },
    { ch: "ዘ", latin: "ze" }, { ch: "የ", latin: "ye" }, { ch: "ደ", latin: "de" }, { ch: "ገ", latin: "ge" },
    { ch: "ጠ", latin: "Te" }, { ch: "ጸ", latin: "Se" }, { ch: "ፈ", latin: "fe" }, { ch: "ፐ", latin: "pe" },
  ],
};
const tibetan: AbugidaSpec = {
  key: "tibetan", label: "藏文鍵盤", translit: translitTibetan, bufRe: /[a-zA-Z'+]/, wordSep: "་",
  hint: "Wylie：打整個音節自動疊寫（bsgrubs→བསྒྲུབས、rgyal→རྒྱལ）；母音 i u e o（a 固有）；空白＝音節點 tsheg；梵文不規則疊字用 + 顯式堆",
  palette: [
    { ch: "ཀ", latin: "k" }, { ch: "ཁ", latin: "kh" }, { ch: "ག", latin: "g" }, { ch: "ང", latin: "ng" },
    { ch: "ཅ", latin: "c" }, { ch: "ཇ", latin: "j" }, { ch: "ཏ", latin: "t" }, { ch: "ད", latin: "d" },
    { ch: "ན", latin: "n" }, { ch: "པ", latin: "p" }, { ch: "བ", latin: "b" }, { ch: "མ", latin: "m" },
    { ch: "ཙ", latin: "ts" }, { ch: "ཞ", latin: "zh" }, { ch: "ཟ", latin: "z" }, { ch: "ཡ", latin: "y" },
    { ch: "ར", latin: "r" }, { ch: "ལ", latin: "l" }, { ch: "ཤ", latin: "sh" }, { ch: "ས", latin: "s" },
    { ch: "ཧ", latin: "h" }, { ch: "ཨ", latin: "a" },
  ],
  marks: [{ mark: "ི", label: "i ི" }, { mark: "ུ", label: "u ུ" }, { mark: "ེ", label: "e ེ" }, { mark: "ོ", label: "o ོ" }, { mark: "་", label: "tsheg ་" }, { mark: "།", label: "shad །" }],
};

export const ABUGIDA_SPECS: Record<string, AbugidaSpec> = { devanagari, geez, tibetan };

export function getAbugidaKeyboard(key: string | undefined) {
  if (!key) return null;
  const spec = ABUGIDA_SPECS[key];
  return spec ? makeAbugidaKeyboard(spec) : null;
}
