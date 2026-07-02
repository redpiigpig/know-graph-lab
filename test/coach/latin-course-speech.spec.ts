import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";

describe("教會拉丁文課程發音", () => {
  const source = readFileSync("pages/coach/[lang]/course.vue", "utf8");

  it("母音與子音卡片會把例字拆成可單獨播放的按鈕", () => {
    expect(source).not.toContain("firstWord(l.examples)");
    expect(source).toContain("v-for=\"word in splitExamples(l.examples)\"");
    expect(source).toContain("@click=\"speakWord(word)\"");
  });

  it("字母／音組本身有獨立朗讀鈕（走 say 載體音節）", () => {
    expect(source).toContain("@click=\"speakPhone(l)\"");
    expect(source).toContain("p.say || splitExamples(p.examples)[0]");
  });

  it("本頁朗讀預設 0.75 倍速", () => {
    expect(source).toContain("function speakWord(text: string, rate = 0.75)");
    expect(source).not.toContain("speakWord(word, 0.86)");
  });

  it("認讀題也會把例字拆成可單獨播放的按鈕", () => {
    expect(source).toContain("v-for=\"word in splitExamples(readCur.item.examples)\"");
  });
});
