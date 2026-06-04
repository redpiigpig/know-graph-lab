// ============================================================================
// 日文「鍵盤」 — 打羅馬字即時轉假名（romaji → かな，內建迷你 IME）
// 與 useGreekKeyboard 同一套「打英文 → 目標文字」邏輯，但假名需要緩衝：
//   - 拗音 きゃ(kya)、促音 っ(kk…)、撥音 ん(nn / n+子音)、濁音半濁音
//   - 平假名／片假名切換；片假名長音 ー（按 -）
//   - 游標前未轉換的羅馬字以拉丁字暫存（pendingLen），湊成假名即替換
// 注意：偵測到作業系統 IME 正在組字（e.isComposing / key==='Process'）就讓行，避免雙重轉換。
// ============================================================================
import { ref } from "vue";

// 平假名對照表（輸出一律平假名，片假名模式再轉換）。key 由長到短最多 4 碼。
const M: Record<string, string> = {
  a: "あ", i: "い", u: "う", e: "え", o: "お",
  ka: "か", ki: "き", ku: "く", ke: "け", ko: "こ",
  ga: "が", gi: "ぎ", gu: "ぐ", ge: "げ", go: "ご",
  sa: "さ", si: "し", shi: "し", su: "す", se: "せ", so: "そ",
  za: "ざ", zi: "じ", ji: "じ", zu: "ず", ze: "ぜ", zo: "ぞ",
  ta: "た", ti: "ち", chi: "ち", tu: "つ", tsu: "つ", te: "て", to: "と",
  da: "だ", di: "ぢ", du: "づ", de: "で", do: "ど",
  na: "な", ni: "に", nu: "ぬ", ne: "ね", no: "の",
  ha: "は", hi: "ひ", hu: "ふ", fu: "ふ", he: "へ", ho: "ほ",
  ba: "ば", bi: "び", bu: "ぶ", be: "べ", bo: "ぼ",
  pa: "ぱ", pi: "ぴ", pu: "ぷ", pe: "ぺ", po: "ぽ",
  ma: "ま", mi: "み", mu: "む", me: "め", mo: "も",
  ya: "や", yu: "ゆ", yo: "よ",
  ra: "ら", ri: "り", ru: "る", re: "れ", ro: "ろ",
  wa: "わ", wo: "を", n: "ん",
  // 拗音
  kya: "きゃ", kyu: "きゅ", kyo: "きょ",
  gya: "ぎゃ", gyu: "ぎゅ", gyo: "ぎょ",
  sha: "しゃ", shu: "しゅ", sho: "しょ", sya: "しゃ", syu: "しゅ", syo: "しょ",
  ja: "じゃ", ju: "じゅ", jo: "じょ", jya: "じゃ", jyu: "じゅ", jyo: "じょ", zya: "じゃ", zyu: "じゅ", zyo: "じょ",
  cha: "ちゃ", chu: "ちゅ", cho: "ちょ", tya: "ちゃ", tyu: "ちゅ", tyo: "ちょ",
  nya: "にゃ", nyu: "にゅ", nyo: "にょ",
  hya: "ひゃ", hyu: "ひゅ", hyo: "ひょ",
  bya: "びゃ", byu: "びゅ", byo: "びょ",
  pya: "ぴゃ", pyu: "ぴゅ", pyo: "ぴょ",
  mya: "みゃ", myu: "みゅ", myo: "みょ",
  rya: "りゃ", ryu: "りゅ", ryo: "りょ",
  // 外來音
  fa: "ふぁ", fi: "ふぃ", fe: "ふぇ", fo: "ふぉ",
  va: "ゔぁ", vi: "ゔぃ", vu: "ゔ", ve: "ゔぇ", vo: "ゔぉ",
  // 小書き
  xa: "ぁ", xi: "ぃ", xu: "ぅ", xe: "ぇ", xo: "ぉ", xtu: "っ", xtsu: "っ", ltu: "っ", xya: "ゃ", xyu: "ゅ", xyo: "ょ",
  la: "ぁ", li: "ぃ", lu: "ぅ", le: "ぇ", lo: "ぉ",
};

const isVowel = (c: string) => "aeiou".includes(c);
const isConsonant = (c: string) => /[a-z]/.test(c) && !isVowel(c);

// 平假名 ぁ-ゖ → 片假名（+0x60）
function toKatakana(s: string): string {
  return s.replace(/[ぁ-ゖ]/g, (c) => String.fromCodePoint(c.codePointAt(0)! + 0x60));
}

// 把一段羅馬字緩衝盡量轉成假名，回傳 {kana, rest}（rest=還湊不成假名的尾巴）
export function romajiToKana(buffer: string, kata = false): { kana: string; rest: string } {
  let out = "";
  let b = buffer.toLowerCase();
  while (b.length) {
    // 促音：同子音相疊（n 除外）→ っ；另 Hepburn "tch"（matcha→まっちゃ）t+c → っ
    if (b.length >= 2 && isConsonant(b[0]) && b[0] !== "n" && (b[0] === b[1] || (b[0] === "t" && b[1] === "c"))) {
      out += "っ"; b = b.slice(1); continue;
    }
    // 撥音 ん（採 wanakana 慣例）：
    //   nn → ん（吃掉兩個 n；這是「打 nn 出 ん」的通用習慣，sennsei→せんせい）
    //   n + 其他子音（非 y）→ ん（吃掉一個 n）
    //   ん＋な行／母音 請用撇號分隔：kon'nichiwa → こんにちわ
    if (b[0] === "n" && b.length >= 2) {
      const c = b[1];
      if (c === "n") { out += "ん"; b = b.slice(2); continue; }
      if (c !== "y" && !isVowel(c)) { out += "ん"; b = b.slice(1); continue; }
    }
    // 由長到短匹配假名
    let matched = false;
    for (let len = Math.min(4, b.length); len >= 1; len--) {
      const seg = b.slice(0, len);
      // 單獨 "n" 暫不收（可能要接 a/y…），等收尾或下一鍵
      if (seg === "n" && b.length === 1) break;
      if (M[seg]) { out += M[seg]; b = b.slice(len); matched = true; break; }
    }
    if (!matched) break;
  }
  return { kana: kata ? toKatakana(out) : out, rest: b };
}

// 收尾：把殘留的單獨 "n" 轉 ん，其餘湊不成的羅馬字原樣保留
function finalizeStr(p: string, kata: boolean): string {
  if (p === "n") return kata ? "ン" : "ん";
  return p;
}

// 給 UI 的五十音點選表（平假名；片假名模式由元件轉換）
export const GOJUON: string[][] = [
  ["あ", "い", "う", "え", "お"],
  ["か", "き", "く", "け", "こ"],
  ["さ", "し", "す", "せ", "そ"],
  ["た", "ち", "つ", "て", "と"],
  ["な", "に", "ぬ", "ね", "の"],
  ["は", "ひ", "ふ", "へ", "ほ"],
  ["ま", "み", "む", "め", "も"],
  ["や", "", "ゆ", "", "よ"],
  ["ら", "り", "る", "れ", "ろ"],
  ["わ", "を", "ん", "ー", "、"],
];

type SetValue = (value: string, cursor: number) => void;

export function useKanaKeyboard() {
  const kata = ref(false);       // false=平假名 true=片假名
  const pendingLen = ref(0);     // 游標前暫存的羅馬字長度

  function reset() { pendingLen.value = 0; }

  // 收尾游標前的暫存（送出前 / 失焦時呼叫）
  function finalize(el: HTMLTextAreaElement, setValue: SetValue) {
    const ss = el.selectionStart ?? el.value.length;
    const pend = pendingLen.value;
    if (pend <= 0) return;
    const head = el.value.slice(0, ss - pend);
    const tail = el.value.slice(ss);
    const fin = finalizeStr(el.value.slice(ss - pend, ss), kata.value);
    pendingLen.value = 0;
    setValue(head + fin + tail, (head + fin).length);
  }

  // 面板點選：先收尾暫存，再插入該假名
  function insert(el: HTMLTextAreaElement, text: string, setValue: SetValue) {
    const ss = el.selectionStart ?? el.value.length;
    const se = el.selectionEnd ?? ss;
    const pend = ss === se ? pendingLen.value : 0;
    const head = finalizeStr(el.value.slice(ss - pend, ss), kata.value);
    const out = el.value.slice(0, ss - pend) + head + text;
    pendingLen.value = 0;
    setValue(out + el.value.slice(se), out.length);
  }

  function onKeydown(e: KeyboardEvent, el: HTMLTextAreaElement, setValue: SetValue): boolean {
    // 系統 IME 正在組字 → 讓行，避免雙重轉換
    if (e.ctrlKey || e.metaKey || e.altKey || e.isComposing || e.key === "Process") return false;
    const k = e.key;
    const ss = el.selectionStart ?? el.value.length;
    const se = el.selectionEnd ?? ss;
    const pend = ss === se ? pendingLen.value : 0;
    const head = el.value.slice(0, ss - pend);
    const tail = el.value.slice(se);
    const pendStr = el.value.slice(ss - pend, ss);

    // 字母：併入緩衝再轉假名
    if (/^[a-zA-Z]$/.test(k)) {
      e.preventDefault();
      const { kana, rest } = romajiToKana(pendStr + k, kata.value);
      const mid = kana + rest;
      pendingLen.value = rest.length;
      setValue(head + mid + tail, (head + mid).length);
      return true;
    }
    // 片假名長音 ー
    if (k === "-" && kata.value) {
      e.preventDefault();
      const mid = finalizeStr(pendStr, kata.value) + "ー";
      pendingLen.value = 0;
      setValue(head + mid + tail, (head + mid).length);
      return true;
    }
    // 撇號 = 明確收掉 ん（kon'nichi → こんにち）
    if (k === "'") {
      e.preventDefault();
      const mid = finalizeStr(pendStr, kata.value);
      pendingLen.value = 0;
      setValue(head + mid + tail, (head + mid).length);
      return true;
    }
    // 空白：收尾暫存 + 插入空白
    if (k === " ") {
      e.preventDefault();
      const mid = finalizeStr(pendStr, kata.value) + " ";
      pendingLen.value = 0;
      setValue(head + mid + tail, (head + mid).length);
      return true;
    }
    // 退格：縮短暫存，交給預設刪字
    if (k === "Backspace") {
      if (pend > 0) pendingLen.value = pend - 1;
      return false;
    }
    // 其他鍵（標點/Enter…）：先把暫存收尾，再交給呼叫端
    if (pend > 0) {
      const mid = finalizeStr(pendStr, kata.value);
      pendingLen.value = 0;
      setValue(head + mid + tail, (head + mid).length);
    }
    return false;
  }

  return { kata, pendingLen, onKeydown, finalize, insert, reset, GOJUON, toKatakana };
}
