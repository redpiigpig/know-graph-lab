import { describe, it, expect } from "vitest";
import {
  normalizeSources,
  mirrorPrimarySource,
  availableViewModes,
  resolveViewMode,
  migrateLegacyViewMode,
  langLabel,
  zipParallel,
  BLANK_PARAGRAPH,
  alignByAnchors,
  chineseNumeral,
  romanNumeral,
} from "~/lib/multilang-sources";

// Contract for the collected-works multi-language schema. See
// .claude/skills/ebook-collected-works/SKILL.md.

describe("normalizeSources", () => {
  it("returns explicit sources honouring source_order", () => {
    const r = normalizeSources({
      sources: { de: "DE", en: "EN" },
      source_order: ["de", "en"],
    });
    expect(r.sources).toEqual({ de: "DE", en: "EN" });
    expect(r.source_order).toEqual(["de", "en"]);
  });

  it("filters source_order to keys that exist", () => {
    const r = normalizeSources({
      sources: { de: "DE" },
      source_order: ["de", "en"], // en not present
    });
    expect(r.source_order).toEqual(["de"]);
  });

  it("appends source keys missing from source_order (no column dropped)", () => {
    const r = normalizeSources({
      sources: { de: "DE", en: "EN", la: "LA" },
      source_order: ["de"], // en + la omitted
    });
    expect(new Set(r.source_order)).toEqual(new Set(["de", "en", "la"]));
    expect(r.source_order[0]).toBe("de"); // explicit order respected first
  });

  it("falls back to the legacy single source", () => {
    const r = normalizeSources({ source_lang: "en", source_text: "Hello" });
    expect(r.sources).toEqual({ en: "Hello" });
    expect(r.source_order).toEqual(["en"]);
  });

  it("treats an empty content source_text ('') as a real source", () => {
    // source_text='' is meaningful (an aligned-but-blank cell), only null/missing is monolingual
    const r = normalizeSources({ source_lang: "de", source_text: "" });
    expect(r.source_order).toEqual(["de"]);
    expect(r.sources).toEqual({ de: "" });
  });

  it("is monolingual (empty) when no sources at all", () => {
    expect(normalizeSources({})).toEqual({ sources: {}, source_order: [] });
    expect(normalizeSources({ source_text: "x", source_lang: null })).toEqual({
      sources: {},
      source_order: [],
    });
    expect(normalizeSources({ sources: {} })).toEqual({ sources: {}, source_order: [] });
  });
});

describe("mirrorPrimarySource (writer-side back-compat)", () => {
  it("mirrors source_text/source_lang to the first source", () => {
    const out = mirrorPrimarySource({
      content: "中譯",
      sources: { de: "DE", en: "EN" },
      source_order: ["de", "en"],
    } as any);
    expect(out.source_lang).toBe("de");
    expect(out.source_text).toBe("DE");
    expect(out.sources).toEqual({ de: "DE", en: "EN" });
    expect(out.source_order).toEqual(["de", "en"]);
  });

  it("legacy two-column chunk round-trips unchanged", () => {
    const out = mirrorPrimarySource({ source_lang: "en", source_text: "Hi" } as any);
    expect(out.source_lang).toBe("en");
    expect(out.source_text).toBe("Hi");
    expect(out.source_order).toEqual(["en"]);
  });

  it("monolingual chunk keeps null source fields", () => {
    const out = mirrorPrimarySource({ content: "純中文" } as any);
    expect(out.source_lang).toBeNull();
    expect(out.source_text).toBeNull();
  });

  it("does not mutate the input", () => {
    const input = { sources: { de: "DE" }, source_order: ["de"] } as any;
    const snapshot = JSON.parse(JSON.stringify(input));
    mirrorPrimarySource(input);
    expect(input).toEqual(snapshot);
  });
});

describe("availableViewModes", () => {
  it("monolingual → only 中", () => {
    expect(availableViewModes([])).toEqual(["zh"]);
  });
  it("legacy bilingual → 中 / 對照 / 英", () => {
    expect(availableViewModes(["en"])).toEqual(["zh", "parallel", "src:en"]);
  });
  it("trilingual → 中 / 對照 / 德 / 英 in source order", () => {
    expect(availableViewModes(["de", "en"])).toEqual(["zh", "parallel", "src:de", "src:en"]);
  });
});

describe("resolveViewMode (stale-mode clamping)", () => {
  it("keeps a valid desired mode", () => {
    expect(resolveViewMode("src:de", ["de", "en"])).toBe("src:de");
    expect(resolveViewMode("parallel", ["de", "en"])).toBe("parallel");
  });
  it("falls back to zh for a source the chunk lacks", () => {
    expect(resolveViewMode("src:de", ["en"])).toBe("zh");
  });
  it("falls back to zh on a monolingual chunk", () => {
    expect(resolveViewMode("parallel", [])).toBe("zh");
    expect(resolveViewMode("src:en", [])).toBe("zh");
  });
  it("falls back to zh for null/undefined/garbage", () => {
    expect(resolveViewMode(null, ["de"])).toBe("zh");
    expect(resolveViewMode(undefined, ["de"])).toBe("zh");
    expect(resolveViewMode("nonsense", ["de"])).toBe("zh");
  });
});

describe("migrateLegacyViewMode", () => {
  it("maps legacy bi → parallel", () => {
    expect(migrateLegacyViewMode("bi", ["en"])).toBe("parallel");
  });
  it("maps legacy en → primary source single-column", () => {
    expect(migrateLegacyViewMode("en", ["en"])).toBe("src:en");
    expect(migrateLegacyViewMode("en", ["de", "en"])).toBe("src:de"); // primary = first
  });
  it("legacy en with no sources → zh", () => {
    expect(migrateLegacyViewMode("en", [])).toBe("zh");
  });
  it("passes through already-generalized values + null", () => {
    expect(migrateLegacyViewMode("zh", ["de"])).toBe("zh");
    expect(migrateLegacyViewMode("parallel", ["de"])).toBe("parallel");
    expect(migrateLegacyViewMode("src:de", ["de"])).toBe("src:de");
    expect(migrateLegacyViewMode(null, ["de"])).toBe("zh");
  });
});

describe("langLabel", () => {
  it("maps known codes to CJK labels", () => {
    expect(langLabel("de")).toBe("德");
    expect(langLabel("en")).toBe("英");
    expect(langLabel("grc")).toBe("希臘");
  });
  it("uppercases unknown codes", () => {
    expect(langLabel("xx")).toBe("XX");
  });
});

describe("zipParallel", () => {
  it("zips equal-length columns by index", () => {
    const rows = zipParallel(
      ["中1", "中2"],
      { de: ["DE1", "DE2"], en: ["EN1", "EN2"] },
      ["de", "en"]
    );
    expect(rows).toHaveLength(2);
    expect(rows[0]).toEqual({ zh: "中1", cols: { de: "DE1", en: "EN1" } });
    expect(rows[1]).toEqual({ zh: "中2", cols: { de: "DE2", en: "EN2" } });
  });

  it("pads short columns with '' rather than shifting rows", () => {
    const rows = zipParallel(
      ["中1", "中2", "中3"],
      { de: ["DE1"], en: ["EN1", "EN2"] },
      ["de", "en"]
    );
    expect(rows).toHaveLength(3); // driven by the longest column (zh)
    expect(rows[1]).toEqual({ zh: "中2", cols: { de: "", en: "EN2" } });
    expect(rows[2]).toEqual({ zh: "中3", cols: { de: "", en: "" } });
  });

  it("a source longer than zh still extends the row count", () => {
    const rows = zipParallel(["中1"], { de: ["DE1", "DE2"] }, ["de"]);
    expect(rows).toHaveLength(2);
    expect(rows[1]).toEqual({ zh: "", cols: { de: "DE2" } });
  });

  it("empty everything → no rows", () => {
    expect(zipParallel([], {}, [])).toEqual([]);
  });
});

// BLANK_PARAGRAPH holds a slot in a source column that only fills SOME indices
// (e.g. a Latin original aligned to the 繁中 by paragraphus number — numbered
// body paragraphs match, headings and footnote blocks have no counterpart).
// The reader rebuilds each column with `split(/\n{2,}/).map(trim).filter(Boolean)`,
// so the filler must survive BOTH trim and the truthiness filter; if it does not,
// every later row in that column silently shifts up.
describe("BLANK_PARAGRAPH", () => {
  const splitLikeReader = (md: string) =>
    md.split(/\n{2,}/).map((p) => p.trim()).filter(Boolean);

  it("survives the reader's paragraph split so positions are preserved", () => {
    const col = ["", "alpha", "", "beta"].map((p) => p || BLANK_PARAGRAPH);
    const paras = splitLikeReader(col.join("\n\n"));
    expect(paras).toHaveLength(4);
    expect(paras[1]).toBe("alpha");
    expect(paras[3]).toBe("beta");
  });

  it("keeps a Latin column aligned with the 中文 column through zipParallel", () => {
    const zh = ["# 第十一章", "17. 我自幼…", "18. 我懇求禰…"];
    const la = [BLANK_PARAGRAPH, "audieram…", "obsecro te…"];
    const rows = zipParallel(zh, { la }, ["la"]);
    expect(rows[1].cols.la).toBe("audieram…");
    expect(rows[2].cols.la).toBe("obsecro te…");
  });

  it("is dropped by the split if a writer uses an ordinary blank instead", () => {
    // Regression guard: NBSP and "" are both filtered out — the bug this exists to prevent.
    expect(splitLikeReader(["", "alpha"].join("\n\n"))).toEqual(["alpha"]);
    expect(splitLikeReader([" ", "alpha"].join("\n\n"))).toEqual(["alpha"]);
  });
});

// alignByAnchors repairs the 對照 grid without touching stored data. Index
// zipping only holds when both sides split into the same number of paragraphs,
// which is true for 30% of 教父 chunks; the rest drift while looking normal.
describe("alignByAnchors", () => {
  it("anchors on the leading section number and blanks the rest", () => {
    // Confessions 卷一第11-18章 shape: the 繁中 side's footnote separator is too
    // short to be recognised, so its footnote items sit in the body between the
    // numbered sections. Index zipping slides §18 up beside a 繁中 footnote.
    const zh = ["# 第十一章", "17. 我自幼就聽聞了…", "(161) 一種西方教會的聖禮…",
                "18. 我懇求禰，我的上帝…"];
    const en = ["Chapter XI.—Seized by Disease…", "17. Even as a boy I had heard…",
                "18. I beseech Thee, my God…"];
    expect(alignByAnchors(zh, en)).toEqual([
      "Chapter XI.—Seized by Disease…",
      "17. Even as a boy I had heard…",
      "",
      "18. I beseech Thee, my God…",
    ]);
  });

  it("folds an extra source paragraph into the stretch's last slot, not the next row", () => {
    const zh = ["1. alpha", "narrative", "2. beta"];
    const en = ["1. alpha", "ref line", "narrative", "2. beta"];
    const got = alignByAnchors(zh, en)!;
    expect(got[0]).toBe("1. alpha");
    expect(got[1]).toBe("ref line\n\nnarrative");
    expect(got[2]).toBe("2. beta"); // the next anchor resets the drift
  });

  it("zips a stretch from its start when the source side is shorter", () => {
    // 《懺悔錄》卷四第1-10章: the rows before the first anchor were already paired
    // correctly by plain index zipping. Collapsing that stretch into one cell —
    // an earlier version of this function did — threw six good rows away.
    const zh = ["第四冊。", "# 第一章", "1. 從我十九歲…", "a", "b", "2. 那些年間…"];
    const en = ["Book IV.", "Chapter I.—…", "1. During this space…", "2. In those years…"];
    const got = alignByAnchors(zh, en)!;
    expect(got.slice(0, 3)).toEqual(["Book IV.", "Chapter I.—…", "1. During this space…"]);
    expect(got[3]).toBe("");
    expect(got[5]).toBe("2. In those years…");
  });

  it("keeps one-to-one granularity when a stretch matches in length", () => {
    const zh = ["1. alpha", "mid", "2. beta", "tail"];
    const en = ["1. A", "MID", "2. B", "TAIL"];
    expect(alignByAnchors(zh, en)).toEqual(["1. A", "MID", "2. B", "TAIL"]);
  });

  it("falls back to page markers when there are no section numbers", () => {
    const zh = ["{{p:226}} 講道集第三十八篇", "他既講完了…", "{{p:227}} 但這些邪惡的魔鬼…"];
    const en = ["{{p:226}} Homily XXXVIII.", "1 Cor. xv. 1, 2", "Having finished…",
                "{{p:227}} But these things…"];
    const got = alignByAnchors(zh, en)!;
    expect(got[0]).toBe("{{p:226}} Homily XXXVIII.");
    expect(got[1]).toBe("1 Cor. xv. 1, 2\n\nHaving finished…");
    expect(got[2]).toBe("{{p:227}} But these things…");
  });

  it("ignores a marker that repeats — it cannot say which occurrence is which", () => {
    const zh = ["1. a", "1. a again", "2. b", "3. c"];
    const en = ["1. A", "1. A again", "2. B", "3. C"];
    const got = alignByAnchors(zh, en)!;
    expect(got[2]).toBe("2. B");
    expect(got[3]).toBe("3. C");
  });

  it("returns null when fewer than two anchors are shared", () => {
    expect(alignByAnchors(["# 前言", "正文"], ["# Preface", "Body"])).toBeNull();
    expect(alignByAnchors(["1. a", "x"], ["1. A", "X"])).toBeNull();
    expect(alignByAnchors([], ["1. A", "2. B"])).toBeNull();
  });

  it("never drops source text", () => {
    const zh = ["1. a", "2. b"];
    const en = ["preamble", "1. A", "extra", "2. B", "trailing"];
    const got = alignByAnchors(zh, en)!;
    for (const p of en) expect(got.join("\n\n")).toContain(p);
  });

  it("output length always matches the 繁中 column", () => {
    const zh = ["1. a", "x", "y", "2. b", "z"];
    const got = alignByAnchors(zh, ["1. A", "2. B"])!;
    expect(got).toHaveLength(zh.length);
  });
});

describe("numeral helpers", () => {
  it("reads Chinese numerals", () => {
    expect(chineseNumeral("一")).toBe(1);
    expect(chineseNumeral("十")).toBe(10);
    expect(chineseNumeral("十二")).toBe(12);
    expect(chineseNumeral("二十一")).toBe(21);
    expect(chineseNumeral("一百")).toBe(100);
    expect(chineseNumeral("一百二十三")).toBe(123);
  });
  it("reads Roman numerals and plain digits", () => {
    expect(romanNumeral("XXI")).toBe(21);
    expect(romanNumeral("IV")).toBe(4);
    expect(romanNumeral("MCMXC")).toBe(1990);
    expect(romanNumeral("21")).toBe(21);
  });
  it("returns null rather than guessing", () => {
    expect(chineseNumeral("甲")).toBeNull();
    expect(chineseNumeral("")).toBeNull();
    expect(romanNumeral("ABC")).toBeNull();
    expect(romanNumeral("")).toBeNull();
  });
});

describe("alignByAnchors — chapter headings", () => {
  it("matches 第N章 against Chapter N across the two numeral systems", () => {
    // 《上帝之城》卷一: no section numbers and no shared page markers; the only
    // thing both sides carry is the chapter number, in different scripts.
    const zh = ["# 第一章——基督名號的敵人", "蓋此塵世城邦屬於眾敵…",
                "第二章——戰爭的慣例中…", "有無數的戰爭歷史…"];
    const en = ["Chapter 1.—Of the Adversaries of the Name of Christ", "For to this earthly city…",
                "Chapter 2.—That It is Quite Contrary to the Usage of War", "There are histories…"];
    expect(alignByAnchors(zh, en)).toEqual(en);
  });

  it("reads Roman-numbered chapter headings too", () => {
    const zh = ["# 第十一章 甲", "x", "# 第十二章 乙", "y"];
    const en = ["Chapter XI.—A", "X", "Chapter XII.—B", "Y"];
    expect(alignByAnchors(zh, en)).toEqual(en);
  });

  it("prefers section numbers over chapter headings when both exist", () => {
    // Section numbers cut finer, so they win; the chapter key is the fallback.
    const zh = ["# 第一章", "1. a", "extra", "2. b"];
    const en = ["Chapter 1.", "1. A", "2. B"];
    const got = alignByAnchors(zh, en)!;
    expect(got[1]).toBe("1. A");
    expect(got[3]).toBe("2. B");
  });

  it("takes the key that yields the most pairs, not the first that yields any", () => {
    // 《上帝之城》卷十三: three shared page markers, four shared chapter numbers.
    // Stopping at the first key with a hit picks the coarser one and leaves the
    // chapter headings a row out of step.
    const zh = ["{{p:246}} 甲", "# 第一章", "# 第二章", "# 第三章", "{{p:247}} 乙"];
    const en = ["{{p:246}} A", "Chapter 1.", "x", "Chapter 2.", "Chapter 3.", "{{p:247}} B"];
    const got = alignByAnchors(zh, en)!;
    expect(got[1]).toBe("Chapter 1.\n\nx");
    expect(got[2]).toBe("Chapter 2.");
    expect(got[3]).toBe("Chapter 3.");
  });
});
