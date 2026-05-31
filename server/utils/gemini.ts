// ============================================================================
// Gemini REST 呼叫共用工具（含 4 把 key 輪替 + quota 退避）
// ============================================================================

type Part = { text: string };
type Content = { role: "user" | "model"; parts: Part[] };

export interface GeminiCallOpts {
  model?: string;           // 預設 gemini-2.5-flash
  system?: string;          // system instruction
  contents: Content[];
  temperature?: number;
  maxOutputTokens?: number;
  json?: boolean;           // responseMimeType application/json
}

const BASE = "https://generativelanguage.googleapis.com/v1beta/models";

// 模組級的輪替指標，讓連續請求分散到不同 key
let keyCursor = 0;

export async function callGemini(opts: GeminiCallOpts): Promise<string> {
  const config = useRuntimeConfig();
  const keys: string[] =
    (config.geminiApiKeys as string[])?.length
      ? (config.geminiApiKeys as string[])
      : [config.geminiApiKey as string].filter(Boolean);

  if (!keys.length) {
    throw createError({ statusCode: 500, message: "未設定 Gemini API key" });
  }

  const model = opts.model ?? "gemini-2.5-flash";
  const body: any = {
    contents: opts.contents,
    generationConfig: {
      temperature: opts.temperature ?? 0.8,
      maxOutputTokens: opts.maxOutputTokens ?? 2048,
      ...(opts.json ? { responseMimeType: "application/json" } : {}),
    },
  };
  if (opts.system) {
    body.systemInstruction = { parts: [{ text: opts.system }] };
  }

  let lastErr = "";
  // 從目前游標開始，最多試完所有 key
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
        continue;
      }

      const data = await res.json();
      const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!text) {
        lastErr = "Gemini 回傳空內容";
        continue;
      }
      // 成功 → 下一次從下一把 key 開始，平均分攤
      keyCursor = (keyCursor + i + 1) % keys.length;
      return text;
    } catch (e: any) {
      lastErr = e?.message || "fetch failed";
    }
  }

  throw createError({ statusCode: 502, message: `Gemini 呼叫失敗：${lastErr}` });
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
