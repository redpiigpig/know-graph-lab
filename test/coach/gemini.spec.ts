// @vitest-environment node
import { describe, it, expect } from "vitest";
import { parseJsonLoose } from "~/server/utils/gemini";

describe("parseJsonLoose 容錯 JSON 解析", () => {
  it("純 JSON", () => {
    expect(parseJsonLoose('{"a":1,"b":"x"}')).toEqual({ a: 1, b: "x" });
  });

  it("去除 ```json 圍欄", () => {
    const t = "```json\n{\"reply\":\"hi\"}\n```";
    expect(parseJsonLoose(t)).toEqual({ reply: "hi" });
  });

  it("去除純 ``` 圍欄", () => {
    expect(parseJsonLoose("```\n{\"x\":true}\n```")).toEqual({ x: true });
  });

  it("夾在前後文字中的物件也能抽出", () => {
    const t = 'Sure! Here is the JSON:\n{"reply":"hello","corrections":[]}\nHope it helps.';
    expect(parseJsonLoose(t)).toEqual({ reply: "hello", corrections: [] });
  });

  it("結構化教練回覆能解析", () => {
    const t = '{"reply":"Hi","translation":"嗨","corrections":[{"original":"i go","fixed":"I went"}],"new_vocab":[],"homework":null}';
    const p = parseJsonLoose<any>(t);
    expect(p.reply).toBe("Hi");
    expect(p.corrections[0].fixed).toBe("I went");
    expect(p.homework).toBeNull();
  });

  it("無效內容會丟錯", () => {
    expect(() => parseJsonLoose("not json at all")).toThrow();
  });
});
