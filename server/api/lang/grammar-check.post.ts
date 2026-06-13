/**
 * POST /api/lang/grammar-check  { language, text }
 * 規則式寫作文法檢查（零 AI）：代理到自架 LanguageTool 服務的 /v2/check。
 * LanguageTool 是開源、上千條規則、無 LLM、穩定無額度限制——使用者「怕 API 爆」的解。
 * 需設 env LANGUAGETOOL_URL（Zeabur 加一個 erikvl87/languagetool Docker 服務）。
 * 只支援現代活語言（en/de/fr…）；古典語（grc/la/hbo）LanguageTool 不支援 → available:false。
 */
const LT_LANG: Record<string, string> = {
  en: "en-US", de: "de-DE", fr: "fr", es: "es", pt: "pt-PT", nl: "nl",
  it: "it", ru: "ru", pl: "pl", ja: "ja-JP", zh: "zh-CN",
};

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const { language, text } = (await readBody(event)) as { language: string; text: string };
  const base = (useRuntimeConfig().languageToolUrl as string) || "";
  const ltLang = LT_LANG[language];

  if (!base) return { available: false, reason: "未設定 LANGUAGETOOL_URL（請在 Zeabur 加一個自架 LanguageTool 服務）", matches: [] };
  if (!ltLang) return { available: false, reason: "LanguageTool 不支援此語言（古典語請用詞形判析／經文重組）", matches: [] };
  if (!text?.trim()) return { available: true, matches: [], text: "" };

  try {
    const r = await $fetch<any>(`${base.replace(/\/$/, "")}/v2/check`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ language: ltLang, text, level: "picky" }).toString(),
      timeout: 15000,
    });
    const matches = (r.matches || []).map((m: any) => ({
      offset: m.offset,
      length: m.length,
      message: m.message,
      shortMessage: m.shortMessage || "",
      bad: text.slice(m.offset, m.offset + m.length),
      replacements: (m.replacements || []).slice(0, 5).map((x: any) => x.value),
      rule: m.rule?.category?.name || m.rule?.id || "",
      type: m.rule?.issueType || "",
    }));
    return { available: true, language: ltLang, matches, count: matches.length };
  } catch (e: any) {
    throw createError({ statusCode: 502, message: `LanguageTool 連線失敗：${String(e?.message || e).slice(0, 120)}` });
  }
});
