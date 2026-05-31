// ============================================================================
// Gemini REST 呼叫共用工具（key 輪替 + quota 退避 + token 用量回傳）
// ============================================================================

// Part 可為文字或 fileData（如 YouTube URL：{ fileData: { fileUri, mimeType } }）
type Part = { text: string } | { fileData: { fileUri: string; mimeType?: string } } | Record<string, any>;
type Content = { role: "user" | "model"; parts: Part[] };

export interface GeminiCallOpts {
  model?: string;
  system?: string;
  contents: Content[];
  temperature?: number;
  maxOutputTokens?: number;
  json?: boolean;           // responseMimeType application/json
  keys?: string[];          // 指定 key 池（語言教練用來分免費/付費）；省略則用共用池
}

export interface GeminiUsage {
  promptTokens: number;
  outputTokens: number;
  totalTokens: number;
}
export interface GeminiResult {
  text: string;
  usage: GeminiUsage;
  model: string;
}

const BASE = "https://generativelanguage.googleapis.com/v1beta/models";
let keyCursor = 0;

// 完整版：回傳文字 + token 用量。所有 key 都 quota 用盡時拋 code='quota_exhausted'。
export async function callGeminiFull(opts: GeminiCallOpts): Promise<GeminiResult> {
  const config = useRuntimeConfig();
  const keys: string[] = opts.keys?.length
    ? opts.keys
    : (config.geminiApiKeys as string[])?.length
      ? (config.geminiApiKeys as string[])
      : [config.geminiApiKey as string].filter(Boolean);

  if (!keys.length) throw createError({ statusCode: 500, message: "未設定 Gemini API key" });

  const model = opts.model ?? (config.geminiModel as string) ?? "gemini-flash-latest";
  const body: any = {
    contents: opts.contents,
    generationConfig: {
      temperature: opts.temperature ?? 0.8,
      maxOutputTokens: opts.maxOutputTokens ?? 2048,
      ...(opts.json ? { responseMimeType: "application/json" } : {}),
    },
  };
  if (opts.system) body.systemInstruction = { parts: [{ text: opts.system }] };

  let lastErr = "";
  let allQuota = true; // 是否每一把 key 都是 quota 問題（用來判斷要不要提示切換付費）

  for (let i = 0; i < keys.length; i++) {
    const key = keys[(keyCursor + i) % keys.length];
    try {
      const res = await fetch(`${BASE}/${model}:generateContent?key=${key}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (res.status === 429 || res.status === 403) {
        lastErr = `quota/forbidden (${res.status})`;
        continue; // 換下一把 key
      }
      if (!res.ok) {
        const e = await res.json().catch(() => ({}));
        lastErr = e?.error?.message || `Gemini ${res.status}`;
        allQuota = false;
        continue;
      }

      const data = await res.json();
      const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!text) {
        lastErr = "Gemini 回傳空內容";
        allQuota = false;
        continue;
      }
      keyCursor = (keyCursor + i + 1) % keys.length;
      const u = data?.usageMetadata ?? {};
      return {
        text,
        model,
        usage: {
          promptTokens: u.promptTokenCount ?? 0,
          outputTokens: (u.candidatesTokenCount ?? 0) + (u.thoughtsTokenCount ?? 0),
          totalTokens: u.totalTokenCount ?? 0,
        },
      };
    } catch (e: any) {
      lastErr = e?.message || "fetch failed";
      allQuota = false;
    }
  }

  if (allQuota) {
    throw createError({ statusCode: 429, data: { code: "quota_exhausted" }, message: `Gemini 額度已用完：${lastErr}` });
  }
  throw createError({ statusCode: 502, message: `Gemini 呼叫失敗：${lastErr}` });
}

// 精簡版：只回文字（向後相容既有呼叫端，如 genealogy parse）
export async function callGemini(opts: GeminiCallOpts): Promise<string> {
  return (await callGeminiFull(opts)).text;
}

// 容錯解析 JSON（去除可能的 markdown 圍欄）
export function parseJsonLoose<T = any>(text: string): T {
  let t = text.trim();
  if (t.startsWith("```")) {
    t = t.replace(/^```(?:json)?/i, "").replace(/```$/i, "").trim();
  }
  const first = t.indexOf("{");
  const last = t.lastIndexOf("}");
  if (first > 0 || last < t.length - 1) {
    if (first !== -1 && last !== -1) t = t.slice(first, last + 1);
  }
  return JSON.parse(t) as T;
}
