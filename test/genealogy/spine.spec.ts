// @vitest-environment node
import { describe, it, expect, vi } from "vitest";
import { bfsPath, resolveSpineWithDiagnostics } from "~/utils/genealogy/spine";

// 小型 parent→children 鄰接表 fixture（純圖、無 DB）：
//   a → b → c → d
//        b → e
// 名字 = id（resolve 用 identity / 查表）
const ch = new Map<string, string[]>([
  ["a", ["b"]],
  ["b", ["c", "e"]],
  ["c", ["d"]],
  ["d", []],
  ["e", []],
]);

describe("bfsPath 最短下行路徑", () => {
  it("src === dst 直接回傳單點路徑", () => {
    expect(bfsPath("a", "a", ch)).toEqual(["a"]);
  });

  it("簡單已知圖回傳預期路徑 a→b→c→d", () => {
    expect(bfsPath("a", "d", ch)).toEqual(["a", "b", "c", "d"]);
  });

  it("分支：a→e 走 a→b→e（不會誤入 c 子樹）", () => {
    expect(bfsPath("a", "e", ch)).toEqual(["a", "b", "e"]);
  });

  it("無下行路徑（逆向 / 不相連）回傳空陣列", () => {
    expect(bfsPath("d", "a", ch)).toEqual([]); // 只能 parent→child，往上不通
    expect(bfsPath("c", "e", ch)).toEqual([]); // c 與 e 是 b 的不同分支
  });

  it("起點不存在於圖中回傳空陣列", () => {
    expect(bfsPath("zzz", "d", ch)).toEqual([]);
  });
});

describe("resolveSpineWithDiagnostics 脊柱降級解析", () => {
  // resolve：identity，名字本身即 id（除非明確當缺失）
  const id = (n: string): string | undefined => n;

  it("完整資料：full=true、path 為 end-to-end 串接、missing 為空", () => {
    const r = resolveSpineWithDiagnostics(["a", "c", "d"], ch, id);
    // a→c 走 a,b,c；c→d 走 c,d（第二段去頭）→ a,b,c,d
    expect(r.path).toEqual(["a", "b", "c", "d"]);
    expect(r.full).toBe(true);
    expect(r.missing).toEqual([]);
    expect(r.brokenAt).toBeUndefined();
  });

  it("某 waypoint 解析不到 → 記入 missing；其餘仍串接，full=false", () => {
    // 'ghost' 解析失敗被濾掉，剩 a、d 仍能 a→b→c→d
    const resolve = (n: string) => (n === "ghost" ? undefined : n);
    const r = resolveSpineWithDiagnostics(["a", "ghost", "d"], ch, resolve);
    expect(r.missing).toEqual(["ghost"]);
    expect(r.path).toEqual(["a", "b", "c", "d"]);
    expect(r.full).toBe(false);
  });

  it("可解析 waypoint 不足 2 個 → path 空、full=false", () => {
    const resolve = (n: string) => (n === "a" ? "a" : undefined);
    const r = resolveSpineWithDiagnostics(["a", "ghost"], ch, resolve);
    expect(r.path).toEqual([]);
    expect(r.full).toBe(false);
    expect(r.missing).toEqual(["ghost"]);
  });

  it("段落間無下行路徑 → 降級回前綴 + brokenAt 標記斷點", () => {
    // a→d OK（a,b,c,d）；但 d→e 無路 → 在 d 斷裂
    const r = resolveSpineWithDiagnostics(["a", "d", "e"], ch, id);
    expect(r.full).toBe(false);
    expect(r.path).toEqual(["a", "b", "c", "d"]); // 只畫到斷點前
    expect(r.brokenAt).toEqual({ from: "d", to: "e" });
  });

  it("第一段就斷 → 至少保留前綴錨點（單一 id）", () => {
    // c→e 不相連，且為第一段 → path 保留 [c]
    const r = resolveSpineWithDiagnostics(["c", "e"], ch, id);
    expect(r.path).toEqual(["c"]);
    expect(r.full).toBe(false);
    expect(r.brokenAt).toEqual({ from: "c", to: "e" });
  });

  it("warn=true 時對缺失 waypoint 發出 console.warn", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const resolve = (n: string) => (n === "ghost" ? undefined : n);
    resolveSpineWithDiagnostics(["a", "ghost", "d"], ch, resolve, { warn: true, label: "X" });
    const msgs = warn.mock.calls.map((c) => c.join(" ")).join("\n");
    expect(msgs).toContain("ghost");
    expect(msgs).toContain("[spine X]");
    warn.mockRestore();
  });
});
