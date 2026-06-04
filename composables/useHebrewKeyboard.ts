// ============================================================================
// 舊約希伯來文「鍵盤」 — 打英文即時對照成希伯來字母（與 useGreekKeyboard 同套邏輯）
//   - 22 子音單鍵對應（學術轉寫，1:1 無狀態）：見 HEBREW_PALETTE
//   - 字尾形（sofit）自動：כ→ך מ→ם נ→ן פ→ף צ→ץ（詞尾自動換、詞中還原）
//   - 母音點（niqqud）以點選面板插入（接在子音之後）
//   - 希伯來文由右至左：輸入框請設 dir="rtl"，但游標/字串索引仍為邏輯順序
// ============================================================================

// 子音：Latin 單鍵 → 希伯來字母（在對照表逐一標示，初學者照表打）
const LOWER: Record<string, string> = {
  a: "א", b: "ב", g: "ג", d: "ד", h: "ה", v: "ו", z: "ז", x: "ח",
  f: "ט", y: "י", k: "כ", l: "ל", m: "מ", n: "נ", s: "ס", e: "ע",
  p: "פ", c: "צ", q: "ק", r: "ר", w: "ש", t: "ת",
  "'": "א", // alef 替代鍵
};

// 字尾形 sofit
const REG_TO_FIN: Record<string, string> = { "כ": "ך", "מ": "ם", "נ": "ן", "פ": "ף", "צ": "ץ" };
const FIN_TO_REG: Record<string, string> = { "ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ" };

const HEBREW_LETTER = /[א-ת]/;       // U+05D0–05EA（含字尾形）
const NIQQUD = /[֑-ׇ]/;              // U+0591–05C7 母音點與重音

// 字尾形正規化：詞尾的 5 個字母用 sofit，詞中還原（1:1，不改長度，可重複套用）
export function normalizeFinals(text: string): string {
  const chars = [...text];
  for (let i = 0; i < chars.length; i++) {
    const base = FIN_TO_REG[chars[i]] ?? chars[i];
    if (!(base in REG_TO_FIN)) continue; // 非可變字尾的字母
    let j = i + 1;
    while (j < chars.length && NIQQUD.test(chars[j])) j++;
    const next = chars[j];
    chars[i] = next && HEBREW_LETTER.test(next) ? base : REG_TO_FIN[base];
  }
  return chars.join("");
}

// 對照表（打英文 → 希伯來字母）
export const HEBREW_PALETTE = Object.entries(LOWER)
  .filter(([latin]) => latin !== "'")
  .map(([latin, heb]) => ({ latin, heb }));

// 常用母音點 / 附加符號（點選插在子音之後）
export const HEBREW_NIQQUD = [
  { mark: "ָ", label: "qamats ָ" },
  { mark: "ַ", label: "patah ַ" },
  { mark: "ֶ", label: "segol ֶ" },
  { mark: "ֵ", label: "tsere ֵ" },
  { mark: "ִ", label: "hiriq ִ" },
  { mark: "ֹ", label: "holam ֹ" },
  { mark: "ֻ", label: "qubuts ֻ" },
  { mark: "ְ", label: "shva ְ" },
  { mark: "ּ", label: "dagesh ּ" },
  { mark: "ׁ", label: "shin dot ׁ" },
  { mark: "ׂ", label: "sin dot ׂ" },
];

type SetValue = (value: string, cursor: number) => void;

export function useHebrewKeyboard() {
  function insert(el: HTMLTextAreaElement, text: string, setValue: SetValue) {
    const start = el.selectionStart ?? el.value.length;
    const end = el.selectionEnd ?? start;
    const before = el.value.slice(0, start) + text;
    setValue(normalizeFinals(before) + el.value.slice(end), before.length);
  }

  function onKeydown(e: KeyboardEvent, el: HTMLTextAreaElement, setValue: SetValue): boolean {
    if (e.ctrlKey || e.metaKey || e.altKey) return false;
    const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
    const start = el.selectionStart ?? el.value.length;
    const end = el.selectionEnd ?? start;
    const head = el.value.slice(0, start);
    const tail = el.value.slice(end);

    const g = LOWER[k];
    if (g) {
      e.preventDefault();
      const head2 = head + g;
      setValue(normalizeFinals(head2) + tail, head2.length);
      return true;
    }
    // 空白：插入並把前一字的字尾字母收成 sofit
    if (e.key === " ") {
      e.preventDefault();
      const head2 = head + " ";
      setValue(normalizeFinals(head2) + tail, head2.length);
      return true;
    }
    return false;
  }

  return { onKeydown, insert, normalizeFinals, HEBREW_PALETTE, HEBREW_NIQQUD };
}
