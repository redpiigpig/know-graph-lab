// @vitest-environment node
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { compileTemplate, parse } from "@vue/compiler-sfc";

describe("希伯來字母獨立課程", () => {
  const page = readFileSync("pages/coach/[lang]/hebrew-alphabet.vue", "utf8");
  const home = readFileSync("pages/coach/[lang]/index.vue", "utf8");

  it("在希伯來文教練首頁有專屬入口", () => {
    expect(home).toContain("/hebrew-alphabet");
    expect(home).toContain("希伯來字母課");
  });

  it("按字母範圍、字尾形與母音點分成六課", () => {
    for (const key of ["alef-he", "vav-kaf", "lamed-ayin", "pe-tav", "finals", "niqqud"])
      expect(page).toContain(`key: "${key}"`);
  });

  it("每個例字附 BBH2 音標而非現代語音朗讀，且每課有辨字測驗", () => {
    // 發音標準為 Pratico–Van Pelt BBH2 的聖經希伯來文系統。裝置只有現代以色列
    // 語音，會把 ח／ḵ 合併、略掉 ע、把 ק 讀成 k，正好抹掉課本要辨的音位，
    // 因此本課不提供機器朗讀，改標課本音標並外連課本配套網站。
    expect(page).not.toContain("speech.speak");
    expect(page).not.toContain("he-IL");
    expect(page).toContain("letter.translit");
    expect(page).toContain("hebrewsyntax.org/bbh2new");
    expect(page).toContain("開始本課辨字測驗");
    expect(page).toContain("coach-hbo-alphabet-progress");
  });

  it("字母資料以 BBH2 轉寫標音，不採現代以色列讀音", () => {
    const alphabets = readFileSync("server/data/alphabets.ts", "utf8");
    const hbo = alphabets.slice(alphabets.indexOf("const hbo: AlphabetSpec"), alphabets.indexOf("const arc: AlphabetSpec"));
    expect(hbo).toContain("translit: \"ḥayyîm\"");   // ח = ḥ，不是現代語的 kh
    expect(hbo).toContain("translit: \"ʿayin\"");    // ע 是濁喉音，不可省略
    expect(hbo).toContain("translit: \"qōḏeš\"");    // ק = q，與 k 有別
    expect(hbo).toContain("translit: \"bayiṯ\"");    // ת 無 dagesh 作軟音 ṯ
    expect(hbo).toContain("BBH2");
  });

  it("Vue 頁面可正確編譯", () => {
    const parsed = parse(page, { filename: "hebrew-alphabet.vue" });
    expect(parsed.errors).toEqual([]);
    const template = compileTemplate({
      id: "hebrew-alphabet",
      filename: "hebrew-alphabet.vue",
      source: parsed.descriptor.template!.content,
    });
    expect(template.errors).toEqual([]);
  });
});
