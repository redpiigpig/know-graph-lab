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

  it("每個例字可獨立點讀，且每課有辨字測驗", () => {
    expect(page).toContain("@click=\"speakExample(letter)\"");
    expect(page).toContain("開始本課辨字測驗");
    expect(page).toContain("coach-hbo-alphabet-progress");
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
