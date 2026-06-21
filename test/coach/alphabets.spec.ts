// @vitest-environment node
import { describe, it, expect } from "vitest";
import { ALPHABETS, alphabetForClient } from "~/server/data/alphabets";

describe("字母教學資料 alphabets", () => {
  it("每份 spec 結構完整、language 與 key 一致", () => {
    for (const [key, spec] of Object.entries(ALPHABETS)) {
      expect(spec.language, `${key} language 不符`).toBe(key);
      expect(spec.title).toBeTruthy();
      expect(spec.intro.length).toBeGreaterThan(5);
      expect(spec.groups.length).toBeGreaterThan(0);
      for (const g of spec.groups) {
        expect(g.letters.length, `${key}/${g.key} 無字母`).toBeGreaterThan(0);
        for (const l of g.letters) {
          expect(l.char, `${key}/${g.key} 缺 char`).toBeTruthy();
          expect(l.name, `${key} ${l.char} 缺 name`).toBeTruthy();
          expect(l.sound, `${key} ${l.char} 缺 sound`).toBeTruthy();
        }
      }
    }
  });

  it("新增的書寫系統都有字母表（接轉寫鍵盤）", () => {
    for (const lang of ["att", "arc", "chu", "ar", "syr", "cop", "hy", "ka", "sa", "pra", "bo", "gez", "mid"])
      expect(alphabetForClient(lang), `缺 ${lang} 字母表`).toBeTruthy();
  });

  it("RTL 文字標 rtl=true（希伯來/亞蘭/阿拉伯/敘利亞/曼達）", () => {
    for (const lang of ["hbo", "arc", "ar", "syr", "mid"]) expect(alphabetForClient(lang)!.rtl).toBe(true);
    for (const lang of ["chu", "hy", "ka", "sa", "bo", "gez"]) expect(alphabetForClient(lang)!.rtl).toBeFalsy();
  });

  it("阿拉伯 28 字母、敘利亞 22 子音、希臘 24（含 att）", () => {
    expect(alphabetForClient("ar")!.groups[0].letters.length).toBe(28);
    expect(alphabetForClient("syr")!.groups[0].letters.length).toBe(22);
    expect(alphabetForClient("att")!.groups[0].letters.length).toBe(24);
  });

  it("英文不提供字母表", () => {
    expect(alphabetForClient("en")).toBeUndefined();
  });
});
