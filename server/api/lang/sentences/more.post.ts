/**
 * POST /api/lang/sentences/more
 * Body: { language:'en', scenario, customSituation?, seen?: string[], usePaid? }
 * 「再給我幾句」/「換類似句」：AI（NVIDIA 主→Gemini）依情境生成更多實用句，
 * 避開 seen（已出現的英文句）。無限延伸寫作/口說例句。
 */
import { scenarioByKey } from "~/server/data/enSentences";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, scenario, customSituation, seen, count, usePaid, kind, length, topic: topicIn } = (await readBody(event)) as {
    language: string;
    scenario?: string;
    customSituation?: string;
    seen?: string[];
    count?: number;
    usePaid?: boolean;
    kind?: "sentence" | "passage";
    length?: "短文" | "長文";
    topic?: string;
  };
  if (language !== "en") throw createError({ statusCode: 400, message: "情境句目前只支援英文" });
  const avoid = (seen || []).slice(0, 20).join(" / ");

  // ── 範文模式：生成一篇「短文/長文」 ──
  if (kind === "passage") {
    const len = length === "長文" ? "長文" : "短文";
    const topic = topicIn || customSituation || "分享想法";
    const sizing = len === "長文"
      ? "寫一段較完整的範文（約 100–160 字、6–10 句），把想法循序展開（鋪陳→理由/細節→轉折或反方→收束）"
      : "寫一篇短文（約 40–60 字、3–4 句），精簡有力";
    const raw = await coachGemini(
      {
        system: `你是英文寫作/口說教練，為做宗教研究、英文 B2+ 的學生示範「${len}」範文。
主題：「${topic}」。${sizing}。內容道地、可直接拿來模仿，題材偏人文/宗教研究或留學旅遊學術情境。
只輸出 JSON：{ "item": { "prompt": "繁中：這篇要完成的任務/情境", "en": "範文（英文）", "zh": "中譯", "note": "重點句型/用語提示（繁中）" } }
繁體中文不可簡體。`,
        contents: [{ role: "user", parts: [{ text: `請給我一篇「${topic}」的${len}範文。${avoid ? `不要和這些重複：${avoid}` : ""}` }] }],
        json: true,
        temperature: 0.7,
        maxOutputTokens: len === "長文" ? 1200 : 700,
      },
      { usePaid: usePaid === true, userId: user.id, supabase }
    );
    let item: any;
    try {
      const p = parseJsonLoose<{ item: any }>(raw).item;
      if (!p?.en) throw new Error("empty");
      item = { id: `aip-${Date.now()}`, topic, topicEn: topic, length: len, prompt: p.prompt || "", en: String(p.en).trim(), zh: p.zh || "", note: p.note || "" };
    } catch {
      throw createError({ statusCode: 502, message: "範文生成失敗，請重試" });
    }
    return { item };
  }

  // ── 句子模式（預設）：生成 N 句實用句 ──
  const sc = scenario ? scenarioByKey(scenario) : undefined;
  const topic = sc ? sc.label : customSituation || "日常實用英語";
  const n = Math.min(10, Math.max(3, count || 5));

  const raw = await coachGemini(
    {
      system: `你是英文口說/寫作教練，為一位做宗教研究、英文 B2+ 的學生出「情境實用句」。
情境主題：「${topic}」。${sc ? `情境說明：${sc.blurb}` : ""}
只輸出 JSON：{ "items": [ { "situation": "繁體中文寫『你想表達什麼/情境』", "en": "道地的英文範例句（建議解答）", "zh": "中譯", "note": "可選：用法/禮貌/道地提示（繁中）" } ] }
要求：出 ${n} 句**實用、口語、道地**的句子，難度 B2+，貼近真實情境、可直接拿來用。${avoid ? `不要重複這些已出現的句子：${avoid}` : ""}繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: `請給我 ${n} 句「${topic}」的實用句。` }] }],
      json: true,
      temperature: 0.7,
      maxOutputTokens: 1536,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let items: any[] = [];
  try {
    items = (parseJsonLoose<{ items: any[] }>(raw).items || [])
      .filter((x) => x?.en)
      .map((x, i) => ({
        id: `ai-${Date.now()}-${i}`,
        situation: x.situation || "",
        en: String(x.en).trim(),
        zh: x.zh || "",
        note: x.note || "",
      }));
  } catch {
    throw createError({ statusCode: 502, message: "生成失敗，請重試" });
  }
  if (!items.length) throw createError({ statusCode: 502, message: "未生成句子，請重試" });
  return { items };
});
