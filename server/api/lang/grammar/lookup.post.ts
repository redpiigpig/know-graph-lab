/**
 * POST /api/lang/grammar/lookup
 * Body: { language:'en', query, usePaid? }
 * 「文法地圖查詢」：使用者打字發問或輸入詞句 → 判斷屬於哪一/哪幾個文法點。
 *  1) 先做關鍵字比對（即時、零成本）
 *  2) 再用 AI（NVIDIA→Gemini）分類到策展 topic id，並用繁中說明是哪個文法點、為什麼
 * 回傳 { matches: [{id,title,category,why}], answer }，id 皆為策展 topic 的有效 id。
 */
import { lookupIndex, topicById, categoryOf } from "~/server/data/enGrammar";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, query, usePaid } = (await readBody(event)) as {
    language: string;
    query: string;
    usePaid?: boolean;
  };
  if (language !== "en") throw createError({ statusCode: 400, message: "文法地圖目前只支援英文" });
  const qy = (query || "").trim();
  if (!qy) throw createError({ statusCode: 400, message: "請輸入問題或要查的句子/文法點" });

  const index = lookupIndex();

  // 1) 關鍵字比對（命中越多越前面）
  const lc = qy.toLowerCase();
  const scored = index
    .map((t) => {
      let score = 0;
      for (const k of t.keywords) if (lc.includes(k.toLowerCase())) score += k.length >= 4 ? 2 : 1;
      if (lc.includes(t.en.toLowerCase())) score += 3;
      if (qy.includes(t.title)) score += 3;
      return { id: t.id, score };
    })
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  // 2) AI 分類（把策展清單給模型，限定只能回有效 id）
  const list = index.map((t) => `${t.id} = ${t.title}（${t.en}）／${t.category}`).join("\n");
  let aiIds: string[] = [];
  let answer = "";
  try {
    const raw = await coachGemini(
      {
        system: `你是英文文法導引老師。下面是「文法地圖」的所有文法點清單（id = 中文名（英文）／分類）：
${list}

使用者會用中文或英文打字發問、或貼一個句子/詞。請判斷這個問題最相關的 1–3 個文法點，**只能從上面清單挑 id**。
只輸出 JSON：{ "ids": ["最相關的 topic id", ...], "answer": "用繁體中文一句話說明這屬於哪個文法點、為什麼，必要時點出關鍵規則" }
若完全無關，ids 給空陣列、answer 說明找不到對應文法點。繁體中文不可簡體。`,
        contents: [{ role: "user", parts: [{ text: qy }] }],
        json: true,
        temperature: 0.2,
        maxOutputTokens: 512,
      },
      { usePaid: usePaid === true, userId: user.id, supabase }
    );
    const parsed = parseJsonLoose<{ ids: string[]; answer: string }>(raw);
    aiIds = Array.isArray(parsed.ids) ? parsed.ids.filter((id) => !!topicById(id)) : [];
    answer = parsed.answer || "";
  } catch {
    // AI 失敗就只靠關鍵字結果
  }

  // 合併 AI + 關鍵字結果（AI 優先、去重）
  const orderedIds = [...aiIds, ...scored.map((s) => s.id)].filter((id, i, arr) => arr.indexOf(id) === i).slice(0, 4);
  const matches = orderedIds.map((id) => {
    const t = topicById(id)!;
    return { id, title: t.title, en: t.en, category: categoryOf(id)?.label ?? "", summary: t.summary };
  });

  if (!answer) {
    answer = matches.length ? `這比較接近「${matches[0].title}」。` : "找不到對應的文法點，換個說法或關鍵字再試試。";
  }
  return { matches, answer };
});
