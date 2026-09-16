import { describe, expect, it } from "vitest";
import { DK_PAGE_LINES, dkPages, dkSlice } from "../server/utils/tripitaka";

/** 造一批假的甘珠爾段：`vols` 給每一函要幾行。 */
function segs(vols: Record<number, number>) {
  const out: any[] = [];
  let i = 0;
  for (const [v, n] of Object.entries(vols)) {
    for (let k = 1; k <= n; k++) {
      const folio = `${Math.ceil(k / 6)}b`;
      out.push({
        i: ++i,
        uid: `DKx_v${v}_${folio}${k}`,
        seg: `DKx_v${v}_${folio}${k}`,
        vol: Number(v),
        folio,
        line: k,
        d: -1,
        kind: "line",
        sources: { bo: "ༀ" },
      });
    }
  }
  return out;
}

describe("甘珠爾的函・葉分頁", () => {
  it("一函一頁時，頁數＝函數", () => {
    const pages = dkPages(segs({ 51: 100, 52: 80 }) as any);
    expect(pages.map((p) => p.key)).toEqual(["51:1", "52:1"]);
    expect(pages[0].count).toBe(100);
    expect(pages[1].count).toBe(80);
  });

  it("函不會跨頁 —— 換函一定另起一頁，就算上一頁還沒滿", () => {
    // 這是最容易寫錯的地方：只按行數切，第 51 函的尾巴會跟第 52 函的頭黏成一頁，
    // 頁籤寫「第 51 函」卻含著第 52 函的內容，畫面上完全看不出來。
    const pages = dkPages(segs({ 51: 5, 52: 5 }) as any);
    expect(pages).toHaveLength(2);
    expect(pages[0].vol).toBe(51);
    expect(pages[1].vol).toBe(52);
  });

  it("超過上限的函會切成多頁，且行數不重不漏", () => {
    const all = segs({ 24: DK_PAGE_LINES * 2 + 37 }) as any;
    const pages = dkPages(all);
    expect(pages).toHaveLength(3);
    expect(pages.map((p) => p.key)).toEqual(["24:1", "24:2", "24:3"]);
    expect(pages.reduce((a, p) => a + p.count, 0)).toBe(all.length);

    const seen = pages.flatMap((p) => dkSlice(all, pages, p.key).map((s) => s.uid));
    expect(seen).toHaveLength(all.length);
    expect(new Set(seen).size).toBe(all.length);
    expect(seen).toEqual(all.map((s: any) => s.uid));
  });

  it("重出葉不會讓切片跑掉", () => {
    // 全帙有重出葉（33xa／33xb）。若切片是靠「找到葉碼相同的那一行」回推起點，
    // 就會跳到前一次出現的地方，內容看起來正常但整段錯位。
    const all = segs({ 7: 20 }) as any;
    for (const s of all.slice(10)) s.folio = all[0].folio; // 後半段葉碼與開頭重覆
    const pages = dkPages(all);
    expect(dkSlice(all, pages, pages[0].key).map((s: any) => s.uid))
      .toEqual(all.map((s: any) => s.uid));
  });

  it("頁鍵不認得時回空陣列，不是整部", () => {
    const all = segs({ 51: 50 }) as any;
    expect(dkSlice(all, dkPages(all), "99:9")).toEqual([]);
  });
});
