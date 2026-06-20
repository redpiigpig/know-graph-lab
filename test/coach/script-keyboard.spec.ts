// @vitest-environment node
import { describe, it, expect } from "vitest";
import { translitChar, getScriptKeyboard, makeScriptKeyboard, SCRIPT_SPECS } from "~/composables/useScriptKeyboard";

// 模擬一個 textarea：只需 value / selectionStart / selectionEnd
function fakeEl(value = "", cursor = value.length) {
  return { value, selectionStart: cursor, selectionEnd: cursor } as unknown as HTMLTextAreaElement;
}
// 模擬逐鍵輸入一串 Latin → 目標文字（走 onKeydown）
function typeScript(specKey: string, s: string): string {
  const kb = getScriptKeyboard(specKey)!;
  let value = "";
  for (const ch of s) {
    const el = fakeEl(value);
    let prevented = false;
    const e = { key: ch, ctrlKey: false, metaKey: false, altKey: false, preventDefault: () => { prevented = true; } } as unknown as KeyboardEvent;
    const handled = kb.onKeydown(e, el, (v) => { value = v; });
    // 未處理（如標點）就照原樣 append（模擬瀏覽器預設）
    if (!handled) value += ch;
    expect(handled).toBe(prevented); // handled 時必有 preventDefault
  }
  return value;
}

describe("通用轉寫鍵盤 useScriptKeyboard", () => {
  it("translitChar：各文字核心對照", () => {
    expect(translitChar("cyrillic", "a")).toBe("а");
    expect(translitChar("cyrillic", "c")).toBe("ц");
    expect(translitChar("coptic", "a")).toBe("ⲁ");
    expect(translitChar("coptic", "w")).toBe("ⲱ");
    expect(translitChar("arabic", "a")).toBe("ا");
    expect(translitChar("arabic", "H")).toBe("ح"); // 大寫鍵＝不同字母
    expect(translitChar("syriac", "a")).toBe("ܐ");
    expect(translitChar("syriac", "T")).toBe("ܛ");
    expect(translitChar("armenian", "a")).toBe("ա");
    expect(translitChar("georgian", "a")).toBe("ა");
    expect(translitChar("georgian", "T")).toBe("თ"); // unicase 大寫鍵
  });

  it("bicameral 大寫鍵自動產生大寫字母（西里爾/科普特/亞美尼亞）", () => {
    expect(translitChar("cyrillic", "A")).toBe("А");
    expect(translitChar("coptic", "B")).toBe("Ⲃ");
    expect(translitChar("armenian", "A")).toBe("Ա");
  });

  it("caseSensitive 文字：未定義的鍵回 undefined（不亂轉）", () => {
    expect(translitChar("arabic", "p")).toBeUndefined(); // 阿拉伯無 p
    expect(translitChar("syriac", "f")).toBeUndefined(); // 此表無 f
  });

  it("getScriptKeyboard：內建 greek/kana/hebrew 與未知回 null（不搶它們的特例邏輯）", () => {
    expect(getScriptKeyboard("greek")).toBeNull();
    expect(getScriptKeyboard("hebrew")).toBeNull();
    expect(getScriptKeyboard("kana")).toBeNull();
    expect(getScriptKeyboard("zz")).toBeNull();
    expect(getScriptKeyboard(undefined)).toBeNull();
    expect(getScriptKeyboard("cyrillic")).not.toBeNull();
  });

  it("onKeydown 逐鍵輸入：拼出整個詞", () => {
    expect(typeScript("cyrillic", "mir")).toBe("мир");          // 和平
    expect(typeScript("coptic", "nai")).toBe("ⲛⲁⲓ");
    expect(typeScript("arabic", "bab")).toBe("باب");           // 門（RTL 邏輯順序）
    expect(typeScript("syriac", "aba")).toBe("ܐܒܐ");
    expect(typeScript("georgian", "ena")).toBe("ენა");         // 語言
  });

  it("onKeydown：空白照插、未對應標點不攔（回退預設）", () => {
    expect(typeScript("cyrillic", "a b")).toBe("а б");
    expect(typeScript("cyrillic", "a1")).toBe("а1"); // 數字不轉、append
  });

  it("palette 含核心字母與額外字母；marks 為附加符號", () => {
    const ar = makeScriptKeyboard(SCRIPT_SPECS.arabic);
    expect(ar.rtl).toBe(true);
    expect(ar.palette.some((p) => p.ch === "ا" && p.latin === "a")).toBe(true);
    expect(ar.palette.some((p) => p.ch === "ء")).toBe(true); // hamza 為 extra（無 latin 單鍵）
    expect(ar.marks.length).toBeGreaterThan(0);
    const cyr = makeScriptKeyboard(SCRIPT_SPECS.cyrillic);
    expect(cyr.rtl).toBe(false);
    expect(cyr.palette.some((p) => p.ch === "ѣ")).toBe(true); // 教會斯拉夫古字母 yat
  });
});
