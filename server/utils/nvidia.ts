// ============================================================================
// NVIDIA NIM 呼叫工具（integrate.api.nvidia.com，OpenAI 相容）
//   - 語言教練主引擎（無限量）：qwen/qwen3-next-80b-a3b-instruct（見 DEFAULT_MODEL；
//     /coach 不可用 deepseek-v4-flash — 長期 429）
//   - 介面對齊 gemini.ts 的 GeminiCallOpts / GeminiResult，方便 coach-ai 共用
//   - 會把 Gemini 風格 contents（role user/model + parts）轉成 OpenAI messages
//   - deepseek 會吐 <think>…</think> 推理區塊，回傳前剝除
// ============================================================================
import type { GeminiCallOpts, GeminiResult } from "~/server/utils/gemini";

const NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions";
const DEFAULT_MODEL = "qwen/qwen3-next-80b-a3b-instruct";
const THINK_RE = /<think>[\s\S]*?<\/think>/gi;

let keyCursor = 0;

// Gemini contents → OpenAI messages（只取 text part；fileData 由呼叫端先擋掉走 Gemini）
function toMessages(opts: GeminiCallOpts): { role: string; content: string }[] {
  const msgs: { role: string; content: string }[] = [];
  if (opts.system) msgs.push({ role: "system", content: opts.system });
  for (const c of opts.contents || []) {
    const text = (c.parts || [])
      .map((p: any) => (typeof p?.text === "string" ? p.text : ""))
      .filter(Boolean)
      .join("\n");
    if (!text) continue;
    msgs.push({ role: c.role === "model" ? "assistant" : "user", content: text });
  }
  return msgs;
}

/**
 * NVIDIA NIM chat 呼叫。回傳文字 + token 用量（介面同 callGeminiFull）。
 * 所有 key 都失敗時拋錯（呼叫端會落到 Gemini fallback）。
 */
export async function callNvidiaFull(opts: GeminiCallOpts & { keys?: string[] }): Promise<GeminiResult> {
  const config = useRuntimeConfig();
  const keys: string[] = opts.keys?.length
    ? opts.keys
    : ((config.nvidiaApiKeys as string[]) || []);
  if (!keys.length) throw createError({ statusCode: 500, message: "未設定 NVIDIA API key" });

  const model = (config.nvidiaModel as string) || DEFAULT_MODEL;
  const body: any = {
    model,
    messages: toMessages(opts),
    temperature: opts.temperature ?? 0.8,
    max_tokens: opts.maxOutputTokens ?? 2048,
  };
  if (opts.json) body.response_format = { type: "json_object" };

  let lastErr = "";
  for (let i = 0; i < keys.length; i++) {
    const key = keys[(keyCursor + i) % keys.length];
    try {
      const res = await fetch(NVIDIA_URL, {
        method: "POST",
        headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (res.status === 429 || res.status === 503) {
        lastErr = `NVIDIA ${res.status}`;
        continue; // 換下一把 key
      }
      if (!res.ok) {
        const t = await res.text().catch(() => "");
        lastErr = `NVIDIA ${res.status}: ${t.slice(0, 200)}`;
        continue;
      }

      const data = await res.json();
      const raw = data?.choices?.[0]?.message?.content;
      const text = typeof raw === "string" ? raw.replace(THINK_RE, "").trim() : "";
      if (!text) {
        lastErr = "NVIDIA 回傳空內容";
        continue;
      }
      keyCursor = (keyCursor + i + 1) % keys.length;
      const u = data?.usage ?? {};
      return {
        text,
        model,
        usage: {
          promptTokens: u.prompt_tokens ?? 0,
          outputTokens: u.completion_tokens ?? 0,
          totalTokens: u.total_tokens ?? 0,
        },
      };
    } catch (e: any) {
      lastErr = e?.message || "fetch failed";
    }
  }

  throw createError({ statusCode: 502, message: `NVIDIA 呼叫失敗：${lastErr}` });
}
