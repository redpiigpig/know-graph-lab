import { describe, it, expect } from "vitest";
import { ERAS, canonWorkCount, TIER_LABEL, type DazangWork } from "~/data/dazangjing";

// Structural invariants for 基督教大藏經 (/dazangjing). Data lives in
// data/dazangjing/{ancient,medieval,early-modern,modern}.ts + index.ts.
// See .claude/skills/scripture-canon/SKILL.md §8 and data/dazangjing/TODO.md.

const ERA_KEYS = ["pre", "ancient", "medieval", "early-modern", "modern"];

type Row = { era: string; col: string; canon: "zheng" | "wai"; w: DazangWork };
function allWorks(): Row[] {
  const rows: Row[] = [];
  for (const era of ERAS)
    for (const c of era.collections)
      for (const canon of ["zheng", "wai"] as const)
        for (const d of c[canon].divisions)
          for (const w of d.works) rows.push({ era: era.key, col: c.key, canon, w });
  return rows;
}

describe("dazangjing era structure", () => {
  it("has the five eras in order, all enabled", () => {
    expect(ERAS.map((e) => e.key)).toEqual(ERA_KEYS);
    expect(ERAS.every((e) => e.enabled)).toBe(true);
  });

  it("each collection has zheng+wai with divisions arrays and basic fields", () => {
    for (const era of ERAS) {
      expect(era.collections.length).toBeGreaterThan(0);
      for (const c of era.collections) {
        expect(c.key && c.name && c.glyph).toBeTruthy();
        expect(Array.isArray(c.zheng.divisions)).toBe(true);
        expect(Array.isArray(c.wai.divisions)).toBe(true);
      }
    }
  });

  it("書信藏 簡稱(glyph) is 函, not 信", () => {
    for (const era of ERAS) {
      const s = era.collections.find((c) => c.key === "shuxin");
      if (s) expect(s.glyph).toBe("函");
    }
  });
});

describe("dazangjing work fields", () => {
  const rows = allWorks();

  it("has a substantial corpus", () => {
    expect(rows.length).toBeGreaterThan(1000);
  });

  it("every work carries title_zh + author/era/place/language + intro", () => {
    const bad = rows.filter(
      ({ w }) =>
        !w.title_zh || !w.author || !w.era || !w.place || !w.language || !w.intro,
    );
    expect(bad.map((r) => `${r.era}/${r.col}/${r.w.title_zh}`)).toEqual([]);
  });

  it("intro is a 100–200 字-ish 簡介 (>= 40 chars)", () => {
    const tooShort = rows.filter(({ w }) => (w.intro ?? "").length < 40);
    expect(tooShort.map((r) => `${r.era}/${r.w.title_zh}`)).toEqual([]);
  });

  it("tier only appears on 經藏(jing) 正藏 and uses a valid value", () => {
    for (const { col, canon, w } of rows) {
      if (!w.tier) continue;
      expect(col).toBe("jing");
      expect(canon).toBe("zheng");
      expect(Object.keys(TIER_LABEL)).toContain(w.tier);
    }
  });
});

describe("dazangjing dedup rule (only 經藏 may overlap)", () => {
  function norm(x?: string) {
    return (x ?? "").toLowerCase().replace(/\(.*?\)/g, "").replace(/[\s,.;:\-–—/’']+/g, "");
  }
  it("no work title appears in >=2 non-經藏 collections within an era", () => {
    for (const era of ERAS) {
      const byTitle = new Map<string, Set<string>>();
      for (const c of era.collections)
        for (const canon of ["zheng", "wai"] as const)
          for (const d of c[canon].divisions)
            for (const w of d.works) {
              const k = w.title_zh;
              if (!byTitle.has(k)) byTitle.set(k, new Set());
              byTitle.get(k)!.add(c.key);
            }
      const violations = [...byTitle.entries()]
        .filter(([, cols]) => [...cols].filter((c) => c !== "jing").length >= 2)
        .map(([t]) => `${era.key}:${t}`);
      expect(violations).toEqual([]);
    }
  });
});

describe("dazangjing canon counts", () => {
  it("canonWorkCount matches manual count per canon", () => {
    for (const era of ERAS)
      for (const c of era.collections) {
        const z = c.zheng.divisions.reduce((n, d) => n + d.works.length, 0);
        expect(canonWorkCount(c.zheng)).toBe(z);
      }
  });
});
