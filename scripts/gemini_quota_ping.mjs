import fs from "node:fs";

function readEnv() {
  const env = { ...process.env };
  if (fs.existsSync(".env")) {
    for (const line of fs.readFileSync(".env", "utf8").split(/\r?\n/)) {
      if (!line || line.trimStart().startsWith("#")) continue;
      const i = line.indexOf("=");
      if (i < 0) continue;
      env[line.slice(0, i)] = line.slice(i + 1).trim().replace(/^["']|["']$/g, "");
    }
  }
  return env;
}

function findGeminiKeys(env) {
  const keys = [];
  const names = ["GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY"];
  for (const name of names) {
    if (env[name]) keys.push(...env[name].split(",").map((s) => s.trim()).filter(Boolean));
  }
  for (const [name, value] of Object.entries(env)) {
    if (/^(GEMINI_API_KEY|Gemini_API_Key|GOOGLE_API_KEY)_\d+$/i.test(name) && value) {
      keys.push(value.trim());
    }
  }
  return [...new Set(keys)];
}

const keys = findGeminiKeys(readEnv());
console.log(`gemini_keys=${keys.length}`);

for (const [idx, key] of keys.entries()) {
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${encodeURIComponent(key)}`;
  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: "Reply with OK." }] }],
        generationConfig: { maxOutputTokens: 8, temperature: 0 },
      }),
      signal: AbortSignal.timeout(20000),
    });
    const text = await res.text();
    let code = "";
    let message = "";
    try {
      const json = JSON.parse(text);
      code = json?.error?.status || "";
      message = json?.error?.message || json?.candidates?.[0]?.finishReason || "";
    } catch {}
    console.log(
      `key#${idx + 1}: status=${res.status} ${res.ok ? "OK" : "FAIL"} code=${code} msg=${String(message).slice(0, 140)}`
    );
  } catch (err) {
    console.log(`key#${idx + 1}: NETWORK_FAIL ${err?.code || err?.name || err}`);
  }
}
