// @vitest-environment node
import { describe, it, expect } from "vitest";
import {
  translitDevanagari, translitGeez, translitTibetan,
  getAbugidaKeyboard, makeAbugidaKeyboard, ABUGIDA_SPECS,
} from "~/composables/useAbugidaKeyboard";

function fakeEl(value = "", cursor = value.length) {
  return { value, selectionStart: cursor, selectionEnd: cursor } as unknown as HTMLTextAreaElement;
}
// 逐鍵打一串，回螢幕最終值（走 onKeydown，模擬瀏覽器預設 append）
function typeKb(specKey: string, s: string): string {
  const kb = getAbugidaKeyboard(specKey)!;
  let value = "";
  for (const ch of s) {
    const el = fakeEl(value);
    const e = { key: ch, ctrlKey: false, metaKey: false, altKey: false, isComposing: false, preventDefault() {} } as unknown as KeyboardEvent;
    const handled = kb.onKeydown(e, el, (v) => { value = v; });
    if (!handled) value += ch;
  }
  return value;
}

describe("天城體 translitDevanagari（ITRANS）", () => {
  it("子音固有母音 a", () => {
    expect(translitDevanagari("ka")).toBe("क");
    expect(translitDevanagari("k")).toBe("क"); // 末尾固有 a
  });
  it("母音記號 matra 與獨立母音", () => {
    expect(translitDevanagari("ki")).toBe("कि");
    expect(translitDevanagari("kii")).toBe("की");
    expect(translitDevanagari("i")).toBe("इ");       // 獨立
    expect(translitDevanagari("aa")).toBe("आ");
  });
  it("合字（子音接子音插虛音符）", () => {
    expect(translitDevanagari("dharma")).toBe("धर्म");
    expect(translitDevanagari("namaste")).toBe("नमस्ते");
    expect(translitDevanagari("OM")).toBe("ॐ");
  });
});

describe("吉茲 translitGeez（fidäl 音節階，SERA）", () => {
  it("孤立子音＝6 階 ə；e→1階(ä)，其餘母音換階", () => {
    expect(translitGeez("he")).toBe("ሀ");   // hä（1 階）
    expect(translitGeez("hu")).toBe("ሁ");
    expect(translitGeez("hi")).toBe("ሂ");
    expect(translitGeez("ha")).toBe("ሃ");
    expect(translitGeez("ho")).toBe("ሆ");
    expect(translitGeez("h")).toBe("ህ");    // 孤立＝6 階 ə
  });
  it("多字母子音與字首母音、整詞拼寫", () => {
    expect(translitGeez("sxa")).toBe("ሣ");  // ś + a
    expect(translitGeez("'a")).toBe("ኣ");   // ʾ(glottal) + a
    expect(translitGeez("selam")).toBe("ሰላም"); // sä-la-m(ə) = 平安
  });
});

describe("藏文 translitTibetan（Wylie，+顯式疊寫）", () => {
  it("子音與固有母音 a", () => {
    expect(translitTibetan("ka")).toBe("ཀ");
    expect(translitTibetan("kha")).toBe("ཁ");
    expect(translitTibetan("a")).toBe("ཨ"); // 獨立母音承載
  });
  it("母音記號", () => {
    expect(translitTibetan("ki")).toBe("ཀི");
    expect(translitTibetan("ku")).toBe("ཀུ");
  });
  it("顯式疊寫 +（後加子音）", () => {
    expect(translitTibetan("r+k")).toBe("རྐ"); // ར + 後加ka(ྐ)
  });
});

describe("有狀態鍵盤工廠：逐鍵輸入與 commit", () => {
  it("天城體逐鍵打整詞", () => {
    expect(typeKb("devanagari", "dharma")).toBe("धर्म");
    expect(typeKb("devanagari", "namaste")).toBe("नमस्ते");
  });
  it("空白 commit 後新詞重新計算（不污染前一詞）", () => {
    expect(typeKb("devanagari", "ka ki")).toBe("क कि");
  });
  it("藏文空白＝音節點 tsheg", () => {
    expect(typeKb("tibetan", "ka kha")).toBe("ཀ་ཁ");
  });
  it("Backspace 退一個 roman 字元後重算", () => {
    const kb = getAbugidaKeyboard("devanagari")!;
    let value = "";
    const press = (key: string) => {
      const el = fakeEl(value);
      const e = { key, ctrlKey: false, metaKey: false, altKey: false, isComposing: false, preventDefault() {} } as unknown as KeyboardEvent;
      const handled = kb.onKeydown(e, el, (v) => { value = v; });
      if (!handled && key.length === 1) value += key;
    };
    "kii".split("").forEach(press);
    expect(value).toBe("की");
    press("Backspace"); // 退掉一個 i → "ki"
    expect(value).toBe("कि");
  });
  it("getAbugidaKeyboard 未知回 null；palette/marks 存在", () => {
    expect(getAbugidaKeyboard("zz")).toBeNull();
    expect(getAbugidaKeyboard(undefined)).toBeNull();
    const dv = makeAbugidaKeyboard(ABUGIDA_SPECS.devanagari);
    expect(dv.palette.length).toBeGreaterThan(0);
    expect(dv.marks.length).toBeGreaterThan(0);
    expect(dv.rtl).toBe(false);
  });
});
