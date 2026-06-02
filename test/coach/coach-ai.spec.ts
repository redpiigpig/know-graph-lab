// @vitest-environment node
import { describe, it, expect } from "vitest";
import { resolveCoachKeys, readUsePaid, monthlyPaidCostTwd } from "~/server/utils/coach-ai";

describe("resolveCoachKeys 選 key 分層", () => {
  const full = { geminiCoachPaidKey: "PAID", geminiCoachFreeKey: "FREE", geminiApiKeys: ["POOL"] };

  it("usePaid 且有付費 key → tier=paid", () => {
    expect(resolveCoachKeys(true, full)).toEqual({ keys: ["PAID"], tier: "paid" });
  });

  it("不付費 → 用專用免費 key", () => {
    expect(resolveCoachKeys(false, full)).toEqual({ keys: ["FREE"], tier: "free" });
  });

  it("免費 key 空 → fallback 共用池", () => {
    expect(resolveCoachKeys(false, { geminiCoachPaidKey: "PAID", geminiCoachFreeKey: "", geminiApiKeys: ["P1", "P2"] }))
      .toEqual({ keys: ["P1", "P2"], tier: "free" });
  });

  it("usePaid 但未設付費 key → 落到免費", () => {
    expect(resolveCoachKeys(true, { geminiCoachPaidKey: "", geminiCoachFreeKey: "FREE", geminiApiKeys: [] }))
      .toEqual({ keys: ["FREE"], tier: "free" });
  });
});

describe("readUsePaid", () => {
  it("只有 usePaid===true 才付費", () => {
    expect(readUsePaid({ usePaid: true })).toBe(true);
    expect(readUsePaid({ usePaid: false })).toBe(false);
    expect(readUsePaid({})).toBe(false);
    expect(readUsePaid({ usePaid: "true" })).toBe(false); // 嚴格布林
  });
});

describe("monthlyPaidCostTwd 估算本月付費成本", () => {
  // 可鏈式、可 await 的假 supabase
  function fakeSupabase(rows: any[]) {
    const chain: any = {
      from: () => chain,
      select: () => chain,
      eq: () => chain,
      gte: () => chain,
      then: (resolve: any) => resolve({ data: rows }),
    };
    return chain;
  }

  it("依模型單價換算 NT$（flash 0.3/2.5 USD per 1M、匯率 32）", async () => {
    // 1,000,000 prompt + 1,000,000 output on flash-latest
    const rows = [{ model: "gemini-flash-latest", prompt_tokens: 1_000_000, output_tokens: 1_000_000 }];
    const cost = await monthlyPaidCostTwd(fakeSupabase(rows), "u1");
    // (0.3 + 2.5) USD * 32 = 89.6
    expect(cost).toBeCloseTo(89.6, 1);
  });

  it("無資料 → 0", async () => {
    expect(await monthlyPaidCostTwd(fakeSupabase([]), "u1")).toBe(0);
  });
});
