// ============================================================================
// 聖經希臘文「鍵盤」 — 打英文即時對照成希臘字母（TLG Beta Code 對應）
// 用於 voiceless 古希臘語教練（Sophia / grc）的輸入框：
//   - 小寫/大寫 a–z → α–ω（Beta Code：h=η, q=θ, c=ξ, x=χ, y=ψ, w=ω, f=φ）
//   - 多調符號 polytonic：) 柔氣 ( 粗氣 / 銳音 \ 抑音 = 揚抑音 | ι下標 + 分音符
//   - 字尾 sigma 自動：詞中 σ、詞尾 ς
// 不需語音；純文字轉寫。任何古希臘輸入框都可重用此 composable。
// ============================================================================

const LOWER: Record<string, string> = {
  a: "α", b: "β", g: "γ", d: "δ", e: "ε", z: "ζ", h: "η", q: "θ",
  i: "ι", k: "κ", l: "λ", m: "μ", n: "ν", c: "ξ", o: "ο", p: "π",
  r: "ρ", s: "σ", t: "τ", u: "υ", f: "φ", x: "χ", y: "ψ", w: "ω",
};
const UPPER: Record<string, string> = {
  A: "Α", B: "Β", G: "Γ", D: "Δ", E: "Ε", Z: "Ζ", H: "Η", Q: "Θ",
  I: "Ι", K: "Κ", L: "Λ", M: "Μ", N: "Ν", C: "Ξ", O: "Ο", P: "Π",
  R: "Ρ", S: "Σ", T: "Τ", U: "Υ", F: "Φ", X: "Χ", Y: "Ψ", W: "Ω",
};

// beta-code 標點 → Unicode 結合附加符號（接在前一個母音/ρ 之後）
const DIACRITICS: Record<string, { mark: string; label: string }> = {
  ")": { mark: "̓", label: "柔氣記號 ᾿" },   // psili / smooth breathing
  "(": { mark: "̔", label: "粗氣記號 ῾" },   // dasia / rough breathing
  "/": { mark: "́", label: "銳音 ´" },        // oxia / acute
  "\\": { mark: "̀", label: "抑音 `" },       // varia / grave
  "=": { mark: "͂", label: "揚抑音 ῀" },      // perispomeni / circumflex
  "|": { mark: "ͅ", label: "ι 下標 ͅ" },       // ypogegrammeni / iota subscript
  "+": { mark: "̈", label: "分音符 ¨" },      // dialytika / diaeresis
};

// 希臘字母：基本希臘區塊 U+0370–03FF + 希臘擴充區 U+1F00–1FFF
const GREEK_LETTER = /[Ͱ-Ͽἀ-῿]/;
// 結合附加符號 U+0300–036F（含 ι 下標 U+0345）
const COMBINING = /[̀-ͯ]/;

// 詞中 σ／詞尾 ς：1:1 取代（不改變長度，游標不位移），可重複套用。
export function normalizeSigma(text: string): string {
  const chars = [...text];
  for (let i = 0; i < chars.length; i++) {
    if (chars[i] !== "σ" && chars[i] !== "ς") continue;
    let j = i + 1;
    while (j < chars.length && COMBINING.test(chars[j])) j++;
    const next = chars[j];
    chars[i] = next && GREEK_LETTER.test(next) ? "σ" : "ς";
  }
  return chars.join("");
}

// 給 UI 用的對照表（打英文 → 希臘字母）
export const GREEK_PALETTE = Object.entries(LOWER).map(([latin, greek]) => ({ latin, greek }));
export const GREEK_DIACRITICS = Object.entries(DIACRITICS).map(([key, v]) => ({ key, ...v }));

type SetValue = (value: string, cursor: number) => void;

export function useGreekKeyboard() {
  // 在游標處插入一段文字（供面板點選用），並正規化字尾 sigma
  function insert(el: HTMLTextAreaElement, text: string, setValue: SetValue) {
    const start = el.selectionStart ?? el.value.length;
    const end = el.selectionEnd ?? start;
    const before = el.value.slice(0, start) + text;
    const out = normalizeSigma(before) + el.value.slice(end);
    setValue(out, before.length);
  }

  // keydown 攔截：回傳 true 表示已處理（呼叫端應視為已 preventDefault）
  function onKeydown(e: KeyboardEvent, el: HTMLTextAreaElement, setValue: SetValue): boolean {
    if (e.ctrlKey || e.metaKey || e.altKey) return false;
    const k = e.key;
    const start = el.selectionStart ?? el.value.length;
    const end = el.selectionEnd ?? start;
    const head = el.value.slice(0, start);
    const tail = el.value.slice(end);

    // 1) 母音/ρ 後的多調符號
    if (DIACRITICS[k]) {
      e.preventDefault();
      if (!head.length || !GREEK_LETTER.test(head[head.length - 1])) return true; // 前面不是希臘字母 → 忽略
      const combined = (head + DIACRITICS[k].mark).normalize("NFC");
      setValue(normalizeSigma(combined) + tail, combined.length);
      return true;
    }

    // 2) 字母 a–z / A–Z → 希臘字母
    const g = LOWER[k] ?? UPPER[k];
    if (g) {
      e.preventDefault();
      const head2 = head + g;
      setValue(normalizeSigma(head2) + tail, head2.length);
      return true;
    }

    // 3) 空白：插入空白並把前一個詞的 σ 收尾成 ς
    if (k === " ") {
      e.preventDefault();
      const head2 = head + " ";
      setValue(normalizeSigma(head2) + tail, head2.length);
      return true;
    }

    // 其他鍵（Enter/Backspace/標點/中文…）照常處理
    return false;
  }

  return { onKeydown, insert, normalizeSigma, GREEK_PALETTE, GREEK_DIACRITICS };
}
