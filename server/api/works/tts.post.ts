/**
 * Gemini 雲端語音合成（TTS）——把一段文字念成語音，串流回瀏覽器。
 *
 *   POST /api/works/tts   { text, voice?, style? }  →  audio/wav
 *
 * Gemini TTS 回傳的是「原始 PCM（16-bit LE, mono, 24kHz）」的 base64，瀏覽器
 * 不能直接播；這裡在後端包上 44-byte WAV 檔頭再回傳，前端拿到就是可播的 WAV。
 * 不落地存檔（符合 Supabase/R2 禁存語音的空間限制），逐段即時生成、即時串流。
 * key 沿用共用 Gemini 池，429/403 自動換下一把。
 */
const BASE = "https://generativelanguage.googleapis.com/v1beta/models";
const VALID_VOICES = new Set([
  "Kore", "Aoede", "Leda", "Charon", "Zephyr", "Puck", "Orus",
  "Callirrhoe", "Fenrir", "Autonoe", "Enceladus", "Sulafat",
]);
let ttsCursor = 0;

// 原始 PCM → WAV：補上標準 44-byte RIFF/WAVE 檔頭
function pcmToWav(pcm: Buffer, sampleRate: number, channels = 1, bits = 16): Buffer {
  const byteRate = (sampleRate * channels * bits) / 8;
  const blockAlign = (channels * bits) / 8;
  const h = Buffer.alloc(44);
  h.write("RIFF", 0);
  h.writeUInt32LE(36 + pcm.length, 4);
  h.write("WAVE", 8);
  h.write("fmt ", 12);
  h.writeUInt32LE(16, 16);
  h.writeUInt16LE(1, 20); // PCM
  h.writeUInt16LE(channels, 22);
  h.writeUInt32LE(sampleRate, 24);
  h.writeUInt32LE(byteRate, 28);
  h.writeUInt16LE(blockAlign, 32);
  h.writeUInt16LE(bits, 34);
  h.write("data", 36);
  h.writeUInt32LE(pcm.length, 40);
  return Buffer.concat([h, pcm]);
}

export default defineEventHandler(async (event) => {
  const body = await readBody<{ text?: string; voice?: string; style?: string }>(event);
  const raw = (body?.text ?? "").trim();
  if (!raw) throw createError({ statusCode: 400, message: "缺少文字" });
  // 單次上限，避免過長請求拖慢延遲／爆量；前端已分段送。
  const text = raw.slice(0, 4000);

  const config = useRuntimeConfig();
  const keys = ((config.geminiApiKeys as string[]) ?? []).filter(Boolean);
  if (!keys.length) throw createError({ statusCode: 500, message: "未設定 Gemini API key" });

  const model = process.env.GEMINI_TTS_MODEL || "gemini-2.5-flash-preview-tts";
  const voice = body?.voice && VALID_VOICES.has(body.voice) ? body.voice : "Kore";
  const style = (body?.style ?? "以沉穩、自然、溫暖的語氣，用臺灣標準國語朗讀下面的文字：").trim();

  const reqBody = {
    contents: [{ parts: [{ text: `${style}\n\n${text}` }] }],
    generationConfig: {
      responseModalities: ["AUDIO"],
      speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } } },
    },
  };

  // preview TTS 偶爾回傳「無音訊」的候選（非配額問題），故多試幾輪並輪替 key。
  const MAX_TRIES = keys.length + 1;
  let lastErr = "";
  let quotaCount = 0;
  let attempts = 0;
  for (let t = 0; t < MAX_TRIES; t++) {
    const key = keys[(ttsCursor + t) % keys.length];
    attempts++;
    try {
      const res = await fetch(`${BASE}/${model}:generateContent?key=${key}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reqBody),
      });
      if (res.status === 429 || res.status === 403) { lastErr = `quota/forbidden (${res.status})`; quotaCount++; continue; }
      if (!res.ok) {
        const e: any = await res.json().catch(() => ({}));
        lastErr = e?.error?.message || `Gemini ${res.status}`;
        continue;
      }
      const data: any = await res.json();
      const part = data?.candidates?.[0]?.content?.parts?.find((p: any) => p?.inlineData?.data);
      const b64 = part?.inlineData?.data;
      if (!b64) { lastErr = `Gemini 回傳空音訊（finishReason=${data?.candidates?.[0]?.finishReason ?? '?'}）`; continue; }
      const mime: string = part.inlineData.mimeType || "";
      const rate = parseInt(mime.match(/rate=(\d+)/)?.[1] || "24000", 10);
      const wav = pcmToWav(Buffer.from(b64, "base64"), rate);
      ttsCursor = (ttsCursor + t + 1) % keys.length;
      setHeader(event, "Content-Type", "audio/wav");
      setHeader(event, "Content-Length", String(wav.length));
      setHeader(event, "Cache-Control", "no-store");
      return wav;
    } catch (e: any) {
      lastErr = e?.message || "fetch failed";
    }
  }

  if (quotaCount === attempts) throw createError({ statusCode: 429, data: { code: "quota_exhausted" }, message: `Gemini 額度已用完：${lastErr}` });
  throw createError({ statusCode: 502, message: `語音合成失敗：${lastErr}` });
});
