// @vitest-environment node
import { describe, it, expect } from "vitest";
import { SCRIPT_NODES, SCRIPT_FAMILIES } from "~/data/scriptGenealogy";

const ids = new Set(SCRIPT_NODES.map((n) => n.id));
const famKeys = new Set(SCRIPT_FAMILIES.map((f) => f.key));

describe("文字族譜資料 scriptGenealogy", () => {
  it("id 唯一", () => {
    expect(ids.size).toBe(SCRIPT_NODES.length);
  });

  it("每個 parent.id 都存在", () => {
    for (const n of SCRIPT_NODES)
      for (const p of n.parents)
        expect(ids.has(p.id), `${n.id} → 不存在的父節點 ${p.id}`).toBe(true);
  });

  it("每個 family 都在 SCRIPT_FAMILIES", () => {
    for (const n of SCRIPT_NODES) expect(famKeys.has(n.family), `${n.id} family=${n.family}`).toBe(true);
  });

  it("無自環、無重複父節點", () => {
    for (const n of SCRIPT_NODES) {
      const seen = new Set<string>();
      for (const p of n.parents) {
        expect(p.id, `${n.id} 自環`).not.toBe(n.id);
        expect(seen.has(p.id), `${n.id} 重複父 ${p.id}`).toBe(false);
        seen.add(p.id);
      }
    }
  });

  it("DAG 無環（Kahn 拓撲排序能消化全部節點）", () => {
    const indeg = new Map<string, number>();
    const adj = new Map<string, string[]>();
    for (const n of SCRIPT_NODES) { indeg.set(n.id, 0); adj.set(n.id, []); }
    for (const n of SCRIPT_NODES) for (const p of n.parents) {
      indeg.set(n.id, indeg.get(n.id)! + 1);
      adj.get(p.id)!.push(n.id);
    }
    const queue = [...indeg].filter(([, d]) => d === 0).map(([id]) => id);
    let processed = 0;
    while (queue.length) {
      const id = queue.shift()!;
      processed++;
      for (const c of adj.get(id)!) {
        indeg.set(c, indeg.get(c)! - 1);
        if (indeg.get(c)! === 0) queue.push(c);
      }
    }
    expect(processed, "有環導致無法拓撲排序").toBe(SCRIPT_NODES.length);
  });

  it("至少含這些代表性文字＋規模 >= 90", () => {
    expect(SCRIPT_NODES.length).toBeGreaterThanOrEqual(90);
    for (const id of ["proto-cuneiform", "egyptian", "phoenician", "greek", "latin", "brahmi", "hanzi", "maya", "hangul", "devanagari", "tibetan", "geez"])
      expect(ids.has(id), `缺 ${id}`).toBe(true);
  });

  it("coach 連結指向合理代碼", () => {
    const coached = SCRIPT_NODES.filter((n) => n.coach);
    expect(coached.length).toBeGreaterThan(10); // 多個文字可深連教練
    for (const n of coached) expect(typeof n.coach).toBe("string");
  });
});
