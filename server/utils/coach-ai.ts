// ============================================================================
// 語言教練的 Gemini 呼叫包裝：
//  - 依使用者偏好選免費 / 付費 key（免費優先）
//  - 免費額度用完 → 拋 code='free_exhausted'，前端跳確認後改付費
//  - 記錄 token 用量（給網頁顯示用量與估計成本）
// ============================================================================
import { callGeminiFull, type GeminiCallOpts } from "~/server/utils/gemini";

export type Tier = "free" | "paid";

// 依 usePaid 解析要用的 key 池與 tier
export function resolveCoachKeys(usePaid: boolean, cfg?: any): { keys: string[]; tier: Tier } {
  const config = cfg ?? useRuntimeConfig();
  const paid = config.geminiCoachPaidKey as string | undefined;
  const free = config.geminiCoachFreeKey as string | undefined;

  if (usePaid && paid) return { keys: [paid], tier: "paid" };

  // 免費：優先用專用免費 key，否則 fallback 既有共用池（Gemini_API_Key_*）
  if (free) return { keys: [free], tier: "free" };
  const pool = (config.geminiApiKeys as string[]) || [];
  return { keys: pool, tier: "free" };
}

interface CoachCtx {
  usePaid: boolean;
  userId: string;
  supabase: any;
}

// 只有站長（allowedEmail）能動用付費 key，避免其他註冊用戶燒錢
async function isOwner(supabase: any, userId: string): Promise<boolean> {
  const config = useRuntimeConfig();
  const owner = config.public.allowedEmail as string | undefined;
  if (!owner) return true; // 未設白名單 → 不限制
  try {
    const { data } = await supabase.auth.admin.getUserById(userId);
    return data?.user?.email === owner;
  } catch {
    return false;
  }
}

// 付費模型估計單價（USD / 1M tokens）
const PAID_PRICES: Record<string, { in: number; out: number }> = {
  "gemini-2.5-flash": { in: 0.3, out: 2.5 },
  "gemini-flash-latest": { in: 0.3, out: 2.5 },
  "gemini-2.5-flash-lite": { in: 0.1, out: 0.4 },
  "gemini-2.0-flash": { in: 0.1, out: 0.4 },
  "gemini-2.5-pro": { in: 1.25, out: 10 },
};
const USD_TO_TWD = 32;

// 本月付費估計成本（NT$）
export async function monthlyPaidCostTwd(supabase: any, userId: string): Promise<number> {
  const monthStart = new Date().toISOString().slice(0, 7) + "-01";
  const { data } = await supabase
    .from("lang_api_usage")
    .select("model, prompt_tokens, output_tokens")
    .eq("user_id", userId)
    .eq("tier", "paid")
    .gte("usage_date", monthStart);
  let usd = 0;
  for (const r of data ?? []) {
    const p = PAID_PRICES[r.model] || { in: 0.3, out: 2.5 };
    usd += (Number(r.prompt_tokens) / 1e6) * p.in + (Number(r.output_tokens) / 1e6) * p.out;
  }
  return Math.round(usd * USD_TO_TWD * 100) / 100;
}

/**
 * 語言教練專用 Gemini 呼叫。回傳純文字。
 * 額度用完時：免費 → 429 code=free_exhausted（前端提示切換）；付費 → 429 code=paid_exhausted。
 * 成功時把 token 用量累加進 lang_api_usage。
 */
export async function coachGemini(opts: GeminiCallOpts, ctx: CoachCtx): Promise<string> {
  const config = useRuntimeConfig();
  // 付費 key 僅限站長使用（保護荷包）
  let usePaid = ctx.usePaid;
  if (usePaid && !(await isOwner(ctx.supabase, ctx.userId))) usePaid = false;
  // 本月付費成本超過上限 → 自動退回免費（防爆帳單）
  if (usePaid) {
    const cap = Number(config.geminiPaidMonthlyCapTwd) || 0;
    if (cap > 0 && (await monthlyPaidCostTwd(ctx.supabase, ctx.userId)) >= cap) {
      usePaid = false;
    }
  }
  const { keys, tier } = resolveCoachKeys(usePaid);
  if (!keys.length) {
    throw createError({
      statusCode: 400,
      data: { code: tier === "paid" ? "no_paid_key" : "no_free_key" },
      message: tier === "paid" ? "尚未設定付費 Gemini key" : "尚未設定 Gemini key",
    });
  }

  let result;
  try {
    result = await callGeminiFull({ ...opts, keys });
  } catch (e: any) {
    if (e?.data?.code === "quota_exhausted") {
      throw createError({
        statusCode: 429,
        data: { code: tier === "free" ? "free_exhausted" : "paid_exhausted", tier },
        message: tier === "free" ? "免費 Gemini 額度今日已用完" : "付費 Gemini 額度已用完",
      });
    }
    throw e;
  }

  // 記錄用量（fire-and-forget，不阻塞回應）
  const today = new Date().toISOString().slice(0, 10);
  ctx.supabase
    .rpc("bump_lang_usage", {
      p_user: ctx.userId,
      p_date: today,
      p_tier: tier,
      p_model: result.model,
      p_prompt: result.usage.promptTokens,
      p_output: result.usage.outputTokens,
    })
    .then(() => {})
    .catch(() => {});

  return result.text;
}

// 從 request body 讀「是否用付費」；預設 false（免費優先）
export function readUsePaid(body: any): boolean {
  return body?.usePaid === true;
}
