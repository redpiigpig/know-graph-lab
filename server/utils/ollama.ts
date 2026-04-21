/**
 * Ollama local AI utility
 * Assumes Ollama is running at localhost:11434
 */

const OLLAMA_BASE = "http://localhost:11434";
const DEFAULT_MODEL = "qwen2.5:7b";
const EMBED_MODEL = "nomic-embed-text";

export async function ollamaChat(
  prompt: string,
  model = DEFAULT_MODEL,
  systemPrompt?: string
): Promise<string> {
  const messages: any[] = [];
  if (systemPrompt) messages.push({ role: "system", content: systemPrompt });
  messages.push({ role: "user", content: prompt });

  const res = await fetch(`${OLLAMA_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model, messages, stream: false }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Ollama chat error: ${err}`);
  }

  const data = await res.json() as any;
  return data.message?.content ?? "";
}

export async function ollamaEmbed(text: string): Promise<number[]> {
  const res = await fetch(`${OLLAMA_BASE}/api/embeddings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: EMBED_MODEL, prompt: text }),
  });

  if (!res.ok) throw new Error(`Ollama embed error: ${await res.text()}`);
  const data = await res.json() as any;
  return data.embedding ?? [];
}

export async function ollamaChatWithImage(
  imageBase64: string,
  prompt: string,
  model = "qwen2.5vl:7b"
): Promise<string> {
  const res = await fetch(`${OLLAMA_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      stream: false,
      messages: [{
        role: "user",
        content: prompt,
        images: [imageBase64],
      }],
    }),
  });

  if (!res.ok) throw new Error(`Ollama vision error: ${await res.text()}`);
  const data = await res.json() as any;
  return data.message?.content ?? "";
}

export async function ollamaStatus(): Promise<{ ok: boolean; models: string[] }> {
  try {
    const res = await fetch(`${OLLAMA_BASE}/api/tags`);
    if (!res.ok) return { ok: false, models: [] };
    const data = await res.json() as any;
    return { ok: true, models: (data.models ?? []).map((m: any) => m.name) };
  } catch {
    return { ok: false, models: [] };
  }
}

export function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] ** 2;
    normB += b[i] ** 2;
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB) + 1e-10);
}
