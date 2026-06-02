import { describe, it, expect } from "vitest";
import {
  normalizeSources,
  mirrorPrimarySource,
  availableViewModes,
  resolveViewMode,
  migrateLegacyViewMode,
  langLabel,
  zipParallel,
} from "~/lib/multilang-sources";

// Contract for the collected-works multi-language schema. See
// .claude/skills/collected-works-multilang/SKILL.md.

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
