/**
 * GET /api/lang/usage  — token 用量 + 估計成本
 * 回傳今日與近 30 天的 token 用量（依 tier/model 分），並用公開單價估算成本。
 * 注意：成本為「估計值」（依 token × 公開單價），非 Google 帳單實際金額。
 */

// 公開單價（USD / 1M tokens）。免費層成本記 0。付費依模型估。
const PRICES: Record<string, { in: number; out: number }> = {
  "gemini-2.5-flash": { in: 0.3, out: 2.5 },
  "gemini-flash-latest": { in: 0.3, out: 2.5 },
  "gemini-2.5-flash-lite": { in: 0.1, out: 0.4 },
  "gemini-2.0-flash": { in: 0.1, out: 0.4 },
  "gemini-2.5-pro": { in: 1.25, out: 10 },
};
const USD_TO_TWD = 32;

function estCost(model: string, tier: string, promptTok: number, outTok: number) {
  if (tier === "free") return 0; // 免費層不計費
  const p = PRICES[model] || { in: 0.3, out: 2.5 };
  return (promptTok / 1e6) * p.in + (outTok / 1e6) * p.out;
}

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const today = new Date().toISOString().slice(0, 10);
  const from30 = new Date(Date.now() - 29 * 86400000).toISOString().slice(0, 10);

  const { data: rows } = await supabase
    .from("lang_api_usage")
    .select("usage_date, tier, model, requests, prompt_tokens, output_tokens")
    .eq("user_id", user.id)
    .gte("usage_date", from30);

  const all = rows ?? [];
  const sum = (filter: (r: any) => boolean) => {
    let req = 0, pin = 0, pout = 0, usd = 0;
    for (const r of all.filter(filter)) {
      req += r.requests;
      pin += Number(r.prompt_tokens);
      pout += Number(r.output_tokens);
      usd += estCost(r.model, r.tier, Number(r.prompt_tokens), Number(r.output_tokens));
    }
    return {
      requests: req,
      promptTokens: pin,
      outputTokens: pout,
      totalTokens: pin + pout,
      costUsd: Math.round(usd * 10000) / 10000,
      costTwd: Math.round(usd * USD_TO_TWD * 100) / 100,
    };
  };

  const monthStart = today.slice(0, 7) + "-01";
  const monthPaid = sum((r) => r.tier === "paid" && r.usage_date >= monthStart);
  const cap = Number(useRuntimeConfig().geminiPaidMonthlyCapTwd) || 0;

  return {
    today: {
      all: sum((r) => r.usage_date === today),
      free: sum((r) => r.usage_date === today && r.tier === "free"),
      paid: sum((r) => r.usage_date === today && r.tier === "paid"),
    },
    last30: sum(() => true),
    last30Paid: sum((r) => r.tier === "paid"),
    monthPaid,                                  // 本月付費估計成本
    paidCapTwd: cap,                            // 每月上限（NT$）
    paidOverCap: cap > 0 && monthPaid.costTwd >= cap, // 是否已達上限（已自動退回免費）
    note: "成本為依 token × 公開單價的估計值，免費層計 0；實際帳單以 Google Cloud Billing 為準。",
  };
});
