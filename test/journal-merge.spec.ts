// @vitest-environment node
import { describe, it, expect } from "vitest";
import { normJournalPart, journalArticleMergeKey } from "~/server/utils/journal-merge";

describe("normJournalPart 期刊欄位正規化", () => {
  it("null / undefined → 空字串", () => {
    expect(normJournalPart(null)).toBe("");
    expect(normJournalPart(undefined)).toBe("");
  });

  it("壓縮連續空白、去頭尾、轉小寫", () => {
    expect(normJournalPart("  The   Foo  Bar  ")).toBe("the foo bar");
  });

  it("換行 / tab 也視為空白並壓縮", () => {
    expect(normJournalPart("A\n\tB")).toBe("a b");
  });

  it("等價變體正規化後相等", () => {
    expect(normJournalPart("Journal Of X")).toBe(normJournalPart("  journal of x "));
  });
});

describe("journalArticleMergeKey 去重合併鍵", () => {
  const base = {
    title: "An Article",
    venue: "Some Journal",
    author: "Jane Doe",
    issue_label: "Vol 1, No 2",
  };

  it("等價輸入（大小寫/空白差異）產生相同 key（碰撞 → 合併）", () => {
    const a = journalArticleMergeKey(base);
    const b = journalArticleMergeKey({
      title: "  an   article ",
      venue: "SOME JOURNAL",
      author: "jane doe",
      issue_label: "vol 1,  no 2",
    });
    expect(a).toBe(b);
  });

  it("title 不同 → key 不同（不誤併）", () => {
    expect(journalArticleMergeKey(base)).not.toBe(
      journalArticleMergeKey({ ...base, title: "Another Article" }),
    );
  });

  it("author 不同 → key 不同", () => {
    expect(journalArticleMergeKey(base)).not.toBe(
      journalArticleMergeKey({ ...base, author: "John Smith" }),
    );
  });

  it("key 以 4 個欄位用 | 串接，且 null 欄位變空", () => {
    const k = journalArticleMergeKey({ title: "T", venue: null, author: null, issue_label: null });
    expect(k).toBe("t|||");
    expect(k.split("|")).toHaveLength(4);
  });
});
