// @vitest-environment node
import { describe, it, expect } from "vitest";
import { romajiToKana } from "~/composables/useKanaKeyboard";
import { normalizeSigma } from "~/composables/useGreekKeyboard";
import { normalizeFinals } from "~/composables/useHebrewKeyboard";

// 模擬逐字輸入：pending 尾巴帶到下一鍵（與 onKeydown 的緩衝/特例行為一致）
const finN = (p: string, kata: boolean) => (p === "n" ? (kata ? "ン" : "ん") : p);
function typeKana(s: string, kata = false): string {
  let pend = "";
  let out = "";
  for (const ch of s) {
    if (ch === "-" && kata) { out += finN(pend, kata) + "ー"; pend = ""; continue; } // 片假名長音
    if (ch === "'") { out += finN(pend, kata); pend = ""; continue; }                // 撇號收掉 ん
    const { kana, rest } = romajiToKana(pend + ch, kata);
    out += kana;
    pend = rest;
  }
  out += finN(pend, kata); // 收尾殘留單獨 n → ん
  return out;
}

describe("日文假名鍵盤 romajiToKana", () => {
  it("基本五十音與濁音", () => {
    expect(typeKana("sakura")).toBe("さくら");
    expect(typeKana("nihongo")).toBe("にほんご");
    expect(typeKana("ringo")).toBe("りんご");
  });

  it("拗音／促音／撥音", () => {
    expect(typeKana("kyou")).toBe("きょう");
    expect(typeKana("gakkou")).toBe("がっこう");   // 促音 っ
    expect(typeKana("jinja")).toBe("じんじゃ");     // ん + 拗音
    expect(typeKana("matcha")).toBe("まっちゃ");    // Hepburn tch
    expect(typeKana("sennsei")).toBe("せんせい");   // nn → ん
    expect(typeKana("mikan")).toBe("みかん");       // 詞尾 n → ん
  });

  it("片假名模式", () => {
    expect(typeKana("ko-hi-", true)).toBe("コーヒー"); // 長音 ー
    expect(typeKana("amerika", true)).toBe("アメリカ");
  });

  it("非羅馬字原樣保留", () => {
    expect(typeKana("ok")).toBe("おk"); // 殘留未成假名的 k 保留
  });
});

describe("希臘文 normalizeSigma（詞中 σ／詞尾 ς）", () => {
  it("詞尾 σ 變 ς，詞中維持 σ", () => {
    expect(normalizeSigma("λογοσ")).toBe("λογος"); // 末尾 → ς
    expect(normalizeSigma("κοσμοσ")).toBe("κοσμος"); // 中 σ、末 ς
    expect(normalizeSigma("λογος")).toBe("λογος"); // 已是 ς 不動
  });

  it("詞尾末字為 ς 的 codepoint 是 U+03C2", () => {
    const r = normalizeSigma("λογοσ");
    expect(r.codePointAt(r.length - 1)).toBe(0x3c2);
  });
});

// 逐字輸入模擬（每打一字就 normalizeFinals，與 onKeydown 行為一致）
const LATIN2HEB: Record<string, string> = {
  a: "א", b: "ב", g: "ג", d: "ד", h: "ה", v: "ו", z: "ז", x: "ח", f: "ט", y: "י",
  k: "כ", l: "ל", m: "מ", n: "נ", s: "ס", e: "ע", p: "פ", c: "צ", q: "ק", r: "ר", w: "ש", t: "ת",
};
function typeHebrew(s: string): string {
  let v = "";
  for (const ch of s) { v += LATIN2HEB[ch] ?? ch; v = normalizeFinals(v); }
  return v;
}

describe("希伯來文鍵盤 normalizeFinals（字尾形 sofit）", () => {
  it("詞尾的 5 個字母自動換 sofit", () => {
    expect(typeHebrew("wlvm")).toBe("שלום");   // mem → ם
    expect(typeHebrew("mlk")).toBe("מלך");      // kaf → ך
    expect(typeHebrew("arc")).toBe("ארץ");      // tsadi → ץ
  });

  it("詞中維持一般形，後接字母則還原", () => {
    expect(typeHebrew("mlkym")).toBe("מלכים");  // 中 kaf 一般形、尾 mem→ם
    expect(normalizeFinals("מ")).toBe("ם");       // 單字尾 → sofit
    expect(normalizeFinals("מל")).toBe("מל");     // 後接字母 → 還原一般形
  });
});
